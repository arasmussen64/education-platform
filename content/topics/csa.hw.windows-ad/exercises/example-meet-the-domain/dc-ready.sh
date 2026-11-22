#!/bin/bash
# Waits until dc1 answers, so that "dc1 has started" means "dc1 can be
# asked". Samba tells systemd it is ready as soon as its main process is
# up; its name server, its directory (LDAP) and its ticket service (the
# KDC) start answering a moment later, and on a slow machine that moment is
# seconds long. Whatever asked in the gap got nothing: a check run right
# after a restart, or SSSD on a member, which then goes offline and lets
# people in from its cache without a ticket. dc1's service runs this
# before it counts as started. Part of the lab's scenery.
#
# It asks dc1 four real questions, once a second, for up to a minute: the
# domain's SRV record, the directory's root, "which domain controller are
# you?" (the question a member asks to find one), and a ticket for a name
# that doesn't exist, which a working KDC refuses by name. The domain's
# name is read from dc1's own Samba settings, so this works for whatever
# domain dc1 was given.
set -u

realm=$(testparm -s --parameter-name=realm 2>/dev/null)
# No domain, nothing to wait for.
[ -n "$realm" ] || exit 0
domain=${realm,,}

# Kerberos settings of this script's own, so that nothing done to
# /etc/krb5.conf changes what it sees.
conf=$(mktemp)
trap 'rm -f "$conf"' EXIT
printf '[libdefaults]\n    default_realm = %s\n[realms]\n    %s = {\n        kdc = 10.0.9.10\n    }\n' "$realm" "$realm" > "$conf"

# Each answer is read into a variable and then compared. (A pipe into
# "grep -q" can stop the program on its left early, which would look like
# no answer.)
answers() {
  local reply
  reply=$(dig +short +time=1 +tries=1 @10.0.9.10 "_ldap._tcp.$domain" SRV 2>/dev/null)
  [[ $reply == *".$domain." ]] || { waiting="its name server"; return 1; }
  reply=$(ldapsearch -x -o nettimeout=2 -H ldap://10.0.9.10 -b '' -s base defaultNamingContext 2>/dev/null)
  [[ $reply == *"defaultNamingContext: DC="* ]] || { waiting="its directory"; return 1; }
  reply=$(timeout 5 samba-tool domain info 10.0.9.10 2>/dev/null)
  [[ $reply == *"DC name"* ]] || { waiting="its answer to a member looking for a domain controller"; return 1; }
  reply=$(echo x | KRB5_CONFIG="$conf" KRB5CCNAME=FILE:/dev/null timeout 5 kinit "nobody-by-this-name@$realm" 2>&1)
  [[ $reply == *"not found in Kerberos database"* ]] || { waiting="its ticket service"; return 1; }
}

waiting=""
for try in $(seq 1 60); do
  if answers; then
    echo "dc1 answers (asked $try time(s))"
    exit 0
  fi
  sleep 1
done
# Not an error for systemd: the lab still starts, and its checks say what
# doesn't work.
echo "dc1 still isn't answering after a minute: no reply from $waiting"
exit 0
