## The issue

Starting from ParallelCluster 2.10.1, the official ParallelCluster Ubuntu 1804 ARM AMI is not compatible with first generation AWS Graviton instances, such as the ones belonging to the a1 family.
The issue, introduced in a recent Ubuntu update, is due to the fact that during an AMI build, when building `initramfs`, only the libraries optimized for the specific running system are installed. This makes it so that the produced AMI, when built on a second generation ARM Graviton chip, is not compatible with the older generation of AWS Graviton Processors.

This limitation is already tracked in the [Ubuntu ticketing system](https://bugs.launchpad.net/ubuntu/+source/initramfs-tools/+bug/1883883) and was introduced when addressing a [bug](https://bugs.launchpad.net/ubuntu/+source/glibc/+bug/1880853) affecting m6g instances.

## The workaround

In case you need to use old generation AWS Graviton instances you need to create a compatible custom AMI to use with ParallelCluster by following these steps:
1. Follow the official documentation to [modify an existing ParallelCluster AMI](https://docs.aws.amazon.com/parallelcluster/latest/ug/tutorials_02_ami_customization.html#modify-an-aws-parallelcluster-ami) and launch a m6g instance running a ParallelCluster Ubuntu 18 ARM AMI.
2. As part of the AMI customization step, connect to the instance and run the following commands:
```
sudo apt purge libc6-lse
sudo update-initramfs -k all -c -t
```
3. Complete the steps to create a custom AMI
4. Create a cluster using the generated AMI with the `custom_ami` parameter.