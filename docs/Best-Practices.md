# Head Node Instance Type

Although the head node doesn't execute any job, its functions and its sizing are crucial to the overall performance of the cluster.

When choosing the instance type to use for your head node you want to evaluate the following items:
* **Cluster size**: the head node orchestrates the scaling logic of the cluster and is responsible of attaching new nodes to the scheduler. If you need to scale up and down the cluster of a considerable amount of nodes then you want to give the head node some extra compute capacity.
* **Shared file systems**: when using shared file systems to share artefacts between compute nodes and the head node take into account that the head node is the node exposing the NFS server. For this reason you want to choose an instance type with enough network bandwidth and enough dedicated EBS bandwidth to handle your workflows.

# Network Performance

There are three hints that cover the whole range of possibilities to improve network communication.

* **Placement Group**: a cluster placement group is a logical grouping of instances within a single Availability Zone. You can find more information on placement group [here](https://docs.aws.amazon.com/en_us/AWSEC2/latest/UserGuide/placement-groups.html).
   * With ParallelCluster 2.x, you can configure the cluster to use your own placement group with `placement_group = <your_placement_group_name>`
or let ParalleCluster create a placement group with the "compute" strategy with `placement_group = DYNAMIC`. Details are [here].
   * With ParallelCluster 3.x, you can configure the queues to use your own placement group with `Networking > PlacementGroup > Id` set to your placement group id or let ParalleCluster create a placement group with `Networking > PlacementGroup > Enabled` set to `true`. Details are [here](https://docs.aws.amazon.com/parallelcluster/latest/ug/Scheduling-v3.html#yaml-Scheduling-SlurmQueues-Networking-PlacementGroup).

* **Enhanced Networking**: consider to choose an instance type that supports Enhanced Networking. For more information about Enhanced Networking see [here](https://docs.aws.amazon.com/en_us/AWSEC2/latest/UserGuide/enhanced-networking.html).

* **Instance bandwidth**: the bandwidth scales with instance size, please consider to choose the instance type which better suits your needs, see [here](https://docs.aws.amazon.com/en_us/AWSEC2/latest/UserGuide/EBSOptimized.html) and [here](https://docs.aws.amazon.com/en_us/AWSEC2/latest/UserGuide/EBSVolumeTypes.html).

# Open MPI

Increase the ulimit to allow a large number of files to be open:

```
# For large scale MPI runs (>1000 ranks)
echo 'sudo prlimit --pid $$ --nofile=10000:10000' >> $HOME/.bashrc
```

Run in a placement group:

```
[cluster yourcluster]
placement_group = DYNAMIC
```

# Limits

There are three limits that effect AWS ParallelCluster. You can check them by going to the [EC2 Console](https://console.aws.amazon.com/ec2/v2/home) > `Limits`



### On demand

<img width="1160" alt="Screen Shot 2019-06-25 at 4 19 52 PM" src="https://user-images.githubusercontent.com/5545980/60107936-0c48c780-9768-11e9-86e5-d690be8e625d.png">

1. `Running On-Demand EC2 instances`, make sure this is at least + 1 greater than the biggest cluster you want to launch. 
2. `Running On-Demand [instace_type] instances`
3. `EC2-VPC Elastic IPs` each cluster launched with `use_public_ips = true` (which the default if you don't set anything) uses 1 elastic ip. So if you want to have more than 5 clusters, you'll need to raise this limit.
