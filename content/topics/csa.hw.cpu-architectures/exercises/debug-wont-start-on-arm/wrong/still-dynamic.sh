# Wrong: two of the three. The Arm copy is released and built without SVE,
# but linked dynamically, so it looks for the Arm loader and C library on
# servers that have nothing but the program.
cd /srv/release
sed -i 's|cp build/shop-resize-amd64 bin/shop-resize|cp build/shop-resize-arm64 bin/shop-resize|' build.sh
sed -i 's/ -march=armv8.2-a+sve / /' build.sh
./build.sh
