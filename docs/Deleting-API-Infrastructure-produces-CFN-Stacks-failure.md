## The issue

ParallelCluster builds container images using ImageBuilder that are used as a part of the deployment of the Pcluster API. When deleting the deployed API Infrastructure, CloudFormation responds with the the following error when trying to delete the ECR repo created as part of the stack:
```
Resource handler returned message: "The repository with name 'aws-parallelcluster-*-*-*-*-*' in registry with id '1234567890' cannot be deleted because it still contains images (Service: Ecr, Status Code: 400, Request ID: *-*-*-*-*, Extended Request ID: null)" (RequestToken: *-*-*-*-*, HandlerErrorCode: GeneralServiceException)
```
This bug affects versions 3.0.0 when deleting the deployed ParallelCluster API infrastructure stack. 

## The root-cause
When deploying the REST API ([How to Deploy ParallelCluster API](https://docs.aws.amazon.com/parallelcluster/latest/ug/api-reference-v3.html)), ParallelCluster builds a container image. When the [EcrImageRecipe](https://github.com/aws/aws-parallelcluster/blob/v3.0.0/api/infrastructure/parallelcluster-api.yaml#L979-L996) is used to build an ECR image to be used by the API, the resulting image is expected to have a single image tag of `3.0.0-1` . After a recent update from ImageBuilder, the resulting image instead has two tags -- `3.0.0-1` and one of the form `importpublicecrimage-3-0-0-*-3.0.0-*` . This is a problem because the ECR API that is used to delete images only deletes the tag, but not the image since there’s still an additional tag left.
## The workaround

While we work on addressing the issue and publish a patched version of the product, here is how you can patch clusters created with affected versions.

### Manually delete images remaining in the ECR repo created by the API infrastructure stack

Create a bash script, e.g. `print-remaining-images.sh`, with the following content and execute the script(remember to change the Fields `CFN_STACK_REGION` and `CFN_STACK_NAME` in the script). The script will print a description of the images still remaining in the ECR repo created by the API infrastructure stack:
```
#!/bin/bash

set -ex
# Input variables to be manually initialized
CFN_STACK_REGION="<AWS region in which ParallelCluster API CFN stack is>"
CFN_STACK_NAME="<name of ParallelCluster API CFN stack>"
# ##

ECR_IMAGE_URI=$(aws cloudformation describe-stacks \
                    --region "${CFN_STACK_REGION}" \
                    --stack-name "${CFN_STACK_NAME}" \
                    --query 'Stacks[0].Outputs[?OutputKey==`UriOfCopyOfPublicEcrImage`].OutputValue' \
                    --output text)
ECR_REPO_NAME=$(echo "${ECR_IMAGE_URI}" | cut -d '/' -f 2 | cut -d ':' -f 1)
aws ecr describe-images \
    --region "${CFN_STACK_REGION}" \
    --repository-name "${ECR_REPO_NAME}" \
    --query 'imageDetails'
```
The output will look similar to the following:
```
+ CFN_STACK_REGION=sa-east-1
+ CFN_STACK_NAME=integ-tests-api-og7g7ny9kwjng755-r300
++ aws cloudformation describe-stacks --region sa-east-1 --stack-name integ-tests-api-og7g7ny9kwjng755-r300 --query 'Stacks[0].Outputs[?OutputKey==`UriOfCopyOfPublicEcrImage`].OutputValue' --output text
+ ECR_IMAGE_URI=XXXXXXXXXXXX.dkr.ecr.sa-east-1.amazonaws.com/aws-parallelcluster-61182390-25ab-11ec-9c1a-0ac5ba14fdc0:3.0.0-1
++ echo XXXXXXXXXXXX.dkr.ecr.sa-east-1.amazonaws.com/aws-parallelcluster-61182390-25ab-11ec-9c1a-0ac5ba14fdc0:3.0.0-1
++ cut -d / -f 2
++ cut -d : -f 1
+ ECR_REPO_NAME=aws-parallelcluster-61182390-25ab-11ec-9c1a-0ac5ba14fdc0
+ aws ecr describe-images --region sa-east-1 --repository-name aws-parallelcluster-61182390-25ab-11ec-9c1a-0ac5ba14fdc0 --query imageDetails
[
    {
        "registryId": "XXXXXXXXXXXX",
        "repositoryName": "aws-parallelcluster-61182390-25ab-11ec-9c1a-0ac5ba14fdc0",
        "imageDigest": "sha256:f47082350740f1838295975d1bc77994ea086c52ab6edad97f0fa669aa275109",
        "imageTags": [
            "importpublicecrimage-3-0-0-61182390-25ab-11ec-9c1a-0ac5ba14fdc0-3.0.0-1"
        ],
        "imageSizeInBytes": 259082128,
        "imagePushedAt": 1633418457.0,
        "imageManifestMediaType": "application/vnd.docker.distribution.manifest.v2+json",
        "artifactMediaType": "application/vnd.docker.container.image.v1+json"
    }
]
```
Any image containing a tag of the form `importpublicecrimage-3-0-0-*-3.0.0-*` is one that was unintentionally left remaining by the cleanup logic in the API’s CFN stack template. You may remove these images using a command like the following (where there values of the `--repository-name` and `--image-ids` come from the previous command’s output):
```
aws ecr batch-delete-image \
    --repository-name aws-parallelcluster-61182390-25ab-11ec-9c1a-0ac5ba14fdc0 \
    --image-ids imageDigest=sha256:f47082350740f1838295975d1bc77994ea086c52ab6edad97f0fa669aa275109
{
    "imageIds": [
        {
            "imageDigest": "sha256:f47082350740f1838295975d1bc77994ea086c52ab6edad97f0fa669aa275109",
            "imageTag": "importpublicecrimage-3-0-0-61182390-25ab-11ec-9c1a-0ac5ba14fdc0-3.0.0-1"
        }
    ],
    "failures": []
}
```