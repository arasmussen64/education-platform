# Wrong: installs the fixes but never says the kernel needs a reboot, so the
# fix isn't actually running.
mkdir -p ~/bin
cat > ~/bin/security-updates <<'EOF'
#!/bin/bash
set -e
sudo apt update > /dev/null
names=$(apt list --upgradable 2>/dev/null | grep '/noble-security' | cut -d/ -f1 | tr '\n' ' ')
if [ -z "$names" ]; then
  echo "nothing to do"
  exit 0
fi
echo "security updates: $names"
sudo apt install -y --only-upgrade $names > /dev/null
EOF
chmod +x ~/bin/security-updates
