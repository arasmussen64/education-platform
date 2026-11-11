# Wrong: the lifetime is the Expires hour minus the Valid starting hour,
# leaving out the minutes and seconds. Right for the domain's whole ten
# hours; for a ticket of 3 hours 59 minutes it says 4.
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
members=$(ldapsearch -Q -LLL -Y GSSAPI -H ldap://dc1.ad.shop.test -b 'DC=ad,DC=shop,DC=test' \
    "(&(objectClass=user)(memberOf=CN=$group,CN=Users,DC=ad,DC=shop,DC=test))" sAMAccountName |
  awk '/^sAMAccountName:/ {print $2}' | sort | tr '\n' ' ')
echo "$group: ${members% }"

# 4. How long the first ticket lasts: Expires minus Valid starting.
klist | awk '/krbtgt\// {split($2, start, ":"); split($4, end, ":"); hours = end[1] - start[1]; if (hours < 0) hours += 24; print "ticket hours: " hours}'
kdestroy -q
EOF
chmod +x ~/bin/domain-report
~/bin/domain-report ldap linux-admins
~/bin/domain-report kerberos stock-team
