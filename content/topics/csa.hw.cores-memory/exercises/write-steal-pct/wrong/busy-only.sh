# Wrong: steal as a share of the busy time only (user, system and steal),
# leaving idle out of the total. On a VM that is idle apart from being
# robbed, that comes out near 100%, though most of the time was idle.
mkdir -p ~/bin
cat > ~/bin/steal-pct <<'EOF'
#!/bin/bash
if [ $# -ne 2 ]; then
  echo "Usage: steal-pct BEFORE AFTER" >&2
  exit 2
fi
paste "$1" "$2" | awk '{
  user = $13 - $2; sys = $15 - $4; steal = $20 - $9
  printf "%.1f\n", steal * 100 / (user + sys + steal)
}'
EOF
chmod +x ~/bin/steal-pct
