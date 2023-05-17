## The issue

The performance of tightly coupled / MPI workloads on clusters with Amazon Linux 2 operating system may be impacted by enabling CloudWatch logging.

Our preliminary analysis has found this is likely related to the CloudWatch Agent version 1.247348.0b251302, you can check which version you have installed by running the command: `yum list amazon-cloudwatch-agent`

This performance issue may affect workloads differently depending on cluster size and applications used.


## The workaround

To overcome the issue there are multiple options.

### Option 1: Downgrade CloudWatch agent with a post-install script

This option can be applied to new or existing clusters after an update operation. Instruction steps follow:

1. Create a bash script, e.g. `disable-cw-script.sh`, with the following content (or add the code to your existing post installation script)
```bash
#!/bin/bash
    
. "/etc/parallelcluster/cfnconfig"
    
case "${cfn_node_type}" in
    ComputeFleet)
        sudo systemctl stop amazon-cloudwatch-agent.service
        sudo yum -y downgrade amazon-cloudwatch-agent-1.247347.4-1.amzn2
        sudo systemctl start amazon-cloudwatch-agent.service
    ;;
    *)
    ;;
esac
```
2. Upload the script to an S3 bucket with correct permissions, see: https://docs.aws.amazon.com/parallelcluster/latest/ug/pre_post_install.html
E.g.:  `aws s3 cp disable-cw-script.sh s3://yourbucket/`
3. Add the following setting to your cluster configuration
```bash
[cluster yourcluster]
post_install = s3://yourbucket/disable-cw-script.sh
...
```
4. Either create a new cluster or follow the next steps to update an existing cluster 

Update an existing cluster with the post installation script configured in the previous steps.

1. Stop the cluster with pcluster stop command
2. Update the cluster with pcluster update command
3. Restart the cluster with pcluster start command

All the compute nodes will start with a version of CloudWatch agent not impacting your cluster.

### Option 2: Create the cluster with CloudWatch logging disabled
This option applies only to new clusters.

Create a cluster with the following configuration:
```ini
[cluster yourcluster]
cw_log_settings = custom-cw
...

[cw_log custom-cw]
enable = false
```

CloudWatch logging and the CloudWatch Agent service will be disabled by default, avoiding the possible performance degradation issue.

### Option 3: Create a custom AMI with a downgraded CloudWatch Agent

This option applies only to new clusters.

1. Follow the official documentation to [modify an existing ParallelCluster AMI](https://docs.aws.amazon.com/parallelcluster/latest/ug/tutorials_02_ami_customization.html#modify-an-aws-parallelcluster-ami)
2. As part of the AMI customization step, connect to the instance and run the following command: `sudo yum -y downgrade amazon-cloudwatch-agent-1.247347.4-1.amzn2`
3. Complete the steps to create a custom AMI
4. Create a cluster using the generated AMI with the `custom_ami` parameter.


### Option 4: Downgrade CloudWatch agent within individual jobs (Slurm only)

This option can be applied to existing Slurm clusters.

Customize your job submission script by adding the steps to downgrade CloudWatch agent. Example:

```bash
#!/bin/bash
#SBATCH --job-name=yourjob
# add your options

# downgrade 
for i in $(scontrol show hostnames $SLURM_JOB_NODELIST)
do
    ssh $i "sudo systemctl stop amazon-cloudwatch-agent.service"
    ssh $i "sudo yum -y downgrade amazon-cloudwatch-agent-1.247347.4-1.amzn2"
    ssh $i "sudo systemctl start amazon-cloudwatch-agent.service"
done

# start your application
sleep 100
```