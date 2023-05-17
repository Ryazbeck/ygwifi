## Description of the problem
ParallelCluster Ubuntu AMIs are shipped with [Unattended Upgrades](https://help.ubuntu.com/community/AutomaticSecurityUpdates) enabled by default. This setting is inherited from the default Ubuntu AMI, that ParallelCluster uses as the starting point for its builds, and is kept unaltered in order to preserve the same packages updates behavior that is configured in the official Ubuntu AMI. The main goal of Unattended Upgrades is to continuously apply updates to the installed Ubuntu packages, security patches included.

Here is the Unattended Upgrades configuration from a ParallelCluster Ubuntu 1804 AMI:
```
$ cat /etc/apt/apt.conf.d/20auto-upgrades
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
$ cat /etc/apt/apt.conf.d/50unattended-upgrades
// Automatically upgrade packages from these (origin:archive) pairs
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}";
    "${distro_id}:${distro_codename}-security";
    "${distro_id}ESMApps:${distro_codename}-apps-security";
    "${distro_id}ESM:${distro_codename}-infra-security";
};
```

Enabling Unattended Upgrades on cluster nodes comes with a minor downside: when compute nodes are launched, a background process is automatically started, once per day, to perform packages updates. HPC jobs started by the scheduler on newly launched compute nodes will contend the host resources for the time it takes to complete packages updates. The overall time depends on the amount of packages that require an update. Of course the older the AMI the bigger is the number of packages that require an update.

Here we are documenting how to build an Ubuntu custom AMI with Unattended Upgrades disabled. **Note that disabling Unattended Upgrades will disable automatic security patching of the installed packages. We advise to do this only if you are aware of the security implications and if the performance of your jobs is affected by the minimal resource utilization caused by the update process.**

## The solution
1. Run the following to retrieve the ParallelCluster Ubuntu AMI to be used as the base AMI:

```
PCLUSTER_VERSION=$(pcluster version)
REGION=eu-west-1  # REPLACE WITH REQUIRED REGION
aws ec2 describe-images --region ${REGION} --filters 'Name=owner-alias,Values=amazon' "Name=name,Values='aws-parallelcluster-${PCLUSTER_VERSION}-ubuntu*'" --query 'sort_by(Images, &CreationDate)[].[Name,ImageId,Architecture]'
```

Here is an example of the expected output for version 2.10.1 and region eu-west-1:
```
[
    [
        "aws-parallelcluster-2.10.1-ubuntu-1804-lts-hvm-arm64-202012160104",
        "ami-0e015ec92f9e262bd",
        "arm64"
    ],
    [
        "aws-parallelcluster-2.10.1-ubuntu-1604-lts-hvm-x86_64-202012221234",
        "ami-0d9c6bf221068c7c3",
        "x86_64"
    ],
    [
        "aws-parallelcluster-2.10.1-ubuntu-1804-lts-hvm-arm64-202012221234",
        "ami-0224e61822e0603ba",
        "arm64"
    ],
    [
        "aws-parallelcluster-2.10.1-ubuntu-1804-lts-hvm-x86_64-202012221234",
        "ami-0cbef8b383ddeff80",
        "x86_64"
    ]
]
```

In the following steps we are going to use the ubuntu-1804 x86 AMI: `ami-0cbef8b383ddeff80`

2. Create a script to disable [Ubuntu Unattended Upgrades](https://help.ubuntu.com/community/AutomaticSecurityUpdates)
```
#!/bin/bash
set -e
sudo sed -i "s/Unattended-Upgrade \"1\"/Unattended-Upgrade \"0\"/g" /etc/apt/apt.conf.d/20auto-upgrades
```

Let's assume you saved this script as `/tmp/disable_unattended_upgrades.sh`

3. Create the custom AMI by running the following command:
```
pcluster createami --ami-id ${AMI_ID} --os ubuntu1804 --post-install file:///tmp/disable_unattended_upgrades.sh --vpc-id ${VPC_ID} --subnet-id ${SUBNET_ID} --region ${REGION}
```
where AMI_ID contains the ID of the base AMI while VPC_ID and SUBNET_ID contain the id of the VPC and the subnet to use for the packer instance that builds the AMI. Note that the subnet requires internet access to build the AMI.

Here is an example of a successful run:
```
❯ pcluster createami --ami-id ami-0cbef8b383ddeff80 --os ubuntu1804 --post-install file:///Users/fdm/disable_unattended_upgrades.sh --vpc-id vpc-047xxx --subnet-id subnet-054xxx
Building AWS ParallelCluster AMI. This could take a while...
Base AMI ID: ami-0cbef8b383ddeff80
Base AMI OS: ubuntu1804
Instance Type: t2.xlarge
Region: eu-west-1
VPC ID: vpc-047xxx
Subnet ID: subnet-054xxx
Template: https://eu-west-1-aws-parallelcluster.s3.eu-west-1.amazonaws.com/templates/aws-parallelcluster-2.10.1.cfn.json
Cookbook: https://eu-west-1-aws-parallelcluster.s3.eu-west-1.amazonaws.com/cookbooks/aws-parallelcluster-cookbook-2.10.1.tgz
Post install script url: file:///Users/fdm/disable_unattended_upgrades.sh
Post install script dir /var/folders/m5/qy5vc5gj48l9n_mfkvfs4zd8hpzrqd/T/tmpujusblr4/script/20201228-144430-disable_unattended_upgrades.sh
Packer log: /var/folders/m5/qy5vc5gj48l9n_mfkvfs4zd8hpzrqd/T/packer.log.20201228-144430.pak091xg
Packer Instance ID: i-065bb719fab6bc653
Packer status: + echo 'RC: 0'	exit code 0

Custom AMI ami-091ad750dcbee3827 created with name custom-ami-aws-parallelcluster-2.10.1-ubuntu-1804-lts-hvm-x86_64-202012281444

To use it, add the following variable to the AWS ParallelCluster config file, under the [cluster ...] section
custom_ami = ami-091ad750dcbee3827
pcluster createami --ami-id ami-0cbef8b383ddeff80 --os ubuntu1804   --vpc-id   5.05s user 4.80s system 2% cpu 7:34.21 total
```

4. Use the [`custom_ami`](https://docs.aws.amazon.com/parallelcluster/latest/ug/cluster-definition.html#custom-ami-section) configuration parameter to use the newly created AMI with your cluster. Note that a custom AMI is only compatible with the ParallelCluster version the AMI is created with.

5. We recommend to re-enable Unattended Upgrades on the head node of the cluster by running the following command: `sudo sed -i "s/Unattended-Upgrade \"0\"/Unattended-Upgrade \"1\"/g" /etc/apt/apt.conf.d/20auto-upgrades`