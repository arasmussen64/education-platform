# Wrong: everything but the new package.
sudo apt update
sudo apt-mark hold shop-report
sudo apt upgrade -y
sudo apt purge -y shop-theme
mkdir -p ~/report
apt list --upgradable 2>/dev/null > ~/report/waiting.txt
if [ -f /run/reboot-required ]; then echo yes > ~/report/reboot.txt; else echo no > ~/report/reboot.txt; fi
