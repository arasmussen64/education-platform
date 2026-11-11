#!/bin/bash
# Lays down the fill-in: the script with its gaps, the folder of samples the
# prompt names, and a second folder it doesn't, with another mix. Some file
# names tell the truth about their architecture and some don't, as names
# can't be trusted; only what's inside the file can.
set -euo pipefail
here=/usr/local/lib/lab
home=/home/learner
work=$(mktemp -d)

cat > "$work/tool.c" <<'EOF'
#include <stdio.h>
int main(void) { puts("a shop tool"); return 0; }
EOF
cat > "$work/lib.c" <<'EOF'
int shop_add(int a, int b) { return a + b; }
EOF
x86() { gcc -O2 -o "$1" "$work/tool.c"; }
x86_static() { gcc -O2 -static -o "$1" "$work/tool.c"; }
arm() { aarch64-linux-gnu-gcc -O2 -static -o "$1" "$work/tool.c"; }
x86_lib() { gcc -O2 -shared -fPIC -o "$1" "$work/lib.c"; }
arm_lib() { aarch64-linux-gnu-gcc -O2 -shared -fPIC -o "$1" "$work/lib.c"; }
jar() {
  # A Java archive with only a stand-in class file in it (its first bytes
  # are all `file` reads).
  local dir
  dir=$(mktemp -d)
  mkdir -p "$dir/META-INF" "$dir/org/shop"
  printf 'Manifest-Version: 1.0\n' > "$dir/META-INF/MANIFEST.MF"
  printf '\312\376\272\276\000\000\000\101' > "$dir/org/shop/Labels.class"
  (cd "$dir" && zip -q -X -r "$1" META-INF org)
  rm -r "$dir"
}

# The samples the prompt names.
s=/srv/samples
mkdir -p "$s"
printf '#!/bin/bash\n# Copies the logs somewhere safe.\ncp -r /var/log/shop /backup/\n' > "$s/backup.sh"
printf '#!/usr/bin/env python3\n# Deploys the shop.\nprint("deploying")\n' > "$s/deploy.py"
printf 'The shop tools. Build them with the notes in the wiki.\n' > "$s/README.txt"
x86 "$s/shop-api"
arm "$s/shop-api-arm64"
x86_lib "$s/libcrc.so"
arm_lib "$s/libcrc-aarch64.so"
# Misnamed: an Arm program whose name says x86_64.
arm "$s/thumb-x86_64"
jar "$s/labels.jar"
chmod 755 "$s/backup.sh" "$s/deploy.py"

# A second folder the prompt doesn't name, for the checks.
m=/usr/local/share/lab/more
mkdir -p "$m"
printf '#!/usr/bin/env python3\nprint("report")\n' > "$m/report.py"
# Misnamed the other way: an x86-64 program whose name says arm64.
x86_static "$m/tool-arm64"
arm_lib "$m/libfast.so"
x86 "$m/agent"
printf '# Notes\nNothing to see here.\n' > "$m/notes.md"
: > "$m/empty.log"
# An archive whose description mentions x86-64, because gzip keeps the
# name of the file it packed. It is not a program.
printf 'old build\n' > "$work/build-x86-64.tar"
touch -d '2026-11-11 09:00:00' "$work/build-x86-64.tar"
gzip -c "$work/build-x86-64.tar" > "$m/old-build.gz"
chmod 755 "$m/report.py"

rm -r "$work"

mkdir -p "$home/bin"
cp "$here/what-arch.starter" "$home/bin/what-arch"
chmod 755 "$home/bin/what-arch"
chown -R learner:learner "$home/bin"
