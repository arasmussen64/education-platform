#!/bin/bash
# variants.sh NAME: applies one fix (as the learner would) inside the lab.
conf=/etc/shop/api.conf
case "$1" in
  solution)
    sudo sed -i 's/^db_keepalive = off/db_keepalive = on/; s/^# db_keepalive_idle =.*/db_keepalive_idle = 10/; s/^# db_keepalive_interval =.*/db_keepalive_interval = 5/; s/^# db_keepalive_count =.*/db_keepalive_count = 3/' $conf
    sudo systemctl restart shop-api ;;
  alt-sysctl-and-switch)
    sudo sed -i 's/^db_keepalive = off/db_keepalive = on/' $conf
    echo 'net.ipv4.tcp_keepalive_time = 10' | sudo tee /etc/sysctl.d/60-keepalive.conf >/dev/null
    sudo sysctl -q -p /etc/sysctl.d/60-keepalive.conf
    sudo systemctl restart shop-api ;;
  idle-above-timeout)
    sudo sed -i 's/^db_keepalive = off/db_keepalive = on/; s/^# db_keepalive_idle =.*/db_keepalive_idle = 45/' $conf
    sudo systemctl restart shop-api ;;
  sysctl-without-switch)
    echo 'net.ipv4.tcp_keepalive_time = 10' | sudo tee /etc/sysctl.d/60-keepalive.conf >/dev/null
    sudo sysctl -q -p /etc/sysctl.d/60-keepalive.conf
    sudo systemctl restart shop-api ;;
  switch-without-idle)
    sudo sed -i 's/^db_keepalive = off/db_keepalive = on/' $conf
    sudo systemctl restart shop-api ;;
  gateway-timeout-raised)
    sudo ip netns exec nat sysctl -qw net.netfilter.nf_conntrack_tcp_timeout_established=3600 ;;
  gateway-accept-all)
    sudo ip netns exec nat nft flush chain inet gateway forward
    sudo ip netns exec nat nft add rule inet gateway forward accept ;;
  heartbeat-loop)
    sudo systemd-run --unit=heartbeat /bin/bash -c 'while sleep 10; do curl -s localhost:8080/order >/dev/null; done' ;;
  runtime-sysctl)
    sudo sed -i 's/^db_keepalive = off/db_keepalive = on/' $conf
    sudo sysctl -qw net.ipv4.tcp_keepalive_time=10
    sudo systemctl restart shop-api ;;
esac
sleep 2
