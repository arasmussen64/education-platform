# Wrong: the jobs run one after another, so the night takes three times as long.
mkdir -p ~/bin
cat > ~/bin/nightly <<'EOF'
#!/usr/bin/env bash
trap 'echo "nightly interrupted" >&2; exit 1' TERM INT
status=0
for name in backup report cleanup; do
  if "/srv/jobs/$name.sh" > /dev/null; then
    echo "$name: ok"
  else
    echo "$name: failed (status $?)"
    status=1
  fi
done
exit "$status"
EOF
chmod +x ~/bin/nightly
