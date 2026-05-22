import os

# Telegram
token = os.environ['TELEGRAM_TOKEN']
token_prod = os.environ['TELEGRAM_TOKEN_PROD']
freelance_chan_id = int(os.environ['FREELANCE_CHAN_ID'])
SUPPORT_CHAT_ID = int(os.environ['SUPPORT_CHAT_ID'])

# Database
DB_PATH = os.environ.get('DB_PATH', '../jobs2.db')

# SSH tunnel
CONFIG = {
    "ssh_proxy": {
        "ssh_host": os.environ['SSH_PROXY_HOST'],
        "ssh_port": int(os.environ['SSH_PROXY_PORT']),
        "ssh_user": os.environ['SSH_PROXY_USER'],
        "identity_file": os.environ['SSH_IDENTITY_FILE'],
        "known_hosts_file": os.environ['SSH_KNOWN_HOSTS'],
        "local_socks_port": int(os.environ.get('SSH_LOCAL_SOCKS_PORT', '2080')),
        "connect_timeout": 10,
        "server_alive_interval": 30,
        "server_alive_count_max": 3,
    },
}

# Logging
QUIET = os.environ.get('QUIET', '0') == '1'
