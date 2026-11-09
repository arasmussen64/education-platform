# The three mistakes:
#   1. `apt upgrade` ran before `apt update`, so it worked from a stale list
#      (here, none at all) and found nothing to upgrade.
#   2. The wrong package was held: shop-agent, the one with the security fix,
#      instead of shop-report, the one that isn't tested yet.
#   3. The reboot note lives in /run/reboot-required, not /etc.
# The first run also left shop-agent held, so the fix releases it.
cat > ~/bin/nightly-patch <<'EOF'
#!/bin/bash
# The nightly patch: keep the report tool where it is (2.1 isn't tested),
# upgrade the rest, and say whether a reboot is needed.
set -e
sudo apt update
sudo apt-mark hold shop-report
sudo apt upgrade -y
if [ -f /run/reboot-required ]; then
  echo "reboot needed"
fi
EOF
sudo apt-mark unhold shop-agent
~/bin/nightly-patch
