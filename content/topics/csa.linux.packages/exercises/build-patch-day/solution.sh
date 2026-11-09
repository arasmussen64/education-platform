# 1. Refresh and look. Two of the three waiting updates are from noble-security.
sudo apt update
apt list --upgradable

# 2. Keep the report tool back, then upgrade the rest.
sudo apt-mark hold shop-report
sudo apt upgrade -y

# 3. Remove the theme and its configuration: purge, not remove.
sudo apt purge -y shop-theme

# 4. The dashboard.
sudo apt install -y shop-dashboard

# 5. The report: what's still waiting, and whether the machine wants a reboot.
mkdir -p ~/report
apt list --upgradable 2>/dev/null > ~/report/waiting.txt
if [ -f /run/reboot-required ]; then echo yes > ~/report/reboot.txt; else echo no > ~/report/reboot.txt; fi
cat ~/report/waiting.txt ~/report/reboot.txt
