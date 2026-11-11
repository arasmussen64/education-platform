# Wrong: the laptop capture's four answers typed in, whatever folder the
# script is given.
cat > ~/bin/under-me <<'EOF'
#!/bin/bash
echo "vendor: Microsoft"
echo "vm: microsoft"
echo "nics: none"
echo "disks: sd"
EOF
