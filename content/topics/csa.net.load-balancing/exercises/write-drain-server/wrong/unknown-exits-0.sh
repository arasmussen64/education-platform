# The reference script, but an unknown name only gets a message on stdout
# and exit status 0, so a caller can't tell it failed.
mkdir -p ~/bin
cat > ~/bin/drain-server <<'EOF'
#!/bin/bash
name=$1
api() { echo "$1" | on lb socat stdio /run/haproxy/admin.sock; }
sessions() { api "show stat" | awk -F, -v s="$name" '$1 == "web" && $2 == s {print $5}'; }
if [ -z "$(sessions)" ]; then echo "drain-server: no web server called '$name'"; exit 0; fi
api "set server web/$name state drain" > /dev/null
waited=0
while [ "$(sessions)" -gt 0 ] && [ "$waited" -lt 10 ]; do sleep 1; waited=$((waited + 1)); done
left=$(sessions)
api "set server web/$name state maint" > /dev/null
if [ "$left" -eq 0 ]; then echo "$name drained in $waited s"; else echo "$name still had $left sessions; set to maintenance anyway"; fi
EOF
chmod +x ~/bin/drain-server
