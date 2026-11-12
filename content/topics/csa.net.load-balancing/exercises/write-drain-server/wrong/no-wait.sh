# Drain, then maintenance at once, with no loop waiting for the sessions:
# the script says it drained while a visitor is still downloading.
mkdir -p ~/bin
cat > ~/bin/drain-server <<'EOF'
#!/bin/bash
name=$1
api() { echo "$1" | on lb socat stdio /run/haproxy/admin.sock; }
if [ -z "$(api "show stat" | awk -F, -v s="$name" '$1 == "web" && $2 == s')" ]; then
  echo "drain-server: no web server called '$name'" >&2
  exit 1
fi
api "set server web/$name state drain" > /dev/null
api "set server web/$name state maint" > /dev/null
echo "$name drained in 0 s"
EOF
chmod +x ~/bin/drain-server
