## Stack Fails creation when enabling Intel HPC platform specification

### Error

_Affecting pcluster versions >= 2.5.1 <=2.6.0_

If in your config you have

```
enable_intel_hpc_platform = true
```

stack creation will fail, because Intel HPC platform specification version 2019.5 requires to be installed using yum version 4.

### Fix

Add the provided pre installation script to the configuration

```
pre_install = https://us-east-1-aws-parallelcluster.s3.amazonaws.com/patches/2.6.0/aws-parallelcluster-cookbook.intel.psxe.patch.sh
```