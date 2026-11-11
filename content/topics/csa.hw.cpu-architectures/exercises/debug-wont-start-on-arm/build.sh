#!/bin/bash
# Builds shop-resize twice: once for this x86-64 build machine, to test it
# here, and once for the fleet's Arm servers, which is the copy released.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build bin

# This machine's copy, tested on the spot.
gcc -O2 -o build/shop-resize-amd64 src/shop-resize.c
build/shop-resize-amd64 --selftest

# The fleet's copy.
aarch64-linux-gnu-gcc -O2 -march=armv8.2-a+sve -o build/shop-resize-arm64 src/shop-resize.c

# Release it.
cp build/shop-resize-amd64 bin/shop-resize
echo "released bin/shop-resize"
