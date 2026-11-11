# Wrong: the members are read on dc1 itself, through on-dc and sudo,
# instead of asked of the directory with svc-report's ticket. Right today
# for the person who wrote it, who can sudo; the report it was meant to be
# signs in as svc-report and has no root on dc1.
cat > ~/bin/domain-report <<'EOF'
#!/bin/bash
# Usage: domain-report SERVICE GROUP
# A short report on the shop's domain, signed in as svc-report with its
# keytab: who offers SERVICE, whether the keytab still works, who is in
# GROUP, and how long the ticket lasts.
set -euo pipefail
service=$1
group=$2
# A ticket cache of the report's own, so the user's own tickets are left alone.
export KRB5CCNAME=FILE:/tmp/domain-report-$(id -u)

# 1. Who offers the service: the domain's SRV record for it, through this
#    machine's resolver. Its fields are priority, weight, port and host.
dig +short "_$service._tcp.ad.shop.test" SRV |
  awk -v service="$service" 'NR == 1 {sub(/\.$/, "", $4); print service ": " $4, $3}'

# 2. The keytab: can it get svc-report a ticket? If not, stop here.
if ! kinit -k -t /etc/svc-report.keytab svc-report@AD.SHOP.TEST; then
  echo "keytab: refused"
  exit 1
fi
echo "keytab: ok"

# 3. The group's members, asked of the directory with that ticket.
members=$(on-dc samba-tool group listmembers "$group" | sort | tr '\n' ' ')
echo "$group: ${members% }"

# 4. How long the first ticket lasts: Expires minus Valid starting.
line=$(klist | grep 'krbtgt/')
start=$(date -d "$(echo "$line" | awk '{print $1, $2}')" +%s)
end=$(date -d "$(echo "$line" | awk '{print $3, $4}')" +%s)
echo "ticket hours: $(( (end - start) / 3600 ))"
kdestroy -q
EOF
chmod +x ~/bin/domain-report
~/bin/domain-report ldap linux-admins
~/bin/domain-report kerberos stock-team
