#!/bin/bash
set -e

USER_ID=${CURRENT_UID:-$(id -u)}
GROUP_ID=${CURRENT_GID:-$(id -g)}

if [ "$USER_ID" = "0" ]; then
    exec "$@"
fi

groupadd -g "$GROUP_ID" bot 2>/dev/null || true
useradd -u "$USER_ID" -g "$GROUP_ID" -m bot 2>/dev/null || true

exec gosu bot "$@"
