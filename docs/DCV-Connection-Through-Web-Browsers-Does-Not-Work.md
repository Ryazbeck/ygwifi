## The issue

### Overview

With ParallelCluster 2.11.4, when running `pcluster dcv connect <cluster-name>`, the web page opened will be blank.

### Details

ParallelCluster 2.11.4 upgraded NICE DCV software to version 2021.2-11190. Starting from [DCV release 2021.2-11048](https://docs.aws.amazon.com/dcv/latest/adminguide/doc-history-release-notes.html#dcv-2021-2-11048), the NICE DCV web viewer is distributed as a stand-alone package on Linux, and is no longer included in the DCV server bundle. However, the ParallelCluster 2.11.4 cookbook only installs DCV server and xdcv. As a result, the web viewer is not installed. This bug will be addressed shortly in version 2.11.5.

## Workaround 

Until version 2.11.5 of ParallelCluster is available, or if you are unable to upgrade your cluster to versions >= 2.11.5, there are alternative methods of resolving this issue. Two possible workarounds to deal with the missing NICE DCV web viewer package in the ParallelCluster deployment are detailed here.

### Method 1: Install NICE DCV web viewer package

To enable the DCV session connection through a web browser on the client machine, you need to first login into the head node of the cluster and install the DCV web viewer package using one of the commands below. The command varies according to the operating system and architecture of the head node:
```
# alinux2 and centos + x86
sudo yum install /opt/parallelcluster/sources/nice-dcv-2021.2-11190-el7-x86_64/nice-dcv-web-viewer-2021.2.11190-1.el7.x86_64.rpm

# alinux2 and centos + ARM
sudo yum install /opt/parallelcluster/sources/nice-dcv-2021.2-11190-el7-aarch64/nice-dcv-web-viewer-2021.2.11190-1.el7.aarch64.rpm

# ubuntu1804 + x86
sudo apt-get install /opt/parallelcluster/sources/nice-dcv-2021.2-11190-ubuntu1804-x86_64/nice-dcv-web-viewer_2021.2.11190-1_amd64.ubuntu1804.deb

# ubuntu1804 + ARM
sudo apt-get install /opt/parallelcluster/sources/nice-dcv-2021.2-11190-ubuntu1804-aarch64/nice-dcv-web-viewer_2021.2.11190-1_arm64.ubuntu1804.deb

# ubuntu2004 + x86
sudo apt-get install /opt/parallelcluster/sources/nice-dcv-2021.2-11190-ubuntu2004-x86_64/nice-dcv-web-viewer_2021.2.11190-1_amd64.ubuntu2004.deb

# ubuntu2004 + ARM
sudo apt-get install /opt/parallelcluster/sources/nice-dcv-2021.2-11190-ubuntu2004-aarch64/nice-dcv-web-viewer_2021.2.11190-1_arm64.ubuntu2004.deb
```



### Method 2: Connect using the native DCV client

With this solution you can connect to the DCV session without the need to install anything else on the head node. Below is the instructions:

1. Follow the [DCV guide](https://docs.aws.amazon.com/dcv/latest/userguide/client.html) to install DCV client to your Linux, Mac, or Windows client machine.
2. Run `pcluster dcv connect --show-url <cluster-name>` to retrieve the DCV session URL. Copy and paste the URL in the DCV client to connect to the remote DCV session. 
    The returned URL is only valid for 30 seconds, so make sure to use it quickly. In the case it expires, you’ll need to re-execute the previous pcluster command to get a new URL.

