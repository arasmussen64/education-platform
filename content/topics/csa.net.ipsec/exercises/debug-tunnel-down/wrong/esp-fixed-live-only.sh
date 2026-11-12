# Wrong: the identity and the clamp fixed in vpn's files, but the ESP
# proposal fixed only in the running charon, from a corrected copy loaded
# by hand (swanctl --load-conns --file). The file still says aes256-sha1,
# so the next boot brings back the old phase 2 failure.
on vpn sed -i 's/branch\.shop\.test/198.51.100.10/' /etc/swanctl/conf.d/cloud.conf
on vpn sed 's/esp_proposals = aes256-sha1$/esp_proposals = aes256gcm16-modp2048/' /etc/swanctl/conf.d/cloud.conf > /tmp/cloud-fixed.conf
on vpn swanctl --load-all > /dev/null
on vpn swanctl --load-conns --file /tmp/cloud-fixed.conf > /dev/null
rm -f /tmp/cloud-fixed.conf
on vpn swanctl --terminate --ike cloud > /dev/null 2>&1 || true
on vpn swanctl --initiate --child cloud-vti > /dev/null 2>&1 || true
for _ in $(seq 1 30); do on office curl -s -m 2 -o /dev/null http://10.20.1.10/ && break; sleep 1; done
on vpn tee /etc/nftables.conf > /dev/null << 'EOF'
#!/usr/sbin/nft -f
flush ruleset
table inet filter {
    chain forward {
        type filter hook forward priority filter; policy accept;
        oifname "vti0" tcp flags syn tcp option maxseg size set 1300
        iifname "vti0" tcp flags syn tcp option maxseg size set 1300
    }
}
EOF
sudo systemctl reload nftables@vpn
