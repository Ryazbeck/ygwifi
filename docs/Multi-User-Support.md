# ParallelCluster >= 3.1.1

ParallelCluster 3.1 supports multiuser authentication based on Active Directory (AD). 
Starting with v3.1.1 clusters can be configured to use an AD domain managed via one of the AWS Directory Service options like Simple AD or AWS Managed Microsoft AD (MSAD).
To quickly get started with AWS managed AD you can follow our [tutorial](https://docs.aws.amazon.com/parallelcluster/latest/ug/tutorials_05_multi-user-ad.html).

Additional info:
* [What's New: AWS ParallelCluster now supports multi-user environments through AWS Directory Service](https://aws.amazon.com/about-aws/whats-new/2022/02/aws-parallelcluster-environments-directory-service/)
* [AWS HPC Blog - Introducing AWS ParallelCluster multiuser support via Active Directory](https://aws.amazon.com/blogs/hpc/introducing-aws-parallelcluster-multiuser-support-via-active-directory/)



# ParallelCluster < 3.1.1

See [#170](https://github.com/aws/aws-parallelcluster/issues/170#issuecomment-364270330)

This approach is a fairly lightweight way of adding users, it gives all users the same permissions. If you want a more robust multi-user approach I suggest you follow the following guide: https://aws.amazon.com/blogs/opensource/managing-aws-parallelcluster-ssh-users-with-openldap/

In order to create a user for the cluster, that user needs to exist on all the compute nodes. If they don't slurm won't be able to schedule jobs and you won't be able to run mpi jobs across multiple nodes.

1. Create user on the head node & generate a new ssh keypair by running the following commands:

```bash
sudo su
USER=<your desired username>
useradd $USER
su $USER
cd ~
ssh-keygen -t rsa -f ~/.ssh/id_rsa -q -P ""
cat ~/.ssh/id_rsa.pub > ~/.ssh/authorized_keys
chmod 600 ~/.ssh/*
```

2. Create a file in the shared directory (assuming `/shared`) with the user's username and UID like so:

```bash
echo "$USER,`id -u $USER`" >> /shared/userlistfile
```

4. Create a script `create-users.sh` that contains:

```bash
#!/bin/bash

. "/etc/parallelcluster/cfnconfig"

IFS=","

if [ "${cfn_node_type}" = "ComputeFleet" ]; then
    while read USERNAME USERID
    do
        # -M do not create home since head node is exporting /homes via NFS
        # -u to set UID to match what is set on the head node
        if ! [ $(id -u $USERNAME 2>/dev/null || echo -1) -ge 0 ]; then
            useradd -M -u $USERID $USERNAME
        fi
    done < "/shared/userlistfile"
fi
```

5. Upload it to S3 

```bash
$ aws s3 cp create-users.sh s3://[your_bucket]/
```

6. Update your config:

**ParallelCluster 2.X**

```ini
[cluster clustername]
s3_read_resource = arn:aws:s3:::[your_bucket]/*
post_install = s3://[your_bucket]/create-users.sh
```

**ParallelCluster 3.X**

```yaml
CustomActions:
    OnNodeConfigured:
        Script: s3://[your_bucket]/create-users.sh
Iam:
    S3Access:
        - BucketName: [your_bucket]
```

6. Stop and update the running cluster:


## ParallelCluster 2.X

```
CLUSTER_NAME=<name of your cluster>
pcluster stop $CLUSTER_NAME
# no need to wait 
pcluster update $CLUSTER_NAME
pcluster start $CLUSTER_NAME
```

## ParallelCluster 3.X

```bash
CLUSTER_NAME=<name of your cluster>
pcluster update-compute-fleet --cluster-name $CLUSTER_NAME --status STOP_REQUESTED
# no need to wait 
pcluster update-cluster --cluster-name $CLUSTER_NAME --cluster-configuration /path/to/config.yaml
pcluster update-compute-fleet --cluster-name $CLUSTER_NAME --status START_REQUESTED
```

## Troubleshooting

1. If the instances fail to come up, check the `/var/log/parallelcluster/slurm_resume.log` log, look for a line that shows that the instance launching:

```bash
2021-12-07 19:03:33,635 - [slurm_plugin.instance_manager:_update_slurm_node_addrs] - INFO - Nodes are now configured with instances: (x1) ["('hpc5a-dy-hpc6a-1', EC2Instance(id='i-0d7fdc67631e391b5', private_ip='172.31.28.192', hostname='ip-172-31-28-192', launch_time=datetime.datetime(2021, 12, 7, 19, 3, 33, tzinfo=tzlocal()), slurm_node=None))"]
```

Grab the instance id, i.e. `i-0d7fdc67631e391b5`

2. Now look at the log, `ip-172-31-28-192.i-0d7fdc67631e391b5.cloud-init-output`, you can query this from the [Cloudwatch logs console](https://console.aws.amazon.com/cloudwatch/home?#logsV2:log-groups), by going to the log group name `/aws/parallelcluster/[cluster-name]` and searching for the instance id:

![image](https://user-images.githubusercontent.com/5545980/153156154-4349a76e-1c10-4c81-8857-83af8203c14e.png)

This will tell you near the end what the failure was with the PostInstall script.