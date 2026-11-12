# Wrong: the ESP proposal and the clamp fixed, but vpn still calls itself
# branch.shop.test, so the provider finds no configuration for it.
on vpn sed -i 's/esp_proposals = aes256-sha1$/esp_proposals = aes256gcm16-modp2048/' /etc/swanctl/conf.d/cloud.conf
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
