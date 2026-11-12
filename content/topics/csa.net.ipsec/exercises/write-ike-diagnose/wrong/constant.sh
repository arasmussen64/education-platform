# Wrong: always "up".
cat > ~/bin/ike-diagnose << 'EOF'
#!/bin/bash
echo up
EOF
chmod +x ~/bin/ike-diagnose
