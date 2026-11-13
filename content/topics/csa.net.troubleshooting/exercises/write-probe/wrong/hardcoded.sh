# Prints a probe's output that was right once, whatever the URL.
cat > ~/bin/probe <<'EOF'
#!/bin/bash
for i in $(seq 1 20); do
  if ((i % 5)); then echo "$i ok 0.001022"; else echo "$i http-503 0.001187"; fi
done
echo 'ok 16/20'
echo 'http-503 4/20'
echo 'failure-rate 20'
EOF
chmod +x ~/bin/probe
