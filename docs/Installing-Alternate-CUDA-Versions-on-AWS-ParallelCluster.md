_Last Updated: 04/06/2023_

CUDA is a parallel computing platform and application programming interface (API) developed by Nvidia for general-purpose computing on GPUs. The default AMIs that AWS ParallelCluster 3.5.1 uses for head nodes and compute instances have CUDA 11.7.1 installed, but there are some cases why you might want to install a different version.

* Compatibility with different software: Certain software may require a specific version of CUDA to be installed to run properly. For example, you may need to install an older version of CUDA to use an older version of a machine learning framework or a simulation application.
* Development and testing: You may need to test software with different versions of CUDA to ensure that it works properly across different hardware and software configurations.
* Performance optimization: Different versions of CUDA may offer different levels of performance optimization for different GPUs. You may want to install a specific version of CUDA that yields better performance for your deep learning or scientific computing  applications.

There are two main paths to install and upgrade CUDA. You can use your system’s package manager, such as apt or yum, or you can use downloadable run files provided by NVIDIA. It is important to pick one method and stick with it, otherwise your system can become unusable due to software conflicts. In the case of the AWS ParallelCluster AMI, that choice is already determined because the AWS HPC engineering team uses NVIDIA run files to install the NVIDIA driver, NVIDIA fabric manager, and the CUDA framework on the AWS ParallelCluster AMIs. Here, we will illustrate how to install alternative versions of CUDA using NVIDIA run files. 

In this document, we will create a custom AMI with **CUDA 11.6** installed alongside the existing **11.7** version. This is an overview of the steps we will take:

1. Launch and log into an Amazon EC2 instance
2. Find out the installed driver version
3. Check compatibility with the installed driver
4. Download the run script from NVIDIA
5. Run the installer
6. [Optional] Test your CUDA environment
7. Create your custom AMI

You will then be able to use the new AMI with ParallelCluster.

### Launch and log into an Amazon EC2 instance

Launch an EC2  instance with at least one NVIDIA GPU using your choice of official ParallelCluster AMIs. The process is described in detail in the [AWS ParallelCluster documentation](https://docs.aws.amazon.com/parallelcluster/latest/ug/building-custom-ami-v3.html#modify-an-aws-parallelcluster-ami-v3). Briefly, 

* Use the `pcluster list-official-images` command to find the AMI ID for your preferred operating system and architecture.
* Navigate to the [Amazon EC2 Console](https://console.aws.amazon.com/ec2/), choose **Images:AMIs**, and search for your AMI ID.
* Choose **Launch instance from AMI.**
* Select an i[nstance type](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/accelerated-computing-instances.html#gpu-instances) with an NVIDIA GPU (such as a `g4dn.2xlarge`).
* Select an SSH key for accessing the instance.
* Launch the instance then log into it via SSH once it is ready.

### Find out the installed NVIDIA driver version

The NVIDIA driver is software that enables communication between a computer's operating system and its NVIDIA graphics processing unit (GPU). CUDA is a parallel computing platform that leverages the power of the NVIDIA GPU to accelerate complex computing tasks. The NVIDIA driver is a prerequisite for CUDA to function. 

Find out your NVIDA driver version with the NVIDIA [System Management Interface](https://developer.nvidia.com/nvidia-system-management-interface) by running the `nvidia-smi` command.

```
$ ec2-user@ip-172-31-12-191:~# nvidia-smi
Wed Apr 5 15:20:35 2023
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 470.141.03 Driver Version: 470.141.03 CUDA Version: 11.4 |
|-------------------------------+----------------------+----------------------+
```

The value for `Driver Version` shows us that NVIDIA driver version **470.141.03** is installed and active. The value for `CUDA Version` tells us this driver shipped with CUDA 11.4. But, [NVIDIA minor version compatibility](https://docs.nvidia.com/deploy/cuda-compatibility/index.html#minor-version-compatibility) means we can run other versions of CUDA with this driver as well. 

### Check compatibility with the installed driver

The CUDA Toolkit release notes are the canonical source of information about driver/CUDA compatibility. Navigate to the release notes page and consult the table “[*CUDA Toolkit and Minimum Required Driver Version for CUDA Minor Version Compatibility*](https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html#id3)”.
 
![cuda-compat-matrix](https://user-images.githubusercontent.com/723861/230439068-acb69d83-fbd1-417a-a12b-4f4f59cd0c0a.jpg)

We are installing CUDA 11.6, which requires driver version **450.80.02** or higher. Since the driver installed on our instance is **470.141.03**, it will be compatible with CUDA 11.6. If you find that you need to upgrade your NVIDIA driver to support the version of CUDA you need, that is a more involved process that is out of scope for this article.

### Download the run script from NVIDIA

We need to retrieve the URL from NVIDIA for the runnable installer, then download it. It is tricky to get the URL programmatically, so we will use an interactive form provided by NVIDIA. 

Navigate to the [CUDA Toolkit Archive](https://developer.nvidia.com/cuda-toolkit-archive). Find the version of CUDA you wish to install (CUDA Toolkit 11.6.2 in this case).

![cuda-dl-form](https://user-images.githubusercontent.com/723861/230439295-fd189b5e-ba5b-4fe8-85cd-1a9a83201dcd.jpg)

Follow its [URL](https://developer.nvidia.com/cuda-11-6-1-download-archive) then select the **Linux** operating system. Select **x86_64** if your instance CPU is Intel or AMD-based or **arm64-sbsa** if it is Graviton-based. Choose the **Centos** distribution, version **7**. Even if you are using a different operating system on your AMI, select Centos/7 - it doesn’t matter for the run file. Then, for Installer Type, choose **runfile (local).**

![cuda-url-form](https://user-images.githubusercontent.com/723861/230439478-021a10f0-30c6-4524-92e4-5178d384fb94.jpg)

Now, copy the URL and set it as a shell variable. Then download it using curl. 

```
$ CUDA_URL=`https``:``//developer.download.nvidia.com/compute/cuda/11.6.1/local_installers/cuda_11.6.1_510.47.03_linux.run``
$ curl -fSL -# -O $CUDA_URL
```

This will download a file named `cuda_11.6.1_510.47.03_linux.run` to your local directory.

### Run the installer

Run the installer with administrator privileges. The `--silent` option lets the script run unattended. The `--toolkit` option instructs the script to only install the CUDA toolkit, not the associated NVIDIA driver.  

```
$ sudo sh cuda_11.6.1_510.47.03_linux.run --silent --toolkit
```

When the installer has completed, verify that the new CUDA version has been installed and is the default CUDA for the system. 

```
$ ls -alth /usr/local | grep cuda
lrwxrwxrwx  1 root   root     21 Apr  5 17:20 cuda -> /usr/local/cuda-11.6/
drwxr-xr-x 16 root   root   4.0K Apr  5 17:05 cuda-11.6
drwxr-xr-x 17 root   root   4.0K Feb 15 14:01 cuda-11.7
```

Now, verify that NVIDIA CUDA Compiler Driver (`nvcc`) can load and tell you its version. 

```
$ /usr/local/cuda/bin/nvcc --version
nvcc: NVIDIA (R) Cuda compiler driverCopyright (c) 2005-2022 NVIDIA Corporation
Built on Thu_Feb_10_18:23:41_PST_2022
Cuda compilation tools, release 11.6, V11.6.112Build cuda_11.6.r11.6/compiler.30978841_0
```

### [Optional] Test your CUDA environment

You can put the CUDA installation through its paces with CUDA Samples repository provided by NVIDIA. 

```
# Navigate to a directory with at least 5 GB free space
$ cd /scratch
# Clone the repository
$ git clone https://github.com/NVIDIA/cuda-samples.git
# List tags
$ cd cuda-samples
$ git tag -l
10.1.1
10.1.2
v10.0
v10.0.1
v10.1
v10.2
v11.0
v11.1
v11.2
v11.3
v11.4
v11.4.1
v11.5
v11.6
v11.8
v12.0
v12.1
v9.2
# Check out the closest version to your CUDA installation
$ git checkout v11.6
# Build the samples repository (this will take a while)
$ make
# Run the tests (this will also take a while)
$ make test
# Clean up (this will remove build artifacts)
$ make clean
```

### Create your custom AMI

While still logged into your instance, clean up un-needed files and data.

* Delete the NVIDIA runfile
* Delete the cuda-samples directory if you downloaded it
* Run this instance preparation script `sudo /usr/local/sbin/ami_cleanup.sh`

Then, in your browser, navigate to the [Amazon EC2 Console](https://console.aws.amazon.com/ec2/). Select your running instance and choose **Instance state** and **Stop instance**. When the instance has stopped, choose **Actions** then **Image and templates** then **Create image.**

Give your new image a distinct name and, optionally, write a short description for it. Then, choose **Create image**. After some period of time, the custom AMI will be built and become available to use. 

### Use your custom AMI with AWS ParallelCluster

In the Amazon EC2 Console, navigate to **Images**. Select **Owned by me** to find your custom image. When its status is **Available**, you can use its AMI ID as a custom AMI in AWS ParallelCluster.  You have three options for doing this:

* [Define one custom AMI for the whole cluster](https://docs.aws.amazon.com/parallelcluster/latest/ug/Image-v3.html)
* [Define a custom AMI for the head node only](https://docs.aws.amazon.com/parallelcluster/latest/ug/HeadNode-v3.html#HeadNode-v3-Image)
* [Define a custom AMI for compute instances in a specific queue](https://docs.aws.amazon.com/parallelcluster/latest/ug/Scheduling-v3.html#Scheduling-v3-SlurmQueues)
