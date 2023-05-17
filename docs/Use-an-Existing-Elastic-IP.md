**Note**: Starting with ParallelCluster 3.x, using an existing Elastic IP is supported without the need for customizing CloudFormation template. Please see [`ElasticIp`](https://docs.aws.amazon.com/parallelcluster/latest/ug/HeadNode-v3.html#yaml-HeadNode-Networking-ElasticIp) parameter for details.

1. Clone the repo:

```bash
$ git clone https://github.com/aws/aws-parallelcluster.git
$ cd aws-parallelcluster/
```
2. Modify the template `cloudformation/aws-parallelcluster.cfn.json` to include a parameter:

```json
"ElasticIpId": {
  "Description": "The Id of the elastic IP to associate with the master instance.",
  "Type": "String"
},
```

3. Modify [#L4568](https://github.com/aws/aws-parallelcluster/blob/develop/cloudformation/aws-parallelcluster.cfn.json#L4568) to reference that parameter:

```json
"AssociateEIP": {
  "Type": "AWS::EC2::EIPAssociation",
  "Properties": {
    "AllocationId": {
      "Ref": "ElasticIpId"
    },
    "NetworkInterfaceId": {
      "Ref": "MasterENI"
    }
  },
  "Condition": "MasterPublicIp"
},
```

4. Remove `MasterEIP` Resource [#L1921](https://github.com/aws/aws-parallelcluster/blob/develop/cloudformation/aws-parallelcluster.cfn.json#L1921):

Remove this block:
```json
"MasterEIP": {
  "Type": "AWS::EC2::EIP",
  "Properties": {
    "Domain": "vpc"
  },
  "Condition": "MasterPublicIp"
},
```

5. Upload the template:

```
$ util/uploadTemplate.sh --bucket [your s3 bucket] --srcdir . --region [aws region]
```

Reference the custom template from your cluster's config:
```ini
[cluster your_cluster]
template_url = https://s3.amazonaws.com/seaam-pcluster/template/aws-parallelcluster.cfn.2.3.1.json
```
