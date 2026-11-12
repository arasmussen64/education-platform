# Wrong: both directions clamped, but to 1460, which an Ethernet link's
# MSS already is: nothing changes, and big segments still vanish.
on vpn sed -i 's/branch\.shop\.test/198.51.100.10/' /etc/swanctl/conf.d/cloud.conf
on vpn sed -i 's/esp_proposals = aes256-sha1$/esp_proposals = aes256gcm16-modp2048/' /etc/swanctl/conf.d/cloud.conf
on vpn swanctl --load-all > /dev/null
for _ in $(seq 1 30); do on office curl -s -m 2 -o /dev/null http://10.20.1.10/ && break; sleep 1; done
on vpn tee /etc/nftables.conf > /dev/null << 'EOF'
#!/usr/sbin/nft -f
flush ruleset
table inet filter {
    chain forward {
        type filter hook forward priority filter; policy accept;
        oifname "vti0" tcp flags syn tcp option maxseg size set 1460
        iifname "vti0" tcp flags syn tcp option maxseg size set 1460
    }
}
EOF
sudo systemctl reload nftables@vpn
