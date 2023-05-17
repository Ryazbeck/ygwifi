# Background

By default, AWS Batch jobs run in a docker image that we've created. That image is based on Amazon Linux 2 and does two things:

1. Mount shared directories
2. Create a hostfile, necessary for mpi jobs

Take a look at the [Dockerfile](https://github.com/aws/aws-parallelcluster/blob/develop/cli/pcluster/resources/batch/docker/alinux/Dockerfile) for specifics.

# Implementation

1. [Create a AWS Batch Cluster](https://docs.aws.amazon.com/parallelcluster/latest/ug/tutorials_03_batch_mpi.html)

2. Go to the [ECR Console](https://console.aws.amazon.com/ecr/repositories) and find an image with a name similar to `paral-docke-t6ayh0ia49nm`

![image](https://user-images.githubusercontent.com/5545980/55993618-6b686700-5c64-11e9-85ee-a1ab267cce3b.png)

3. Grab that URI, it should look like: `112850485306.dkr.ecr.us-east-1.amazonaws.com/paral-docke-t6ajh0ia39nm`

4. Create a Makefile with the following contents:

```make
# Makefile
distro=alinux
uri=[URI from ECR console]

build:
        docker build -f Dockerfile -t pcluster-$(distro) .

tag:
        docker tag pcluster-$(distro) $(uri):$(distro)

push: build tag
        docker push $(uri):$(distro)
```

4. Now, put the `Dockerfile` in the same directory as the above `Makefile`. You can then authenticate with ecr and push:

```
$ $(aws ecr get-login --no-include-email --region [your_region])
$ make push
```

5. On the cluster you can submit a job, which will automatically use the new image from your `Dockerfile`

```
$ awsbsub -n 2 hostname 
```

# Adding to existing Dockerfile

If you instead prefer to add to the existing dockerfile, maybe to add packages your application requires, do the following:

```bash
$ git clone https://github.com/aws/aws-parallelcluster.git
$ cd aws-parallelcluster/cli/pcluster/resources/batch/docker/
```

Create the `Makefile` shown above and amend the `build` step to add `$(distro)/Dockerfile`.

```Makefile
build:
        docker build -f $(distro)/Dockerfile -t pcluster-$(distro) .
```

Then you can edit the `alinux/Dockerfile` and `scripts/entrypoint.sh` files before pushing in the same manner as shown above.