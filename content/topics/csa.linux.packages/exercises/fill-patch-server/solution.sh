# The finished script. In the lab you'd fill the four gaps with nano; here
# it's written in one go.
cat > ~/bin/patch-server <<'EOF'
#!/bin/bash
# Patches this server the careful way: refresh the list, show what's
# waiting, keep the report tool where it is (2.1 isn't tested yet), upgrade
# everything else, and say whether a reboot is needed.
set -e
sudo apt update
apt list --upgradable 2>/dev/null
sudo apt-mark hold shop-report
sudo apt upgrade -y
if [ -f /run/reboot-required ]; then
  echo "reboot needed: $(tr '\n' ' ' < /run/reboot-required.pkgs)"
else
  echo "no reboot needed"
fi
EOF
~/bin/patch-server
apt policy shop-report
