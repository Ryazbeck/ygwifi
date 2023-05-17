Only applicable for `pcluster>=v2.10.0 && scheduler == slurm`.

## Overview

Starting with AWS ParallelCluster version 2.10, you have additional control over instance launch behavior. By default, in versions <= 2.9, instances in a batch follow a soft launch (best-effort strategy), with at least some of the batch launching when some of the requested instances fail. However, with version 2.10, you can opt to configure instances in a batch to have a firm launch using an all-or-nothing launch behavior. As such, the entire batch fails if any one of the instances in the batch cannot be provisioned.

## How to enable this feature

To enable the all-or-nothing launch behavior for dynamic nodes for firm launches, set `all_or_nothing_batch = True` in the `ResumeProgram` config at `/etc/parallelcluster/slurm_plugin/parallelcluster_slurm_resume.conf`.

To further configure instance launch behavior with respect to the specific requirements of your application, you can set the `max_batch_size` parameter. This parameter specifies the upper limit to the number of instances in your launch batch. The next section provides a more in-depth explanation for this parameter as well as several related considerations.

*Note* The default settings are `all_or_nothing_batch = False` and `max_batch_size = 500`. These settings ensure that instances in a batch have a soft launch with a smaller number of `RunInstances` calls.

The following example is a `ResumeProgram` config with the firm (all-or-nothing) launch behavior enabled:
```
$ cat /etc/parallelcluster/slurm_plugin/parallelcluster_slurm_resume.conf
# DO NOT MODIFY
[slurm_resume]
cluster_name = demo
region = us-east-2
proxy = NONE
dynamodb_table = parallelcluster-demo
hosted_zone = ZXXXXXXXXXXXXXXX
dns_domain = demo.pcluster
use_private_hostname = false
master_private_ip = 172.x.x.x
master_hostname = ip-172-x-x-x.us-east-2.compute.internal
# Options added:
all_or_nothing_batch = True      
max_batch_size = 100             
```
## Understanding the launch-batch and `ResumeProgram` workflow

With its improved Slurm integration added to AWS ParallelCluster in version 2.9, dynamic nodes in ParallelCluster use the Slurm cloud bursting plugin and rely on the Slurm integrated power saving mechanism (for more details you can consult our [Slurm user guide](https://docs.aws.amazon.com/parallelcluster/latest/ug/multiple-queue-mode-slurm-user-guide.html)).

The workflow to launch instances for dynamic nodes is as follows:

1. A job is submitted to Slurm.
2. Slurm allocates the job to multiple nodes, putting any node that is in the `POWER_SAVED` state into the `POWER_UP` state.
3. Slurm calls `ResumeProgram` at a specified time internal to request nodes that need to be launched as part of the `POWER_UP` workflow. No job information is passed into `ResumeProgram`. Slurm can call `ResumeProgram` with nodes from multiple jobs but doesn’t pass node-job correspondence information into `ResumeProgram`.
4. Slum calls `ResumeProgram` with a list of nodes to launch. The nodes are parsed from the input following the same order in which they are passed.
5. For each of the instance types in a queue or partition, AWS ParallelCluster groups the nodes into batches based on their `max_batch_size` parameter configuration and uses the `RunInstances` call to launch these batches. Each call is referred to as a launch-batch.
6. The `RunInstances` call also launches the nodes along with each of their corresponding instances. Any node that can’t be launched is placed in the POWER_DOWN state later reset to the `POWER_SAVED` state.
7. When the launched instances finish the configuration process, slurmd is started on compute instance. At this time, the job can also begin to use the corresponding slurm node.

The all_or_nothing_batch parameter modifies how `RunInstances` calls behave. By default, `RunInstances` calls follow a soft launch strategy in which some but not necessarily all instances in a launch-batch are launched by the call. If `all_or_nothing_batch = True` is set, each `RunInstances` call follows a firm launch strategy. For this, all instances in a launch-batch must be launched. If the capacity for the entire launch-batch isn’t reached, then the `RunInstances` call fails and no instance is launched.

## `ResumeProgram` workflow examples

* Let's assume `max_batch_size = 4` and Slurm calls `ResumeProgram` with the following list of nodes `queue1-dy-c5xlarge-[1-5], queue1-dy-t2micro-2, queue2-dy-c5xlarge[1-3]`. This results in the following:
    * For every instance type in every queue and partition, nodes are grouped in to launch-batches according to the max_batch_size = 4 configuration. Therefore, we need to have the following batches: `queue1-dy-c5xlarge-[1-4], queue1-dy-c5xlarge-5, queue1-dy-t2micro-2, queue2-dy-c5xlarge-[1-3]`. One `RunInstances` call is made for every launch-batch.
    * If `all_or_nothing_batch = False` is set, and `RunInstances` call for `queue2-dy-c5xlarge-[1-3]` can’t launch at full capacity, and can only launch one c5.xlarge instance, then queue2-dy-c5xlarge-1 is configured with the successfully launched instance, and  queue2-dy-c5xlarge-[2-3] is marked down due to an unsuccessful launch for other instances.
    * If `all_or_nothing_batch = True` is set, and the `RunInstances` call for `queue2-dy-c5xlarge-[1-3]` can’t launch at full capacity, the entire `RunInstances` call fails and no instance is launched. `queue2-dy-c5xlarge-[1-3]` is marked down due to an unsuccessful launch of the instances.

## Limits

The following are the limits on this feature:

* Requests are executed on the basis of Slurm requests rather a job basis. Slurm groups multiple job requests that are submitted within close succession. This can sometimes result in failed an instance launch for groups of jobs even when the capacity is available to satisfy some (though not all) of the jobs.
    * Example: Three jobs are submitted in close succession. Job1 is allocated to `queue1-dy-c5xlarge-[1-4]`, Job 2 is allocated to `queue1-dy-c5xlarge-[5-6]`, and Job 3 is allocated to `queue1-dy-c5xlarge-[7-8]`. For this, `max_batch_size = 10`,  `all_or_nothing_batch = True` are set. Slurm calls `ResumeProgram` to `POWER_UP` `queue1-dy-c5xlarge-[1-8]`. Because the `max_batch_size = 10` is set, `queue1-dy-c5xlarge-[1-8]` is grouped into the same launch-batch. However, because of this, if the entire capacity can’t be launched, then `queue1-dy-c5xlarge-[1-8]` fails, causing all three jobs to fail.
    * This limit can be mitigated by spacing out job requests so each call to `ResumeProgram` only contains the nodes that are required for one job. We recommend waiting at least one minute between submitting two jobs, so that each call to `ResumeProgram` only contains nodes from one job each time.
* Firm all-or-nothing scaling is achieved on a per-instance type basis. You can’t use multiple instance types for all-or-nothing scaling. If you want to run a job that requires multiple instance types (for example, the P3dn and C5n instances types), all-or-nothing scaling guarantee isn’t plausible.
    * *Example: *Job1 is allocated to `queue1-dy-c5xlarge-[1-4],queue1-dy-t2micro-1`,  `max_batch_size = 10`, and `all_or_nothing_batch = True` is set. The launch-batches are `queue1-dy-c5xlarge-[1-4]` and `queue1-dy-t2micro-1`. These launch-batches are launched by two separate `RunInstances` calls.
* All-or-nothing isn’t guaranteed if a node set allocated to a job isn’t contiguous.
    * Slurm most often calls `ResumeProgram` with an ordered node list, and `ResumeProgram` groups nodes into launch-batches based on the order they are passed in. As a result, launch-batches aren’t correlated correctly with node used by each job.
    * Example: Two jobs are submitted in close succession. If Job1 is allocated to `queue1-dy-c5xlarge-[1, 3-4]`, Job 2 is allocated to `queue1-dy-c5xlarge-[2, 5-6]`, and `max_batch_size=3` is set. Slurm calls `ResumeProgram` with `queue1-dy-c5xlarge-[1-6]`, and launch-batches are `queue1-dy-c5xlarge-[1-3]`, and `queue1-dy-c5xlarge-[4-6]`, which don’t correspond to the two jobs directly
    * Using --contiguous when submitting your jobs might help.
* The maximum number of nodes that can be launched in a firm launch is limited to maximum number of instance-launches possible with a `RunInstances` call. This number is restricted by the limitations of the `RunInstances` API. By default, the API can allow up to 500 instance to be launched in a single `RunInstances` call (`max_batch_size = 500`). If you want to increase this limit, contact AWS customer support.
* This functionality is only available as a per-cluster option, all queues would be subject to the same `all_or_nothing_batch` and `max_batch_size` settings.
* If an instance fails during boot (for example an EC2 instance or a node fails), then the specific node that fails is automatically terminated. Then, Slurm reassigns the job to a new node or new set of nodes. In most cases, Slurm reuses the previously successful nodes and requests a replacement for the failed instance or instances. When this occurs, all-or-nothing scaling canot be guaranteed because the nodes running the job are from different launch-batches.
* This feature is only available for dynamic nodes.
    * The `ResumeProgram` workflow is only applicable for dynamic nodes
    * Static nodes are managed separately by clustermgtd on a soft launch, best-effort basis.

## Example use case for the all-or-nothing batches

With all-or-nothing batches, you can opt to configure a launch-batch to be launched with a soft launch or a firm launch. Note that all-or-nothing scaling can’t be guaranteed on a per-job basis because launch-batches don’t directly correspond to all the nodes required by a job.

The following example illustrates how all-or-nothing batches functions. Homogeneous jobs are submitted in a way that matches each launch batch with all the nodes required by a job. In practice, a majority of job submissions are heterogeneous in terms of instance type and the number of nodes required. 

We recommend that, when you enable all-or-nothing batches, you set the batch size to the largest number of single-instance-type instances that is required for a job. This is so that your largest launches can all be completed in a all-or-nothing launch behavior.

 Consider the following conditions when setting your batch size.

* Large `max_batch_size`: Large launches can follow an all-or-nothing strategy. However, smaller launches for small jobs might be grouped together, and might collectively fail if there isn’t enough capacity for the entire group.
* Small `max_batch_size`: Small launches can be separated into independent launch batches, but large launches might be separated into multiple launch batches, and an all-or-nothing launch strategy can’t be adapted use large launches.


Example Scenario

* Consider the following scenario. The following details the initial state of a cluster. There is no job in the queues. Consider the scheduled2 queue. In this queue, there are 5,000 nodes. It is in the POWER_SAVING state.
```
$ sinfo
PARTITION   AVAIL  TIMELIMIT  NODES  STATE NODELIST 
scheduled1*    up   infinite     20  idle~ scheduled1-dy-m54xlarge-[1-20] 
scheduled2     up   infinite   5000  idle~ scheduled2-dy-c5xlarge-[1-5000] 
$ squeue
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
```
* Submit jobs that require 50 nodes for each job and use all-or-nothing behavior for launch-batches.
* Add the options `all_or_nothing_batch = True` to the `ResumeProgram` config located at `/etc/parallelcluster/slurm_plugin/parallelcluster_slurm_resume.conf`. This turns on the all-or-nothing launch behavior for each launch-batch
* The default setting is `max_batch_size = 500`. Don't change this setting, but understand that, because the queue only contains one instance type, all the nodes in a queue are most likely grouped into one launch batch. Then, because of this, if the entire batch can’t be launched, this might also cause multiple small jobs to fail.
* Because the largest number of single-instance-type instances that can be required for a job is 50 for this example, each launch batch can only correspond to 1 job only. For this, set max_batch_size = 50 to `ResumeProgram` config located at `/etc/parallelcluster/slurm_plugin/parallelcluster_slurm_resume.conf`. Note that `ResumeProgram` config will have other parameters already in place. Don’t modify those parameters.
```
$ cat /etc/parallelcluster/slurm_plugin/parallelcluster_slurm_resume.conf
# DO NOT MODIFY
[slurm_resume]
cluster_name = scheduled
region = us-east-2
proxy = NONE
dynamodb_table = parallelcluster-scheduled
hosted_zone = ZXXXXXXXXXXXXXXX
dns_domain = scheduled.pcluster
use_private_hostname = false
master_private_ip = 172.x.x.x
master_hostname = ip-172-x-x-x.us-east-2.compute.internal
# Option added:
all_or_nothing_batch = True
max_batch_size = 50
```
* Submit 20 “sleep 300” array jobs, each requiring 50 nodes, or 1000 nodes in total. Failed jobs in most cases are re-queued, but to clearly show which jobs failed because of unsuccessful launch, specify the ——no-requeue option so that jobs that failed are removed from the queue.
```
# -a 1-20: submit 20 array jobs
# -N 50: each job requires 50 nodes
# -p scheduled2: submit job to scheduled2 queue/partition
# --exclusive: allocate each node to a job completely, so no 2 jobs will share a node
# --no-requeue: no automatic requeue in case of failure
# --contiguous: allocated nodes must form a contiguous set
$ sbatch --wrap "sleep 300" -a 1-20 -N 50 -p scheduled2 --exclusive --no-requeue --contiguous
```
* After the job is submitted, 1000 nodes total are assigned to jobs by Slurm. Because the nodes were initially in the POWER_SAVING state, Slurm places the nodes in the `POWER_UP` state and calls `ResumeProgram` to launch instances for the nodes. 
```
# 1000 nodes placed into `POWER_UP` state
$ sinfo
PARTITION   AVAIL  TIMELIMIT  NODES  STATE NODELIST 
scheduled1*    up   infinite     20  idle~ scheduled1-dy-m54xlarge-[1-20] 
scheduled2     up   infinite   1000 alloc# scheduled2-dy-c5xlarge-[1-1000] 
scheduled2     up   infinite   4000  idle~ scheduled2-dy-c5xlarge-[1001-5000]
```
* 1000 nodes are launched in batches of up to 50 by `ResumeProgram`. With `all_or_nothing_batch = True` set, each launch-batch of 50 nodes, the number of instances launched is also 50 withstanding that this capacity can be reached. Otherwise, the number of instances launched is lower if the capacity is lower. If there is no capacity, all instances for each launch-batch and the entire batch fail.

* Because of capacity limitations, you can only launch 300 instances (6 batches of 50) for 300 nodes. The remaining 700 nodes (14 batches failed to launch) are reset and put back into POWER_DOWN.
```
# Only able to launch 300 nodes
# Failed 700 nodes placed into down automatically by `ResumeProgram`
$ sinfo
PARTITION   AVAIL  TIMELIMIT  NODES  STATE NODELIST 
scheduled1*    up   infinite     20  idle~ scheduled1-dy-m54xlarge-[1-20] 
scheduled2     up   infinite    300 alloc# scheduled2-dy-c5xlarge-[1-300] 
scheduled2     up   infinite    700  down# scheduled2-dy-c5xlarge-[301-1000] 
scheduled2     up   infinite   4000  idle~ scheduled2-dy-c5xlarge-[1001-5000]
```
* Because of how the job was setup and because of the max_batch_size setting, the node set is allocated to jobs according to the launch-batches. Six jobs run successfully because there are six successful launch batch. The other jobs failed because their launch batch also failed.
```
# 6 job able to run, the rest failed and removed from queue because no-requeue
$ squeue
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON) 
             872_1 scheduled     wrap   ubuntu CF       1:25     50 scheduled2-dy-c5xlarge-[1-50] 
             872_2 scheduled     wrap   ubuntu CF       1:25     50 scheduled2-dy-c5xlarge-[51-100] 
             872_3 scheduled     wrap   ubuntu CF       1:25     50 scheduled2-dy-c5xlarge-[101-150] 
             872_4 scheduled     wrap   ubuntu CF       1:25     50 scheduled2-dy-c5xlarge-[151-200] 
             872_5 scheduled     wrap   ubuntu CF       1:25     50 scheduled2-dy-c5xlarge-[201-250] 
             872_6 scheduled     wrap   ubuntu CF       1:25     50 scheduled2-dy-c5xlarge-[251-300]
# After a bit of time, jobs are up and running, 700 failed to launch nodes in POWER_DOWN
$ squeue
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON) 
             872_5 scheduled     wrap   ubuntu  R       0:01     50 scheduled2-dy-c5xlarge-[201-250] 
             872_1 scheduled     wrap   ubuntu  R       1:01     50 scheduled2-dy-c5xlarge-[1-50] 
             872_2 scheduled     wrap   ubuntu  R       1:01     50 scheduled2-dy-c5xlarge-[51-100] 
             872_3 scheduled     wrap   ubuntu  R       1:01     50 scheduled2-dy-c5xlarge-[101-150] 
             872_4 scheduled     wrap   ubuntu  R       1:01     50 scheduled2-dy-c5xlarge-[151-200] 
             872_6 scheduled     wrap   ubuntu  R       1:01     50 scheduled2-dy-c5xlarge-[251-300] 
$ sinfo
PARTITION   AVAIL  TIMELIMIT  NODES  STATE NODELIST 
scheduled1*    up   infinite     20  idle~ scheduled1-dy-m54xlarge-[1-20] 
scheduled2     up   infinite    700  idle% scheduled2-dy-c5xlarge-[301-1000] 
scheduled2     up   infinite   4000  idle~ scheduled2-dy-c5xlarge-[1001-5000] 
scheduled2     up   infinite    300  alloc scheduled2-dy-c5xlarge-[1-300] 
```
## Summary

You can enable the all-or-nothing scaling behavior at launch-batch level by setting `all_or_nothing_batch = True` in the `ResumeProgram` config at `/etc/parallelcluster/slurm_plugin/parallelcluster_slurm_resume.conf`.

We recommend that, if you set `all_or_nothing_batch = True`, you should set `max_batch_size` to the largest number of single-instance-type instances that can be used for a job. As such, so your largest launches are made in all-or-nothing fashion.

You should consider the following conditions when setting your `max_batch_size`:

* Large `max_batch_size`: Large launches can be made in all-or-nothing fashion. However, smaller launches for small jobs might be grouped together, and might fail collective if capacity for the entire group cannot be satisfied
* Small `max_batch_size`: Small launches can be separated into even smaller, separate launch batches, but large launches might be separated into multiple launch batches, and all-or-nothing behavior will not apply to large launches.


`ResumeProgram` logs are located in `/var/log/parallelcluster/slurm_resume.log`, and might be helpful to debug and understand launch behavior. As a general rule, having control over `all_or_nothing_batch` and `max_batch_size` options in the `ResumeProgram` workflow can allow you to have greater control over how dynamic nodes are launched.
