# Wrong: the third line divides CUBIC's rate by BBR's, the wrong way up.
mkdir -p ~/bin
cat > ~/bin/cc-compare << 'EOF'
#!/bin/bash
if [ $# -ne 2 ]; then
  echo "usage: cc-compare HOST SECONDS" >&2
  exit 2
fi
cubic=$(iperf3 -c "$1" -t "$2" -C cubic -f m | awk '/receiver$/ {print $7}')
bbr=$(iperf3 -c "$1" -t "$2" -C bbr -f m | awk '/receiver$/ {print $7}')
awk -v c="$cubic" -v b="$bbr" 'BEGIN {printf "cubic %.1f\nbbr %.1f\nbbr/cubic %.1f\n", c, b, c / b}'
EOF
chmod +x ~/bin/cc-compare
