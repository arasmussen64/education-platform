# Wrong: it trusts the file's name instead of what's inside. thumb-x86_64
# is an Arm program, and tool-arm64 in the other folder is an x86-64 one.
cat > ~/bin/what-arch <<'EOF'
#!/bin/bash
for path in "$@"; do
  case "$path" in
    *.sh|*.py|*.txt|*.md|*.jar|*.log|*.gz) arch=not-a-program ;;
    *arm64*|*aarch64*) arch=aarch64 ;;
    *) arch=x86-64 ;;
  esac
  echo "$path $arch"
done
EOF
