# Public-Private Networking

![image](https://aws-parallelcluster.readthedocs.io/en/latest/_images/networking_two_subnets.jpg)

Several networking scenarios call for having a public and private subnet pair with a NAT gateway. For example:

### use_public_ips = False

This is useful if you want to set the `use_public_ips = false` flag. This flag turns off elastic ip's, which have a low default limit of `5`, limiting the number of clusters a customer can create without raising this limit. If you follow this guide, you'll only need 1 Elastic IP for the NAT gateway.

**Note**: this parameter is only in ParallelCluster 2.x. With ParallelCLuster 3.x, please use [`ElasticIp`](https://docs.aws.amazon.com/parallelcluster/latest/ug/HeadNode-v3.html#yaml-HeadNode-Networking-ElasticIp) parameter to control the setting.

### AWS Batch Multi-node Parallel

To use the AWS Batch integration, you'll need to use a public, private subnet pair setup with a NAT Gateway. See [AWS Batch networking](https://aws-parallelcluster.readthedocs.io/en/latest/networking.html#aws-parallelcluster-with-awsbatch-scheduler) for more information.

## How to

`pcluster configure` helps you create VPC and subnets automatically.

If you wish to create the VPC and subnets manually, follow the guide below:

To make this work, you'll need a public and private subnet, the private subnet routes through a NAT gateway. To create these subnets do:

1. In the [VPC Dashboard](https://console.aws.amazon.com/vpc/home) , click "VPC Wizard"

<p align="center">
<img width="647" src="https://user-images.githubusercontent.com/5545980/55517061-0d180480-5624-11e9-8e6a-ce34615ad79c.png" alt="image">
</p>

2. Select the second tab "VPC with Public and Private Subnets"

<p align="center">
<img width="647" src="https://user-images.githubusercontent.com/5545980/55517117-35076800-5624-11e9-84e1-6932c5bf306e.png" alt="image">
</p>

3. Create the VPC, giving it a name, like `public-private`:

<p align="center">
<img src="https://user-images.githubusercontent.com/5545980/55517284-caa2f780-5624-11e9-9002-7ec7551172ed.png" alt="image">
</p>

4. Enable "Auto-assign public ip's" on the `Public Subnet`.

<p align="center">
<img src="https://user-images.githubusercontent.com/5545980/55517368-135ab080-5625-11e9-9de2-e099262d0627.png" alt="image">
</p>

5. From your `~/.parallelcluster/config` file add a vpc section that includes your newly created vpc and subnets, and reference it in your cluster section:

```
[cluster mycluster]
...
vpc_settings = public-private

[vpc public-private]
vpc_id = [VPC you created]
master_subnet_id = [Public Subnet]
compute_subnet_id = [Private Subnet]
use_public_ips = false
```

6. Create the cluster! When you ssh in, you'll need to grab the public ip from the EC2 console, rather than `pcluster ssh cluster`. **Update** This will be fixed in version `>= 2.3.1` :-)