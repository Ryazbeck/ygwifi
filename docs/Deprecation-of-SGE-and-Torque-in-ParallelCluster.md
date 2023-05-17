Support for SGE and Torque schedulers has been dropped for ParallelCluster >= 2.11.5.

---

All software (like SGE and Torque) needs constant updating to make sure it still builds on new OS distributions as they come along and - most importantly - is able to be run securely, given that hackers don’t rest looking for new ways of breaching systems. 

At AWS, security is our "job zero", so we pay attention when code falls into what we see as disrepair. We’ve been struggling with SGE and Torque for some time. It’s been getting more complicated to fit them happily into our CI/CD (automated build) pipelines and it’s now just plain hard to harden them. That means being exposed to the unintended consequences of coding decisions made years ago when most of the operating systems you use now didn’t exist.

Lately, we’ve realized just how limited that future is (in fact we think the end of the runway is pretty visible) so we’ve chosen now as the time to talk to you about it, rather than wait for an abrupt end when it just won’t compile or when there’s a security gotcha that we just can’t fix. We’re not planning to stop support immediately, but we’re signalling that migrating your workload can’t be put off another day.

### Deprecation in the Future

Versions 2.0.0 - 2.7.0 of ParallelCluster have included SGE and Torque as job schedulers available through cluster configuration options (in addition to Slurm and AWS Batch). SGE and Torque are open source schedulers created and maintained by a community, but for which there has not been active development in some time (2016-SGE, 2018-Torque). To minimize the risk of unfixable bugs or security issues affecting your business processes, we will be sunsetting our support for these two job schedulers in future releases of ParallelCluster.

Customers are welcome to continue using past releases of ParallelCluster if they wish to continue using SGE and Torque. For customers that wish to continue using later releases of ParallelCluster, however, they may wish in some cases to transition their workloads to using either Slurm or AWS Batch as their workload manager. In many cases, migrating from one job scheduler to another is a straightforward process that can be accomplished with minimal changes. We have compiled a few resources that could be useful as part of this process:

* [Transition from SGE to SLURM](https://github.com/aws/aws-parallelcluster/wiki/Transition-from-SGE-to-SLURM) will provide inormation on how to move from SGE to SLURM.

### Other resources:

* SchedMD, the maintainers of the open source job scheduler Slurm, have published what they describe as a Rosetta Stone for workload managers that can be used to translate commands specific to SGE or Torque (in addition to PBS, LSF, and LoadLeveler) into Slurm commands. https://slurm.schedmd.com/rosetta.pdf 
* There are also wrappers available for several SGE and Torque commands. More information is available on SchedMD’s website at https://slurm.schedmd.com/faq.html#torque
* Stanford Research Computing Center has prepared a guide to assist their users in migrating from SGE to Slurm. https://srcc.stanford.edu/sge-slurm-conversion
* The University of Georgia’s computing resource center has published its own guide to assist their users in migrating from Torque to Slurm. https://wiki.gacrc.uga.edu/wiki/Migrating_from_Torque_to_Slurm

Our documentation also includes information on the commands supported by AWS Batch (https://docs.aws.amazon.com/parallelcluster/latest/ug/awsbatchcli.html) as well as a guided tutorial showing how to run an MPI job within ParallelCluster (https://docs.aws.amazon.com/parallelcluster/latest/ug/tutorials_03_batch_mpi.html)