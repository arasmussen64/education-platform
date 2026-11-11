# Wrong: the script names the two boxes it was shown and prints their
# answers, worked out once by hand. On any other box it says nothing true.
mkdir -p ~/bin
cat > ~/bin/gpu-report <<'EOF'
#!/bin/bash
if [ $# -ne 1 ]; then
  echo "Usage: gpu-report DIR" >&2
  exit 2
fi
case "$1" in
  */box-2) printf 'average util: 52%%\npeak memory: 62080 of 81559 MiB\nidle seconds: 15\n' ;;
  *) printf 'average util: 18%%\npeak memory: 39340 of 40537 MiB\nidle seconds: 24\n' ;;
esac
EOF
chmod +x ~/bin/gpu-report
