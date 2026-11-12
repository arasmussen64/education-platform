# Wrong: the script never checks its arguments, so without them it runs
# iperf3 against nothing and exits 0 with empty numbers.
mkdir -p ~/bin
cat > ~/bin/cc-compare << 'EOF'
#!/bin/bash
cubic=$(iperf3 -c "$1" -t "$2" -C cubic -f m | awk '/receiver$/ {print $7}')
bbr=$(iperf3 -c "$1" -t "$2" -C bbr -f m | awk '/receiver$/ {print $7}')
awk -v c="$cubic" -v b="$bbr" 'BEGIN {printf "cubic %.1f\nbbr %.1f\n", c, b; if (c > 0) printf "bbr/cubic %.1f\n", b / c}'
EOF
chmod +x ~/bin/cc-compare
