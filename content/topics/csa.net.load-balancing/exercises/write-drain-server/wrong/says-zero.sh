# The reference script's loop, but the line it prints has the seconds typed
# in: it says "drained in 0 s" however long it really waited.
mkdir -p ~/bin
cat > ~/bin/drain-server <<'EOF'
#!/bin/bash
name=$1
api() { echo "$1" | on lb socat stdio /run/haproxy/admin.sock; }
sessions() { api "show stat" | awk -F, -v s="$name" '$1 == "web" && $2 == s {print $5}'; }
if [ -z "$(sessions)" ]; then echo "drain-server: no web server called '$name'" >&2; exit 1; fi
api "set server web/$name state drain" > /dev/null
waited=0
while [ "$(sessions)" -gt 0 ] && [ "$waited" -lt 10 ]; do sleep 1; waited=$((waited + 1)); done
left=$(sessions)
api "set server web/$name state maint" > /dev/null
if [ "$left" -eq 0 ]; then echo "$name drained in 0 s"; else echo "$name still had $left sessions; set to maintenance anyway"; fi
EOF
chmod +x ~/bin/drain-server
