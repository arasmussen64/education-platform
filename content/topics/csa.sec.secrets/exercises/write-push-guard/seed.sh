#!/bin/bash
# Builds the lab's scenery while the image is built: the shop's git server
# (a bare repository in /srv/git/shop.git that the learner may push to and
# whose hooks folder is theirs), a clone of it in ~/shop to try pushes
# from, and an empty /etc/gitleaks for the server's scanner settings.
# Nothing here is random, and nothing here is a secret: the one key-shaped
# value is a made-up test fixture, put together from pieces so that the
# text of this file isn't itself a finding for a scanner.
set -euo pipefail

export HOME=/root
git config --global init.defaultBranch main

# The people who may push are in the group "git"; the repository's files
# stay writable by the group whoever pushes (--shared=group).
groupadd git
usermod -aG git learner
install -d -o root -g git -m 2775 /srv/git
git init -q --bare --shared=group /srv/git/shop.git

# The repository's first three commits, made in a scratch clone and pushed.
# The dates are fixed, so the commits are the same in every build.
work=$(mktemp -d)
git clone -q /srv/git/shop.git "$work/shop" 2> /dev/null
cd "$work/shop"
git config user.name "Sam Okafor"
git config user.email "sam@shop.test"

commit() {
  local day=$1 message=$2
  git add -A
  GIT_AUTHOR_DATE="2026-04-$day 09:30:00 +0000" GIT_COMMITTER_DATE="2026-04-$day 09:30:00 +0000" \
    git commit -q -m "$message"
}

printf '# shop\n\nThe shop'"'"'s order service.\n' > README.md
commit 06 "Start the order service"

mkdir -p app
cat > app/charge.sh << 'EOF'
#!/bin/bash
# Charges one order at the payment gateway. The key is read from a file
# that only this service's user can read; it is never in this repository.
key_file=${PAYGATE_KEY_FILE:-/etc/shop/paygate.key}
curl -s -H @<(printf 'Authorization: Bearer %s' "$(cat "$key_file")") \
  -d "order=$1" http://127.0.0.1:9440/charges
EOF
commit 07 "Charge orders at the payment gateway"

# A test fixture: a key in the gateway's format that was never anyone's.
mkdir -p tests/fixtures
fake="pg_""live_""TESTONLY00""TESTONLY00""TESTONLY0000"
printf '# Not a real key: the tests only need something key-shaped.\npaygate_key = %s\n' "$fake" \
  > tests/fixtures/paygate.conf
commit 08 "Add a fixture for the charge tests"

git push -q origin main
cd /
rm -rf "$work"
chgrp -R git /srv/git/shop.git
chmod -R g+rwX /srv/git/shop.git
# The hooks folder: the learner writes pre-receive here.
chown -R learner:git /srv/git/shop.git/hooks
rm -f /srv/git/shop.git/hooks/*.sample

# git refuses to read a repository that belongs to another user unless it
# is told the repository is trusted. This one is the server's own.
git config --system --add safe.directory /srv/git/shop.git

# The learner's own clone, to try pushes from.
runuser -u learner -- env HOME=/home/learner git clone -q /srv/git/shop.git /home/learner/shop
runuser -u learner -- env HOME=/home/learner git -C /home/learner/shop config user.name "Learner"
runuser -u learner -- env HOME=/home/learner git -C /home/learner/shop config user.email "learner@shop.test"

# Where the server's own scanner settings go. The learner writes
# server.toml here.
install -d -o learner -g git -m 775 /etc/gitleaks
