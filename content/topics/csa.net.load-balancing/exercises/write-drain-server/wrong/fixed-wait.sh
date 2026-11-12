# Drains, then always waits the whole 10 seconds before it looks at the
# sessions, with no loop: a server with nobody on it waits as long as a busy
# one, and the patch night takes far longer than it needs.
mkdir -p ~/bin
cat > ~/bin/drain-server <<'EOF'
#!/bin/bash
name=$1
api() { echo "$1" | on lb socat stdio /run/haproxy/admin.sock; }
sessions() { api "show stat" | awk -F, -v s="$name" '$1 == "web" && $2 == s {print $5}'; }
if [ -z "$(sessions)" ]; then echo "drain-server: no web server called '$name'" >&2; exit 1; fi
api "set server web/$name state drain" > /dev/null
sleep 10
left=$(sessions)
api "set server web/$name state maint" > /dev/null
if [ "$left" -eq 0 ]; then echo "$name drained in 10 s"; else echo "$name still had $left sessions; set to maintenance anyway"; fi
EOF
chmod +x ~/bin/drain-server
