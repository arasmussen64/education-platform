# The reference: three faults, found one after another, each from the
# evidence the last fix uncovers. "on vpn tee FILE << 'EOF'" writes the
# lines up to EOF into FILE on vpn, as typing them into nano would.

# 1. Phase 1: vpn calls itself branch.shop.test (an old template's
#    identity). vpn logs AUTHENTICATION_FAILED in IKE_AUTH; the provider's
#    log says "no matching peer config found" for that identity. The sheet
#    says vpn's identity is its outside address.
on vpn swanctl --list-sas
journalctl -u strongswan@vpn --no-pager -n 6 -o cat
cloud-vpn-log | grep -B 1 -A 1 'peer config'
on vpn sed -i 's/branch\.shop\.test/198.51.100.10/' /etc/swanctl/conf.d/cloud.conf
on vpn swanctl --load-all > /dev/null
sleep 3

# 2. Phase 2: now the IKE_SA is established, and the provider refuses the
#    CHILD_SA: NO_PROPOSAL_CHOSEN. Its log shows what vpn offered (AES-CBC
#    with SHA-1, no DH group) and what it takes (AES-GCM with DH group 14).
#    The sheet's ESP proposal, with its PFS group, goes back.
on vpn swanctl --list-sas
cloud-vpn-log | grep 'proposals'
on vpn sed -i 's/esp_proposals = aes256-sha1$/esp_proposals = aes256gcm16-modp2048/' /etc/swanctl/conf.d/cloud.conf
on vpn swanctl --load-all > /dev/null
for _ in $(seq 1 30); do on office curl -s -m 2 -o /dev/null http://10.20.1.10/ && break; sleep 1; done

# 3. The tunnel's MTU: the front page loads, the report hangs. The new
#    line carries 1,400 bytes and its routers send no "fragmentation
#    needed", so big segments vanish. vpn clamps the MSS only on the way out
#    of wan, where nothing from the office goes now: it leaves through vti0.
#    Clamp SYNs in both directions on vti0, to at most 1400 - 54 (ESP with
#    AES-GCM) - 40 (IPv4 and TCP) = 1306; 1300 leaves a margin. Then load
#    the file, so the running rules are the ones a boot loads.
on office curl -s -m 5 http://10.20.1.10/
on office curl -s -m 5 -o /dev/null -w '%{size_download} bytes\n' http://10.20.1.10/report.txt
on vpn tee /etc/nftables.conf > /dev/null << 'EOF'
#!/usr/sbin/nft -f
# vpn's firewall. It passes the office's traffic, and clamps the maximum
# segment size of new TCP connections so that their segments fit through
# the tunnel: 1,400 bytes on the provider's new line, less 54 for ESP with
# AES-GCM, less 40 for the IPv4 and TCP headers, is 1306 at most. Both
# directions: the office's SYNs going into the tunnel, and the cloud's
# SYN-ACKs coming out of it.
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
on office curl -s -m 10 -o /dev/null -w '%{size_download} bytes\n' http://10.20.1.10/report.txt
head -c 400000 /dev/zero | on office nc -N -w 10 10.20.1.10 9000
