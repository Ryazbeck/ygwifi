### The issue

Beginning on 2020-12-07 the creation of custom AMIs with the CentOS 8 operating system is failing.
The problem affects both the use case of [building a custom ParallelCluster AMI](https://docs.aws.amazon.com/parallelcluster/latest/ug/tutorials_02_ami_customization.html#build-a-custom-aws-parallelcluster-ami) through the `pcluster createami` command and the one of [use of a custom AMI at runtime](https://docs.aws.amazon.com/parallelcluster/latest/ug/tutorials_02_ami_customization.html#use-a-custom-ami-at-runtime).
 This issue does not affect the use of default ParallelCluster AMIs, nor does it affect the creation of custom AMIs by [modifying a ParallelCluster AMI](https://docs.aws.amazon.com/parallelcluster/latest/ug/tutorials_02_ami_customization.html#modify-an-aws-parallelcluster-ami). 

No other operating systems supported by ParalleCluster are impacted.


### Affected ParallelCluster version

This issue affects ParallelCluster 2.10.0.
The issue is due to a [change in the name](https://git.centos.org/rpms/centos-repos/c/b759b17557b9577e8ea156740af0249ab1a22d70) of the PowerTools package in the [release 8.3](https://access.redhat.com/articles/3078#RHEL8). See [related issue](https://bugzilla.redhat.com/show_bug.cgi?id=1900785).


### Error details

When using the `pcluster createami` command using `centos8` as `base_os` the following error will be thrown:

```
packer status: ==> builds finished but no artifacts were created.
       packer status:     exit code 1
       
       no custom ami created
```
By looking at packer logs the root reason can be identified: The PowerTools repository is no longer available.

```
Error: No matching repo to modify: PowerTools
```


### The fix

The issue has been fixed in the develop branch by [patch #831](https://github.com/aws/aws-parallelcluster-cookbook/pull/831). 2.10.1 contains the fix as well.