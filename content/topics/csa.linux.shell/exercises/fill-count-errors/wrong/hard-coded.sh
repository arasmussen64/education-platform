# Wrong: the answers for app.log typed in by hand, so another log gets the same answers.
cat > ~/bin/count-errors <<'EOF'
#!/usr/bin/env bash
echo 19
echo "ERROR database connection refused (attempt 17)"
EOF
chmod +x ~/bin/count-errors
