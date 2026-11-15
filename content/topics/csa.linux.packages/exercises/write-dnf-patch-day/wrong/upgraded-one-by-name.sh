# Wrong: nothing is locked, and only shop-agent is upgraded, by name. Every
# package is at the right version today, but nothing holds the other two:
# the next "dnf upgrade", by a person or by a nightly job, moves both.
echo 2 > ~/patch/bad-transaction.txt
sudo dnf downgrade -y shop-report
sudo dnf install -y shop-dashboard-1.0
sudo dnf upgrade -y shop-agent
