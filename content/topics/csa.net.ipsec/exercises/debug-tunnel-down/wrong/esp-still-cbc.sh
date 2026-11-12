# Wrong: the identity and the clamp fixed, but the ESP proposal is still
# the old template's AES-CBC with SHA-1, which the provider refuses.
on vpn sed -i 's/branch\.shop\.test/198.51.100.10/' /etc/swanctl/conf.d/cloud.conf
on vpn swanctl --load-all > /dev/null
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
sleep 5
