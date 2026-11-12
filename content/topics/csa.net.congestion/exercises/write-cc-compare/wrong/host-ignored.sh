# Wrong: the script always measures dr1, the site it was tried on, whatever
# HOST it is given.
mkdir -p ~/bin
cat > ~/bin/cc-compare << 'EOF'
#!/bin/bash
if [ $# -ne 2 ]; then
  echo "usage: cc-compare HOST SECONDS" >&2
  exit 2
fi
cubic=$(iperf3 -c 10.0.6.20 -t "$2" -C cubic -f m | awk '/receiver$/ {print $7}')
bbr=$(iperf3 -c 10.0.6.20 -t "$2" -C bbr -f m | awk '/receiver$/ {print $7}')
awk -v c="$cubic" -v b="$bbr" 'BEGIN {printf "cubic %.1f\nbbr %.1f\nbbr/cubic %.1f\n", c, b, b / c}'
EOF
chmod +x ~/bin/cc-compare
