#!/bin/bash
# Usage: try-fault.sh NAME SED-EXPR   (applies the sed to the lab's cloud.conf, re-initiates, prints both logs)
name=$1; expr=$2
cp /etc/swanctl/conf.d/cloud.conf /root/cloud.conf.good 2>/dev/null || true
cp /root/cloud.conf.good /etc/swanctl/conf.d/cloud.conf
swanctl --terminate --ike cloud --timeout 5 >/dev/null 2>&1
sed -i "$expr" /etc/swanctl/conf.d/cloud.conf
sleep 1
since=$(date '+%Y-%m-%d %H:%M:%S')
swanctl --load-all --noprompt >/dev/null 2>&1
swanctl --initiate --child cloud-vti --timeout 8 > /root/initiate-$name.txt 2>&1
sleep 2
echo "===== $name: lab (journalctl -u strongswan)"
journalctl -u strongswan --since "$since" --no-pager -o short | grep -v swanctl | sed 's/^.*charon-systemd\[[0-9]*\]: //' | head -40
echo "===== $name: cloud (journalctl -u lab-cloud)"
journalctl -u lab-cloud --since "$since" --no-pager -o short | sed 's/^.*charon-systemd\[[0-9]*\]: //' | head -40
echo "===== $name: swanctl --initiate said"; tail -5 /root/initiate-$name.txt
cp /root/cloud.conf.good /etc/swanctl/conf.d/cloud.conf
