# Wrong: the runaway is stopped through its service, so it stays down for
# now, but the service is still enabled: after the next reboot it is back,
# eating a CPU again.
sudo systemctl stop shop-tailer
mkdir -p ~/triage
printf 'culprit: shop-tailer\ncause: a busy loop of failing openat calls on a missing queue path\n' > ~/triage/finding.txt
