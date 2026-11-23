#!/bin/bash
# The three fixes, each at its cause.
set -e
# 1. The redirect address registered for the orders site had a typo.
# 2. The access token named an audience the stock API isn't.
sudo sed -i -e 's|/oidc/callbak"|/oidc/callback"|' -e 's|https://apis.shop.test|https://api.shop.test|' \
  /etc/netns/idp/keycloak/realms/shop.json
sudo realm-apply shop
# 3. The orders server's clock ran eight minutes fast: its time sync was
#    asking a time server whose name no longer exists.
sudo sed -i 's|time-old.shop.test|time.shop.test|' /etc/netns/app/chrony/chrony.conf
# If that restart fails, say why. (On a GitHub runner it failed and this PC
# never showed it: the next run prints the two services' own words, and any
# AppArmor refusals, so the cause can be read in CI's log.)
if ! sudo systemctl restart timesync@app; then
  {
    echo "--- systemctl status"
    sudo systemctl status timesync@app chrony@ntp --no-pager -l || true
    echo "--- journal"
    sudo journalctl -u timesync@app -u chrony@ntp -u machine-clocks -n 60 --no-pager || true
    echo "--- by hand"
    sudo ip netns exec app /usr/local/lib/netlab/lab-enter app /usr/local/lib/idlab/timesync --check || true
    sudo ip netns exec app /usr/local/lib/netlab/lab-enter app /usr/local/lib/idlab/timesync --settle 2; echo "settle exit: $?"
    echo "--- apparmor"
    sudo dmesg 2>/dev/null | grep -i -E "apparmor|audit" | tail -15 || true
    cat /sys/module/apparmor/parameters/enabled 2>/dev/null || true
  } >&2
  exit 1
fi
