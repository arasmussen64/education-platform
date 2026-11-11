#!/bin/bash
# Lays down the worked example: two C programs to build, and an archive
# with a compiled library inside to look into.
set -euo pipefail
here=/usr/local/lib/lab
home=/home/learner

mkdir -p "$home/src" "$home/lib"
cp "$here/hello.c" "$here/count.c" "$home/src/"

# crc.jar: what a Java library looks like from outside. The class file is a
# stand-in (only the first bytes of one, which is all `file` reads); the
# library inside is a real one, compiled here for x86-64.
jar=$(mktemp -d)
mkdir -p "$jar/META-INF" "$jar/org/shop" "$jar/native"
printf 'Manifest-Version: 1.0\nCreated-By: the shop build\n' > "$jar/META-INF/MANIFEST.MF"
printf '\312\376\272\276\000\000\000\101' > "$jar/org/shop/Crc.class"
cat > "$jar/crc.c" <<'EOF'
/* A checksum, as a library that a Java program loads. */
unsigned int shop_crc(const unsigned char *data, unsigned long length) {
    unsigned int crc = 0xFFFFFFFFu;
    for (unsigned long i = 0; i < length; i++) {
        crc ^= data[i];
        for (int bit = 0; bit < 8; bit++) {
            crc = (crc >> 1) ^ (0xEDB88320u & (0u - (crc & 1u)));
        }
    }
    return ~crc;
}
EOF
gcc -O2 -shared -fPIC -o "$jar/native/libcrc.so" "$jar/crc.c"
rm "$jar/crc.c"
# The same date on every file, so the archive's listing is the same in
# every build of the image.
find "$jar" -exec touch -d '2026-11-11 09:00:00' {} +
(cd "$jar" && zip -q -X -r "$home/lib/crc.jar" META-INF org native)
rm -r "$jar"

chown -R learner:learner "$home/src" "$home/lib"
