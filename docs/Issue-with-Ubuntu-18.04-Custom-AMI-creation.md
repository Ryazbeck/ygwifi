### The issue

Beginning on 2020-12-10 the creation of custom AMIs with the Ubuntu 18.04 operating system is failing.
The problem affects both the use case of [building a custom ParallelCluster AMI](https://docs.aws.amazon.com/parallelcluster/latest/ug/tutorials_02_ami_customization.html#build-a-custom-aws-parallelcluster-ami) through the `pcluster createami` command and the one of [use of a custom AMI at runtime](https://docs.aws.amazon.com/parallelcluster/latest/ug/tutorials_02_ami_customization.html#use-a-custom-ami-at-runtime).
 This issue does not affect the use of default ParallelCluster AMIs, nor does it affect the creation of custom AMIs by [modifying a ParallelCluster AMI](https://docs.aws.amazon.com/parallelcluster/latest/ug/tutorials_02_ami_customization.html#modify-an-aws-parallelcluster-ami). 

No other operating systems supported by ParalleCluster are impacted.


### Affected ParallelCluster versions

This issue affects all versions of ParallelCluster supporting Ubuntu 18.04, from 2.5.0 up to 2.10.0.
 The root cause of this issue lies in the [sge_preinstall.sh](https://github.com/aws/aws-parallelcluster-cookbook/blob/v2.10.0/files/ubuntu-18.04/sge_preinstall.sh) script from the [ParallelCluster cookbook project](https://github.com/aws/aws-parallelcluster-cookbook) that was relying on the Ubuntu Eoan (19.10) repo, which is no longer available.


### Error details

When using the pcluster createami command using ubuntu1804 as base_os the following error will be thrown:

```
packer status: ==> builds finished but no artifacts were created.
       packer status:     exit code 1
       
       no custom ami created
```
By looking at packer logs the root reason can be identified: The eoan (Ubuntu 19.10) repository is no longer available.

```
ubuntu1804: ---- Begin output of sh /tmp/sge_preinstall.sh ----
ubuntu1804: STDOUT: Downloading and extracting source packages for sge-8.1.9+dfsg-9build1
ubuntu1804: Hit:1 http://us-east-1.ec2.archive.ubuntu.com/ubuntu bionic InRelease
ubuntu1804: Hit:2 http://us-east-1.ec2.archive.ubuntu.com/ubuntu bionic-updates InRelease
ubuntu1804: Hit:3 http://us-east-1.ec2.archive.ubuntu.com/ubuntu bionic-backports InRelease
ubuntu1804: Ign:4 http://us-east-1.ec2.archive.ubuntu.com/ubuntu eoan InRelease
ubuntu1804: Err:5 http://us-east-1.ec2.archive.ubuntu.com/ubuntu eoan Release
ubuntu1804:   404  Not Found [IP: 18.232.150.247 80]
ubuntu1804: Hit:6 http://security.ubuntu.com/ubuntu bionic-security InRelease
ubuntu1804: Hit:7 https://fsx-lustre-client-repo.s3.amazonaws.com/ubuntu bionic InRelease
ubuntu1804: Reading package lists...
ubuntu1804: STDERR: WARNING: apt does not have a stable CLI interface. Use with caution in scripts.
ubuntu1804:
ubuntu1804: E: The repository 'http://us-east-1.ec2.archive.ubuntu.com/ubuntu eoan Release' does not have a Release file.
ubuntu1804: ---- End output of sh /tmp/sge_preinstall.sh ----
```


### The workaround

The issue has been fixed in the 2.10 branch by [patch #835](https://github.com/aws/aws-parallelcluster-cookbook/pull/835). v2.10.1 contains a solution as well.

For 2.10.0 we have provided a patched cookbook archive at the URL https://us-east-1-aws-parallelcluster.s3.amazonaws.com/patches/2.10.0/aws-parallelcluster-cookbook-2.10.0.patch-20201211.tgz that can be used to create an Ubuntu 18.04 custom AMI. For 2.9.1 we have provided a similarly patched cookbook [here](https://raw.githubusercontent.com/aws/aws-parallelcluster-cookbook/release-2.9/patched-cookbooks/aws-parallelcluster-cookbook-2.9.1.tgz).

This custom cookbook URL must be specified when using the pcluster createami command to create a custom Ubuntu18.04 ParallelCluster AMI through the `-cc` parameter like in the example below:
```
$ pcluster createami -cc https://us-east-1-aws-parallelcluster.s3.amazonaws.com/patches/2.10.0/aws-parallelcluster-cookbook-2.10.0.patch-20201211.tgz -ai <base_ami> -os ubuntu1804 
```
No viable solutions are currently available for the use case "Custom AMI at Runtime".
