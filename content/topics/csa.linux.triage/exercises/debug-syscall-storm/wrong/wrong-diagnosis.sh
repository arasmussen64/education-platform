# Wrong: stopped the runaway, but the finding blames a memory leak, which
# isn't what strace showed; the next person is sent the wrong way.
sudo systemctl disable --now shop-tailer
mkdir -p ~/triage
printf 'culprit: shop-tailer\ncause: a memory leak filling up RAM\n' > ~/triage/finding.txt
