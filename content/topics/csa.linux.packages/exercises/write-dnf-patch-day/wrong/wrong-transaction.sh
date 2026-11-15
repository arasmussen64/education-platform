# Wrong: everything is patched and held correctly, but the file names the
# newest transaction in the history as it stood, 3, which reinstalled
# shop-agent, instead of the one that upgraded shop-report.
echo 3 > ~/patch/bad-transaction.txt
sudo dnf downgrade -y shop-report
sudo dnf versionlock add shop-report
sudo dnf install -y shop-dashboard-1.0
sudo dnf versionlock add shop-dashboard
sudo dnf upgrade -y
