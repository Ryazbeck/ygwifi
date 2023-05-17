The following steps let you create a cluster using instances with encrypted root volumes.

1. Create a custom AMI choosing one of the first two methods described in the official doc [here](https://docs.aws.amazon.com/parallelcluster/latest/ug/tutorials_02_ami_customization.html):
   * [Modify an AWS ParallelCluster AMI](https://docs.aws.amazon.com/parallelcluster/latest/ug/tutorials_02_ami_customization.html#modify-an-aws-parallelcluster-ami)
   * [Build a Custom AWS ParallelCluster AMI](https://docs.aws.amazon.com/parallelcluster/latest/ug/tutorials_02_ami_customization.html#build-a-custom-aws-parallelcluster-ami) 
2. Copy the AMI to a new one using encryption, as described [here](https://aws.amazon.com/blogs/aws/new-encrypted-ebs-boot-volumes/)
3. Use the new encrypted AMI ID as `custom_ami` parameter value in ParallelCluster configuration file
4. Create the cluster 
