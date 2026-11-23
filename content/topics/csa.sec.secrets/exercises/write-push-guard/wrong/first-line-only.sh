# Wrong: the hook reads one line and scans that. A push that brings two
# branches gets the second one through unread.
cat > /etc/gitleaks/server.toml << 'EOF'
title = "The shop's git server"

[extend]
useDefault = true

[[rules]]
id = "paygate-key"
description = "A payment gateway API key"
regex = '''pg_live_[A-Za-z0-9]{32}'''

[allowlist]
description = "Test fixtures may hold key-shaped values"
paths = ['''^tests/fixtures/''']
EOF

cat > /srv/git/shop.git/hooks/pre-receive << 'EOF'
zero=0000000000000000000000000000000000000000
status=0
read -r old new ref
for line in one; do
  # A deleted branch brings no commits.
  [ "$new" = "$zero" ] && continue
  if [ "$old" = "$zero" ]; then
    # A new branch: the commits no branch here has yet.
    range="$new --not --all"
  else
    range="$old..$new"
  fi
  if ! gitleaks detect --no-banner --redact -v --source . \
    --config /etc/gitleaks/server.toml --log-opts="$range"; then
    echo "Refused: a commit pushed to $ref adds a secret (above: the rule and the commit)."
    echo "Revoke that secret now, then take the commit out of your branch and push again."
    status=1
  fi
done
exit $status
EOF
chmod +x /srv/git/shop.git/hooks/pre-receive
