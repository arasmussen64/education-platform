# Wrong: counts the lines and says ok.
cat > ~/bin/chain-verify << 'EOF'
#!/bin/bash
echo "ok $(wc -l < "$1")"
EOF
chmod +x ~/bin/chain-verify
