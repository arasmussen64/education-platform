# Drains and waits for the sessions with no limit: one visitor who never
# leaves keeps the patch waiting for ever.
mkdir -p ~/bin
cat > ~/bin/drain-server <<'EOF'
#!/bin/bash
name=$1
api() { echo "$1" | on lb socat stdio /run/haproxy/admin.sock; }
sessions() { api "show stat" | awk -F, -v s="$name" '$1 == "web" && $2 == s {print $5}'; }
if [ -z "$(sessions)" ]; then echo "drain-server: no web server called '$name'" >&2; exit 1; fi
api "set server web/$name state drain" > /dev/null
waited=0
while [ "$(sessions)" -gt 0 ]; do sleep 1; waited=$((waited + 1)); done
api "set server web/$name state maint" > /dev/null
echo "$name drained in $waited s"
EOF
chmod +x ~/bin/drain-server
