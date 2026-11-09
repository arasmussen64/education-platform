# Wrong: the reboot answer is a guess, not what the machine says, and the
# kernel package did change.
sudo apt update
sudo apt-mark hold shop-report
sudo apt upgrade -y
sudo apt purge -y shop-theme
sudo apt install -y shop-dashboard
mkdir -p ~/report
apt list --upgradable 2>/dev/null > ~/report/waiting.txt
echo no > ~/report/reboot.txt
