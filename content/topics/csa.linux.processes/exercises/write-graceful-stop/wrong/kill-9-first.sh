# Wrong: KILL straight away. The process never gets to clean up, and the
# script calls that "politely".
mkdir -p ~/bin
cat > ~/bin/graceful-stop <<'EOF'
#!/usr/bin/env bash
name="$1"
pid=$(pgrep -x "$name") || { echo "$name is not running"; exit 1; }
kill -9 $pid
echo "stopped $name politely"
EOF
chmod +x ~/bin/graceful-stop
