# Wrong: never refreshes the list, so on this server it finds nothing waiting.
mkdir -p ~/bin
cat > ~/bin/security-updates <<'EOF'
#!/bin/bash
set -e
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
