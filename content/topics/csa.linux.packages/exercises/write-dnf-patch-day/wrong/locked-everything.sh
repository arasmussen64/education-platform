# Wrong: every one of the shop's packages is locked, the agent included,
# so the upgrade has nothing it may change and the agent's fix is never
# installed. A lock is for the packages that mustn't move, not for all of
# them.
echo 2 > ~/patch/bad-transaction.txt
sudo dnf downgrade -y shop-report
sudo dnf install -y shop-dashboard-1.0
sudo dnf versionlock add 'shop-*'
sudo dnf upgrade -y
