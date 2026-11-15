# Wrong: the two packages are put right and locked, and then the upgrade
# is never run: shop-agent is still at 1.0, with its newer version waiting.
echo 2 > ~/patch/bad-transaction.txt
sudo dnf downgrade -y shop-report
sudo dnf versionlock add shop-report
sudo dnf install -y shop-dashboard-1.0
sudo dnf versionlock add shop-dashboard
dnf check-update || true
