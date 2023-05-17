## Introduction

When using a shared cluster resource access to utilize the compute nodes is guarded by a resource scheduler such as SLURM, SGE, PBS Pro et al.
They line up jobs to be run sequentially, allow for prioritization and job placement within the cluster.

SLURM is one of the most popular open-source job schedulers and this document intends to help end-users transition off their current scheduler to SLURM.
Transition to a new scheduler comes down to learn and practice new commands to handle the lifecycle of a job (submit/view/cancel/..), view resources like queues and compute nodes and adjust the way submit scripts are written. In some cases the last step can be made easier by using a compatibility mode to use existing submit scripts.

### Son of Grid Engine
Son of Grid Engine (SGE) is the open source community version that previously continued development of Sun Grid Engine (also referred to as SGE). It's this version (Son of Grid Engine) that has been used inside of ParallelCluster. Moving off SGE to SLURM needs some adjustments in how to interact with the scheduler by using SLURM commands and adjust the submission scripts.

#### Nomenclature

* **queue/partition** SGE uses the term queues, while SLRUM calls them partitions
* **node-count** SGE has no concept of node counts, SLURM has

#### Commands
Firstly, common commands used in SGE have an equivalent in the SLURM environment. The following table reviews the most common once.

| User Command | SGE | SLURM |
|--------------|-----|---------|
| Interactive Login | `qlogin` | `srun --pty [-p $partition_name] [--time=hh:mm:ss] bash` |
| Job submission | `qsub $script_file` | `sbatch $script_file` |
| Job deletion | `qdel $job_id` | `scancel $job_id` |
| Job status by job | `qstat -u \* -j $job_id` | `squeue $job_id` |
| Job status by user | `qstat -u $user_name` | `squeue -u $user_name` |
| Job hold | `qhold $job_id` | `scontrol hold $job_id` |
| Job release | `qrls $job_id` | `scontrol release $job_id` |
| Queue list | `qconf -sql` | `squeue` |
| List nodes | `qhost	` | `sinfo -N` OR `scontrol show nodes` |
| Cluster status | `qhost -q` | `sinfo` |
| GUI | `qmon` | `sview` |

#### Environment Variables

Environment variables are used within a script to get access to information about the running job.

| Information | SGE | SLURM |
|--------------|-----|---------|
| Job ID | `$JOB_ID` | `$SLURM_JOBID` |
| Submit directory | `$SGE_O_WORKDIR` | `$SLURM_SUBMIT_DIR` |
| Submit host | `$SGE_O_HOST` | `$SLURM_SUBMIT_HOST` |
| Node list | `$PE_HOSTFILE` | `$SLURM_JOB_NODELIST` |
| Job Array Index | `$SGE_TASK_ID` | `$SLURM_ARRAY_TASK_ID` |

#### Job Specification

Submission scripts are able to inform the scheduler about certain parameters of the submission using a directive and options. The following table collects the most common specifications.

| Information | SGE | SLURM |
|--------------|-----|---------|
| Script directive | `#$` | `#SBATCH` |
| queue/partition | `-q $queue` | `-p $partition` |
| count of nodes  | N/A | `-N [min[-max]]` |
| CPU count | `-pe smp <count>` OR `-pe orte <count>` | `-n <count>` |
| Wall clock limit | `-l h_rt=<seconds>` | `-t <min>` OR `-t <days-hh:mm:ss>` |
| stdout file | `-o <file_name>` | `-o <file_name>` |
| stderr file | `-e <file_name>` | `-e <file_name>` |
| combine stdout/stderr | `-j yes` | use `-o` without `-e` |
| copy environment | `-V` | `--export=(ALL/NONE/<variables>)` |
| event notification | `-m abe` | `--mail-type=<events>` |
| send notification email | `-M <address>` | `--mail-user=<address>` |
| job name | `-N <name>` | `--job-name=<name>` |
| Restart job | `-r (yes|no)` | `--[no-]requeue` (NOTE: configurable default) |
| set working directory | `-wd <dir_name>` | `--workdir=<dir_name>` |
| Resource sharing | `-l exclusive` | `--exclusive` OR `—shared` |
| Memory size | `-l mem_free=<memory>(K|M|G)` | `--mem[-per-cpu]=<memory>(K|M|G)` |
| Charge to an account | `-A <account>` | `--account=<account>` |
| Tasks per node | fixed rule in parallel environment (PE) | `--tasks-per-node=<count>` |
| Job dependency | `-hold_jid <job_id>` OR `-hold_jid=<job_name>` | `--depend=[<state>:]<job_id>` |
| Job project | `-P <name>` | `--wckey=<name>` |
| Job host preferences | `-q <queue>@<node>` OR `-q <queue>@@<hostgroup>` | `--nodelist=<nodes>` AND/OR `—exclude=<nodes>` |
| Quality of service | N/A` | `--qos=<name>` |
| Job arrays | `-t $array_spec` | `--array=$array_spec` |
| Generic Resources | `-l $resource=$value` | `--gres=<resource_spec>` |
| Licenses | `-l <license>=<count>` | `--licenses=<license_spec>` |
| Begin Time | `-a <YYMMDDhhmm>` | `--begin=<YYYY-MM-DD[THH:MM[:SS]]>` |

### Submit Scripts

<table><tr>
<th><big><center>SGE</center></big></th>
<th><big><center>SLURM        </center></big></th></tr><tr><td colspan="2">
<b>Single-core application</b>
</td></tr><tr><td><pre>
#!/bin/bash


#$ -N test
#$ -j y
#$ -o test.output
#$ -cwd
#$ -M $USER@stanford.edu
#$ -m bea
##Request 5 hours run time
#$ -l h_rt=5:0:0
#$ -P your_project_id_here


<call your app here>
</pre></td><td><pre>
#!/bin/bash -l
# NOTE the -l flag!

#SBATCH -J test
#SBATCH -o test."%j".out
#SBATCH -e test."%j".err
#Default in slurm
#SBATCH --mail-user $USER@stanford.edu
#SBATCH —mail-type=ALL
#Request 5 hours run time
#SBATCH -t 5:0:0
#SBATCH -p normal

<load modules, call your app here>
</pre></td></tr><tr><td colspan="2">
<b>MPI application w/o Hyperthreading</b>
</td></tr><tr><td>
</td><td><pre>
#!/bin/bash -l

#Standard output and error:
#SBATCH -o ./tjob.out.%j
#SBATCH -e ./tjob.err.%j
#Initial working directory:
#SBATCH -D ./
#Job Name:
#SBATCH -J test_slurm
#Queue (Partition):
#SBATCH --partition=general
#Number of nodes and MPI tasks per node:
#SBATCH --nodes=8
#SBATCH --ntasks-per-node=32
#
#Wall clock limit:
#SBATCH --time=24:00:00
#Run the program:
srun ./myprog > prog.out
</pre></td></tr><tr><td colspan="2">
<b>Hybrid MPI/OpenMP w/o hyperthreading</b>
</td></tr><tr><td>
</td><td><pre>
#!/bin/bash -l
#Standard output and error:
#SBATCH -o ./tjob_hybrid.out.%j
#SBATCH -e ./tjob_hybrid.err.%j
#Initial working directory:
#SBATCH -D ./
#Job Name:
#SBATCH -J test_slurm
#Queue (Partition):
#SBATCH --partition=general
##Number of nodes and MPI tasks per node:
#SBATCH --nodes=8
#SBATCH --ntasks-per-node=4
##for OpenMP:
#SBATCH --cpus-per-task=8
#
##Wall clock limit:
#SBATCH --time=24:00:00
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
##For pinning threads correctly:
export OMP_PLACES=cores
##Run the program:
srun ./myprog > prog.out
</pre></td></tr><tr><td colspan="2">
<b>Batch job using job steps</b>
</td></tr><tr><td>
</td><td><pre>
#!/bin/bash
##Submit a chain of batch jobs with dependencies
#
##Number of jobs to submit:
NR_OF_JOBS=6
##Batch job script:
JOB_SCRIPT=./my_batch_script
echo "Submitting job chain of ${NR_OF_JOBS}"
echo "jobs for batch script ${JOB_SCRIPT}:"
JOBID=$(sbatch ${JOB_SCRIPT} 2>&1 | awk '{print $(NF)}')
echo "  " ${JOBID}
I=1
while [ ${I} -lt ${NR_OF_JOBS} ]; do
JOBID=$(sbatch --dependency=afterany:${JOBID} \
        ${JOB_SCRIPT} 2>&1 | awk '{print $(NF)}')
echo "  " ${JOBID}
let I=${I}+1
done
</pre></td></tr><tr><td colspan="2">
<b>Batch job using job array</b>
</td></tr><tr><td>
</td><td><pre>
#!/bin/bash -l
##specify the indexes of the job array elements
#SBATCH --array=1-20
##Standard output and error:
##Standard output, %A = job ID, %a = job array index
#SBATCH -o job_%A_%a.out
##Standard error, %A = job ID, %a = job array index
#SBATCH -e job_%A_%a.err
##Initial working directory:
#SBATCH -D ./
##Job Name:
#SBATCH -J test_array
##Queue (Partition):
#SBATCH --partition=general
##Number of nodes and MPI tasks per node:
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=40
#
##Wall clock limit:
#SBATCH --time=24:00:00

##Run the program:
srun ./myprog > prog.out
</pre></td></tr><tr><td colspan="2">
<b>MPI Batch job using GPUs</b>
</td></tr><tr><td>
</td><td><pre>
#!/bin/bash -l
##Standard output and error:
#SBATCH -o ./tjob.out.%j
#SBATCH -e ./tjob.err.%j
##Initial working directory:
#SBATCH -D ./
#
#SBATCH -J test_slurm
##Queue:
##If using both GPUs of a node
#SBATCH --partition=gpu
##If using only 1 GPU of a shared node
###SBATCH --partition=gpu:1
##Node feature:
#SBATCH --constraint="gpu"
##Specify number of GPUs to use:
# If using both GPUs of a node
#SBATCH --gres=gpu:2
### If using only 1 GPU of a shared node
###SBATCH --gres=gpu:1

#
##Number of nodes and MPI tasks per node:
#SBATCH --nodes=1
##If using both GPUs of a node
#SBATCH --ntasks-per-node=32
##If using only 1 GPU of a shared node
###SBATCH --ntasks-per-node=16
#
##wall clock limit:
#SBATCH --time=24:00:00

module load cuda
##Run the program:
srun ./my_gpu_prog > prog.out
</pre></td></tr>
</table>

<!--
### Tips & Tricks

#### Requeuehold

To keep track which jobs are actually failed or not inside the script.
```
scontrol requeuehold ${SLURM_JOB_ID}
```
And for an array job.
```
scontrol requeuehold ${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID})
```
-->