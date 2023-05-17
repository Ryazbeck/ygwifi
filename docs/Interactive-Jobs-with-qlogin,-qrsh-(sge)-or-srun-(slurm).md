### Interactive Jobs/Sessions with AWS ParallelCluster

**qlogin** is a [standard SGE command](http://manpages.org/qlogin), that starts an interactive session on one of the compute nodes. 

**qrsh** is a [standard SGE command](http://manpages.org/qrsh) that submits an interactive job, this jobs runs immediately and logs output to stdout.

**srun** is a [standard SLURM command](http://manpages.org/srun) that run a parallel job. If necessary, srun will first create a resource allocation in which to run the parallel job.

Since `qrsh` and `qlogin` behave largely the same in AWS ParallelCluster, I'm only going to discuss `qlogin` but you can substitute `qrsh` for `qlogin` in the following explanation:

### How to submit Interactive Jobs

If you have available running hosts you can submit a `qlogin` request and open an interactive session on a running compute node:
```bash
# qhost --> I have 1 running host
[ec2-user@ip-10-0-0-51 ~]$ qhost
HOSTNAME                ARCH         NCPU NSOC NCOR NTHR  LOAD  MEMTOT  MEMUSE  SWAPTO  SWAPUS
----------------------------------------------------------------------------------------------
global                  -               -    -    -    -     -       -       -       -       -
ip-10-0-2-196           lx-amd64        2    1    2    2  0.34    3.9G  212.9M     0.0     0.0

# qstat --> I don't have running jobs
[ec2-user@ip-10-0-0-51 ~]$ qstat

# qlogin --> I'll be redirect to the running compute node
[ec2-user@ip-10-0-0-51 ~]$ qlogin
Your job 2 ("QLOGIN") has been submitted
waiting for interactive job to be scheduled ...
Your interactive job 2 has been successfully scheduled.
Establishing builtin session to host ip-10-0-2-196.eu-west-1.compute.internal ...
[ec2-user@ip-10-0-2-196 ~]$ 

# qstat --> Now I have a running job associated to the qlogin submission
[ec2-user@ip-10-0-2-196 ~]$ qstat
job-ID  prior   name       user         state submit/start at     queue                          slots ja-task-ID
-----------------------------------------------------------------------------------------------------------------
      2 0.55500 QLOGIN     ec2-user     r     06/06/2019 10:22:54 all.q@ip-10-0-2-196.eu-west-1.     1
```
Instead, if you have no compute nodes, you are not able to use `qlogin` to connect to the host
```bash
# qstat --> I have 2 running jobs and 1 in pending --> no free compute nodes
[ec2-user@ip-10-0-0-51 ~]$ qstat
job-ID  prior   name       user         state submit/start at     queue                          slots ja-task-ID
-----------------------------------------------------------------------------------------------------------------
      3 0.55500 STDIN      ec2-user     r     06/06/2019 10:23:54 all.q@ip-10-0-2-196.eu-west-1.     1
      4 0.55500 STDIN      ec2-user     r     06/06/2019 10:23:54 all.q@ip-10-0-2-196.eu-west-1.     1
      5 0.55500 STDIN      ec2-user     qw    06/06/2019 10:23:48                                    1

# qlogin --> I'm not able to start an interactive job.
[ec2-user@ip-10-0-0-51 ~]$ qlogin
Your job 7 ("QLOGIN") has been submitted
waiting for interactive job to be scheduled ...Your "qlogin" request could not be scheduled, try again later.
```
Check your configuration for the following parameters:

```ini
[cluster ...]
initial_queue_size = ...
maintain_initial_size = ...
```
* **initial_queue_size** --> sets the initial number of EC2 instances to launch as compute nodes in the cluster.
* **maintain_initial_size** --> Boolean flag to maintain initial size of the Auto Scaling group for traditional schedulers.

  * If set to true, the Auto Scaling group will never have fewer members than the value of `initial_queue_size`. The cluster can still scale up to the value of `max_queue_size`.
  * If set to false, the Auto Scaling group can scale down to 0 members to prevent resources from sitting idle when they are not needed.
 
So if you'd like to use `qlogin` you should set `initial_queue_size > 0` and `mantain_initial_size = true`.

### Interactive Jobs/Sessions with AWS ParallelCluster in [Multiple Queue Mode](https://docs.aws.amazon.com/parallelcluster/latest/ug/queue-mode.html)

AWS ParallelCluster version 2.9.0 introduced multiple queue mode.
Multiple queue mode is supported when scheduler is set to slurm and the queue_settings setting is defined.

Without Multiple Queue Mode, user can only submit `srun` interactive command if required nodes are already in the cluster.

**When using Multiple Queue Mode, user now has the ability to run `srun` interactive commands that require scaling.**

```bash
# Initial state of cluster, with most nodes in power saving
$ sinfo
PARTITION AVAIL  TIMELIMIT  NODES  STATE NODELIST 
efa          up   infinite      4  idle~ efa-dy-c5n18xlarge-[1-4] 
efa          up   infinite      1   idle efa-st-c5n18xlarge-1 
gpu          up   infinite     10  idle~ gpu-dy-g38xlarge-[1-10] 
ondemand     up   infinite     20  idle~ ondemand-dy-c52xlarge-[1-10],ondemand-dy-t2xlarge-[1-10] 
spot*        up   infinite     13  idle~ spot-dy-c5xlarge-[1-10],spot-dy-t2large-[1-3] 
spot*        up   infinite      2   idle spot-st-t2large-[1-2] 

# Simple job we will be running
$ cat hostname.sh 
#!/bin/bash
sleep 30
hostname >> /shared/output.txt

# Run srun command that requires 2 nodes from ondemand queue and send process to background
# Note there is currently no available nodes in ondemand queue
$ srun -N 2 -p ondemand hostname.sh &
[1] 19784

# Job is in CF(CONFIGURING) state, 2 nodes are being powering up to run the job
$ squeue
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON) 
                20  ondemand hostname   ubuntu CF       0:36      2 ondemand-dy-c52xlarge-[1-2] 
$ sinfo
PARTITION AVAIL  TIMELIMIT  NODES  STATE NODELIST 
efa          up   infinite      4  idle~ efa-dy-c5n18xlarge-[1-4] 
efa          up   infinite      1   idle efa-st-c5n18xlarge-1 
gpu          up   infinite     10  idle~ gpu-dy-g38xlarge-[1-10] 
ondemand     up   infinite      2   mix# ondemand-dy-c52xlarge-[1-2] 
ondemand     up   infinite     18  idle~ ondemand-dy-c52xlarge-[3-10],ondemand-dy-t2xlarge-[1-10] 
spot*        up   infinite     13  idle~ spot-dy-c5xlarge-[1-10],spot-dy-t2large-[1-3] 
spot*        up   infinite      2   idle spot-st-t2large-[1-2]

# After several minutes nodes are launched and available, job is in R(Running) state
$ squeue
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON) 
                20  ondemand hostname   ubuntu  R       0:17      2 ondemand-dy-c52xlarge-[1-2] 
$ sinfo
PARTITION AVAIL  TIMELIMIT  NODES  STATE NODELIST 
efa          up   infinite      4  idle~ efa-dy-c5n18xlarge-[1-4] 
efa          up   infinite      1   idle efa-st-c5n18xlarge-1 
gpu          up   infinite     10  idle~ gpu-dy-g38xlarge-[1-10] 
ondemand     up   infinite     18  idle~ ondemand-dy-c52xlarge-[3-10],ondemand-dy-t2xlarge-[1-10] 
ondemand     up   infinite      2    mix ondemand-dy-c52xlarge-[1-2] 
spot*        up   infinite     13  idle~ spot-dy-c5xlarge-[1-10],spot-dy-t2large-[1-3] 
spot*        up   infinite      2   idle spot-st-t2large-[1-2] 

# Job finished and our output looks good
$ scontrol show job 20
JobId=20 JobName=hostname.sh
...
   JobState=COMPLETED Reason=None Dependency=(null)
...

$ cat /shared/output.txt 
ondemand-dy-c52xlarge-2
ondemand-dy-c52xlarge-1

# 2 nodes are power saved after `scaledown_idle_time` and cluster is back in initial state
$ sinfo
PARTITION AVAIL  TIMELIMIT  NODES  STATE NODELIST 
efa          up   infinite      4  idle~ efa-dy-c5n18xlarge-[1-4] 
efa          up   infinite      1   idle efa-st-c5n18xlarge-1 
gpu          up   infinite     10  idle~ gpu-dy-g38xlarge-[1-10] 
ondemand     up   infinite     20  idle~ ondemand-dy-c52xlarge-[1-10],ondemand-dy-t2xlarge-[1-10] 
spot*        up   infinite     13  idle~ spot-dy-c5xlarge-[1-10],spot-dy-t2large-[1-3] 
spot*        up   infinite      2   idle spot-st-t2large-[1-2]
```