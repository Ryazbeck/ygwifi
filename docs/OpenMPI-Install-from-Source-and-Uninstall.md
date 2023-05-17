### Open MPI installation

Download openmpi and install it with EFA support. This is useful if you need `openmpi-devel` and efa support. 
If you just need `openmpi-devel` skip to the uninstall section.

```bash
wget https://download.open-mpi.org/release/open-mpi/v4.0/openmpi-4.0.1.tar.gz
gunzip -c openmpi-4.0.1.tar.gz | tar xf -
cd openmpi-4.0.1
./configure --prefix=/shared --with-libfabric=/opt/amazon/efa --with-sge # Install in the shared dir on the head-node
make all install
# confirm it has sge support
ompi_info | grep gridengine
```

### Remove default openmpi

In AWS ParallelCluster `2.4.0` we started including openmpi 3.1.4 by default. This is installed using the aws efa installer script as detailed [here](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/efa-start.html#efa-start-enable)

You can uninstall it (to install from source or from package repositories) in the following way:

**Ubuntu**
```bash
sudo apt-get remove openmpi
```

**Centos / Amazon Linux**
```
sudo yum remove openmpi
```