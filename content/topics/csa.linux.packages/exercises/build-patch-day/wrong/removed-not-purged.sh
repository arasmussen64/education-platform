# Wrong: remove keeps the configuration file and leaves dpkg's "rc" record.
sudo apt update
sudo apt-mark hold shop-report
sudo apt upgrade -y
sudo apt remove -y shop-theme
sudo apt install -y shop-dashboard
mkdir -p ~/report
apt list --upgradable 2>/dev/null > ~/report/waiting.txt
if [ -f /run/reboot-required ]; then echo yes > ~/report/reboot.txt; else echo no > ~/report/reboot.txt; fi
