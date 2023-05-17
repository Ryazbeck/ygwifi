# How to use a native NICE DCV client

[NICE DCV](https://docs.aws.amazon.com/dcv/index.html) is integrated within ParallelCluster to work only with a Web Browser client.
To use a [native client](https://docs.aws.amazon.com/dcv/latest/userguide/client.html) there are some alternatives listed below.

## 1. Connect to the session created by ParallelCluster

* 1.Execute the `pcluster dcv connect clustername` command with the `--show-url` flag and copy the `authToken` value and the `session-id` from the output:
    ```
    $ pcluster dcv connect clustername --key-path key.pem --show-url
    https://head-node-public-ip:8443?authToken=TOKEN-ID#session-id
    ```
* 2a. (Windows client only) 
Open a Command Prompt and execute the following command, within 30 seconds:
    ```
    dcvviewer https://head-node-public-ip:8443#session-id --auth-token=TOKEN-ID
    ```
* 2b. (Mac and Linux client) 
Create a `connection.dcv` file with the following content:
    ```
    [version]
    format=1.0

    [connect]
    host=head-node-public-ip
    port=8443
    sessionid=session-id
    authtoken=TOKEN-ID
    ```
     Open a shell and execute the following command, within 30 seconds:
    ```
    dcvviewer connection.dcv
    ```


## 2. Skip ParallelCluster integration

It is possible to skip ParallelCluster integration and use NICE DCV with a custom authentication.
To change the NICE DCV server's authentication method, you must configure the `authentication` parameter in the `dcv.conf` file and comment the `auth-token-verifier` one.

1. Connect to the head node instance with the `pcluster ssh clustername` command.
1. Navigate to `/etc/dcv/` and open the `dcv.conf` with your preferred text editor.
1. Locate the `authentication` parameter in the `[security]` section, replace the existing value with either `system` or `none`, according to the [official documentation](https://docs.aws.amazon.com/dcv/latest/adminguide/security-authentication.html#set-authentication-linux) and comment the `auth-token-verifier` one:
    ```
    [security] 
    authentication=method
    ...
    #auth-token-verifier="https://localhost:8444"
    ```
1. Save and close the file.
1. Restart the `dcvserver` service. NOTE: all the running sessions will be automatically closed.


From this moment it's possible to use NICE DCV without the involvement of ParallelCluster.
1. Connect to the head node instance with the `pcluster ssh clustername` command.
1. Start a new session: `dcv create-session new-session-id`
1. Open the native client and specify `head-node-public-ip:8443` in the connection dialog.
