# Straight to maintenance, no drain and no waiting: a sticky visitor is sent
# elsewhere mid-visit, and the script returns while downloads still run.
mkdir -p ~/bin
cat > ~/bin/drain-server <<'EOF'
#!/bin/bash
name=$1
api() { echo "$1" | on lb socat stdio /run/haproxy/admin.sock; }
if [ -z "$(api "show stat" | awk -F, -v s="$name" '$1 == "web" && $2 == s')" ]; then
  echo "drain-server: no web server called '$name'" >&2
  exit 1
fi
api "set server web/$name state maint" > /dev/null
echo "$name drained in 0 s"
EOF
chmod +x ~/bin/drain-server
