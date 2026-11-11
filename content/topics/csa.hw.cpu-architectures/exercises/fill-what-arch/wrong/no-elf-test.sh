# Wrong: the patterns look for the architecture's name anywhere in file's
# description, without asking for an ELF file first. A gzip archive names
# the file it packed, build-x86-64.tar, so it is taken for an x86-64
# program.
cat > ~/bin/what-arch <<'EOF'
#!/bin/bash
for path in "$@"; do
  kind=$(file -b "$path")
  case "$kind" in
    *x86-64*) arch=x86-64 ;;
    *aarch64*) arch=aarch64 ;;
    *) arch=not-a-program ;;
  esac
  echo "$path $arch"
done
EOF
