# The reference script, written in one go; in the lab you'd use nano.
mkdir -p ~/bin
cat > ~/bin/security-updates <<'EOF'
#!/bin/bash
# Installs the waiting security fixes and nothing else, then says whether
# the machine needs a reboot.
set -e
sudo apt update > /dev/null
names=$(apt list --upgradable 2>/dev/null | grep '/noble-security' | cut -d/ -f1 | tr '\n' ' ')
if [ -z "$names" ]; then
  echo "nothing to do"
  exit 0
fi
echo "security updates: $names"
sudo apt install -y --only-upgrade $names > /dev/null
if [ -f /run/reboot-required ]; then
  echo "reboot needed"
fi
EOF
chmod +x ~/bin/security-updates
~/bin/security-updates
~/bin/security-updates
apt policy shop-report
