### The issue

When provisioning AMIs via either the `pcluster createami` command(on pcluster 2.x) or `pcluster build-image` command(on pcluster 3.0.0), the arm_pl_install recipe in the ParallelCluster cookbook will fail with the following error message:
```
FATAL: OpenSSL::SSL::SSLError: remote_file[/opt/parallelcluster/sources/gcc-9.3.0.tar.gz] (aws-parallelcluster::arm_pl_install line 75) had an error: OpenSSL::SSL::SSLError: SSL Error connecting to https://ftp.gnu.org/gnu/gcc/gcc-9.3.0/gcc-9.3.0.tar.gz - SSL_connect returned=1 errno=0 state=error: certificate verify failed (certificate has expired)
```
This error is the result of the [Letsencrypt Root CA X3 expiration](https://community.letsencrypt.org/t/help-thread-for-dst-root-ca-x3-expiration-september-2021/149190) on 30 September 2021. The certificate embedded in CINC version used is outdated. See Github issue on Chef for more details: https://github.com/chef/chef/issues/12126.

### Affected ParallelCluster versions
This issue affects ParallelCluster from `2.10.1` to `3.0.0` when using createami/build-image with ARM architecture base AMI.

### The workaround
1. Create script and name it `add_cinc_certificates.sh` with the following contents. Replace ParallelCluster version you are using in the script.
```
#!/bin/bash

VERSION="<Replace with ParallelCluster version>"
git clone https://github.com/aws/aws-parallelcluster-cookbook.git
cd ./aws-parallelcluster-cookbook
git fetch origin
git checkout v$VERSION

ex ./recipes/arm_pl_install.rb <<eof
/return unless node\['conditions'\]\['arm_pl_supported'\]/ append
# Prevent Chef from using outdated/distrusted CA certificates
# https://github.com/chef/chef/issues/12126
if node['platform'] == 'ubuntu'
  execute 'Updating CA certificates...' do
    command 'apt-get install -y ca-certificates && update-ca-certificates --verbose --fresh'
  end
  link '/opt/cinc/embedded/ssl/certs/cacert.pem' do
    to '/etc/ssl/certs/ca-certificates.crt'
  end
else
  execute 'Updating CA certificates...' do
    command 'yum install -y ca-certificates && update-ca-trust'
  end
  # centos8 ca certificates file contains DST ROOT CA X3
  if node['platform'] == "centos" && node['platform_version'].to_i == 8
    execute 'Remove DST ROOT CA X3' do
      command 'sed -i \'/# DST Root CA X3/,/-----END CERTIFICATE-----/d\' /etc/ssl/certs/ca-bundle.crt && update-ca-trust'
    end
  end
  link '/opt/cinc/embedded/ssl/certs/cacert.pem' do
    to '/etc/ssl/certs/ca-bundle.crt'
  end
end
.
xit
eof
cd ..
tar zcvf "$(pwd)/aws-parallelcluster-cookbook-${VERSION}.tgz" ./aws-parallelcluster-cookbook
```
2. Make script executable
```
chmod +x add_cinc_certificates.sh
```
3. Execute the script with 
```
./add_cinc_certificates.sh
```
4. A tar file with name `aws-parallelcluster-cookbook-$VERSION.tgz` will be generated. Upload the generated cookbook to your S3 bucket.
5. Use the custom cookbook to create custom AMI
For pcluster2,
the cookbook can be used as the value passed to the `-cc` argument of the `pcluster createami` command:
```
pcluster createami -ai $BASE_AMI_ID -os $BASE_AMI_OS \
  -cc your-cookbook-url
```
For pcluster3, 
the cookbook can be added in the image config.
Create an BuildImage config as the following, name it `patchconfig.yaml`
```
Image:
  Name: <replace_with_image_name>
Build:
  InstanceType: c6g.4xlarge
  ParentImage:<replace_with_parant_image_id>
DevSettings:
  Cookbook:
    ChefCookbook: your_cookbook_url
```
Then run the following command to create the image:
```
pcluster build-image --region $Region --image-id $your_image_id \
  --image-configuration patchconfig.yaml
```
