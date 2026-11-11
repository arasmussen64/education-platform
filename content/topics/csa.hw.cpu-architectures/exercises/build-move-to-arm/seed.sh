#!/bin/bash
# Lays down the build: the shop's service under /srv/shop as its x86-64
# servers run it today, a second tree with another mix for the checks
# (/usr/local/share/lab/depot, which the prompt doesn't name), what each
# program's self-test prints when it runs correctly, and the checksums of
# the shop's sources.
set -euo pipefail
here=/usr/local/lib/lab
work=$(mktemp -d)

cat > "$work/lib.c" <<'EOF'
int shop_lib(int a, int b) { return a * 31 + b; }
EOF
cat > "$work/tool.c" <<'EOF'
#include <stdio.h>
int main(void) { puts("a tool from somewhere else"); return 0; }
EOF
# A Java archive: a manifest, stand-in class files (the first bytes of one,
# which is all `file` reads), and, if given, a compiled library inside.
jar() {
  local out=$1 class=$2 lib_name=${3:-} lib_cc=${4:-}
  local dir
  dir=$(mktemp -d)
  mkdir -p "$dir/META-INF" "$dir/$(dirname "$class")"
  printf 'Manifest-Version: 1.0\nCreated-By: the shop build\n' > "$dir/META-INF/MANIFEST.MF"
  printf '\312\376\272\276\000\000\000\101' > "$dir/$class"
  if [ -n "$lib_name" ]; then
    mkdir -p "$dir/native"
    "$lib_cc" -O2 -shared -fPIC -o "$dir/native/$lib_name" "$work/lib.c"
  fi
  find "$dir" -exec touch -d '2026-11-11 09:00:00' {} +
  (cd "$dir" && zip -q -X -r "$out" .)
  rm -r "$dir"
}

# The shop, as its x86-64 servers run it.
shop=/srv/shop
mkdir -p "$shop/bin" "$shop/src" "$shop/lib/python/receipts" "$shop/lib/python/imaging" \
  "$shop/lib/java" "$shop/agents" "$shop/etc" "$shop/images/index"
cp "$here/shop-api.c" "$here/shop-thumb.c" "$here/BUILD.txt" "$shop/src/"
gcc -O2 -march=x86-64-v3 -o "$shop/bin/shop-api" "$shop/src/shop-api.c"
gcc -O2 -march=x86-64-v3 -o "$shop/bin/shop-thumb" "$shop/src/shop-thumb.c"
printf '#!/bin/bash\n# Nightly backup of the orders.\ntar -czf /backup/orders.tgz /var/lib/shop/orders\n' > "$shop/bin/backup.sh"
printf '#!/usr/bin/env python3\n# The daily sales report.\nprint("sales report")\n' > "$shop/bin/report.py"
chmod 755 "$shop/bin/backup.sh" "$shop/bin/report.py"
printf '# Pure Python: receipts.\n' > "$shop/lib/python/receipts/__init__.py"
printf 'def receipt(total):\n    return f"Total: {total:.2f}"\n' > "$shop/lib/python/receipts/format.py"
printf '# Resizes pictures with a compiled part, _resize.\n' > "$shop/lib/python/imaging/__init__.py"
gcc -O2 -shared -fPIC -o "$shop/lib/python/imaging/_resize.cpython-312-x86_64-linux-gnu.so" "$work/lib.c"
jar "$shop/lib/java/orders.jar" org/shop/orders/Order.class libcrc-linux-x86_64.so gcc
jar "$shop/lib/java/labels.jar" org/shop/labels/Label.class
gcc -O2 -static -o "$shop/agents/metrics-agent" "$work/tool.c"
printf 'metrics-agent 7.2, from the monitoring vendor. We have no source for it.\n' > "$shop/agents/README.txt"
printf 'port = 8080\nthumbnails = /var/lib/shop/thumbs\n' > "$shop/etc/shop.conf"
cp "$here/images.txt" "$shop/images/images.txt"
cp "$here/images-README.txt" "$shop/images/README.txt"
cp "$here"/index/*.json "$shop/images/index/"

# A second tree with another mix, for the checks. Names here don't always
# tell the truth: convert-amd64 is an Arm program.
depot=/usr/local/share/lab/depot
mkdir -p "$depot/tools" "$depot/lib" "$depot/java" "$depot/scripts" "$depot/archive" "$depot/docs"
gcc -O2 -o "$depot/tools/sync" "$work/tool.c"
aarch64-linux-gnu-gcc -O2 -static -o "$depot/tools/sync-arm64" "$work/tool.c"
aarch64-linux-gnu-gcc -O2 -static -o "$depot/tools/convert-amd64" "$work/tool.c"
gcc -O2 -shared -fPIC -o "$depot/lib/libold.so" "$work/lib.c"
aarch64-linux-gnu-gcc -O2 -shared -fPIC -o "$depot/lib/libfast.so" "$work/lib.c"
jar "$depot/java/exporter.jar" org/depot/Exporter.class libexport.so gcc
jar "$depot/java/importer.jar" org/depot/Importer.class libimport.so aarch64-linux-gnu-gcc
jar "$depot/java/plain.jar" org/depot/Plain.class
printf '#!/bin/bash\necho running\n' > "$depot/scripts/run.sh"
printf 'old build\n' > "$work/build-x86-64.tar"
gzip -c "$work/build-x86-64.tar" > "$depot/archive/old-build.gz"
printf 'Where the depot came from.\n' > "$depot/docs/notes.txt"

# What each self-test prints when the program runs correctly, from a plain
# build for this machine (no -march, so it runs on any x86-64 CPU).
expected=/usr/local/share/lab/expected
mkdir -p "$expected"
for program in shop-api shop-thumb; do
  gcc -O2 -o "$work/$program" "$shop/src/$program.c"
  "$work/$program" --selftest > "$expected/$program.txt"
done

# The checks' helper, and the sources' checksums.
mkdir -p /usr/local/libexec/lab
cp "$here/audit-truth" /usr/local/libexec/lab/audit-truth
chmod 755 /usr/local/libexec/lab/audit-truth
(cd "$shop/src" && sha256sum shop-api.c shop-thumb.c BUILD.txt) > /usr/local/share/lab/src.sha256

rm -r "$work"
mkdir -p /home/learner/bin
chown learner:learner /home/learner/bin
