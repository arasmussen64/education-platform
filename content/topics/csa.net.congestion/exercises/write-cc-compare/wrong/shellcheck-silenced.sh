# Wrong: the numbers are right, but iperf3's HOST and SECONDS are used
# without quotes, and instead of quoting them, ShellCheck's warning is
# switched off.
mkdir -p ~/bin
cat > ~/bin/cc-compare << 'EOF'
#!/bin/bash
if [ $# -ne 2 ]; then
  echo "usage: cc-compare HOST SECONDS" >&2
  exit 2
fi
host=$1
seconds=$2
rate() {
  # shellcheck disable=SC2086
  iperf3 -c $host -t $seconds -C "$1" -f m | awk '/receiver$/ {print $7}'
}
cubic=$(rate cubic)
sleep 1
bbr=$(rate bbr)
awk -v c="$cubic" -v b="$bbr" 'BEGIN {
  printf "cubic %.1f\n", c
  printf "bbr %.1f\n", b
  printf "bbr/cubic %.1f\n", b / c
}'
EOF
chmod +x ~/bin/cc-compare
