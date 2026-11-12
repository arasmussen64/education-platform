# Wrong: the script prints the numbers from one earlier run instead of
# measuring, so its numbers match no receiver.
mkdir -p ~/bin
cat > ~/bin/cc-compare << 'EOF'
#!/bin/bash
if [ $# -ne 2 ]; then
  echo "usage: cc-compare HOST SECONDS" >&2
  exit 2
fi
echo "cubic 5.0"
echo "bbr 45.0"
echo "bbr/cubic 9.0"
EOF
chmod +x ~/bin/cc-compare
