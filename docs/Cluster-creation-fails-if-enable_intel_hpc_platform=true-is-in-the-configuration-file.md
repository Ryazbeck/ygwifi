## The issue

Starting September 2021, cluster creation fails if `enable_intel_hpc_platform=true` is set in the cluster configuration file due to the earlier versions of Intel HPC Platform being obsoleted/removed. 

## Affected ParallelCluster versions

2.10.0 and earlier.

## Error details

Cluster creation will fail with an error message:

```
> pcluster create -nr parallelcluster-mycluster
Beginning cluster creation for cluster: parallelcluster-mycluster
Creating stack named: parallelcluster-mycluster
Status: parallelcluster-mycluster - CREATE_FAILED
Cluster creation failed. Failed events:
- AWS::CloudFormation::WaitCondition MasterServerWaitCondition Received FAILURE signal with UniqueId i-083957254c3b7488b
```

The `cfn-init.log` in the Master node contains either of the following error messages

```
No package intel-hpc-platform-*-2018.0-1.el7 available.
```
```
Package intel-hpc-platform-hpc-cluster is obsoleted by intel-hpc-platform-2.0-hpc-cluster, trying to install intel-hpc-platform-2.0-hpc-cluster-2.0-1.el7.x86_64 instead
```

## The workaround
### Method 1
**We strongly recommend you upgrading to the latest 2.11.x or 3.x ParallelCluster to create the new cluster.**
### Method 2
Generally, we need to slightly upgrade the version of the Intel HPC platform and use a flag to force the installation of the obsoleted package. 

A `pre_install` script could be used to achieve the goal:
```
#!/bin/bash
​
. "/etc/parallelcluster/cfnconfig"
​
case "${cfn_node_type}" in
    MasterServer)
        sed -i "s/yum -y install --downloadonly --downloaddir=\/opt\/intel\/rpms/yum -y install --downloadonly --setopt=obsoletes=0 --downloaddir=\/opt\/intel\/rpms/" /etc/chef/cookbooks/aws-parallelcluster/recipes/intel_install.rb
        sed -i "s/2018.0-1.el7/2018.0-*.el7/" /etc/chef/cookbooks/aws-parallelcluster/attributes/default.rb
        wget -O "${cfn_shared_dir}/env2" https://sourceforge.net/projects/env2/files/env2/download --tries 6 --waitretry 10
    ;;
    *)
    ;;
esac

cp "${cfn_shared_dir}/env2" /opt/parallelcluster/scripts/env2
chmod 0755 /opt/parallelcluster/scripts/env2
```
You can create a file containing the script above and upload the file (e.g. to AWS S3).
Then use the URL of the file for [pre_install](https://docs.aws.amazon.com/parallelcluster/latest/ug/cluster-definition.html#pre-install) parameter in the configuration file

To learn more about pre install script and post install script, see [this guide](https://docs.aws.amazon.com/parallelcluster/latest/ug/pre_post_install.html).