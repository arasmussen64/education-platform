# Wrong: the report tool isn't held, so the untested 2.1 goes in with the rest.
cat > ~/bin/patch-server <<'EOF'
#!/bin/bash
set -e
sudo apt update
apt list --upgradable 2>/dev/null
sudo apt-mark showhold
sudo apt upgrade -y
if [ -f /run/reboot-required ]; then
  echo "reboot needed: $(tr '\n' ' ' < /run/reboot-required.pkgs)"
else
  echo "no reboot needed"
fi
EOF
