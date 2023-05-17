## The issue

Starting on 2021-05-29, cluster creation fails in China regions when using AWS Batch as the scheduler due to the use of non-ICP-compliant URLs in the public Amazon Linux 2 Docker image used as the base image when building the Docker images used for the cluster's Batch ComputeEnvironment.


## Affected ParallelCluster versions

All currently released versions are affected by this issue.


## Error details

Cluster creation will fail with an error message like the following:

```
> pcluster create -nr china-batch-cluster-creation-issue
Beginning cluster creation for cluster: china-workaround-test-bad
Creating stack named: parallelcluster-china-workaround-test-bad
Status: parallelcluster-china-workaround-test-bad - CREATE_FAILED
Cluster creation failed.  Failed events:
  - AWS::CloudFormation::Stack parallelcluster-china-workaround-test-bad The following resource(s) failed to create: [AWSBatchStack].
  - AWS::CloudFormation::Stack AWSBatchStack Embedded stack arn:aws-cn:cloudformation:cn-north-1:166444331239:stack/parallelcluster-chi
na-workaround-test-bad-AWSBatchStack-PLPTNMEG5Y9Z/ecdcf8d0-c31b-11eb-9415-02576d546c96 was not successfully created: The following reso
urce(s) failed to create: [DockerBuildWaitCondition, JobQueue].
    - AWS::CloudFormation::Stack parallelcluster-china-workaround-test-bad-AWSBatchStack-PLPTNMEG5Y9Z The following resource(s) failed
to create: [DockerBuildWaitCondition, JobQueue].
    - AWS::Batch::JobQueue JobQueue Resource creation cancelled
    - AWS::CloudFormation::WaitCondition DockerBuildWaitCondition WaitCondition received failed message: 'Build Failed. See the CodeBui
ld logs for further details.' for uniqueId: arn:aws-cn:codebuild:cn-north-1:166444331239:build/parallelcluster-china-workaround-test-ba
d-build-docker-images-project:11be76f4-018a-4f7d-85d3-ed3711ce220f
```

The logs of the failed CodeBuild run will contain an error message like the following:

```
Step 3/12 : RUN yum update -y     && yum -y install     aws-cli     binutils     gcc     iproute     nfs-utils     openssh-server     openssh-clients     openmpi     openmpi-devel     python2     python2-setuptools     python2-pip     which      hostname     && yum clean all     && rm -rf /var/cache/yum     && mkdir /var/run/sshd     && mkdir -p /parallelcluster/bin     && export DEBIAN_FRONTEND=noninteractive
 ---> Running in a8f6a0e0797b
Loaded plugins: ovl, priorities


 One of the configured repositories failed (Unknown),
 and yum doesn't have enough cached data to continue. At this point the only
 safe thing yum can do is fail. There are a few ways to work "fix" this:

     1. Contact the upstream for the repository and get them to fix the problem.

     2. Reconfigure the baseurl/etc. for the repository, to point to a working
        upstream. This is most often useful if you are using a newer
        distribution release than is supported by the repository (and the
        packages for the previous distribution release still work).

     3. Run the command with the repository temporarily disabled
            yum --disablerepo=<repoid> ...

     4. Disable the repository permanently, so yum won't use it by default. Yum
        will then just ignore the repository until you permanently enable it
        again or use --enablerepo for temporary usage:

            yum-config-manager --disable <repoid>
        or
            subscription-manager repos --disable=<repoid>

     5. Configure the failing repository to be skipped, if it is unavailable.
        Note that yum will try to contact the repo. when it runs most commands,
        so will have to try and fail each time (and thus. yum will be be much
        slower). If it is a very temporary problem though, this is often a nice
        compromise:

            yum-config-manager --save --setopt=<repoid>.skip_if_unavailable=true

Cannot find a valid baseurl for repo: amzn2-core/2/x86_64
Could not retrieve mirrorlist http://amazonlinux.default.amazonaws.com/2/core/latest/x86_64/mirror.list error was
14: curl#56 - "Recv failure: Connection reset by peer"
The command '/bin/sh -c yum update -y     && yum -y install     aws-cli     binutils     gcc     iproute     nfs-utils     openssh-server     openssh-clients     openmpi     openmpi-devel     python2     python2-setuptools     python2-pip     which      hostname     && yum clean all     && rm -rf /var/cache/yum     && mkdir /var/run/sshd     && mkdir -p /parallelcluster/bin     && export DEBIAN_FRONTEND=noninteractive' returned a non-zero code: 1
```

## The workaround

A longer term fix for this issue will be provided in the next release of ParallelCluster. As a temporary workaround you can manually modify the Dockerfile used to build container images for Batch clusters in the `pcluster` CLI. The following shows how to do this for v2.10.4.

### Clone the CLI repo and check out the tag matching the desired version

```
tilne@38f9d3528167:china-batch-workaround-test> git clone https://github.com/aws/aws-parallelcluster.git
Cloning into 'aws-parallelcluster'...
remote: Enumerating objects: 29902, done.
remote: Counting objects: 100% (975/975), done.
remote: Compressing objects: 100% (499/499), done.
remote: Total 29902 (delta 520), reused 704 (delta 399), pack-reused 28927
Receiving objects: 100% (29902/29902), 12.17 MiB | 3.06 MiB/s, done.
Resolving deltas: 100% (20878/20878), done.
tilne@38f9d3528167:china-batch-workaround-test> cd aws-parallelcluster/
tilne@38f9d3528167:aws-parallelcluster> git checkout v2.10.4
Note: checking out 'v2.10.4'.

You are in 'detached HEAD' state. You can look around, make experimental
changes and commit them, and you can discard any commits you make in this
state without impacting any branches by performing another checkout.

If you want to create a new branch to retain commits you create, you may
do so (now or later) by using -b with the checkout command again. Example:

  git checkout -b <new-branch-name>

HEAD is now at 02ae270b Update AMI List Build Number aws-parallelcluster-cookbook Git hash: 2b581c3b1d427b734fde70a150ede8e38d309cea aw
s-parallelcluster-node Git hash: 35a8b6acedfef47bab86aa101d9bd52065917816
```

### Modify the Dockerfile and the script used to build Docker images for a Batch cluster's ComputeEnvironment

```
tilne@38f9d3528167:aws-parallelcluster> cd cli/src/pcluster/resources/batch/
tilne@38f9d3528167:batch> git status
HEAD detached at v2.10.4
nothing to commit, working tree clean
tilne@38f9d3528167:batch> vim docker/alinux2/Dockerfile
tilne@38f9d3528167:batch> vim docker/build-docker-images.sh
tilne@38f9d3528167:batch> git status
HEAD detached at v2.10.4
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git checkout -- <file>..." to discard changes in working directory)

        modified:   docker/alinux2/Dockerfile
        modified:   docker/build-docker-images.sh

no changes added to commit (use "git add" and/or "git commit -a")
tilne@38f9d3528167:batch> git diff
diff --git a/cli/src/pcluster/resources/batch/docker/alinux2/Dockerfile b/cli/src/pcluster/resources/batch/docker/alinux2/Dockerfile
index 737e94dc..b777c9c5 100644
--- a/cli/src/pcluster/resources/batch/docker/alinux2/Dockerfile
+++ b/cli/src/pcluster/resources/batch/docker/alinux2/Dockerfile
@@ -2,6 +2,12 @@ FROM public.ecr.aws/amazonlinux/amazonlinux:2

 ENV USER root

+ARG AWS_REGION
+RUN echo "amazonlinux-2-repos-${AWS_REGION}.s3" > /etc/yum/vars/amazonlinux
+RUN echo "amazonaws.com.cn" > /etc/yum/vars/awsdomain
+RUN echo "https" > /etc/yum/vars/awsproto
+RUN echo "${AWS_REGION}" > /etc/yum/vars/awsregion
+
 RUN yum update -y \
     && yum -y install \
     aws-cli \
diff --git a/cli/src/pcluster/resources/batch/docker/build-docker-images.sh b/cli/src/pcluster/resources/batch/docker/build-docker-imag
es.sh
index bedd4dd9..9078e8a4 100755
--- a/cli/src/pcluster/resources/batch/docker/build-docker-images.sh
+++ b/cli/src/pcluster/resources/batch/docker/build-docker-images.sh
@@ -8,7 +8,7 @@ build_docker_image() {
         echo "Dockerfile not found for image ${image}. Exiting..."
         exit 1
     fi
-    docker build -f "${image}/Dockerfile" -t "${IMAGE_REPO_NAME}:${image}" .
+    docker build --build-arg AWS_REGION="${AWS_REGION}" -f "${image}/Dockerfile" -t "${IMAGE_REPO_NAME}:${image}" .
 }

 if [ -z "${IMAGE}" ]; then
```

### Uninstall the existing `pcluster` CLI

```
tilne@38f9d3528167:batch> pip uninstall -y aws-parallelcluster
Found existing installation: aws-parallelcluster 2.10.4
Uninstalling aws-parallelcluster-2.10.4:
  Successfully uninstalled aws-parallelcluster-2.10.4
```

### Install the modified version of the CLI

```
tilne@38f9d3528167:batch> cd ../../../../
tilne@38f9d3528167:cli> python -m pip install -e $(pwd)
Obtaining file:///tmp/china-batch-workaround-test/aws-parallelcluster/cli
Requirement already satisfied: setuptools in /Users/tilne/.pyenv/versions/3.8.1/envs/china-batch-dockerfile-issue-v3/lib/python3.8/site
-packages (from aws-parallelcluster==2.10.4) (41.2.0)
Requirement already satisfied: boto3>=1.16.14 in /Users/tilne/.pyenv/versions/3.8.1/envs/china-batch-dockerfile-issue-v3/lib/python3.8/
site-packages (from aws-parallelcluster==2.10.4) (1.17.85)
Requirement already satisfied: future<=0.18.2,>=0.16.0 in /Users/tilne/.pyenv/versions/3.8.1/envs/china-batch-dockerfile-issue-v3/lib/p
ython3.8/site-packages (from aws-parallelcluster==2.10.4) (0.18.2)
Requirement already satisfied: tabulate<=0.8.7,>=0.8.2 in /Users/tilne/.pyenv/versions/3.8.1/envs/china-batch-dockerfile-issue-v3/lib/p
ython3.8/site-packages (from aws-parallelcluster==2.10.4) (0.8.7)
Requirement already satisfied: ipaddress>=1.0.22 in /Users/tilne/.pyenv/versions/3.8.1/envs/china-batch-dockerfile-issue-v3/lib/python3
.8/site-packages (from aws-parallelcluster==2.10.4) (1.0.23)
Requirement already satisfied: PyYAML>=5.3.1 in /Users/tilne/.pyenv/versions/3.8.1/envs/china-batch-dockerfile-issue-v3/lib/python3.8/s
ite-packages (from aws-parallelcluster==2.10.4) (5.4.1)
Requirement already satisfied: jinja2>=2.11.0 in /Users/tilne/.pyenv/versions/3.8.1/envs/china-batch-dockerfile-issue-v3/lib/python3.8/
site-packages (from aws-parallelcluster==2.10.4) (3.0.1)
Requirement already satisfied: jmespath<1.0.0,>=0.7.1 in /Users/tilne/.pyenv/versions/3.8.1/envs/china-batch-dockerfile-issue-v3/lib/py
thon3.8/site-packages (from boto3>=1.16.14->aws-parallelcluster==2.10.4) (0.10.0)
Requirement already satisfied: s3transfer<0.5.0,>=0.4.0 in /Users/tilne/.pyenv/versions/3.8.1/envs/china-batch-dockerfile-issue-v3/lib/
python3.8/site-packages (from boto3>=1.16.14->aws-parallelcluster==2.10.4) (0.4.2)
Requirement already satisfied: botocore<1.21.0,>=1.20.85 in /Users/tilne/.pyenv/versions/3.8.1/envs/china-batch-dockerfile-issue-v3/lib
/python3.8/site-packages (from boto3>=1.16.14->aws-parallelcluster==2.10.4) (1.20.85)
Requirement already satisfied: python-dateutil<3.0.0,>=2.1 in /Users/tilne/.pyenv/versions/3.8.1/envs/china-batch-dockerfile-issue-v3/l
ib/python3.8/site-packages (from botocore<1.21.0,>=1.20.85->boto3>=1.16.14->aws-parallelcluster==2.10.4) (2.8.1)
Requirement already satisfied: urllib3<1.27,>=1.25.4 in /Users/tilne/.pyenv/versions/3.8.1/envs/china-batch-dockerfile-issue-v3/lib/pyt
hon3.8/site-packages (from botocore<1.21.0,>=1.20.85->boto3>=1.16.14->aws-parallelcluster==2.10.4) (1.26.5)
Requirement already satisfied: MarkupSafe>=2.0 in /Users/tilne/.pyenv/versions/3.8.1/envs/china-batch-dockerfile-issue-v3/lib/python3.8
/site-packages (from jinja2>=2.11.0->aws-parallelcluster==2.10.4) (2.0.1)
Requirement already satisfied: six>=1.5 in /Users/tilne/.pyenv/versions/3.8.1/envs/china-batch-dockerfile-issue-v3/lib/python3.8/site-p
ackages (from python-dateutil<3.0.0,>=2.1->botocore<1.21.0,>=1.20.85->boto3>=1.16.14->aws-parallelcluster==2.10.4) (1.16.0)
Installing collected packages: aws-parallelcluster
  Running setup.py develop for aws-parallelcluster
Successfully installed aws-parallelcluster-2.10.4
```

The newly installed version of the `pcluster` CLI can now be used to create clusters in China regions using AWS Batch as the scheduler.