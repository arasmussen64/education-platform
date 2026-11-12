# Wrong: neither test says which algorithm to use (no -C), so both use the
# system's default, CUBIC, and the ratio comes out near 1.
mkdir -p ~/bin
cat > ~/bin/cc-compare << 'EOF'
#!/bin/bash
if [ $# -ne 2 ]; then
  echo "usage: cc-compare HOST SECONDS" >&2
  exit 2
fi
cubic=$(iperf3 -c "$1" -t "$2" -f m | awk '/receiver$/ {print $7}')
bbr=$(iperf3 -c "$1" -t "$2" -f m | awk '/receiver$/ {print $7}')
awk -v c="$cubic" -v b="$bbr" 'BEGIN {printf "cubic %.1f\nbbr %.1f\nbbr/cubic %.1f\n", c, b, b / c}'
EOF
chmod +x ~/bin/cc-compare
