#!/bin/bash
# WRONG: the other two faults are mended; the database's firewall is as it
# was.
# The reference repair. A learner makes these edits in nano; this makes
# them with sed (-i changes the file in place; "s/OLD/NEW/" swaps OLD for
# NEW on each line that has it) and writes the database's firewall whole
# with "on db tee FILE <<'EOF'", which puts everything up to the line EOF
# into FILE as typed.
set -e

# 1. nginx asked each device for a certificate without checking who signed
#    it (optional_no_ca), and payroll turned away only a device that showed
#    none. Now only the shop's device CA counts, and payroll wants SUCCESS.
on zt sed -i 's/ssl_verify_client optional_no_ca;/ssl_verify_client optional;/' /etc/nginx/sites-enabled/default
on zt sed -i 's/if (\$ssl_client_verify = NONE) {/if ($ssl_client_verify != SUCCESS) {/' /etc/nginx/sites-enabled/default

# 2. nginx uses the longest location that matches an address, so
#    /payroll/api/ had a policy of its own, and it asked for staff. It asks
#    for hr now, as the rest of payroll does.
on zt sed -i '/location \/payroll\/api\/ {/,/^    }/ s|auth_request /decide/staff;|auth_request /decide/hr;|' /etc/nginx/sites-enabled/default
on zt nginx -t
sudo systemctl reload nginx@zt

# 3. The database accepted its port from the whole apps network. It
#    accepts payroll's address alone now.
on db tee /etc/nftables.conf > /dev/null <<'EOF'
#!/usr/sbin/nft -f
# db: payroll's database. It answers payroll alone, and starts no
# connections of its own.
flush ruleset

table inet filter {
  chain input {
    type filter hook input priority filter; policy drop;
    ct state established,related accept
    iifname "lo" accept
    ip saddr 10.20.0.0/24 tcp dport 5432 accept
  }
  chain output {
    type filter hook output priority filter; policy drop;
    ct state established,related accept
    oifname "lo" accept
  }
}
EOF
sudo systemctl restart nftables@db
