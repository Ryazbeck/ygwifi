## The issue
ParallelCluster daemon running on the head node, `clustermgtd`, is not restarted after a node reboot and the cluster is not going to scale up to serve submitted jobs. Moreover, the cluster cannot be updated while the `clustermgtd` is down.
The root cause is the `supervisord` service that remains inactive after restarting the head node. The issue only happens on the Ubuntu platform, versions 18.04 and 20.04, while the problem doesn't occur on the other supported operating systems.

## The workaround

To overcome the issue, please follow the steps below:
1. After the head node is restarted, connect to it via ssh
2. Check the `supervisord` service status
```
# supervisord service is inactive
ubuntu@ip-172-31-42-169:~$ systemctl status supervisord.service
● supervisord.service - LSB: Start/stop supervisor
   Loaded: loaded (/etc/init.d/supervisord; generated)
   Active: inactive (dead)
     Docs: man:systemd-sysv-generator(8)
```
3. Start the `supervisord` service
```
sudo service supervisor start
```
4. Check the supervisord service status again
```
ubuntu@ip-172-31-42-169:~$ systemctl status supervisord.service
● supervisord.service - LSB: Start/stop supervisor
   Loaded: loaded (/etc/init.d/supervisord; generated)
   Active: active (running) since Fri 2021-09-17 19:56:36 UTC; 13s ago
     Docs: man:systemd-sysv-generator(8)
  Process: 1755 ExecStart=/etc/init.d/supervisord start (code=exited, status=0/S
    Tasks: 4 (limit: 4915)
   CGroup: /system.slice/supervisord.service
           ├─1778 /opt/parallelcluster/pyenv/versions/3.7.10/envs/cookbook_virtu
           ├─1786 /opt/parallelcluster/pyenv/versions/3.7.10/envs/node_virtualen
           └─1796 /opt/parallelcluster/pyenv/versions/3.7.10/envs/cookbook_virtu

```
5. (optional) Submit a job by launching a compute node to verify that job submission works.