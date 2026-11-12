# Wrong: the rates come from the summary line ending "sender", which counts
# what shop handed to its kernel to send, not what the receiver got; across
# a lossy link the two differ by far more than 10%.
mkdir -p ~/bin
cat > ~/bin/cc-compare << 'EOF'
#!/bin/bash
if [ $# -ne 2 ]; then
  echo "usage: cc-compare HOST SECONDS" >&2
  exit 2
fi
cubic=$(iperf3 -c "$1" -t "$2" -C cubic -f m | awk '/sender$/ {print $7}')
bbr=$(iperf3 -c "$1" -t "$2" -C bbr -f m | awk '/sender$/ {print $7}')
awk -v c="$cubic" -v b="$bbr" 'BEGIN {printf "cubic %.1f\nbbr %.1f\nbbr/cubic %.1f\n", c, b, b / c}'
EOF
chmod +x ~/bin/cc-compare
