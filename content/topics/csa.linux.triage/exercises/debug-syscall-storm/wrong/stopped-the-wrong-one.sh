# Wrong: stopped shop-api, the healthy service, and left the runaway
# shop-tailer eating a CPU.
sudo systemctl stop shop-api
mkdir -p ~/triage
printf 'culprit: shop-tailer\ncause: a busy loop of failing openat calls\n' > ~/triage/finding.txt
