### The issue

Beginning on 2021-02-25 the creation of clusters might fail. The problem is transient intermittent and affects `pcluster create` and `pcluster update` commands.
Only the validations performed in ParallelCluster CLI are impacted by this issue; the actual creation of the cluster stack is not affected, and existing clusters will continue to work. The issue is due to a dryrun call that is performed during configuration validation, which always uses latest Amazon Linux AMI as parameter. If the AMI used in the dryrun is not suitable for the instance type, the dryrun may fail.

### Affected ParallelCluster versions

The issue affects all versions from 2.8.0 to 2.10.1.

### Error details

When using `pcluster create` or `pcluster update` command, an error may be thrown like the one below:

 ```
 ERROR: Unable to validate configuration parameters for instance type 'c6g.medium'. Please double check your cluster configuration.
 The architecture 'arm64' of the specified instance type does not match the architecture 'x86_64' of the specified AMI. Specify an instance type and an AMI that have matching architectures, and try again. You can use 'describe-instance-types' or 'describe-images' to discover the architecture of the instance type or AMI.
 ```
This error is intermittent, depending on the latest Amazon Linux AMI retrieved by pcluster. 

### The workaround

Since the issue involves only the validation phase in the CLI and not the cluster creation itself, the workaround is just to disable sanity checks in the configuration:

 ```
 [global]
 ...
 sanity_check = false
 ```

 Be aware that setting `sanity_check = false` disables all validations for cluster configuration settings with the risk to propagate invalid settings data to the cluster.

### The fix

The issue was fixed in the develop branch by patch [#2487](https://github.com/aws/aws-parallelcluster/pull/2487) and released in version 2.10.2.