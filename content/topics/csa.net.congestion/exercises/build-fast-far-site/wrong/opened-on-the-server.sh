# Wrong: BBR is set properly, and UDP 443 is let in by a new firewall on
# shop itself, but fw, the firewall in front of it, still drops it. Every
# firewall on the path has to let HTTP/3 through.
echo 'net.ipv4.tcp_congestion_control = bbr' | on shop tee /etc/sysctl.d/60-bbr.conf > /dev/null
on shop sysctl -p /etc/sysctl.d/60-bbr.conf
on shop tee /etc/nftables.conf > /dev/null << 'EOF'
#!/usr/sbin/nft -f
flush ruleset

table inet filter {
    chain input {
        type filter hook input priority filter; policy drop;
        iif lo accept
        ct state established,related accept
        tcp dport { 22, 80, 443 } accept
        udp dport 443 accept
    }
}
EOF
sudo systemctl enable --now nftables@shop
