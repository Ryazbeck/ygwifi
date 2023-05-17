### The issue

On 2021-02-07 version 3.4 of the [cryptography python package](https://github.com/pyca/cryptography/blob/master/CHANGELOG.rst#34---2021-02-07) was released. This package is a transitive dependency of the [aws-parallelcluster-node python package](https://pypi.org/project/aws-parallelcluster-node/), which provides the daemons that manage a cluster's scaling logic. This new version of the `cryptography` package causes the installation of the `aws-parallelcluster-node` package to fail when occuring as part of the `pcluster createami` command or at cluster runtime. This issue does not affect AMIs which already have the aforementioned packages installed.


### Affected ParallelCluster versions

This issue affects all versions of ParallelCluster up to v2.9.1.

### Error details

When provisioning AMIs via either the `pcluster createami` command or at cluster runtime, the `base_install` recipe in the ParallelCluster cookbook will fail with the following error message:

```
        =============================DEBUG ASSISTANCE=============================
        If you are seeing a compilation error please try the following steps to
        successfully install cryptography:
        1) Upgrade to the latest pip and try again. This will fix errors for most
           users. See: https://pip.pypa.io/en/stable/installing/#upgrading-pip
        2) Read https://cryptography.io/en/latest/installation.html for specific
           instructions for your platform.
        3) Check our frequently asked questions for more information:
           https://cryptography.io/en/latest/faq.html
        4) Ensure you have a recent Rust toolchain installed.
        =============================DEBUG ASSISTANCE=============================
    
    error: Can not find Rust compiler
```

This error is the result of the 3.4.0 release of the `cryptography` package dropping support for `manylinux1` wheels and adding a dependency on Rust when a pre-compiled wheel cannot be used. Dropping support for `manylinux1` is significant because the virtual environment into which the `aws-parallelcluster-node` package is installed on the AMIs used by a cluster uses `pip==18.1` which only supports `manylinux1` wheels. The dependency on Rust is significant because when `pip` attempts to compile portions of the dependencies as opposed to using the pre-compiled wheels, it fails because the Rust compiler is not installed.

### The workaround

For v2.9.1 the recommended workaround is to use the archive of a patched cookbook that can be found [here](https://raw.githubusercontent.com/aws/aws-parallelcluster-cookbook/release-2.9/patched-cookbooks/aws-parallelcluster-cookbook-2.9.1.tgz). This cookbook contains the contents of the release-2.9 branch up until [this commit](https://github.com/aws/aws-parallelcluster-cookbook/commit/7133bd7afdc4ac4e5fad635b7bba9754494d5125). It can be used as the value passed to the `-cc` argument of the `pcluster createami` command:

```bash
pcluster createami -ai $BASE_AMI_ID -os $BASE_AMI_OS \
  -cc https://raw.githubusercontent.com/aws/aws-parallelcluster-cookbook/release-2.9/patched-cookbooks/aws-parallelcluster-cookbook-2.9.1.tgz
```
It can also be used as the value of the `custom_chef_cookbook` parameter in the `[cluster]` section of a ParallelCluster configuration file:

```ini
custom_chef_cookbook = https://raw.githubusercontent.com/aws/aws-parallelcluster-cookbook/release-2.9/patched-cookbooks/aws-parallelcluster-cookbook-2.9.1.tgz
```

Note that this also serves as v2.9.1-specific workaround to the Ubuntu 18.04 custom AMI creation issue described [here](https://github.com/aws/aws-parallelcluster/wiki/Issue-with-Ubuntu-18.04-Custom-AMI-creation).

If you'd like to apply these fixes but do not wish to use the patched cookbook you can do so by making the changes from the following commits:
* https://github.com/aws/aws-parallelcluster-cookbook/commit/7133bd7afdc4ac4e5fad635b7bba9754494d5125
* https://github.com/aws/aws-parallelcluster-cookbook/commit/a355c7d2f59ff1d252ab868886bababe5b36a0eb
* https://github.com/aws/aws-parallelcluster-cookbook/commit/e4c0197bd6bbd691f489200584a900b9d2c3d492

Note: If you're using ParallelCluster from 2.6.0 to 2.9.1 you are also affected by the [Custom-AMI-creation-(pcluster-createami)-fails-with-ParallelCluster-versions-from-2.6.0-to-2.10.3](https://github.com/aws/aws-parallelcluster/wiki/Custom-AMI-creation-(pcluster-createami)-fails-with-ParallelCluster-versions-from-2.6.0-to-2.10.3) issue, so you need to merge the two changes in the cookbook code.