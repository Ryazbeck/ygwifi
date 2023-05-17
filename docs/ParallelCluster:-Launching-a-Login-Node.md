## Background

High Performance Computing (HPC) clusters typically consist of the following nodes:

* **Compute nodes:** These nodes are used to execute jobs submitted by the user. They may vary in characteristics (processing power, storage capability etc.) depending on the nature of jobs that will be executed in them
* **Head node:** This node manages the scheduling and monitoring of jobs and compute nodes.
* **Login node(s):** These nodes provide an interface for the user to submit jobs for execution

ParallelCluster supports creation of a HPC cluster that consists of a single head node and compute nodes. Job submissions (both batch and interactive) can be done from the head node.
The steps listed in the next section show how to launch a login node for an existing cluster.
* * *

## Launching a login node in ParallelCluster

The following are the general steps needed to launch a login node in a cluster:

* Create a [security group](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-security-groups.html) for the login node
* Update the cluster configuration to include the login node security group
* Launch the login node using the same AMI and in the same VPC as the head node
* Create access to Slurm and job results from the head node using NFS
* Copy Munge key from head node and start the Munge daemon
* Add cluster search domain for node name resolution

### Create security groups for the login node

The security groups will be used to dictate the flow of traffic between the login node and other cluster nodes
Two security groups will be needed:

* A security group to allow SSH access as well as traffic to the login node from the cluster nodes (referred to as “**LoginNode-Bastion**” security group from here on)
* A security group to allow traffic to the cluster nodes from the login node (referred to as “**LoginNode-Cluster**” security group from here on)

To create the **LoginNode-Bastion** and the **LoginNode-Cluster** security groups, the head node’s VPC ID will be needed.
To get the head node’s VPC ID, you can run the command:

```
aws ec2 describe-instances \
    --filters \
    Name=tag:parallelcluster:node-type,Values=HeadNode \
    Name=tag:parallelcluster:cluster-name,Values=<CLUSTER_NAME> \
    --query \
    "Reservations[0].Instances[0].VpcId"
```

To create the **LoginNode-Bastion** security group, use this CLI command:

```
aws ec2 create-security-group \
    --description "ClusterName LoginNode-Bastion security group" \
    --group-name <LoginNode-Bastion Security Group Name> \
    --vpc-id <HEADNODE_VPC_ID>
```

e.g.

```
aws ec2 create-security-group \           
    --description "ClusterName LoginNode-Bastion security group" \
    --group-name LoginNode-Bastion-SG \
    --vpc-id vpc-123456789
```

Take note of the security group ID as it will be used when assigning rules to the security group.
To create the **LoginNode-Cluster** security group, use a similar command with a different security group name:

```
aws ec2 create-security-group \
    --description "ClusterName LoginNode-Cluster security group" \
    --group-name <LoginNode-Cluster Security Group Name> \
    --vpc-id <HEADNODE_VPC_ID>
```

Take note of the security group ID as it will be used when assigning rules to the security group.

The **LoginNode-Bastion** security group should allow traffic based on these rules:

* ***Allow SSH*** Traffic from any source (0.0.0.0/0) or specific IP based on the cluster configuration

```
aws ec2 authorize-security-group-ingress \
    --group-id <LoginNode-Bastion Security Group ID> \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0
```

* ***Allow All*** Traffic from the **LoginNode-Cluster** security group

```
aws ec2 authorize-security-group-ingress \
    --group-id <LoginNode-Bastion Security Group ID> \
    --protocol -1 \
    --port -1 \
    --source-group <LoginNode-Cluster Security Group ID>
```

The **LoginNode-Cluster** security group should allow traffic based on these rules:

```
aws ec2 authorize-security-group-ingress \
    --group-id <LoginNode-Cluster Security Group ID> \
    --protocol -1 \
    --port -1 \
    --source-group <LoginNode-Bastion Security Group ID>
```

### Update the cluster configuration with the **LoginNode-Cluster** security group

Update the cluster configuration to include the **LoginNode-Cluster** security group as an additional security group e.g. [HeadNode-AdditionalSecurityGroups](https://docs.aws.amazon.com/parallelcluster/latest/ug/HeadNode-v3.html#yaml-HeadNode-Networking-AdditionalSecurityGroups) / [Scheduling-AdditionalSecurityGroups](https://docs.aws.amazon.com/parallelcluster/latest/ug/Scheduling-v3.html#yaml-Scheduling-SlurmQueues-Networking-AdditionalSecurityGroups)

```
HeadNode:
  ...
  Networking:
    ...
    AdditionalSecurityGroups:
      - <LoginNode-Cluster Security Group ID>
...
Scheduling:
  Scheduler: slurm
  SlurmQueues:
  - Name: queue
    Networking:
      ...
      AdditionalSecurityGroups:
      - <LoginNode-Cluster Security Group ID>
      ...
```

This will ensure that the login node security group dependency will not prevent cluster deletion.

Run the `pcluster update-cluster` command.

### Launch the login node

* Use the same AMI and subnet as the head node
* It is recommended to use the same subnet (AZ) as the head node to reduce latency
* To get the above information you can use this command:

```
aws ec2 describe-instances \
    --filters \
    Name=tag:parallelcluster:node-type,Values=HeadNode \
    Name=tag:parallelcluster:cluster-name,Values={CLUSTER_NAME} \
    | grep -iE "ImageId|SubnetId|VpcId|KeyName|InstanceType"
```

* The security group created earlier should also be used during instance creation

To launch the instance, the `run-instances` command can be used.

```
aws ec2 run-instances \
    --subnet-id "<HEADNODE_SUBNET_ID>" \
    --image-id "<HEADNODE_IMAGE_ID>" \
    --key-name "<KEYNAME>" \
    --instance-type "<INSTANCE_TYPE>" \
    --security-group-ids "<LoginNode-Bastion Security Group ID>" \
    --tag-specifications 'ResourceType="instance",Tags=[{Key="Name",Value="LoginNode"}]'
```

### Create access to Slurm commands and job results from the login node using NFS

To ensure that Slurm commands and job results can be accessed by the login node, the Slurm installation folder (`/opt/slurm`) and Home folder (`/home`) in the head node will be mounted to the login node using NFS

```
sudo mkdir -p /opt/slurm
sudo mount --verbose -t nfs <HEADNODE_INTERNAL_IP>:/opt/slurm /opt/slurm
sudo mount --verbose -t nfs <HEADNODE_INTERNAL_IP>:/home /home
```

E.g.

```
sudo mkdir -p /opt/slurm
sudo mount --verbose -t nfs 10.0.0.125:/opt/slurm /opt/slurm
sudo mount --verbose -t nfs 10.0.0.125:/home /home
```

The head node’s private IP address can be obtained using ParallelCluster CLI `describe-cluster-instances` command
E.g.

```
pcluster describe-cluster-instances \
    --cluster-name <CLUSTER_NAME> \
    --node-type HeadNode \
    --region <REGION> \
    --query "instances[0].privateIpAddress"
```

To ensure that the directories are mounted even after login node reboots, add this entry in the `/etc/fstab` file

```
{HEADNODE_PRIVATE_IP}:/opt/slurm  /opt/slurm  nfs  rw  0  0
{HEADNODE_PRIVATE_IP}:/home  /home  nfs  rw  0  0
```


Add this script in the `/etc/profile.d/slurm.sh` file to add the Slurm installation path. Create the file if it doesn’t exist (Remember to create the file in the `/etc/profile.d` folder)

```
#
# slurm.sh:
#   Setup slurm environment variables
#

PATH=$PATH:/opt/slurm/bin
MANPATH=$MANPATH:/opt/slurm/share/man
```

You may need to login/ssh into the head node again to ensure that the new PATH variable adopts the new values
Alternatively you can run this command:

```
source /etc/profile.d/slurm.sh
```

### Copy Munge key to authenticate with head node

The Munge Key is used for authentication of communications between Slurm components. All nodes in the cluster must be configured with the same `munge.key` file. To ensure that the login node can submit jobs and interact with other Slurm components, it must have a running Munge daemon that uses the same Munge key as other nodes in the cluster.

Copy munge key from shared dir
For **alinux2**:

```
sudo cp /home/ec2-user/.munge/.munge.key /etc/munge/munge.key
```

For **centos7:**

```
sudo cp /home/centos/.munge/.munge.key /etc/munge/munge.key
```

For **ubuntu 1804** and **ubuntu 2004**:

```
sudo cp /home/ubuntu/.munge/.munge.key /etc/munge/munge.key
```

Set ownership and permission on the key

```
sudo chown munge:munge /etc/munge/munge.key
sudo chmod 0600 /etc/munge/munge.key
```

Ensure that the munge daemon is up

```
sudo systemctl enable munge
sudo systemctl start munge
```

The diagram below shows the configuration of security groups and expected daemons that will run in each cluster node.

![PCluster-LoginNode (4) (1)](https://user-images.githubusercontent.com/16361787/213747354-d308b94e-d5aa-42f3-9c60-3b702614a9d0.jpg)


### Add cluster search domain for node name resolution

To ensure that the login node can resolve the DNS names of the cluster nodes, run the following commands which add the DNS resolver entry when the network manager starts

For **centos7** and **alinux2:**

Add the following line to the `/etc/dhcp/dhclient.conf` file to ensure that the cluster’s search domain is used by the network manager.

```
...
append domain-name " {CLUSTER_NAME_LOWERCASE}.pcluster.";
...
```

To ensure the network manager uses the additional DNS resolver, restart the network manager

```
sudo systemctl restart network
```


For ***Ubuntu1804*** and ***Ubuntu2004*:**

Add the following line to the `/etc/systemd/resolved.conf` file to ensure that the “Resolve” section has a “Domains” entry with the cluster’s search domain.

```
[Resolve]
...
Domains=<CLUSTER_NAME_LOWERCASE>.pcluster.
...
```

Restart the `systemd-resolved` service to ensure that the search domain is added to the `/etc/resolv.conf` file.

```
sudo service systemd-resolved restart
```

### Job submission

Jobs can now be submitted from the login node using standard Slurm job submission commands.

```
ssh <LOGIN_NODE_IP_ADDRESS>
```

```
srun <COMMAND>
```

* * *

## Limitations

* The steps in this document focus on Slurm scheduler only
* The login node is not part of the cluster stack. The login node therefore may require maintenance depending on which cluster stack changes are made. For example, deleting the cluster will not automatically delete the login node as well. The login node deletion will have to be handled manually.

* * *

## Common issues associated with use of login nodes

### Slurm user and ID mismatch

The login node and head node needs to have the “slurm” user and corresponding user ID in sync (by default user ID is `401`).
If there is a mismatch of the `slurm` user (and ID) between the login node and head node, errors such as the one below may occur during job submission

```
srun: error: Security violation, slurm message from uid 401
```

To fix this, ensure that the login node and head node have a “slurm” user and the corresponding user ID match.

### Slurm configuration mismatch

Unexpected errors could occur if there is a mismatch between the Slurm configuration in the login node and the one in the head node. The Slurm configuration file can be found at `/opt/slurm/etc/slurm.conf` on both the login node and head node. For example, if the **SlurmUser** attribute in the `slurm.conf` is not set, the following error could occur during job submission from the login node.

```
srun: error: Security violation, slurm message from uid 401
```

The `/opt/slurm/` directory should be mounted to the login node from the head node to avoid this error.
