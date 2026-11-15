# Wrong: the script is the reference one without its first line,
# #!/bin/bash, so it is left to whatever shell happens to start it, and
# ShellCheck can't tell which shell it is written for (SC2148).
mkdir -p ~/bin
cat > ~/bin/cc-compare << 'EOF'
if [ $# -ne 2 ]; then
  echo "usage: cc-compare HOST SECONDS" >&2
  exit 2
fi
host=$1
seconds=$2
rate() {
  iperf3 -c "$host" -t "$seconds" -C "$1" -f m | awk '/receiver$/ {print $7}'
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
