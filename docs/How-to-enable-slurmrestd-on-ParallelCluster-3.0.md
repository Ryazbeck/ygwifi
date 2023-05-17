The version of Slurm compiled and shipped with ParallelCluster 3.0 is not built with `slurmrestd` support. 

In order to use `slurmrestd` as part of ParallelCluster 3.0 you'd have to recompile Slurm after installing `jsonc` and `http-parser` libraries that are required by `slurmrestd`, see [SchedMD documentation](https://slurm.schedmd.com/rest.html). You can either recompile Slurm after you create your cluster or you can do this as part of a custom AMI creation. The instructions to recompile Slurm in a running cluster are the following:

1. Download the Slurm package with the same version of the one shipped with the version of ParallelCluster you are using (check it in [Relase Notes](https://github.com/aws/aws-parallelcluster/releases)). In the following instructions we're using the Slurm 20.11.8 included in ParallelCluster 3.0.0:
```
curl https://download.schedmd.com/slurm/slurm-20.11.8.tar.bz2 -o /tmp/slurm-20.11.8.tar.bz2
tar -xf /tmp/slurm-20.11.8.tar.bz2  -C /tmp/
```
If you want you could reuse the locally cached version under `/etc/chef/local-mode-cache/cache/slurm-slurm-20-11-8-1`

2. Make sure there are no running compute nodes with `pcluster describe-cluster-instances --node-type ComputeNode --cluster-name name`. 
If there are, please stop them with `pcluster update-compute-fleet --status STOP_REQUESTED --cluster-name name` before continuing.

3. Login on the head node with `pcluster ssh --cluster-name name` and stop `slurmctld` daemon:
```
sudo systemctl stop slurmctld
```

4. Install deps and recompile Slurm
```
cd /tmp/slurm-20.11.8/
sudo su -
yum install -y json-c-devel http-parser-devel

source /opt/parallelcluster/pyenv/versions/3.7.10/envs/cookbook_virtualenv/bin/activate
./configure --prefix=/opt/slurm --with-pmix=/opt/pmix --enable-slurmrestd
CORES=$(grep processor /proc/cpuinfo | wc -l)
make -j $CORES
make install
make install-contrib
deactivate
```

5. Start slurmctld
```
sudo systemctl start slurmctld
```

6. Follow [SchedMD documentation](https://slurm.schedmd.com/rest.html) to enable and configure `slurmrestd`. 


To have some examples of usage with AWS ParallelCluster, interested readers can read the [Using the Slurm REST API to integrate with distributed architectures on AWS](https://aws.amazon.com/blogs/hpc/using-the-slurm-rest-api-to-integrate-with-distributed-architectures-on-aws/) blog post.