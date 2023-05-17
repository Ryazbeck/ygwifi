## Description of the problem
Cluster was created with an EBS volume configured with a snapshot as the source for the volume, see [ebs_snapshot_id](https://docs.aws.amazon.com/parallelcluster/latest/ug/ebs-section.html#ebs-snapshot-id).
The snapshot was then deleted after the cluster creation and it's not available anymore.

## The solution
To be able to perform the update, be sure that the following points are verified in the cluster configuration:
* keep the `ebs_snapshot_id` set with the value of the deleted snapshot.
* make sure that `volume_size` is also set. If it was not, please add it and make sure it reflects the size of the existing volume.
* disable the sanity check, setting `sanity_check` to `false`

After that, cluster update can be performed with the `pcluster update` command.