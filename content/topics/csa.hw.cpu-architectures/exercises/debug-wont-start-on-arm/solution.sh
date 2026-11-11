# The three faults, all in the recipe:
#   1. It released the wrong copy: the x86-64 one it builds to test on the
#      build machine. Under the Arm emulator that is "Invalid ELF image for
#      this architecture"; on a real Arm server, "Exec format error".
#   2. Once the Arm copy is released, it can't start: it was linked
#      dynamically and looks for /lib/ld-linux-aarch64.so.1, the Arm loader,
#      which the servers (and this x86-64 machine) don't have. -static puts
#      the C library inside the program.
#   3. Then it starts and dies with "Illegal instruction" (signal 4, exit
#      status 132): -march=armv8.2-a+sve let the compiler do the shading
#      loop with SVE instructions, which Neoverse N1 doesn't have. Without
#      -march, the compiler uses only what every 64-bit Arm CPU has.
# In the lab you'd make the three edits with nano; here the recipe is
# written out whole.
cat > /srv/release/build.sh <<'EOF'
#!/bin/bash
# Builds shop-resize twice: once for this x86-64 build machine, to test it
# here, and once for the fleet's Arm servers, which is the copy released.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build bin

# This machine's copy, tested on the spot.
gcc -O2 -o build/shop-resize-amd64 src/shop-resize.c
build/shop-resize-amd64 --selftest

# The fleet's copy: no -march, so nothing the oldest servers' Neoverse N1
# lacks, and statically linked, since the servers have nothing installed
# but the program.
aarch64-linux-gnu-gcc -O2 -static -o build/shop-resize-arm64 src/shop-resize.c

# Release it: the Arm copy.
cp build/shop-resize-arm64 bin/shop-resize
echo "released bin/shop-resize"
EOF
/srv/release/build.sh
file /srv/release/bin/shop-resize
qemu-aarch64-static -cpu neoverse-n1 /srv/release/bin/shop-resize --selftest
