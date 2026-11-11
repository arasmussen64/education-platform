# Wrong: the answer for the example in the prompt, typed in. It prints the
# same three lines whatever it's asked.
mkdir -p ~/bin
cat > ~/bin/arm-saving <<'EOF'
#!/bin/bash
echo "per hour: 0.0192"
echo "percent: 19.0"
echo "per month for 40: 560.64"
EOF
chmod +x ~/bin/arm-saving
