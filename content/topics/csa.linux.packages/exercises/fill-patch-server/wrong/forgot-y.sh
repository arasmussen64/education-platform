# Wrong: without -y, apt asks "Do you want to continue?", and a script
# nobody is watching gets no answer, so nothing is upgraded.
cat > ~/bin/patch-server <<'EOF'
#!/bin/bash
sudo apt update
apt list --upgradable 2>/dev/null
sudo apt-mark hold shop-report
sudo apt upgrade < /dev/null || true
if [ -f /run/reboot-required ]; then
  echo "reboot needed: $(tr '\n' ' ' < /run/reboot-required.pkgs)"
else
  echo "no reboot needed"
fi
EOF
