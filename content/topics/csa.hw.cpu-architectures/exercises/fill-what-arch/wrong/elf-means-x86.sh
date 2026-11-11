# Wrong: every ELF file is called x86-64. ELF is the format of every Linux
# program, whatever CPU it was built for; the architecture is further along
# file's line.
cat > ~/bin/what-arch <<'EOF'
#!/bin/bash
for path in "$@"; do
  kind=$(file -b "$path")
  case "$kind" in
    ELF*) arch=x86-64 ;;
    *) arch=not-a-program ;;
  esac
  echo "$path $arch"
done
EOF
