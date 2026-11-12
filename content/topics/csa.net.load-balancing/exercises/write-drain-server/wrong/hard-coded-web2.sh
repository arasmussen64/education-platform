# The reference script with the server's name typed in: it drains web2,
# whatever name it is given.
mkdir -p ~/bin
cat > ~/bin/drain-server <<'EOF'
#!/bin/bash
name=web2
api() { echo "$1" | on lb socat stdio /run/haproxy/admin.sock; }
sessions() { api "show stat" | awk -F, -v s="$name" '$1 == "web" && $2 == s {print $5}'; }
case $1 in web1 | web2 | web3) ;; *) echo "drain-server: no web server called '$1'" >&2; exit 1 ;; esac
api "set server web/$name state drain" > /dev/null
waited=0
while [ "$(sessions)" -gt 0 ] && [ "$waited" -lt 10 ]; do sleep 1; waited=$((waited + 1)); done
left=$(sessions)
api "set server web/$name state maint" > /dev/null
if [ "$left" -eq 0 ]; then echo "$1 drained in $waited s"; else echo "$1 still had $left sessions; set to maintenance anyway"; fi
EOF
chmod +x ~/bin/drain-server
