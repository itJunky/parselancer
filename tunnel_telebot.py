#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import atexit
import contextlib
import re
import socket
import subprocess
import time

from telebot import apihelper


def escape_markdown_v2(text):
    return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)


class SSHTunnelTeleBotAPI(object):
    def __init__(self, config):
        self.config = config
        self.ssh_process = None
        atexit.register(self.stop)

    def _wait_for_local_port(self, host, port, timeout=10.0):
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                sock = socket.create_connection((host, port), timeout=1)
                sock.close()
                return True
            except OSError:
                time.sleep(0.2)
        return False

    def _build_proxy_url(self):
        local_port = self.config["ssh_proxy"]["local_socks_port"]
        return "socks5h://127.0.0.1:{0}".format(local_port)

    def start(self):
        if self.ssh_process is not None and self.ssh_process.poll() is None:
            return

        cfg = self.config["ssh_proxy"]
        local_port = cfg["local_socks_port"]

        cmd = [
            "ssh",
            "-N",
            "-D", "127.0.0.1:{0}".format(local_port),
            "-p", str(cfg["ssh_port"]),
            "-o", "ExitOnForwardFailure=yes",
            "-o", "BatchMode=yes",
            "-o", "ConnectTimeout={0}".format(cfg.get("connect_timeout", 10)),
            "-o", "ServerAliveInterval={0}".format(cfg.get("server_alive_interval", 30)),
            "-o", "ServerAliveCountMax={0}".format(cfg.get("server_alive_count_max", 3)),
        ]

        if cfg.get("identity_file"):
            cmd += ["-i", cfg["identity_file"]]

        cmd += ["{0}@{1}".format(cfg["ssh_user"], cfg["ssh_host"])]

        self.ssh_process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        deadline = time.time() + cfg.get("connect_timeout", 10)
        while time.time() < deadline:
            if self.ssh_process.poll() is not None:
                err = self.ssh_process.stderr.read().strip()
                self.ssh_process = None
                raise RuntimeError("SSH tunnel failed to start: {0}".format(err or "unknown error"))

            if self._wait_for_local_port("127.0.0.1", local_port, timeout=0.5):
                return

            time.sleep(0.2)

        self.stop()
        raise RuntimeError("SSH SOCKS tunnel did not start within timeout")

    def stop(self):
        if self.ssh_process is None:
            return

        if self.ssh_process.poll() is None:
            self.ssh_process.terminate()
            try:
                self.ssh_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.ssh_process.kill()
                self.ssh_process.wait()

        self.ssh_process = None

    @contextlib.contextmanager
    def wrap_api(self):
        old_proxy = getattr(apihelper, "proxy", None)
        self.start()
        try:
            apihelper.proxy = {
                "http": self._build_proxy_url(),
                "https": self._build_proxy_url(),
            }
            yield
        finally:
            apihelper.proxy = old_proxy
            self.stop()

    def call(self, func, *args, **kwargs):
        with self.wrap_api():
            return func(*args, **kwargs)

    def format_text(self, subject, message):
        subject_escaped = escape_markdown_v2(subject)
        message_escaped = escape_markdown_v2(message)
        return "*{0}*\n\n{1}".format(subject_escaped, message_escaped)

    def send_message(self, bot, chat_id, subject, message, **kwargs):
        text = self.format_text(subject, message)
        kwargs = dict(kwargs)
        kwargs["parse_mode"] = "MarkdownV2"

        with self.wrap_api():
            result = bot.send_message(chat_id, text, **kwargs)

        return result
