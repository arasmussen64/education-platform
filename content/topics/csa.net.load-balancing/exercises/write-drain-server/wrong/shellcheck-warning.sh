# Wrong: the script drains, waits and reports as it should, but its last
# test reads $left without quotes, which ShellCheck points out (SC2086),
# and the script was left that way.
mkdir -p ~/bin
cat > ~/bin/drain-server <<'EOF'
#!/bin/bash
name=$1
api() {
  echo "$1" | on lb socat stdio /run/haproxy/admin.sock
}
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
if [ $left -eq 0 ]; then
  echo "$name drained in $waited s"
else
  echo "$name still had $left sessions; set to maintenance anyway"
fi
EOF
chmod +x ~/bin/drain-server
