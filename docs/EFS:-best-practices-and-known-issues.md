# Best practices

* [When to Choose Amazon EFS: aka EFS vs EBS vs S3](https://aws.amazon.com/efs/when-to-choose-efs/)
* [Walkthrough: Create Writable Per-User Subdirectories](https://docs.aws.amazon.com/efs/latest/ug/accessing-fs-nfs-permissions-per-user-subdirs.html)

# Known issues

## Stack Fails creation when using EFS with head and compute subnets in different availability zones

### Error

_Affecting pcluster versions <= 2.5.1_

If in your config you have enabled EFS and are using head and compute subnets that are in different availability zones:

```
[vpc diff]
vpc_id = vpc-01234567
master_subnet_id = subnet-0123abcd123 # in us-east-1a
compute_subnet_id = subnet-0123efg123 # in us-east-1b

[efs fs]
shared_dir = /efs
```

Stack creation will fail, this is because we are only creating EFS mount targets in the head node AZ and not creating a mount target in the compute AZ.

### Fix

Fixed with 2.6.0. Please try to use head and compute subnet that are in the same AZ when using EFS for pcluster versions <= 2.5.1.