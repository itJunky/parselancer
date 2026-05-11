import os

CONFIG = {
    "ssh_proxy": {
        "ssh_host": "your.ssh.host",
        "ssh_port": 22,
        "ssh_user": "youruser",
        "identity_file": os.path.expanduser("~/.ssh/id_rsa"),
        "local_socks_port": 1080,
        "connect_timeout": 10,
        "server_alive_interval": 30,
        "server_alive_count_max": 3,
    },
}
