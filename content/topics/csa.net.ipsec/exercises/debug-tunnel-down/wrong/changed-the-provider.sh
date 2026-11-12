# Wrong: the provider's gateway edited to accept vpn's identity and its
# old ESP proposal, instead of fixing vpn to match the sheet.
sudo sed -i 's/      id = 198.51.100.10/      id = branch.shop.test/; s/id-2 = 198.51.100.10/id-2 = branch.shop.test/; s/esp_proposals = aes256gcm16-modp2048,aes128gcm16-modp2048/esp_proposals = aes256-sha1/' /etc/netns/cloud/swanctl/conf.d/office.conf
on cloud swanctl --load-all > /dev/null
on vpn swanctl --initiate --child cloud-vti > /dev/null || true
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
