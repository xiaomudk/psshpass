# psshpass

<hr />
批量执行shell命令脚本(可以自动登陆服务器)
```
Usage:
Usage:
psshpass [options]... command
        -h               host_file
        -H               [user@]host[:port]
        -u               set default user(default:root)
        -p               set default password
        -P               set default Port(default:22)
        -i               identity_file
        -t               timeout (default:60s),0 mean no timeout
        -c               maximum number of concurrent connections (default:1)
        -x               host,host,...  set node exclusion list on command line,This option may be used in combination with any other of the node selection options
        -d               host file directory, Conflicts with -h and -H options
        -g               groupname      target hosts in psshpass group 'groupname'
        -X               groupname      exclude hosts in psshpass group 'groupname',This option may be used in combination with any other of the node selection options
        -o               output filename
                         --version
                         --help
```


