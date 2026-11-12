# Wrong: only nc's exit status: open if it connected, refused otherwise.
# No layer 2 test, and no timing.
mkdir -p ~/bin
cat > ~/bin/why-not <<'EOF'
#!/bin/bash
host=$1
port=$2
if nc -z -w 2 "$host" "$port" 2> /dev/null; then
  echo open
else
  echo refused
fi
EOF
chmod +x ~/bin/why-not
