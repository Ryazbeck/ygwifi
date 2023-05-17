Starting with ParallelCluster 2.6.0, [CloudWatch logs integration](https://docs.aws.amazon.com/parallelcluster/latest/ug/cloudwatch-logs.html) is enabled by default. This means a cluster's system, scheduler, and node daemon logs are stored in a CloudWatch log group. These logs prove particularly useful when debugging issues with ephemeral compute nodes, like unexpected scaling behavior and node initialization failures.

CloudWatch Logs Insights provides one method for interacting with your cluster's log data. The [user guide](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/AnalyzingLogData.html) contains information that will enable you to query and analyze your cluster's log data from the CloudWatch console.

Nevertheless, it's sometimes easier to work with the log files on your local machine. There are two ways to export logs depending on the version of ParallelCluster:

Starting with ParallelCluster 3.0.0, `export-cluster-logs` is added. Follow this [guide](https://docs.aws.amazon.com/parallelcluster/latest/ug/troubleshooting-v3.html#troubleshooting-v3-get-logs) to retrieve logs.

With ParallelCluster 2.6.0 to 2.11.x, you can use the [utility script in this repo](https://github.com/aws/aws-parallelcluster/blob/release-2.11/util/logging/retrieve-cluster-logs.py) to extract an archive of a cluster's logs from CloudWatch. Note: the script only works with Python 3.x. Here's an example:

```bash
#!/bin/bash
BUCKET=logs-export-bucket
CLUSTER_NAME=cluster-with-logs
CLUSTER_REGION=us-west-1
wget https://raw.githubusercontent.com/aws/aws-parallelcluster/release-2.11/util/logging/retrieve-cluster-logs.py
python3 retrieve-cluster-logs.py --cluster ${CLUSTER_NAME} --region ${CLUSTER_REGION} --bucket ${BUCKET}
```

That script will write a tarball containing a file for each of a cluster's log streams to the working directory. It does this by first exporting to the specified S3 bucket an archive of all log streams containing data. It then downloads and combines these individual archives into a single archive.

![cloudwatch-logs-archive](https://user-images.githubusercontent.com/55806862/75693747-44d86380-5c5c-11ea-90fa-ea843136be86.png)

There are a few things to keep in mind when using this script:
* It depends on the `boto3` python module.
* At a minimum, the following [CloudWatch](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/permissions-reference-cwl.html) and [S3](https://docs.aws.amazon.com/AmazonS3/latest/dev/using-with-s3-actions.html) permissions are required:
  * s3:GetBucketLocation
  * s3:GetBucketLocation
  * s3:ListBucket
  * s3:GetObject
  * logs:DescribeLogGroups
  * logs:FilterLogEvents
  * logs:CreateExportTask
  * logs:DescribeExportTasks
* The bucket supplied to the script must [reside in the same region as the cluster's log group](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/S3ExportTasks.html#CreateS3Bucket), and the bucket's owner must [enable the access CloudWatch requires](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/S3ExportTasks.html#S3Permissions).
* Depending on a cluster's age and size, the quantity of log data may be quite large. This is important because the data exported to S3 is not deleted. You can utilize the script's `--from-time` and `--to-time` parameters to reduce the amount of data exported to S3.
* Always ensure that any sensitive information has been removed when attaching logs extracted by this script to github issues.
***
