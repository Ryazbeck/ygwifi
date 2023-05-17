A small number of users have been affected by an issue in submitting multi-node parallel jobs with AWS Batch as the job scheduler. This issue is fixable in one of two ways. 

The default recommended course of action is to upgrade to AWS ParallelCluster 2.5.0 or later by running the standard command for updating the software: `pip3 install aws-parallelcluster --upgrade --user`. In the event that a software upgrade is not feasible, then this issue can also be resolved through self-patching by applying the script below that has been authored by the AWS ParallelCluster team.

The recommended course of action if you are affected by this issue is to copy the script below and paste it into a new .sh file of your choosing on your local machine. The script can then be run for each combination of cluster and region that are affected by this issue as follows:
`<filename>.sh -r <affected region> -c <affected cluster name>`

For example, if I copy-pasted the script below and saved my shell script as `batch_patch.sh`, the name of my cluster were `default`, and my cluster was located in `us-east-1`, I would run the patching script by running this command from a command line of my local machine:
`batch_patch.sh -r us-east-1 -c default`

Please note the following requirements to successfully run this batch script:

* The AWS CLI (instructions for downloading the CLI can be found [here](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html))
* The zip command
* The tar command

```
#!/bin/bash
set -e

usage()
{
    echo "usage: script-name.sh -r region -c cluster-name"
}


CLUSTER_NAME=
REGION=

while [ "$1" != "" ]; do
    case $1 in
        -r | --region )         shift
                                REGION=$1
                                ;;
        -c | --cluster-name )   shift
                                CLUSTER_NAME=$1
                                ;;
        -h | --help )           usage
                                exit
                                ;;
        * )                     usage
                                exit 1
    esac
    shift
done

if [ -z "${CLUSTER_NAME}" ] || [ -z "${REGION}" ]; then
    usage
    exit
fi

STACK_NAME="parallelcluster-${CLUSTER_NAME}"
S3_BUCKET=$(aws cloudformation describe-stacks --stack-name "${STACK_NAME}" --query "Stacks[0].Outputs[?OutputKey=='ResourcesS3Bucket'].OutputValue" --output text --region ${REGION})
WD="/tmp/pcluster-awsbatch-fix"

echo "Dowloading patched artifacts"
curl -s -L https://github.com/aws/aws-parallelcluster/tarball/b781987 > /tmp/pcluster-awsbatch-fix.tar.gz
mkdir -p "${WD}" && tar -xf /tmp/pcluster-awsbatch-fix.tar.gz -C "${WD}"
cd "${WD}/aws-aws-parallelcluster-b781987/cli/pcluster/resources/batch/docker/" && zip --quiet -r "${WD}/artifacts.zip" ./*

echo "Uploading patched artifacts to ${S3_BUCKET}"
aws s3 cp "${WD}/artifacts.zip" s3://${S3_BUCKET}/docker/artifacts.zip --region ${REGION}

CODEBUILD_PROJECT="${STACK_NAME}-build-docker-images-project"
BUILD_ID=$(aws codebuild start-build --project-name ${CODEBUILD_PROJECT} --query "build.id" --output text --region ${REGION})

echo "Applying patch to docker image..."
BUILD_STATUS=
while [ "${BUILD_STATUS}" != "SUCCEEDED" ] && [ "${BUILD_STATUS}" != "FAILED" ]; do
    sleep 20
    BUILD_STATUS=$(aws codebuild batch-get-builds --ids ${BUILD_ID} --query "builds[0].buildStatus" --output text --region ${REGION})
    echo "Build status is ${BUILD_STATUS}"
done 

echo "Patch applied successfully!"
```