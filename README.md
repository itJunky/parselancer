# parselancer
Bot for sending alert about new job in your category on any freelance sites

Our Group in Telegram:
https://t.me/getFreeLanceChat

## Running with Docker Compose

Pass the host user's UID/GID so the container can write to mounted files:

```bash
CURRENT_UID=$(id -u) CURRENT_GID=$(id -g) docker compose up
```

To run a single service:

```bash
CURRENT_UID=$(id -u) CURRENT_GID=$(id -g) docker compose run --rm parser
```
