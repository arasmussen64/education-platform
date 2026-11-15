# Wrong: the dashboard is installed by name alone, which gives the newest
# version, 1.1, the one that needs a database the shop doesn't run. The
# lock then holds it at the wrong version.
echo 2 > ~/patch/bad-transaction.txt
sudo dnf downgrade -y shop-report
sudo dnf versionlock add shop-report
sudo dnf install -y shop-dashboard
sudo dnf versionlock add shop-dashboard
sudo dnf upgrade -y
