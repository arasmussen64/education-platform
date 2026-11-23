# Wrong: the hook never looks for a deleted branch, hands gitleaks a
# range that ends in 40 zeros, and refuses when the scan fails: nobody
# can delete a branch any more.
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
  if [ "$old" = "$zero" ]; then
    range="$new --not --all"
  else
    range="$old..$new"
  fi
  if ! gitleaks detect --no-banner --redact -v --source . \
    --config /etc/gitleaks/server.toml --log-opts="$range"; then
    echo "Refused: a commit pushed to $ref adds a secret."
    status=1
  fi
done
exit $status
EOF
chmod +x /srv/git/shop.git/hooks/pre-receive
