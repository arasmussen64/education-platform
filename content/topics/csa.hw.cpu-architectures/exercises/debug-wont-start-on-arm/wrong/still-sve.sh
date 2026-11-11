# Wrong: two of the three. The Arm copy is released and statically linked,
# but still built for SVE, which Neoverse N1 doesn't have. Tested with
# -cpu max (every feature the emulator knows) it would pass; on the fleet's
# oldest servers it dies with Illegal instruction.
cd /srv/release
sed -i 's|cp build/shop-resize-amd64 bin/shop-resize|cp build/shop-resize-arm64 bin/shop-resize|' build.sh
sed -i 's/ -march=armv8.2-a+sve / -march=armv8.2-a+sve -static /' build.sh
./build.sh
