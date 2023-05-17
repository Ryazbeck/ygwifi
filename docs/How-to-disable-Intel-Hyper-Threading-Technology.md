Starting from ParallelCluster 2.5.0 you can disable hyperthreading by configuring the [`disable_hyperthreading`](https://docs.aws.amazon.com/parallelcluster/latest/ug/cluster-definition.html#disable-hyperthreading) configuration parameter in the `cluster` section.

If you're using an instance type that doesn't support disabling hyperthreading specifying CpuOptions (see [CPU Cores and Threads Per CPU Core Per Instance Type](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-optimize-cpu.html#cpu-options-supported-instances-values)) or if you are using ParallelCluster 2.4.1 or older versions you can disable hyperthreading (on Amazon Linux) by following the two steps below.

## 1. Set scheduler to use cores

You have to pass an additional setting at cluster creation time, by using the `extra_json` parameter, which enable you to set the number of slots per instances to vpcus, cores, or a number.

To set the number of slots per instance to be only the number of **cores**, you have to set the following in your config:
```ini
[cluster yourcluster]
...
extra_json = { "cluster" : { "cfn_scheduler_slots" : "cores" } }
```  

## 2. Turn off hyper-threading in a post-install script
If you are using Amazon Linux, you have to create a script with the following content:

```bash
#!/bin/bash

for cpunum in $(cat /sys/devices/system/cpu/cpu*/topology/thread_siblings_list | cut -s -d, -f2- | tr ',' '\n' | sort -un)
do
    echo 0 > /sys/devices/system/cpu/cpu$cpunum/online
done
```
Upload the script with the correct permissions to S3 and use as [Post Install script](https://aws-parallelcluster.readthedocs.io/en/latest/pre_post_install.html) by configuring the `post_install` configuration parameter.

```ini
[cluster yourcluster]
...
post_install = s3://<bucket-name>/yourscript.sh
```

See [Disabling Intel Hyper-Threading Technology on Amazon Linux](https://aws.amazon.com/blogs/compute/disabling-intel-hyper-threading-technology-on-amazon-linux/) for more details.