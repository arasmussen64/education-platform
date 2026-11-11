# Wrong: any image with an index is called multi. An index can list one
# platform only, as the shop's own image's does: amd64 and nothing else.
# 1. The audit. file decides what each file is from its contents: an ELF
#    file for aarch64 runs on Arm, any other ELF file doesn't. A .jar is a
#    zip archive: list it with unzip -l, and ask file about each library
#    inside with unzip -p, without unpacking anything.
mkdir -p ~/bin ~/report ~/out
cat > ~/bin/arm-audit <<'EOF'
#!/bin/bash
# Usage: arm-audit DIR
# Prints every file under DIR that can't run on a 64-bit Arm server as it
# is: programs and libraries built for another architecture, and Java
# archives with such a library inside. One path a line, sorted.
set -euo pipefail
find "$1" -type f | sort | while read -r path; do
  case "$(file -b "$path")" in
    ELF*aarch64*) continue ;;
    ELF*) echo "$path"; continue ;;
  esac
  case "$path" in
    *.jar)
      for entry in $(unzip -l "$path" | awk '$4 ~ /\.so$/ {print $4}'); do
        case "$(unzip -p "$path" "$entry" | file -b -)" in
          ELF*aarch64*) ;;
          ELF*) echo "$path"; break ;;
        esac
      done
      ;;
  esac
done
EOF
chmod +x ~/bin/arm-audit
~/bin/arm-audit /srv/shop

# 2. The plan: rebuild what the shop has the source of, ask the vendor for
#    the rest.
~/bin/arm-audit /srv/shop | while read -r path; do
  name=$(basename "$path")
  if [ -f "/srv/shop/src/$name.c" ]; then
    echo "$path rebuild"
  else
    echo "$path vendor"
  fi
done > ~/report/plan.txt
cat ~/report/plan.txt

# 3. The images: an index that lists an arm64 manifest offers Arm. The
#    files are on one line, so the pattern allows a space after the colon
#    or none.
while read -r image file; do
  if grep -q 'image.index' "/srv/shop/images/$file"; then
    echo "$image multi"
  else
    echo "$image x86-only"
  fi
done < /srv/shop/images/images.txt > ~/report/images.txt
cat ~/report/images.txt

# 4. The builds: the cross-compiler, statically linked, and no -march, so
#    the compiler uses only what every 64-bit Arm CPU has. The notes' SVE
#    flag would make shop-thumb die on Neoverse N1, which has no SVE.
aarch64-linux-gnu-gcc -O2 -static -o ~/out/shop-api /srv/shop/src/shop-api.c
aarch64-linux-gnu-gcc -O2 -static -o ~/out/shop-thumb /srv/shop/src/shop-thumb.c
file ~/out/shop-api ~/out/shop-thumb
qemu-aarch64-static -cpu neoverse-n1 ~/out/shop-api --selftest
qemu-aarch64-static -cpu neoverse-n1 ~/out/shop-thumb --selftest
