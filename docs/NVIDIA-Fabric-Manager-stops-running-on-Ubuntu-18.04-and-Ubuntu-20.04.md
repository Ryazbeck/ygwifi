## The issue

On clusters created with Ubuntu 18.04 and Ubuntu 20.04 official AMIs, nvidia-fabricmanager will be
automatically updated to an incompatible version and stop working when nodes are launched.

The impact is limited to EC2 instances and applications that make use of NVIDIA Fabric Manager.
At the time of writing only **p4d** instances are affected.

Affected ParallelCluster versions: >= 2.10.0, <= 2.11.1

## The root-cause

Issue started on Jul 21 2021 when Ubuntu published the nvidia-fabricmanager package to its official repo: http://archive.ubuntu.com/ubuntu/pool/multiverse/f/fabric-manager-460/.
Since then, unattended-upgrades, that are enabled by default on ParallelCluster Ubuntu AMIs, are causing the Fabric Manager to be upgraded to a version that is incompatible with the installed NVIDIA drivers.

## The workaround

While we work on addressing the issue and publish a patched version of the product, here is how you can patch clusters created with affected versions.

### Option 1: patch cluster with a pre-install script (requires cluster nodes to have internet access)

1. Create a bash script, e.g. `fix-fabricmanager.sh`, with the following content (or add the code to your existing pre installation script)

```bash
#!/bin/bash

set -ex

nvswitches=$(lspci -d 10de:1af1 | wc -l)

if [ "${nvswitches}" -gt "1" ]; then
    # From https://docs.nvidia.com/datacenter/tesla/tesla-installation-notes/index.html#ubuntu-lts
    distribution=$(. /etc/os-release;echo ${ID}${VERSION_ID} | sed -e 's/\.//g')
    echo "deb http://developer.download.nvidia.com/compute/cuda/repos/${distribution}/x86_64 /" | sudo tee /etc/apt/sources.list.d/cuda.list
    sudo apt-get update --allow-releaseinfo-change

    driver_version=$(nvidia-smi | grep -oP "(?<=Driver Version: )[0-9.]+")
    driver_major=$(echo ${driver_version} | cut -d. -f1)

    sudo apt-get install -y --allow-downgrades nvidia-fabricmanager-${driver_major}=${driver_version}*
    sudo apt-mark hold nvidia-fabricmanager-${driver_major}
    sudo systemctl enable nvidia-fabricmanager.service
    sudo systemctl start nvidia-fabricmanager.service
fi
```

2. Upload the script to an S3 bucket with correct permissions, see: https://docs.aws.amazon.com/parallelcluster/latest/ug/pre_post_install.html
E.g.:  `aws s3 cp fix-fabricmanager.sh s3://yourbucket/`

3. Add the following setting to your cluster configuration
```bash
[cluster yourcluster]
pre_install = s3://yourbucket/fix-fabricmanager.sh
...
```
4. Either create a new cluster or follow the next steps to update an existing cluster 

Update an existing cluster with the pre installation script configured in the previous steps.

1. Stop the cluster with `pcluster stop` command
2. Update the cluster with `pcluster update` command
3. Restart the cluster with `pcluster start` command

### Option 2: create a custom Ubuntu AMI with unattended-upgrades disabled

This option applies only to new clusters.

1. Follow the official documentation to [modify an existing ParallelCluster AMI](https://docs.aws.amazon.com/parallelcluster/latest/ug/tutorials_02_ami_customization.html#modify-an-aws-parallelcluster-ami)
2. As part of the AMI customization step, connect to the instance and run the following commands: 
```
sudo sed -i "s/Update-Package-Lists \"1\"/Update-Package-Lists \"0\"/g" /etc/apt/apt.conf.d/20auto-upgrades
sudo sed -i "s/Unattended-Upgrade \"1\"/Unattended-Upgrade \"0\"/g" /etc/apt/apt.conf.d/20auto-upgrades
```
3. Complete the steps to create a custom AMI
4. Create a cluster using the generated AMI with the [custom_ami](https://docs.aws.amazon.com/parallelcluster/latest/ug/cluster-definition.html#custom-ami-section) parameter.