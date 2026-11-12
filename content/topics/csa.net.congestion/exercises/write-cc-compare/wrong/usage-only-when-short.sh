# Wrong: the script prints its usage line only when it's given fewer than
# two arguments. Given three, it measures as if the third weren't there and
# exits 0, though anything but two arguments is a mistake to point out.
mkdir -p ~/bin
cat > ~/bin/cc-compare << 'EOF'
#!/bin/bash
if [ $# -lt 2 ]; then
  echo "usage: cc-compare HOST SECONDS" >&2
  exit 2
fi
cubic=$(iperf3 -c "$1" -t "$2" -C cubic -f m | awk '/receiver$/ {print $7}')
sleep 1
bbr=$(iperf3 -c "$1" -t "$2" -C bbr -f m | awk '/receiver$/ {print $7}')
awk -v c="$cubic" -v b="$bbr" 'BEGIN {printf "cubic %.1f\nbbr %.1f\nbbr/cubic %.1f\n", c, b, b / c}'
EOF
chmod +x ~/bin/cc-compare
