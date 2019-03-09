#!/usr/bin/env bash

QUAYENTRY=${QUAYENTRY:=$@}
QUAYENTRY=${QUAYENTRY:=worker}

if ! whoami &> /dev/null; then
  if [ -w /etc/passwd ]; then
    echo "${USER_NAME:-default}:x:$(id -u):0:${USER_NAME:-default} user:${HOME}:/sbin/nologin" >> /etc/passwd
  fi
fi

case "$QUAYENTRY" in
    "shell")
        echo "Entering shell mode"
        exec /bin/bash
        ;;
    "worker")
        echo "Running both interactive and batch scripts"
        supervisord -c supervisord.conf 2>&1
        ;;
    *)
        echo "Running '$QUAYENTRY'"
        exec $QUAYENTRY
        ;;
esac

