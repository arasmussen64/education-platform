# Wrong: the report tool is put back and the dashboard installed at the
# older version, but nothing is locked, so the upgrade that follows moves
# both straight to the newest version.
echo 2 > ~/patch/bad-transaction.txt
sudo dnf downgrade -y shop-report
sudo dnf install -y shop-dashboard-1.0
sudo dnf upgrade -y
