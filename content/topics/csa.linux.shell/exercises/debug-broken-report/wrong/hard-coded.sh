# Wrong: the right answers for access.log typed in by hand, so every other log
# gets the same three lines.
cat > ~/bin/report <<'EOF'
#!/usr/bin/env bash
echo "requests: 600"
echo "failed: 36"
echo "top: /home"
EOF
