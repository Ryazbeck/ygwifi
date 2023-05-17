# Slurm will not mark non responsive node as down, if node is within ResumeTimeout

## Issue description
Issue was first reported in [issue #2117](https://github.com/aws/aws-parallelcluster/issues/2117) and applicable to pcluster running on new slurm scaling architecture, `aws-parallelcluster>=2.9.0` and `scheduler==slurm`.

The issue is slurm will not mark non-responsive nodes as `down` within `ResumeTimeout` of node power up.
Slurm will requeue jobs automatically if a node running the job is `down`.
As a result, this issue might also result in long requeue time for jobs that have non-responsive nodes.

ParallelCluster current sets ResumeTimeout to 3600 seconds, so in practice customer may need to wait ~1 hr for slurm to place a newly launched, non-responsive node into down.

The issue can be reproduced by powering up a node and making node non-responsive within ~1 hr of launch time by killing `slurmd` on compute or stopping the backing instance.

## Not applicable
This issue is not applicable to the following scenarios, in which ParallelCluster process will actively set problematic nodes to `down`:
* Terminated instances
* Instances with scheduled event
* Instances with failing instance status check == `impaired`
* Instances with failing system status check == `impaired`
* Instances failing during bootstrap process. These instances will self-terminate, and fall under terminated instances case.

## Root cause
Based on communication with SchedMD, we confirm that this issue is due to designed behavior of slurm.

Currently slurm's logic will not place non-responsive node in `down` nor mark node as non-responsive with `*` suffix, if node is within `ResumeTimeout` of the node's power_up time.

After `ResumeTimeout` expires, normal logic regarding non-responsive nodes will take place, and `SlurmdTimeout` will solely control how long slurm will wait before marking non-responsive nodes as down.

In general, ParallelCluster's current integration with slurm was designed to mostly rely on scheduler to provide health check regrading the operating status of nodes. As a result, users might experience this slurm health check issue directly in cluster operation.

## Mitigation
Since the issue is dependent on `ResumeTimeout`, the issue can be mitigated if users modify `ResumeTimeout` to be a shorter time.

From the official documentation of ResumeTimeout:
> Maximum time permitted (in seconds) between when a node resume request is issued and when the node is actually available for use

ParallelCluster current sets ResumeTimeout to 3600 seconds because different customer might have different bootstrap time, and we do not want to impose a low limit on the maximum time permitted for a node to join the cluster.

However, users can tune `ResumeTimeout` to the specific time it take for their compute instances to complete bootstrapping and join the cluster.

Please follow the below instructions to modify `ResumeTimeout`:
1. Stop cluster by executing `pcluster stop <cluster name>`
2. ssh into Head node with `pcluster ssh <cluster name>`.
3. Manually set `ResumeTimeout` to chosen time by modify `/opt/slurm/etc/slurm.conf` in Head node.
3. Restart `slurmctld` by executing `sudo systemctl restart slurmctld` or `sudo service slurmctld restart`, depending on your OS
4. Verify that new `ResumeTimeout` is set in slurm by executing `scontrol show config | grep "ResumeTimeout"`
5. Start cluster by executing `pcluster start <cluster name>`

Here are some things to consider when tuning `ResumeTimeout`:
* This is the max time allowed between a node being powered up and a compute instance joining the cluster by starting slurmd. If slurmd is not started on a compute instance by `ResumeTimeout` the node will be marked as down
* This time will need to be longer than the compute instance bootstrap time
* This time will need to be longer, if user has limits applicable to `RunInstances` that delays launch of instances on a large scale
* It's always better to start with a longer ResumeTimeout to prevent issues and lower to follow the actual time it takes for compute to join cluster for a particular setup
* As a general starting point, `ResumeTimeout=1200`, i.e. 20 mins, should be a safe timeout for most cluster setups

## Next steps
We have communicated with SchedMD why we think this behavior is undesirable and inconsistent with the documentation on `ResumeTimeout` and `SlurmdTimeout`. We will try to continually push for a change regarding this behavior.


