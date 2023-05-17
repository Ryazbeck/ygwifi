If you see:

```bash
$ pcluster create mycluster
Creating stack named: parallelcluster-mycluster
Status: parallelcluster-mycluster - ROLLBACK_IN_PROGRESS                        
Cluster creation failed.  Failed events:
  - AWS::EC2::Instance MasterServer Received FAILURE signal with UniqueId i-07af1cb218dd6a081
```

There was a problem creating the cluster, to diagnose, re-run the create with the `--norollback` flag. Then ssh into the cluster:

```bash
$ pcluster create mycluster --norollback
...
$ pcluster ssh mycluster
```

From there, there's three log files that will tell you what error occurred:

* `/var/log/cfn-init.log` start here, likely you'll see an error like `Command chef failed`, look above that line for the specific error
* `/var/log/cloud-init.log` if you don't see anything telling in `cfn-init.log` this a good resource
* `/var/log/cloud-init-output.log` you can view the stdout of the cfn-init command. Usually not needed.

## Attach Volume Failure

### Error 

_Affecting pcluster versions <= 2.1.1_

If in the `/var/log/cfn-init.log` file you see this, 

```bash
STDERR: Traceback (most recent call last):
  File "/usr/local/sbin/attachVolume.py", line 90, in <module>
    main()
  File "/usr/local/sbin/attachVolume.py", line 68, in main
    response = ec2.attach_volume(VolumeId=volumeId, InstanceId=instanceId, Device=dev)
  File "/usr/lib/python2.7/site-packages/botocore/client.py", line 357, in _api_call
    return self._make_api_call(operation_name, kwargs)
  File "/usr/lib/python2.7/site-packages/botocore/client.py", line 661, in _make_api_call
    raise error_class(parsed_response, operation_name)
botocore.exceptions.ClientError: An error occurred (InvalidParameterValue) when calling the AttachVolume operation: Invalid value '/dev/sdb' for unixDevice. Attachment point /dev/sdb is already in use
```
#### Fix

This is a known bug in `pcluster-2.1.1` that effects NVME based instances type, such as c5, m5, z1d. See [#823](https://github.com/aws/aws-parallelcluster/issues/823) for more info. 

Upgrade to a version > 2.1.1 to fix.

## Valid Fully-Formed Launch Template

### Error 

If you see:

```
$ pcluster create mycluster
Beginning cluster creation for cluster: mycluster
Creating stack named: parallelcluster-mycluster
Status: parallelcluster-mycluster - CREATE_FAILED                               
Cluster creation failed.  Failed events:
  - AWS::CloudFormation::Stack parallelcluster-mycluster The following resource(s) failed to create: [ComputeFleet]. 
  - AWS::AutoScaling::AutoScalingGroup ComputeFleet You must use a valid fully-formed launch template. The requested configuration is currently not supported. Please check the documentation for supported configurations. (Service: AmazonAutoScaling; Status Code: 400; Error Code: ValidationError; Request ID: 1737665d-2b08-11e9-9141-df273bd3069e)
```

#### Fix

This issue means the requested instance type isn't available in the region you requested. This can either be due to insufficient capacity in that region / availability zone, or it's unable to get the instances you need in the placement group you requested (see 3).

1. Change placement group by changing the `compute_subnet_id` or, if you only use one subnet, `master_subnet_id`.
2. Try a different region by changing the `aws_region_name = ` in your `~/.parallelcluster/config`
3. If you're using a placement group, change `placement = compute` in your config. It defaults to this as of `2.2.0`. By requesting a placement group with different head node and compute instances types, it becomes less likely that those instances are co-located, and hence the instance launch will fail to find the instances it needs to launch the cluster. Setting `placement = compute` changes this, by only putting the compute instances in the placement group.