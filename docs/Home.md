Welcome to the AWS ParallelCluster Wiki

### Schedulers ⏱🗓
* [Interactive Jobs with qlogin, qrsh (sge) or srun (slurm)](https://github.com/aws/aws-parallelcluster/wiki/Interactive-Jobs-with-qlogin,-qrsh-(sge)-or-srun-(slurm))
* [Deprecation of SGE and Torque in ParallelCluster](https://github.com/aws/aws-parallelcluster/wiki/Deprecation-of-SGE-and-Torque-in-ParallelCluster)
* [Transition from SGE to SLURM](https://github.com/aws/aws-parallelcluster/wiki/Transition-from-SGE-to-SLURM)
* [How to enable slurmrestd on ParallelCluster 3.0](https://github.com/aws/aws-parallelcluster/wiki/How-to-enable-slurmrestd-on-ParallelCluster-3.0)

### Development 👨‍💻
* [How to setup Public Private Networking](https://github.com/aws/aws-parallelcluster/wiki/Public-Private-Networking)
* [Open MPI Install from Source and Uninstall](https://github.com/aws/aws-parallelcluster/wiki/OpenMPI-Install-from-Source-and-Uninstall)
* [Git Pull Request Instructions](https://github.com/aws/aws-parallelcluster/wiki/Git-Pull-Request-Instructions)

### Best Practices 👩‍💻
* [General Best Practices](https://github.com/aws/aws-parallelcluster/wiki/Best-Practices)
* [EFS](https://github.com/aws/aws-parallelcluster/wiki/EFS:-best-practices-and-known-issues)
* [FSx](https://github.com/aws/aws-parallelcluster/wiki/FSx:-best-practices-and-known-issues)

### Debugging 🕷
* [Slurm issues](https://github.com/aws/aws-parallelcluster/wiki/Slurm-Issues)
* [Stack Creation Failures](https://github.com/aws/aws-parallelcluster/wiki/Stack-Creation-Failures)

### Logging 🖨
* [Creating an Archive of a Cluster's Logs](https://github.com/aws/aws-parallelcluster/wiki/Creating-an-Archive-of-a-Cluster's-Logs)
* [CloudWatch Logs](https://github.com/aws/aws-parallelcluster/wiki/CloudWatch-Logs)

### Ninja Hacks 🚀
* [ParallelCluster: Launching a Login Node](https://github.com/aws/aws-parallelcluster/wiki/ParallelCluster:-Launching-a-Login-Node)
* [Launch instances with ODCR (On-Demand-Capacity-Reservations)](https://github.com/aws/aws-parallelcluster/wiki/Launch-instances-with-ODCR-(On-Demand-Capacity-Reservations))
* [Configuring all_or_nothing_batch launches](https://github.com/aws/aws-parallelcluster/wiki/Configuring-all_or_nothing_batch-launches)
* [MultiUser Support](https://github.com/aws/aws-parallelcluster/wiki/Multi-User-Support)
* [ParallelCluster Awesomeness](https://github.com/aws/aws-parallelcluster/wiki/ParallelCluster-Awesomeness)
* [Self patch a Cluster Used for Submitting Multi node Parallel Jobs through AWS Batch](https://github.com/aws/aws-parallelcluster/wiki/Self-patch-a-Cluster-Used-for-Submitting-Multi-node-Parallel-Jobs-through-AWS-Batch)
* [AWS Batch with a custom Dockerfile](https://github.com/aws/aws-parallelcluster/wiki/AWS-Batch-with-a-custom-Dockerfile)
* [Use an Existing Elastic IP](https://github.com/aws/aws-parallelcluster/wiki/Use-an-Existing-Elastic-IP)
* [Create cluster with encrypted root volumes](https://github.com/aws/aws-parallelcluster/wiki/Create-cluster-with-encrypted-root-volumes)
* [How to use a native NICE DCV Client](https://github.com/aws/aws-parallelcluster/wiki/NICE-DCV-integration)
* [Create Ubuntu AMI with Unattended Upgrades disabled](https://github.com/aws/aws-parallelcluster/wiki/Create-Ubuntu-AMI-with-Unattended-Upgrades-disabled)
* [Update cluster when snapshot associated to EBS volume is deleted](https://github.com/aws/aws-parallelcluster/wiki/Cluster-Update-when-EBS-Snapshot-Used-at-Cluster-Creation-doesn't-Exist-Anymore)
* [Installing Alternate CUDA Versions on AWS ParallelCluster](https://github.com/aws/aws-parallelcluster/wiki/Installing-Alternate-CUDA-Versions-on-AWS-ParallelCluster)

### Known Issues 3.x 🚨
* [(3.2.0 3.5.1) GPU nodes not coming back online after `scontrol reboot`](https://github.com/aws/aws-parallelcluster/wiki/(3.2.0-3.5.1)-GPU-nodes-not-coming-back-online-after-scontrol-reboot)
* [(3.0.0-3.5.1) ParallelCluster CLI raises exception “module 'flask.json' has no attribute 'JSONEncoder'”](https://github.com/aws/aws-parallelcluster/wiki/(3.0.0-3.5.1)-ParallelCluster-CLI-raises-exception-%E2%80%9Cmodule-'flask.json'-has-no-attribute-'JSONEncoder'%E2%80%9D)
* [(3.3.0-3.5.1) Cluster updates can break Slurm accounting functionality](https://github.com/aws/aws-parallelcluster/wiki/(3.3.0-3.5.1)-Cluster-updates-can-break-Slurm-accounting-functionality)
* [(3.0.0-3.2.1) Running nodes might be mistakenly replaced when new jobs are scheduled](https://github.com/aws/aws-parallelcluster/wiki/(3.0.0-3.2.1)-Running-nodes-might-be-mistakenly-replaced-when-new-jobs-are-scheduled)
* [(3.3.0-3.5.0) Update cluster to remove shared EBS volumes can potentially cause node launching failures](https://github.com/aws/aws-parallelcluster/wiki/(3.3.0-3.5.0)-Update-cluster-to-remove-shared-EBS-volumes-can-potentially-cause-node-launching-failures)
* [(3.0.0-3.5.0) DCV virtual session on Ubuntu 20.04 might show a black screen](https://github.com/aws/aws-parallelcluster/wiki/(3.5.0-and-earlier)-DCV-virtual-session-on-Ubuntu-20.04-might-show-a-black-screen)
* [(3.3.0-3.4.1) Custom AMI creation fails on Ubuntu 20.04 during MySQL packages installation](https://github.com/aws/aws-parallelcluster/wiki/(3.3.0-3.4.1)-Custom-AMI-creation-fails-on-Ubuntu-20.04-during-MySQL-packages-installation)
* [(3.3.0-3.4.0) Slurm cluster NodeName and NodeAddr mismatch after cluster scaling](https://github.com/aws/aws-parallelcluster/wiki/(3.3.0-3.4.0)-Slurm-cluster-NodeName-and-NodeAddr-mismatch-after-cluster-scaling)
* [(3.0.0-3.2.1) ParallelCluster API cannot create new cluster](https://github.com/aws/aws-parallelcluster/wiki/(3.0.0--3.2.1)--ParallelCluster-API-cannot-create-new-cluster)
* [(3.1.x) Termination of idle dynamic compute nodes potentially broken after performing a cluster update](https://github.com/aws/aws-parallelcluster/wiki/(3.1.x)-Termination-of-idle-dynamic-compute-nodes-potentially-broken-after-performing-a-cluster-update)
* [(3.0.0-3.1.4) ParallelCluster API Stack Upgrade Fails for ECR resources](https://github.com/aws/aws-parallelcluster/wiki/(3.0.0-3.1.4)-ParallelCluster-API-Stack-Upgrade-Fails-for-ECR-resources)
* [(3.0.0-3.1.4) Unable to perform cluster update when using API or documented user policies](https://github.com/aws/aws-parallelcluster/wiki/(3.0.0-3.1.4)-Unable-to-perform-cluster-update-when-using-API-or-documented-user-policies)
* [(3.0.0-3.1.3) Unable to create cluster or custom image when using API or CLI with documented user policies](https://github.com/aws/aws-parallelcluster/wiki/(3.0.0-3.1.3)-Unable-to-create-cluster-or-custom-image-when-using-API-or-CLI-with-documented-user-policies)
* [(3.0.0-3.1.3) AWSBatch Multi node Parallel jobs fail if no EBS defined in cluster](https://github.com/aws/aws-parallelcluster/wiki/(3.0.0-3.1.3)-AWSBatch---Multi-node-Parallel-jobs-fail-if-no-EBS-defined-in-cluster)
* [(3.1.1-3.1.2) Profiles not loaded when connected through NICE DCV session](https://github.com/aws/aws-parallelcluster/wiki/(3.1.1-3.1.2)-Profiles-not-loaded-when-connected-through-NICE-DCV-session)
* [(3.0.0-3.1.3) build image creates invalid images when using aws-cdk.aws-imagebuilder==1.153](https://github.com/aws/aws-parallelcluster/wiki/(3.0.0-3.1.3)-build-image-creates-invalid-images-when-using-aws-cdk.aws-imagebuilder-1.153.0)
* [(3.0.0-3.1.2) build image stack deletion failed after image successfully created](https://github.com/aws/aws-parallelcluster/wiki/(3.0.0-3.1.2)-build-image-stack-deletion-failed-after-image-successfully-created)
* [(3.1.1) Issue with clusters in isolated networks](https://github.com/aws/aws-parallelcluster/wiki/(3.1.1)-Issue-with-clusters-in-isolated-networks)
* [(3.0.0) Cluster scaling fails after a head node reboot on Ubuntu 18.04 and Ubuntu 20.04](https://github.com/aws/aws-parallelcluster/wiki/ParallelCluster-3.0.0-on-Ubuntu-18-and-20:-scaling-daemon-is-down-after-a-head-node-reboot)
* [(3.0.0) Deleting API Infrastructure produces CFN Stacks failure](https://github.com/aws/aws-parallelcluster/wiki/Deleting-API-Infrastructure-produces-CFN-Stacks-failure)

### Known Issues (3.x and 2.x) 🚨
* [(2.2.1 3.3.0) Risk of deletion of managed FSx for Lustre file system when updating a cluster](https://github.com/aws/aws-parallelcluster/wiki/(2.2.1-3.3.0)-Risk-of-deletion-of-managed-FSx-for-Lustre-file-system-when-updating-a-cluster)
* [(3.0.2 / 2.11.3 and earlier) Possible performance degradation due to log4j cve 2021 44228 hotpatch service on Amazon Linux 2.](https://github.com/aws/aws-parallelcluster/wiki/Possible-performance-degradation-due-to-log4j-cve-2021-44228-hotpatch-service-on-Amazon-Linux-2)
* [(2.10.1-2.11.2 and 3.0.0) Custom AMI creation (`pcluster createami` or `pcluster build-image`) fails with ARM architecture](https://github.com/aws/aws-parallelcluster/wiki/Custom-AMI-creation-(pcluster-createami-or-build-image)-fails-with-ARM-architecture)

#### Fixed
* [(3.0.2 / 2.11.3 and earlier) Custom AMI creation fails for centos7 and ubuntu1804](https://github.com/aws/aws-parallelcluster/wiki/(3.0.2,-2.11.3-and-earlier)-Custom-AMI-creation-(pcluster-build-image-or-createami)-fails-for-centos7-and-ubuntu1804) Issue started on 12/8/2021, resolved on 1/20/2022

### Known Issues 2.x 🚨
* [(2.8.0-2.10.1) Configuration validation failure: architecture of AMI and instance type does not match](https://github.com/aws/aws-parallelcluster/wiki/Configuration-validation-failure:-architecture-of-AMI-and-instance-type-does-not-match)
* [(2.10.0) Issue with CentOS 8 Custom AMI creation](https://github.com/aws/aws-parallelcluster/wiki/Issue-with-CentOS-8-Custom-AMI-creation)
* [(2.5.0-2.10.0) Issue with Ubuntu 18.04 Custom AMI creation](https://github.com/aws/aws-parallelcluster/wiki/Issue-with-Ubuntu-18.04-Custom-AMI-creation)
* [(2.10.1-2.10.2) Issue running Ubuntu 18 ARM AMI on first generation AWS Graviton instances
](https://github.com/aws/aws-parallelcluster/wiki/Issue-running-Ubuntu-18-ARM-AMI-on-first-generation-AWS-Graviton-instances)
* [(2.10.1-2.10.2) P4d support on Amazon Linux 1](https://github.com/aws/aws-parallelcluster/wiki/P4d-support-on-Amazon-Linux-1)
* [(2.6.0-2.10.3) Custom AMI creation (`pcluster createami`) fails](https://github.com/aws/aws-parallelcluster/wiki/Custom-AMI-creation-(pcluster-createami)-fails-with-ParallelCluster-versions-from-2.6.0-to-2.10.3)
* [(2.9.1 and earlier) Custom AMI creation (`pcluster createami`) fails](https://github.com/aws/aws-parallelcluster/wiki/Custom-AMI-creation-(pcluster-createami)-fails-with-ParallelCluster-2.9.1-and-earlier)
* [(2.10.0 and earlier) Cluster creation fails if `enable_intel_hpc_platform=true` is in the configuration file](https://github.com/aws/aws-parallelcluster/wiki/Cluster-creation-fails-if-enable_intel_hpc_platform=true-is-in-the-configuration-file)
* [(2.10.4 and earlier) Batch cluster creation fails in China regions](https://github.com/aws/aws-parallelcluster/wiki/Batch-cluster-creation-in-China-regions-fails-with-parallelCluster-2.10.4-and-earlier)
* [(2.11.0) Possible performance degradation on Amazon Linux 2 when enabling CloudWatch Logging](https://github.com/aws/aws-parallelcluster/wiki/Possible-performance-degradation-on-ALinux2-when-using-ParallelCluster-2.11.0-and-custom-AMIs-from-2.6.0-to-2.11.0)
* [(2.10.0-2.11.1) NVIDIA Fabric Manager stops running on Ubuntu 18.04 and Ubuntu 20.04](https://github.com/aws/aws-parallelcluster/wiki/NVIDIA-Fabric-Manager-stops-running-on-Ubuntu-18.04-and-Ubuntu-20.04)
* [(2.11.2 and earlier) Custom AMI creation (pcluster createami) fails when building SGE](https://github.com/aws/aws-parallelcluster/wiki/(2.11.2-and-earlier)-Custom-AMI-creation-(pcluster-createami)-fails-when-building-SGE)
* [(2.11.4) DCV Connection Through Web Browsers Does Not Work](https://github.com/aws/aws-parallelcluster/wiki/DCV-Connection-Through-Web-Browsers-Does-Not-Work)
* [(2.10.0-2.11.4) Tags in number interpreted as integer instead of string possible cause value error in Compute resource launch template](https://github.com/aws/aws-parallelcluster/wiki/(2.10.0---2.11.4)-Tags-in-number-interpreted-as-integer-instead-of-string-possible-cause-value-error-in-Compute-resource-launch-template)
* [(2.11.7 and earlier) Cluster creation fails with awsbatch scheduler](https://github.com/aws/aws-parallelcluster/wiki/(2.11.7-and-earlier)-Cluster-creation-fails-with-awsbatch-scheduler)


### Deprecated 🦴
* [How to disable Intel Hyper Threading Technology](https://github.com/aws/aws-parallelcluster/wiki/How-to-disable-Intel-Hyper-Threading-Technology)
* [Intel HPC platform specification issue](https://github.com/aws/aws-parallelcluster/wiki/Intel-HPC-platform-specification-issue)
