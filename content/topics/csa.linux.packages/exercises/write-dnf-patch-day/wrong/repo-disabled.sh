# Wrong: instead of locking the two packages, the repository is switched
# off once the agent is upgraded. dnf then offers no updates for anything,
# so nothing moves, but nothing can be patched or installed either: the
# next security fix for shop-agent will never arrive.
echo 2 > ~/patch/bad-transaction.txt
sudo dnf downgrade -y shop-report
sudo dnf install -y shop-dashboard-1.0
sudo dnf upgrade -y shop-agent
sudo sed -i 's/^enabled=1$/enabled=0/' /etc/yum.repos.d/shop.repo
