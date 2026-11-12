# Wrong: the script always runs each test for 5 seconds, the length it was
# tried with, whatever SECONDS it is given.
mkdir -p ~/bin
cat > ~/bin/cc-compare << 'EOF'
#!/bin/bash
if [ $# -ne 2 ]; then
  echo "usage: cc-compare HOST SECONDS" >&2
  exit 2
fi
cubic=$(iperf3 -c "$1" -t 5 -C cubic -f m | awk '/receiver$/ {print $7}')
bbr=$(iperf3 -c "$1" -t 5 -C bbr -f m | awk '/receiver$/ {print $7}')
awk -v c="$cubic" -v b="$bbr" 'BEGIN {printf "cubic %.1f\nbbr %.1f\nbbr/cubic %.1f\n", c, b, b / c}'
EOF
chmod +x ~/bin/cc-compare
