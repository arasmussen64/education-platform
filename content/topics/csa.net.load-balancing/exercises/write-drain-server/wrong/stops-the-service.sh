# Drains, then stops the server's program to end its sessions quickly: the
# visitor's download is cut off.
mkdir -p ~/bin
cat > ~/bin/drain-server <<'EOF'
#!/bin/bash
name=$1
api() { echo "$1" | on lb socat stdio /run/haproxy/admin.sock; }
sessions() { api "show stat" | awk -F, -v s="$name" '$1 == "web" && $2 == s {print $5}'; }
if [ -z "$(sessions)" ]; then echo "drain-server: no web server called '$name'" >&2; exit 1; fi
api "set server web/$name state drain" > /dev/null
sudo systemctl stop "shop-web@$name"
waited=0
while [ "$(sessions)" -gt 0 ] && [ "$waited" -lt 10 ]; do sleep 1; waited=$((waited + 1)); done
api "set server web/$name state maint" > /dev/null
sudo systemctl start "shop-web@$name"
echo "$name drained in $waited s"
EOF
chmod +x ~/bin/drain-server
