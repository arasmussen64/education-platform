# The finished script, then one run of it. In the lab you'd fill the gaps
# with nano; here `cat > FILE <<'EOF'` writes the whole file in one go:
# everything up to the line EOF goes into the file as it is.
#   realm list --name-only:  the domains this machine belongs to, by name
#   realm join:              joins it, asking for the administrator's password
#   --enable mkhomedir:      the login step that makes a home directory
#   realm permit -g:         permits a group (-g) rather than one person
cat > ~/bin/join-this-server <<'EOF'
#!/bin/bash
# Usage: join-this-server
# Makes this server a member of the shop's domain, ad.shop.test, the way
# every new server is set up: joined with the domain administrator's
# account, a home directory made at each person's first login, and only
# the domain group linux-admins allowed to log in. It is run when a server
# is built, and again whenever someone isn't sure it was, so running it a
# second time must change nothing.
set -euo pipefail

domain=ad.shop.test
group=linux-admins@ad.shop.test

# Four values are gaps, written as three underscores in a row. Stop before
# anything changes if one is still unfilled.
if grep -q '_\{3\}' "$0"; then
  echo "join-this-server: fill in every gap first" >&2
  exit 1
fi

# 1. Join, unless this machine is a member already. The first gap asks
#    realm for the name of each domain this machine belongs to, one a line
#    (--name-only), which prints nothing at all before it has been joined.
if realm list --name-only | grep -qx "$domain"; then
  echo "join-this-server: already a member of $domain"
else
  # realm asks for the administrator's password.
  sudo realm join -U Administrator "$domain"
fi

# 2. A home directory made at each person's first login.
sudo pam-auth-update --enable mkhomedir

# 3. Only the group may log in, by any way into the machine.
sudo realm permit -g "$group"

realm list
EOF
# The password goes in on standard input only so this file can run by
# itself: in the lab, run ~/bin/join-this-server and type it when asked.
echo 'Shop-Admin-1' | ~/bin/join-this-server
# Run it again: it says it's already a member, and changes nothing.
~/bin/join-this-server
