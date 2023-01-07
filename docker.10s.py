#!/usr/bin/env python3
import subprocess
import json
from operator import itemgetter

docker = (
    subprocess.check_output(
        ["docker", "ps", "--no-trunc", "--format", "{{json .}}", "-a"]
    )
    .decode()
    .strip()
)
container_running = 0
container_count = 0
container_details = []
for container in docker.splitlines():
    container = json.loads(container)
    container_count += 1
    if container["Status"][:2] == "Up":
        container_running += 1
    container_details.append(container)


if container_count == 0:
    print("No 📦|font=monospace")
else:
    print("{}/{} 📦|font=monospace".format(container_running, container_count))
    print("---")
    sorted = sorted(container_details, key=itemgetter('Names'))
    for container in sorted:
        alive = container["Status"][:2] == "Up"
        line = ""
        line += "%5s:" % container["ID"][:5]
        line += "%40s" % container["Names"][:40]
        line += " %30s" % container["Image"][-30:]
        line += "%30s" % container["Status"][:30]
        line += " 💚" if alive else " 💀"
        line += "|font=monospace"
        if alive:
            line += " bash='%s' terminal=true" % ("docker exec -ti " +container["ID"] + " sh")
        print(line)
