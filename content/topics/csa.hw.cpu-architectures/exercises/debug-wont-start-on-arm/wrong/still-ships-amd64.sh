# Wrong: two of the three. The Arm copy is built right (no SVE, static),
# but the recipe still releases the x86-64 copy.
cd /srv/release
sed -i 's/ -march=armv8.2-a+sve / -static /' build.sh
./build.sh
