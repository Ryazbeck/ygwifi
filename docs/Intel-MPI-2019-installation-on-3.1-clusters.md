As part of [ParallelCluster 3.1.1 release](https://github.com/aws/aws-parallelcluster/releases), Intel MPI has been upgraded from 2019U8 to 2021U4.

To use Intel MPI 2019 in a cluster created with ParallelCluster >= 3.1.1, it is required to install it through [Spack](https://github.com/spack/spack/blob/develop/var/spack/repos/builtin/packages/intel-mpi/package.py) or through a manual installation in a shared folder of the Head Node.

The following script is an example of manual installation of Intel MPI 2019U8, this must be executed in the Head Node of the cluster and it will install the library in a folder shared between Head Node and compute nodes. The shared folder can be a subfolder of `/opt/intel`, the `home` of the user or a folder from a shared storage (EBS, EFS, FSx).

```
#!/bin/bash

# Please modify SHARED_FOLDER value according to your cluster setup
SHARED_FOLDER="/shared/intelmpi"

intelmpi_version="2019.8.254"
intelmpi_installer="l_mpi_${intelmpi_version}.tgz"
intelmpi_installer_url="https://registrationcenter-download.intel.com/akdlm/irc_nas/tec/16814/${intelmpi_installer}"

wget ${intelmpi_installer_url}
tar -xf ${intelmpi_installer}
cd l_mpi_${intelmpi_version}/
./install.sh -s silent.cfg --accept_eula --install_dir ${SHARED_FOLDER}
cd ..
rm -rf l_mpi_${intelmpi_version}*
```
You can verify the new installation by loading the new module, called `mpi`.
```
# Load new modulefile
$ module use "/shared/intelmpi/impi/2019.8.254/intel64/modulefiles/"
$ module avail
------------- /shared/intelmpi/impi/2019.8.254/intel64/modulefiles/ -------------
mpi

# Load intelmpi 2019 module before using it
$ module load mpi
```

The installation is complete.
The new module can now be used and loaded in the job submission script:
```
#!/bin/bash

module use "/shared/intelmpi/impi/2019.8.254/intel64/modulefiles/"
module load mpi

mpirun ...
```
Note: to download and install updated versions of Intel MPI 2019, please refer to Spack or official Intel MPI website.
