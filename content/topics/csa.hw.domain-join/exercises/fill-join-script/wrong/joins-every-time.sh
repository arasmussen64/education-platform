# Wrong: the script joins every time it runs, without asking first
# whether this machine is a member already. The first run works; a
# second stops at "realm: Already joined to this domain", and with
# set -e nothing after it runs.
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
# realm asks for the administrator's password.
sudo realm join -U Administrator "$domain"

# 2. A home directory made at each person's first login.
sudo pam-auth-update --enable mkhomedir

# 3. Only the group may log in, by any way into the machine.
sudo realm permit -g "$group"

realm list
EOF
# The password goes in on standard input only so this file can run by
# itself: in the lab, run ~/bin/join-this-server and type it when asked.
echo 'Shop-Admin-1' | ~/bin/join-this-server
