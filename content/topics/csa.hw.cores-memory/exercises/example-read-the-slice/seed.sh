#!/bin/bash
# Builds the lab's three machines under /srv/machines: for each, a small copy
# of the parts of /proc and /sys that lscpu reads, so `lscpu --sysroot DIR`
# reads it the way it reads a real machine. They are constructed, not
# captured: written from a shape (sockets, cores per socket, threads per
# core) in the kernel's own layout, with invented model names. The checks
# compute their answers from these same trees.
set -euo pipefail

# mask_of TOTAL CPU...: the kernel's hexadecimal mask of a set of CPUs, as in
# topology/thread_siblings: groups of 32 CPUs, the highest group first. lscpu
# reads the masks, not the lists, so both are written.
mask_of() {
  local total=$1 group word cpu out=""
  shift
  for ((group = (total + 31) / 32 - 1; group >= 0; group--)); do
    word=0
    for cpu in "$@"; do
      if ((cpu / 32 == group)); then word=$((word | (1 << (cpu % 32)))); fi
    done
    out+=$(printf '%08x' "$word")
    if ((group > 0)); then out+=","; fi
  done
  echo "$out"
}

# list_of CPU...: the kernel's list form of the same set, like 0-23,48-71.
list_of() {
  local out="" start="" prev="" cpu
  for cpu in $(printf '%s\n' "$@" | sort -n); do
    if [ -z "$start" ]; then
      start=$cpu
    elif ((cpu != prev + 1)); then
      out+="${out:+,}$(span "$start" "$prev")"
      start=$cpu
    fi
    prev=$cpu
  done
  echo "${out:+$out,}$(span "$start" "$prev")"
}
span() { if (($1 == $2)); then echo "$1"; else echo "$1-$2"; fi; }

# machine DIR SOCKETS CORES_PER_SOCKET THREADS_PER_CORE KIND
# KIND is x86 or arm. Each socket is one NUMA node. CPUs are numbered as Linux
# numbers most x86 servers: the first thread of every core, socket by socket,
# then the second threads in the same order, so CPU 0's sibling on a 96-CPU
# machine is CPU 48.
machine() {
  local dir=$1 sockets=$2 cores=$3 threads=$4 kind=$5
  local total=$((sockets * cores * threads)) firsts=$((sockets * cores))
  local sys="$dir/sys/devices/system" cpu thread socket core x y
  mkdir -p "$sys/cpu" "$sys/node" "$dir/proc"
  for name in possible present online; do echo "0-$((total - 1))" > "$sys/cpu/$name"; done
  : > "$dir/proc/cpuinfo"
  for ((cpu = 0; cpu < total; cpu++)); do
    thread=$((cpu / firsts))
    socket=$(((cpu % firsts) / cores))
    core=$((cpu % cores))
    local siblings=() package=()
    for ((x = 0; x < threads; x++)); do siblings+=($((x * firsts + socket * cores + core))); done
    for ((x = 0; x < threads; x++)); do
      for ((y = 0; y < cores; y++)); do package+=($((x * firsts + socket * cores + y))); done
    done
    local topology="$sys/cpu/cpu$cpu/topology"
    mkdir -p "$topology"
    echo 1 > "$sys/cpu/cpu$cpu/online"
    echo "$socket" > "$topology/physical_package_id"
    echo "$core" > "$topology/core_id"
    echo 0 > "$topology/die_id"
    mask_of "$total" "${siblings[@]}" > "$topology/thread_siblings"
    list_of "${siblings[@]}" > "$topology/thread_siblings_list"
    mask_of "$total" "${package[@]}" > "$topology/core_siblings"
    list_of "${package[@]}" > "$topology/core_siblings_list"
    cp "$topology/thread_siblings" "$topology/core_cpus"
    cp "$topology/thread_siblings_list" "$topology/core_cpus_list"
    cp "$topology/core_siblings" "$topology/package_cpus"
    cp "$topology/core_siblings_list" "$topology/package_cpus_list"
    if [ "$kind" = x86 ]; then
      printf 'processor\t: %d\nvendor_id\t: GenuineIntel\ncpu family\t: 6\nmodel\t\t: 143\nmodel name\t: Intel(R) Xeon(R) Platinum (constructed)\nphysical id\t: %d\nsiblings\t: %d\ncore id\t\t: %d\ncpu cores\t: %d\nflags\t\t: fpu sse sse2 ht hypervisor\n\n' \
        "$cpu" "$socket" $((cores * threads)) "$core" "$cores" >> "$dir/proc/cpuinfo"
    else
      printf 'processor\t: %d\nBogoMIPS\t: 2100.00\nFeatures\t: fp asimd evtstrm aes pmull sha1 sha2 crc32 atomics\nCPU implementer\t: 0x41\nCPU architecture: 8\nCPU variant\t: 0x1\nCPU part\t: 0xd0c\nCPU revision\t: 1\n\n' \
        "$cpu" >> "$dir/proc/cpuinfo"
    fi
  done
  for ((socket = 0; socket < sockets; socket++)); do
    local members=()
    for ((cpu = 0; cpu < total; cpu++)); do
      if (((cpu % firsts) / cores == socket)); then members+=("$cpu"); fi
    done
    mkdir -p "$sys/node/node$socket"
    mask_of "$total" "${members[@]}" > "$sys/node/node$socket/cpumap"
    list_of "${members[@]}" > "$sys/node/node$socket/cpulist"
  done
  echo "0-$((sockets - 1))" > "$sys/node/online"
  echo "0-$((sockets - 1))" > "$sys/node/possible"
}

machine /srv/machines/web-1 1 1 2 x86
machine /srv/machines/arm-1 1 2 1 arm
machine /srv/machines/db-1 2 24 2 x86

# What `numactl --hardware` would print on db-1, in its own layout: each
# node's CPUs, its memory and what is free (node 1 is nearly full), and the
# table of distances (10 is local, 21 the other node).
{
  echo "available: 2 nodes (0-1)"
  for node in 0 1; do
    cpus=""
    for ((cpu = 0; cpu < 96; cpu++)); do
      if (((cpu % 48) / 24 == node)); then cpus+=" $cpu"; fi
    done
    echo "node $node cpus:$cpus"
    if ((node == 0)); then echo "node 0 size: 192998 MB"; echo "node 0 free: 151208 MB"; fi
    if ((node == 1)); then echo "node 1 size: 193512 MB"; echo "node 1 free: 3140 MB"; fi
  done
  echo "node distances:"
  echo "node   0   1 "
  echo "  0:  10  21 "
  echo "  1:  21  10 "
} > /srv/machines/db-1/numactl-hardware.txt

cat > /srv/machines/README <<'EOF'
Three machines for the walkthrough: web-1, arm-1 and db-1.

They are constructed, not captured. The lab's seed script wrote each one
from a shape (sockets, cores per socket, threads per core), in the layout
the kernel uses for /proc/cpuinfo and /sys/devices/system, with invented
model names. `lscpu --sysroot /srv/machines/NAME` reads one as it would read
a real machine. db-1/numactl-hardware.txt is constructed the same way, in
the layout `numactl --hardware` prints.
EOF

chmod -R a+rX /srv/machines
