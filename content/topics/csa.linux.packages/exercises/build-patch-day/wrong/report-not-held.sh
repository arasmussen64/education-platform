# Wrong: nothing held, so the untested report tool is upgraded with the rest.
sudo apt update
sudo apt upgrade -y
sudo apt purge -y shop-theme
sudo apt install -y shop-dashboard
mkdir -p ~/report
apt list --upgradable 2>/dev/null > ~/report/waiting.txt
if [ -f /run/reboot-required ]; then echo yes > ~/report/reboot.txt; else echo no > ~/report/reboot.txt; fi
