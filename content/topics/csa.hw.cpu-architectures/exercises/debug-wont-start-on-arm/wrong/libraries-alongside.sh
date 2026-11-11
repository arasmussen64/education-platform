# Wrong: the Arm copy is released and built without SVE, still linked
# dynamically, with the cross-compiler's Arm libraries copied into the
# release beside it. The program still looks for its loader at
# /lib/ld-linux-aarch64.so.1, where the servers have nothing; and shipping
# a C library with every program is a second thing to keep up to date.
cd /srv/release
sed -i 's|cp build/shop-resize-amd64 bin/shop-resize|cp build/shop-resize-arm64 bin/shop-resize|' build.sh
sed -i 's/ -march=armv8.2-a+sve / /' build.sh
./build.sh
mkdir -p bin/lib
cp /usr/aarch64-linux-gnu/lib/ld-linux-aarch64.so.1 /usr/aarch64-linux-gnu/lib/libc.so.6 bin/lib/
