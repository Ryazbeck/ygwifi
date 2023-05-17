# ParallelCluster CloudWatch Logs Integration



## Background

Keeping track of log files from a running cluster can be a pain. Some logs, such as `/var/log/nodewatcher`, are stored on the compute instances and disappear when compute nodes are removed. Other logs are stored on the head node, but are inaccessible once a cluster has been deleted.

### Enabling CloudWatch Logging for versions >= 3.0.0

CloudWatch logging is enabled by default. The documentation can be found [here](https://docs.aws.amazon.com/parallelcluster/latest/ug/cloudwatch-logs-v3.html). Please refer to [this page](https://docs.aws.amazon.com/parallelcluster/latest/ug/troubleshooting-v3.html#troubleshooting-v3-get-logs) for instructions for retrieving  cluster's logs.


### Enabling CloudWatch Logging for versions >= 2.6.0

Starting in ParallelCluster 2.6.0, CloudWatch logging is enabled by default. The documentation can be found [here](https://docs.aws.amazon.com/parallelcluster/latest/ug/cloudwatch-logs.html). Please refer to [this page](https://github.com/aws/aws-parallelcluster/wiki/Creating-an-Archive-of-a-Cluster's-Logs) for instructions for retrieving cluster's logs.

#### Collecting Data for Additional Logs

If you desire to store data in CloudWatch for logs not included in the default configuration, you can do so using the following directions.

But first, **please be aware of the cost associated with enabling additional logging**. One of the criteria for selecting the logs included in the default CloudWatch agent configuration was that they aren't expected to generate a significant volume of data. It's possible to incur significant cost if the additional logs generate a large amount of data, especially on large clusters. CloudWatch pricing information can be found [here](https://aws.amazon.com/cloudwatch/pricing).

The high-level overview of the process is:
1. Generate the default CloudWatch agent configuration files.
1. Add entries for other desired logs to these configurations.
1. Restart the CloudWatch agents on the head node and compute nodes with the new configurations.

##### Re-generate the default configs

On the head node of a running cluster, run the following:

```bash
#!/bin/bash
# PLATFORM=amazon if using alinux2 or alinux
# PLATFORM=ubuntu if using ubuntu1604 or ubuntu1804
# PLATFORM=centos if using centos6 or centos7
source /etc/parallelcluster/cfnconfig

# Head Node config
sudo /usr/local/bin/write_cloudwatch_agent_json.py --platform ${PLATFORM} --config /usr/local/etc/cloudwatch_log_files.json --log-group /aws/parallelcluster/"$(echo ${stack_name} | cut -d '-' -f2-)"  --scheduler ${cfn_scheduler} --node-role MasterServer
sudo mv /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json ${cfn_shared_dir}/master-amazon-cloudwatch-agent.json

# Compute Fleet config
sudo /usr/local/bin/write_cloudwatch_agent_json.py --platform ${PLATFORM} --config /usr/local/etc/cloudwatch_log_files.json --log-group /aws/parallelcluster/"$(echo ${stack_name} | cut -d '-' -f2-)"  --scheduler ${cfn_scheduler} --node-role ComputeFleet
sudo mv /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json ${cfn_shared_dir}/compute-amazon-cloudwatch-agent.json
```

##### Manually add config entries for additional logs to each of the two configs

After the last step there will be CloudWatch agent configuration files in the cluster's shared directory for the head node and compute nodes. Each will have a JSON object structured according to [this documentation](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Agent-Configuration-File-Details.html). Add new entries to the `collect_list` array for each log you wish to collect data for.

For example, if on the compute nodes i wanted to collect data from `/tmp/application/some-debug-log.txt`, I'd add the following object to the `collect_list` array in compute-amazon-cloudwatch-agent.json
```json
{
  "log_group_name": "/aws/parallelcluster/${SAME_LOG_GROUP_AS_OTHER_ENTRIES}",
  "file_path": "/tmp/application/some-debug-log.txt",
  "log_stream_name": "${SAME_HOSTNAME_AS_OTHER_ENTRIES}.{instance_id}.some-debug-log"
}
```

The timestamp_format that's in other entires is not required, but nice to have if you want to query on timestamps in [CloudWatch insights](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/AnalyzingLogData.html).

##### Restarting the CloudWatch daemons with updated configurations

On the head node:
```bash
#!/bin/bash
source /etc/parallelcluster/cfnconfig
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c file:${cfn_shared_dir}/master-amazon-cloudwatch-agent.json -s
```

On the compute nodes:
```bash
source /etc/parallelcluster/cfnconfig
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c file:${cfn_shared_dir}/compute-amazon-cloudwatch-agent.json -s
```

Note that the previous command needs to be run on all of the compute nodes. On a running cluster, this could be done using the scheduler, but when new compute nodes come up as the cluster scales they will use the default config.

You can get around this by wrapping this process in a post_install script. In order to do this, you could generate the desired configs on a running cluster using the first two steps above, upload these configs to an S3 bucket, and then either update the current cluster or create a new cluster that uses a post_install script like the following:
```bash
#!/bin/bash
source /etc/parallelcluster/cfnconfig

wget -O ${cfn_shared_dir}/master-amazon-cloudwatch-agent.json https://${BUCKET_NAME}.s3.${BUCKET_REGION}.amazonaws.com/cloudwatch_agent_configs/master.json 
wget -O ${cfn_shared_dir}/compute-amazon-cloudwatch-agent.json cp https://${BUCKET_NAME}.s3.${BUCKET_REGION}.amazonaws.com/cloudwatch_agent_configs/compute.json

if [ "${cfn_node_type}" == "MasterServer" ]; then
  sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c file:${cfn_shared_dir}/master-amazon-cloudwatch-agent.json -s
else
  sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c file:${cfn_shared_dir}/compute-amazon-cloudwatch-agent.json -s
fi
```


### Enabling CloudWatch logging versions < 2.6.0

For ParallelCluster versions < 2.6.0, the following instructions can be used to add these logs to CloudWatch, which are accessible even after the cluster has been deleted.
```
/var/log/sqswatcher
/var/log/jobwatcher
/var/log/nodewatcher # for each compute node
/opt/sge/default/spool/qmaster/messages
```
**Note**: CloudWatch does incur minimal additional costs, generally < $1. See https://aws.amazon.com/cloudwatch/pricing/ for more information.

### Steps

1. Add to the [CloudFormation Template #L1674](https://github.com/aws/aws-parallelcluster/blob/develop/cloudformation/aws-parallelcluster.cfn.json#L1674) the following additional permissions:

```json
{
  "Sid": "CloudWatchLogs",
  "Action": [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:DescribeLogStreams"
  ],
  "Effect": "Allow",
  "Resource": [
      "arn:aws:logs:*:*:*"
  ]
}
```

2. Upload this new template to your S3 bucket:
```bash
$ aws s3 cp aws-parallelcluster.cfn.json s3://[your_bucket]
```

3. Create a file `post_install.sh` with the following contents:

```bash
#!/bin/bash
########
# NOTE #
########
#
# THIS FILE IS PROVIDED AS AN EXAMPLE AND NOT INTENDED TO BE USED BESIDES TESTING
# USE IT AS AN EXAMPLE BUT NOT AS IS FOR PRODUCTION
#

# Setup the SSH authentication
ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
AZ=$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone)
REGION=$(echo "${AZ}" | sed 's/[a-z]$//')

export AWS_DEFAULT_REGION=${REGION}

# install and setup cloudwatch to push in logs in the local region
sudo yum install awslogs -y
cat > /etc/awslogs/awscli.conf << EOF
[plugins]
cwlogs = cwlogs
[default]
region = ${REGION}
EOF

# check if this is the head node instance
MASTER=false
if [[ $(aws ec2 describe-instances \
            --instance-id ${ID} \
            --query 'Reservations[].Instances[].Tags[?Key==`Name`].Value[]' \
            --output text) = "Master" ]]; then
    MASTER=true
fi

if ${MASTER}; then

# Setup cloudwatch logs for head node
cat >>/etc/awslogs/awslogs.conf << EOF
[/opt/sge/default/spool/qmaster/messages]
datetime_format = %b %d %H:%M:%S
file = /opt/sge/default/spool/qmaster/messages
buffer_duration = 5000
log_stream_name = {instance_id}
initial_position = start_of_file
log_group_name = pcluster-master-sge-qmaster-messages

[/var/log/jobwatcher]
datetime_format = %b %d %H:%M:%S
file = /var/log/jobwatcher
buffer_duration = 5000
log_stream_name = {instance_id}
initial_position = start_of_file
log_group_name = pcluster-master-job-watcher

[/var/log/sqswatcher]
datetime_format = %b %d %H:%M:%S
file = /var/log/sqswatcher
buffer_duration = 5000
log_stream_name = {instance_id}
initial_position = start_of_file
log_group_name = pcluster-master-sqs-watcher
EOF


else

# Setup cloudwatch logs for compute
cat >>/etc/awslogs/awslogs.conf << EOF

[/var/log/nodewatcher]
datetime_format = %b %d %H:%M:%S
file = /var/log/nodewatcher
buffer_duration = 5000
log_stream_name = {instance_id}
initial_position = start_of_file
log_group_name = pcluster-compute-node-watcher
EOF

fi

# start awslogs
sudo service awslogs start
sudo chkconfig awslogs on
```

4. Upload this file to S3

```bash
$ aws s3 cp --acl public-read post_install.sh s3://[your_cluster]
```

5. Create a cluster with your custom template and your post_install file:
```ini
[cluster default]
...
post_install = s3://[your_bucket]/post_install.sh
template_url = https://s3.amazonaws.com/[your_bucket]/template/aws-parallelcluster.cfn.json
```

6. Create the cluster

```bash
$ pcluster create mycluster
Status: CREATE_COMPLETE
MasterServer: RUNNING
MasterPublicIP: 18.214.13.107
ClusterUser: ec2-user
MasterPrivateIP: 172.31.18.7
```

7. Now go to the [CloudWatch Console](https://console.aws.amazon.com/cloudwatch/home) > **Logs** section

You'll see your log files there:

```bash
pcluster-compute-node-watcher        # is /var/log/nodewatcher
pcluster-master-job-watcher          # is /var/log/jobwatcher
pcluster-master-sge-qmaster-messages # is /opt/sge/default/spool/qmaster/messages
pcluster-master-sqs-watcher          # is /var/log/sqswatcher
```