# Wrong: shop-report is locked before it is put back. versionlock locks the
# version that is installed, 2.1, the broken one, and the downgrade that
# follows then finds nothing it is allowed to install: dnf says "cannot
# downgrade" and the package stays where it was.
echo 2 > ~/patch/bad-transaction.txt
sudo dnf versionlock add shop-report
sudo dnf downgrade -y shop-report
sudo dnf install -y shop-dashboard-1.0
sudo dnf versionlock add shop-dashboard
sudo dnf upgrade -y
