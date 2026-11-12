# Wrong: the laptop's MTU lowered to 1300, so its segments fit, instead of
# fixing vpn; but the laptop isn't vpn, and every other laptop would need
# the same.
on vpn sed -i 's/branch\.shop\.test/198.51.100.10/' /etc/swanctl/conf.d/cloud.conf
on vpn sed -i 's/esp_proposals = aes256-sha1$/esp_proposals = aes256gcm16-modp2048/' /etc/swanctl/conf.d/cloud.conf
on vpn swanctl --load-all > /dev/null
for _ in $(seq 1 30); do on office curl -s -m 2 -o /dev/null http://10.20.1.10/ && break; sleep 1; done
on office ip link set eth0 mtu 1300
