# The server's settings, then the hook.
# (cat > FILE << 'EOF' writes the lines up to EOF into FILE, as they are.)

# The built-in rules, the shop's own rule, and the one allowed path.
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

# The hook. For each branch in the push it works out which commits are
# new to the server and has gitleaks scan exactly those, with the
# server's settings. gitleaks reads the repository it is run in, a bare
# one, so a .gitleaks.toml inside a pushed commit is only a file in a
# commit: nobody reads it as settings.
cat > /srv/git/shop.git/hooks/pre-receive << 'EOF'
#!/bin/bash
# pre-receive: refuses a push when any commit it brings adds a secret.
zero=0000000000000000000000000000000000000000
status=0
while read -r old new ref; do
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

# Try it: a clean commit goes through, a commit with a key-shaped value
# doesn't. ("|| true": the second push is meant to fail.)
cd ~/shop
echo "Orders ship within a day." >> README.md
git commit -q -am "Say when orders ship"
git push origin main
echo "charge with pg_live_$(openssl rand -hex 16)" > notes.txt
git add notes.txt
git commit -q -m "Notes"
git push origin main || true
git reset -q --hard origin/main
