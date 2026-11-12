# A reference solution. "cat > FILE << 'EOF'" writes everything up to the
# line EOF into the file; the quotes round 'EOF' keep the shell from
# expanding the $ signs as it writes, so the script gets them as typed.
mkdir -p ~/bin
cat > ~/bin/cc-compare << 'EOF'
#!/bin/bash
# cc-compare HOST SECONDS: measures one TCP connection to HOST's iperf3
# server with CUBIC and then with BBR, each for SECONDS, and prints the rate
# the receiver counted for each, in Mbit/s, and how many times BBR's rate
# is CUBIC's. Run it on the sending machine: congestion control is the
# sender's choice. iperf3's -C picks the algorithm for that one test.
if [ $# -ne 2 ]; then
  echo "usage: cc-compare HOST SECONDS" >&2
  exit 2
fi
host=$1
seconds=$2

# One test with one algorithm: the receiver's rate, from the summary line
# that ends "receiver" (-f m: always in Mbits/sec; the rate is field 7).
rate() {
  iperf3 -c "$host" -t "$seconds" -C "$1" -f m | awk '/receiver$/ {print $7}'
}

cubic=$(rate cubic)
# The receiver takes one test at a time and needs a moment to listen again.
sleep 1
bbr=$(rate bbr)
awk -v c="$cubic" -v b="$bbr" 'BEGIN {
  printf "cubic %.1f\n", c
  printf "bbr %.1f\n", b
  printf "bbr/cubic %.1f\n", b / c
}'
EOF
chmod +x ~/bin/cc-compare
# Try it on the lossy link to dr1, then on the clean one to dr2.
on shop ~/bin/cc-compare 10.0.6.20 4
on shop ~/bin/cc-compare 10.0.7.20 3
