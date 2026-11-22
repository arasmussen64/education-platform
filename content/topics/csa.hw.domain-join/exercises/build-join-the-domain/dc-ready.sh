#!/bin/bash
# Waits until dc1 answers, so that "dc1 has started" means "dc1 can be
# asked". Samba tells systemd it is ready as soon as its main process is
# up; its name server, its directory (LDAP) and its ticket service (the
# KDC) start answering a moment later, and on a slow machine that moment is
# seconds long. Anything that asked in the gap got nothing: SSSD, started
# at the same boot, found no domain controller, went offline and let people
# in from its cache without a ticket. lab-dc.service runs this before it
# counts as started, and SSSD starts after it. Part of the lab's scenery.
#
# It asks dc1 four real questions, once a second, for up to two minutes:
# the domain's SRV record, the directory's root, "which domain controller
# are you?" (the question a member asks to find one), and a ticket for a
# name that doesn't exist, which a working KDC refuses by name.
set -u

# Kerberos settings of this script's own, so that nothing the learner does
# to /etc/krb5.conf changes what it sees.
conf=$(mktemp)
trap 'rm -f "$conf"' EXIT
printf '[libdefaults]\n    default_realm = AD.SHOP.TEST\n[realms]\n    AD.SHOP.TEST = {\n        kdc = 10.0.9.10\n    }\n' > "$conf"

# Each answer is read into a variable and then compared. (A pipe into
# "grep -q" can stop the program on its left early, which would look like
# no answer.)
answers() {
  local reply
  reply=$(dig +short +time=1 +tries=1 @10.0.9.10 _ldap._tcp.ad.shop.test SRV 2>/dev/null)
  [[ $reply == *"dc1.ad.shop.test." ]] || { waiting="its name server"; return 1; }
  reply=$(ldapsearch -x -o nettimeout=2 -H ldap://10.0.9.10 -b '' -s base defaultNamingContext 2>/dev/null)
  [[ $reply == *"defaultNamingContext: DC=ad,DC=shop,DC=test"* ]] || { waiting="its directory"; return 1; }
  reply=$(timeout 5 samba-tool domain info 10.0.9.10 2>/dev/null)
  [[ $reply == *"dc1.ad.shop.test"* ]] || { waiting="its answer to a member looking for a domain controller"; return 1; }
  reply=$(echo x | KRB5_CONFIG="$conf" KRB5CCNAME=FILE:/dev/null timeout 5 kinit nobody-by-this-name@AD.SHOP.TEST 2>&1)
  [[ $reply == *"not found in Kerberos database"* ]] || { waiting="its ticket service"; return 1; }
}

waiting=""
for try in $(seq 1 120); do
  if answers; then
    echo "dc1 answers (asked $try time(s))"
    exit 0
  fi
  sleep 1
done
# Not an error for systemd: the lab still starts, and its checks say what
# doesn't work.
echo "dc1 still isn't answering after two minutes: no reply from $waiting"
exit 0
