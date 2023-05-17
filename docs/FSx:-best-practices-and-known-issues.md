# Best practices

The sources are the official [FSx performance documentation](https://docs.aws.amazon.com/fsx/latest/LustreGuide/performance.html) and [configuring lustre file striping wiki](https://wiki.lustre.org/Configuring_Lustre_File_Striping).

## FSx performance optimization and file striping

> All file data in Lustre is stored on disks called object storage targets (OSTs). All file metadata [...] is stored on disks called metadata targets (MDTs). Amazon FSx for Lustre file systems are composed of a single MDT and multiple OSTs.
> Amazon FSx for Lustre automatically spreads your file data across the OSTs that make up your file system to balance storage capacity with throughput and IOPS load.

> Using Lustre, you can configure how files are striped across OSTs. When a file is striped across multiple OSTs, read or write requests to the file are spread across those OSTs, increasing the aggregate throughput or IOPS your applications can drive through it.

> One of the main factors leading to the high performance of Lustre™ file systems is the ability to stripe data over multiple OSTs.

Setting up a striped layout for large files (especially files larger than a gigabyte in size) is important for several reasons:
* Prevents a single large file from filling an OST, possibly causing storage exhaustion on that OST (this could be your case).
* Improves throughput by allowing multiple OSTs and their associated servers to contribute IOPS, network bandwidth and CPU resources. This is especially true for large sequential reads in which Lustre can concurrently request data from multiple OSTs.
* Reduces the likelihood that a small subset of OSTs will become hot spots that limit overall performance.

The FSx layout (stripe count, stripe size) of a file is fixed when the file is first created. 
Double check [the layout of the FSx](https://docs.aws.amazon.com/fsx/latest/LustreGuide/performance.html#storage-layout), the [strip configuration](https://docs.aws.amazon.com/fsx/latest/LustreGuide/performance.html#striping-data).

Note: it's possible to change the layout of a file after it is created, as suggested [here](https://wiki.lustre.org/Configuring_Lustre_File_Striping).

## FSx file striping and ParallelCluster

When using FSx with ParallelCluster it's possible to configure the stripe count and the maximum amount of data per file by setting the [`imported_file_chunk_size`](https://docs.aws.amazon.com/parallelcluster/latest/ug/fsx-section.html#fsx-imported-file-chunk-size) configuration parameter in the [`fsx`](https://docs.aws.amazon.com/parallelcluster/latest/ug/fsx-section.html) section.


## Using FSx with Amazon EC2 Spot Instances
> When Amazon EC2 interrupts a Spot Instance, it provides a Spot Instance interruption notice, which gives the instance a two-minute warning before Amazon EC2 interrupts it. 

> To ensure that Amazon FSx file systems are unaffected by EC2 Spot Instances Interruptions, we recommend unmounting Amazon FSx file systems prior to terminating or hibernating EC2 Spot Instances. 

See [Handling Amazon EC2 spot instance interruptions](https://docs.aws.amazon.com/fsx/latest/LustreGuide/working-with-ec2-spot-instances.html)

# Known issues

## Pre/Post installation script failing on `apt update` (Ubuntu)

### Error

If during the execution of a Pre/Post installation script you have an `apt update` failing with the following error:

```
E: Repository 'https://fsx-lustre-client-repo.s3.amazonaws.com/ubuntu bionic InRelease' changed its 'Origin' value from '' to 'AWS-FSx-for-Lustre'
E: Repository 'https://fsx-lustre-client-repo.s3.amazonaws.com/ubuntu bionic InRelease' changed its 'Suite' value from '' to 'stable'
```

The stack creation and/or the cluster scale up will fail.

### Fix

Add a flag to the `apt` command to accept the upstream changes on the FSx repository:

```
apt update --allow-releaseinfo-change
```
or 
```
apt update -y
```

## Stack Fails creation when specifying `imported_file_chunk_size`

### Error

If in your config you have:

```
[fsx fs]
shared_dir = /fsx
storage_capacity = 14400
imported_file_chunk_size = 1024
```

Stack creation will fail, this is because the `import_path` is required when using `imported_file_chunk_size` or `export_path`.

### Fix

Add `import_path` to your FSx config.

```
[fsx fs]
shared_dir = /fsx
storage_capacity = 14400
import_path = s3://your_bucket
imported_file_chunk_size = 1024
```

## File System fails creation when using requester-pay Buckets

### Error 

If during stack creation you see this:

```bash
$ pcluster create fsx-requester-pay-s3
Beginning cluster creation for cluster: fsx-requester-pay-s3
Creating stack named: parallelcluster-fsx-requester-pay-s3
Status: parallelcluster-fsx-requester-pay-s3 - ROLLBACK_IN_PROGRESS
Cluster creation failed.  Failed events:
  - AWS::CloudFormation::Stack EBSCfnStack Resource creation cancelled
  - AWS::IAM::InstanceProfile RootInstanceProfile Resource creation cancelled
  - AWS::EC2::EIPAssociation AssociateEIP Resource creation cancelled
  - AWS::CloudFormation::Stack FSXSubstack Embedded stack arn:aws:cloudformation:us-east-1:753979222379:stack/parallelcluster-fsx-requester-pay-s3-FSXSubstack-1WHT3VJ4298XE/ed68b7e0-3c3f-11e9-a755-0e0d3a451244 was not successfully created: The following resource(s) failed to create: [FileSystem].
```

And your config specifies a bucket with the **requester-pay** model:

```
[fsx fs]
shared_dir = /fsx
storage_capacity = 3600
imported_file_chunk_size = 1024
import_path = s3://gcgrid . # requester pay bucket
```

See [#901](https://github.com/aws/aws-parallelcluster/issues/901)

#### Fix

The bucket doesn't allow the `GetBucketAcl` Permission. You can check it by:

```
$ aws s3api get-bucket-acl --bucket gcgrid
An error occurred (AccessDenied) when calling the GetBucketAcl operation: Access Denied
```

If you are the bucket owner you can add this permission to the bucket. Otherwise contact the bucket owner and have them add it.

