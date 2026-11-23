# Wrong: when the pushed commit carries a .gitleaks.toml, the hook
# scans with that file ("the repository knows its own exceptions"), so
# whoever pushes decides what the server lets through.
cat > /etc/gitleaks/server.toml << 'EOF'
title = "The shop's git server"

[extend]
useDefault = true

[[rules]]
id = "paygate-key"
description = "A payment gateway API key"
regex = '''pg_live_[A-Za-z0-9]{32}'''

[allowlist]
paths = ['''^tests/fixtures/''']
EOF
cat > /srv/git/shop.git/hooks/pre-receive << 'EOF'
#!/bin/bash
zero=0000000000000000000000000000000000000000
status=0
while read -r old new ref; do
  [ "$new" = "$zero" ] && continue
  if [ "$old" = "$zero" ]; then
    range="$new --not --all"
  else
    range="$old..$new"
  fi
  config=/etc/gitleaks/server.toml
  if git cat-file -e "$new:.gitleaks.toml" 2> /dev/null; then
    config=$(mktemp --suffix=.toml)
    git show "$new:.gitleaks.toml" > "$config"
  fi
  if ! gitleaks detect --no-banner --redact -v --source . \
    --config "$config" --log-opts="$range"; then
    echo "Refused: a commit pushed to $ref adds a secret."
    status=1
  fi
done
exit $status
EOF
chmod +x /srv/git/shop.git/hooks/pre-receive
