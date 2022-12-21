#!/usr/bin/env python3
import psutil

COLOR_HIGH = "#cc575d"
COLOR_MEDIUM = "#d19a66"
COLOR_NORMAL = "#ffffff"
ICON_RAM = "🐏"
RAM_THRESHOLD_MEDIUM = 50
RAM_THRESHOLD_HIGH = 70

ICON_CPU = "⚙️"
CPU_COLUMNS = 4
CPU_THRESHOLD_MEDIUM = 50
CPU_THRESHOLD_HIGH = 70

SCALE_BYTES = 1024

####

stats = psutil.virtual_memory()
mem = stats.percent
cpus = psutil.cpu_percent(interval=1, percpu=True)


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
    return "%8.2f%s" % (bytes, suffix)


def get_color(num, medium_threshold, high_threshold):
    if num >= high_threshold:
        return COLOR_HIGH

    if num >= medium_threshold:
        return COLOR_MEDIUM

    return COLOR_NORMAL


def get_avg_cpu(cpus):
    total = 0
    for cpu in cpus:
        total += cpu
    return total / len(cpus)


def divide_chunks(l, n):
    chunks = []
    for i in range(0, len(l), n):
        chunks.append(l[i : i + n])
    return chunks


####

avg_cpu = get_avg_cpu(cpus)
print(
    "%s<span color='%s'>%3.d%%</span> %s<span color='%s'>%3.d%%</span>| font=monospace"
    % (
        ICON_RAM,
        get_color(mem, RAM_THRESHOLD_MEDIUM, RAM_THRESHOLD_HIGH),
        mem,
        ICON_CPU,
        get_color(avg_cpu, CPU_THRESHOLD_MEDIUM, CPU_THRESHOLD_HIGH),
        avg_cpu,
    )
)

print("---")

cpu_i = 0
for chunk in divide_chunks(cpus, CPU_COLUMNS):
    group = ""
    for cpu in chunk:
        cpu_i += 1
        group += (
            " <span color='#666666'>%2.d</span><span color='%s'>[%3.d%%]</span>"
            % (cpu_i, get_color(cpu, CPU_THRESHOLD_MEDIUM, CPU_THRESHOLD_HIGH), cpu)
        )
    print("CPU:%s|font=monospace" % (group))


print("---")
print("RAM Total:     %s|font=monospace" % (humanize(stats.total)))
print("RAM Available: %s|font=monospace" % (humanize(stats.available)))
print("RAM Used:      %s|font=monospace" % (humanize(stats.used)))
print("RAM Buffers:   %s|font=monospace" % (humanize(stats.buffers)))
print("RAM Cached:    %s|font=monospace" % (humanize(stats.cached)))
print("RAM Shared:    %s|font=monospace" % (humanize(stats.shared)))
