# The reference script, written to ~/bin/drain-server. cat > FILE <<'EOF'
# writes every line up to EOF into the file (the quotes round 'EOF' keep the
# shell from touching the $ signs inside); a learner writes it with nano.
mkdir -p ~/bin
cat > ~/bin/drain-server <<'EOF'
#!/bin/bash
# drain-server NAME: takes the web server NAME out of rotation without
# cutting anyone off: drain it, wait (10 seconds at most) until its sessions
# have finished, then put it in maintenance.
name=$1

# api COMMAND: one command to HAProxy's runtime API on lb, and its answer.
api() {
  echo "$1" | on lb socat stdio /run/haproxy/admin.sock
}

# sessions: how many sessions NAME has open now (show stat's 5th field,
# scur), or nothing when HAProxy has no web server of that name.
sessions() {
  api "show stat" | awk -F, -v s="$name" '$1 == "web" && $2 == s {print $5}'
}

if [ -z "$(sessions)" ]; then
  echo "drain-server: HAProxy has no web server called '$name'" >&2
  exit 1
fi

api "set server web/$name state drain" > /dev/null
waited=0
while [ "$(sessions)" -gt 0 ] && [ "$waited" -lt 10 ]; do
  sleep 1
  waited=$((waited + 1))
done
left=$(sessions)
api "set server web/$name state maint" > /dev/null

if [ "$left" -eq 0 ]; then
  echo "$name drained in $waited s"
else
  echo "$name still had $left sessions; set to maintenance anyway"
fi
EOF
chmod +x ~/bin/drain-server
~/bin/drain-server web2
echo "set server web/web2 state ready" | on lb socat stdio /run/haproxy/admin.sock
