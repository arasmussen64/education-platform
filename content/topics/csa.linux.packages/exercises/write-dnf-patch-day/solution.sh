# 1. Look first: what is installed, what the repository has, and what an
# upgrade would change. (dnf check-update ends with status 100 when
# something is waiting, which isn't an error.)
rpm -q shop-agent shop-report shop-dashboard || true
dnf list --showduplicates 'shop-*'
dnf check-update || true

# 2. The history, newest first. Transaction 2's command was
# "upgrade -y shop-report", and its details show 2.0 replaced by 2.1.
dnf history
dnf history info 2
echo 2 > ~/patch/bad-transaction.txt

# 3. shop-report back to 2.0, then locked there. The lock goes on after
# the downgrade: versionlock locks whatever version is installed.
sudo dnf downgrade -y shop-report
sudo dnf versionlock add shop-report

# 4. The dashboard at the older version, by name and version, and locked.
sudo dnf install -y shop-dashboard-1.0
sudo dnf versionlock add shop-dashboard
dnf versionlock list

# 5. Everything else. Only shop-agent moves, from 1.0 to 1.1.
sudo dnf upgrade -y
rpm -q shop-agent shop-report shop-dashboard
dnf check-update
