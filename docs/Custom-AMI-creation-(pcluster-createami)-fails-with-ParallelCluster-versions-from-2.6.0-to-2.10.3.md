### The issue

On 2021-05-12 all the Slurm packages other than 20.02.7 and 20.11.7 versions were removed from the SchedMD repository. The software is a dependency of the `aws-parallelcluster-cookbook`, which provides the recipes to install and configure the Slurm scheduler. 
The lack of the older versions of the Slurm packages causes the execution of the ParallelCluster recipes to fail when running a `pcluster createami` command. This issue does not affect official or custom AMIs where ParallelCluster recipes where executed and Slurm packages installed.

### Affected ParallelCluster versions

This issue affects all versions of ParallelCluster from v2.6.0 to v2.10.3 included.

### Error details

When creating AMIs via either the `pcluster createami` command, the `slurm_install` recipe in the ParallelCluster cookbook will fail with the following error message in the standard output:

```
packer status: custom-alinux:     =======================================================================..
packer status: custom-alinux:     error executing action `create` on resource 'remote_file[/opt/parallelc..
packer status: custom-alinux:     =======================================================================..
packer status: custom-alinux:
packer status: custom-alinux:     net::httpserverexception
packer status: custom-alinux:     ------------------------
packer status: custom-alinux:     404 "not found"
```

### The workaround

For v2.10.3 the recommended workaround is to use the patched ParallelCluster cookbook [aws-parallelcluster-cookbook-2.10.3.tgz](https://us-east-1-aws-parallelcluster.s3.amazonaws.com/patches/2.10.3/aws-parallelcluster-cookbook-2.10.3.tgz) for building new custom AMIs. This cookbook contains the updated reference to the new Slurm package to install and it can be used as argument of the `-cc` option of the `pcluster createami` command:

```bash
pcluster createami -ai ${BASE_AMI_ID} -os ${BASE_AMI_OS} \
  -cc https://us-east-1-aws-parallelcluster.s3.amazonaws.com/patches/2.10.3/aws-parallelcluster-cookbook-2.10.3.tgz
```

If you need to apply the fix to your personal custom cookbook you can simply replicate the changes from the following commit: https://github.com/aws/aws-parallelcluster-cookbook/pull/951

Note: If you're using ParallelCluster from 2.6.0 to 2.9.1 you are also affected by the [Custom-AMI-creation-(pcluster-createami)-fails-with-ParallelCluster-2.9.1-and-earlier](https://github.com/aws/aws-parallelcluster/wiki/Custom-AMI-creation-(pcluster-createami)-fails-with-ParallelCluster-2.9.1-and-earlier) issue, so you need to merge the two changes in the cookbook code.