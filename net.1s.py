#!/usr/bin/env python3
import psutil
import time
import subprocess

COLOR_HIGH = "#cc575d"
COLOR_MEDIUM = "#d19a66"
COLOR_NORMAL = "#ffffff"
SCALE_BYTES = 1024

NET_THRESHOLD_MEDIUM = 1024 * 1024 * 10
NET_THRESHOLD_HIGH = 1024 * 1024 * 50
PING_THRESHOLD_MEDIUM = 20
PING_THRESHOLD_HIGH = 100

# Wireguard VPN prefixes
VPN_PREFIXES = ["wg", "dts"]

# Addresses to ping
PING = ["google.com"]

####


def humanize(bytes):
    suffix = "B"
    if bytes > SCALE_BYTES:
        bytes /= SCALE_BYTES
        suffix = "K"
    if bytes > SCALE_BYTES:
        bytes /= SCALE_BYTES
        suffix = "M"
    if bytes > SCALE_BYTES:
        bytes /= SCALE_BYTES
        suffix = "G"
    return "%4.f%s" % (bytes, suffix)


def get_color(num, medium_threshold, high_threshold):
    if num >= high_threshold:
        return COLOR_HIGH

    if num >= medium_threshold:
        return COLOR_MEDIUM

    return COLOR_NORMAL


def ping(server, count=1, wait_sec=1):
    cmd = "ping -c {} -W {} {}".format(count, wait_sec, server).split(" ")
    try:
        output = subprocess.check_output(cmd).decode().strip()
        lines = output.split("\n")
        timing = lines[-1].split()[3].split("/")
        return {
            "to": server,
            "type": "rtt",
            "min": float(timing[0]),
            "avg": float(timing[1]),
            "max": float(timing[2]),
            "mdev": float(timing[3]),
        }
    except Exception:
        return {"avg": -1, "to": server}


####

count = psutil.net_io_counters()
recv, sent = count.bytes_recv, count.bytes_sent
time.sleep(1)
count = psutil.net_io_counters()
recv, sent = count.bytes_recv - recv, count.bytes_sent - sent

net_if_stats = psutil.net_if_stats()

is_connected_vpn = False
for key in net_if_stats:
    for prefix in VPN_PREFIXES:
        if prefix in key:
            is_connected_vpn = True

PINGS = {}
LAST_AVG_PING = 0
for to_ping in PING:
    PINGS[to_ping] = ping(to_ping)
    LAST_AVG_PING = PINGS[to_ping]["avg"]


print(
    "{down}{up}{ping}{vpn}|font=monospace".format(
        down="👇<span color='%s'>%s</span>"
        % (get_color(recv, NET_THRESHOLD_MEDIUM, NET_THRESHOLD_HIGH), humanize(recv)),
        up="☝<span color='%s'>%s</span>"
        % (get_color(sent, NET_THRESHOLD_MEDIUM, NET_THRESHOLD_HIGH), humanize(sent)),
        vpn=(" 🔒" if is_connected_vpn else ""),
        ping=" 🔗<span color='%s'>%4.dms</span>"
        % (
            get_color(LAST_AVG_PING, PING_THRESHOLD_MEDIUM, PING_THRESHOLD_HIGH),
            LAST_AVG_PING,
        ),
    )
)
print("---")
for key in net_if_stats:
    if net_if_stats[key].isup:
        print(f"Interface {key} is up|font=monospace")

for ping in PINGS:
    print(
        "Ping to %s: <span color='%s'>%4.dms</span>|font=monospace"
        % (
            PINGS[ping]["to"],
            get_color(PINGS[ping]["avg"], PING_THRESHOLD_MEDIUM, PING_THRESHOLD_HIGH),
            PINGS[ping]["avg"],
        )
    )
