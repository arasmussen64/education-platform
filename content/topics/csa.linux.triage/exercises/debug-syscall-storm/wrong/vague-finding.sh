# Wrong: the runaway is stopped for good, but the note never says which
# system call it was: "too many system calls" gives the next person
# nothing to search the code for.
sudo systemctl disable --now shop-tailer
mkdir -p ~/triage
printf 'culprit: shop-tailer\ncause: it was making far too many system calls\n' > ~/triage/finding.txt
