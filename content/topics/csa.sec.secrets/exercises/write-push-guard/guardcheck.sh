# guardcheck.sh: the trial behind the checks of the push-guard lab.
# A check starts with:   . /usr/local/lib/lab/guardcheck.sh
# and asks for one finding:   guard_finding buried-refused
#
# The trial copies the shop's bare repository, with the learner's
# pre-receive hook in it, into a folder of its own, clones the copy as the
# learner and pushes to it: clean commits, and commits that hold secrets
# made up on the spot, in formats a scanner finds by their shape (a cloud
# access key ID, a code-hosting token, a private key, the payment
# gateway's own key). The hook reads the server's settings where the
# learner wrote them, /etc/gitleaks/server.toml. Nothing of the learner's
# is changed: the real repository never receives a push.
#
# All eight checks ask about one hook and one settings file, so the trial
# runs once for the eight: its findings are kept for a minute in
# /run/lab-guard, under the checksum of the two files. A changed file, or
# a minute gone by, means a new trial.
. /usr/local/lib/lab/checklib-sec.sh

server=/srv/git/shop.git
hook=$server/hooks/pre-receive
settings=/etc/gitleaks/server.toml
findings=/run/lab-guard

# note ASPECT TEXT: the trial's finding for one check; the first one said
# for an aspect is the one that counts.
note() {
  grep "^$1: " "$findings.new" > /dev/null 2>&1 || echo "$1: $2" >> "$findings.new"
}

all_aspects() {
  local aspect
  for aspect in clean-accepted secret-refused buried-refused new-branch fixtures-only own-rule pushed-config-ignored no-secret-printed; do
    note "$aspect" "$1"
  done
}

# pick ALPHABET COUNT: COUNT characters drawn at random from ALPHABET.
pick() {
  python3 -c 'import secrets, sys
print("".join(secrets.choice(sys.argv[1]) for _ in range(int(sys.argv[2]))))' "$1" "$2"
}

upper=ABCDEFGHIJKLMNOPQRSTUVWXYZ
lower=abcdefghijklmnopqrstuvwxyz
digits=0123456789

run_trial() {
  local work clone aws hub pem pay pay2 pay3 odd n before added

  : > "$findings.new"
  chmod 600 "$findings.new"
  [ -x "$hook" ] || {
    all_aspects "$hook is missing, or isn't executable"
    return
  }
  [ -s "$settings" ] || {
    all_aspects "there is no $settings"
    return
  }

  work=$(mktemp -d /var/tmp/guard-check.XXXXXX)
  # shellcheck disable=SC2064
  trap "rm -rf '$work'" EXIT
  cp -a "$server" "$work/server.git"
  chown -R learner:learner "$work"
  clone=$work/clone

  # as_learner COMMAND...: in the clone, as the learner, stopped after 20
  # seconds.
  as_learner() {
    (cd "$clone" && runuser -u learner -- env HOME=/home/learner timeout 20 "$@")
  }
  # put PATH: standard input as that file in the clone, written by the
  # learner (a file of root's there couldn't be cleaned away again).
  # put -a PATH adds to the file.
  put() {
    local how='>'
    if [ "$1" = -a ]; then
      how='>>'
      shift
    fi
    as_learner bash -c 'mkdir -p "$(dirname "$1")" && cat '"$how"' "$1"' _ "$1"
  }
  # commit MESSAGE: everything in the clone, as one commit.
  commit() {
    as_learner git add -A
    as_learner git commit -q -m "$1"
  }
  # push REF...: pushes to the copy. The output of every push is kept, in
  # push.N, for the last check. True when the server took it.
  n=0
  push() {
    n=$((n + 1))
    as_learner git push origin "$@" > "$work/push.$n" 2>&1
  }
  # at_server REF: the commit REF names in the copy, or nothing.
  at_server() {
    git -C "$work/server.git" rev-parse -q --verify "refs/heads/$1" 2> /dev/null
  }
  # back: the clone as the server's main is, on main.
  back() {
    as_learner git checkout -q -f main
    as_learner git reset -q --hard origin/main
    as_learner git clean -q -fdx
  }

  (cd "$work" && runuser -u learner -- env HOME=/home/learner git clone -q "$work/server.git" clone) 2> /dev/null || {
    all_aspects "the check couldn't clone a copy of the repository"
    return
  }
  as_learner git config user.name "Check"
  as_learner git config user.email "check@shop.test"

  # The secrets, made here. Each has a shape that gitleaks' own rules, or
  # the shop's rule, find by pattern.
  aws="AKIA$(pick "${upper}234567" 16)"
  hub="ghp_$(pick "$upper$lower$digits" 36)"
  pem=$(openssl genpkey -algorithm ed25519 2> /dev/null)
  pay="pg_live_$(pick "$upper$lower$digits" 32)"
  pay2="pg_live_$(pick "$upper$lower$digits" 32)"
  pay3="pg_live_$(pick "$upper$lower$digits" 32)"
  odd="d$(openssl rand -hex 3)"
  printf '%s\n' "$aws" "$hub" "$pay" "$pay2" "$pay3" > "$work/secrets"
  echo "$pem" | sed -n 2p >> "$work/secrets"

  # 1. Clean work is accepted: two commits to main, a new branch, and the
  # branch's removal.
  echo "Delivery notes go out with order $((RANDOM % 9000 + 1000))." | put -a "README.md"
  commit "Mention delivery notes"
  echo "echo packed" | put "app/pack-$odd.sh"
  commit "Add a packing step"
  if ! push main; then
    note clean-accepted "a push of two commits with no secret in them was refused"
  elif [ "$(at_server main)" != "$(as_learner git rev-parse HEAD)" ]; then
    note clean-accepted "a clean push was accepted, but the server's main didn't move"
  fi
  as_learner git checkout -q -b "topic-$odd"
  echo "echo labelled" | put "app/label-$odd.sh"
  commit "Add a labelling step"
  push "topic-$odd" || note clean-accepted "a new branch with no secret in it was refused"
  as_learner git checkout -q main
  push --delete "topic-$odd" || note clean-accepted "deleting a branch was refused"
  note clean-accepted ok
  back

  # 2. A secret in the newest commit.
  before=$(at_server main)
  printf '#!/bin/bash\nexport AWS_ACCESS_KEY_ID=%s\naws s3 sync . s3://shop-site\n' "$aws" | put "deploy.sh"
  commit "Add the deploy script"
  added=$(as_learner git rev-parse HEAD)
  if push main || [ "$(at_server main)" != "$before" ]; then
    note secret-refused "a push whose newest commit adds a cloud access key was accepted"
  elif ! grep 'aws-access-token' "$work/push.$n" > /dev/null || ! grep "${added:0:7}" "$work/push.$n" > /dev/null; then
    note secret-refused "the push was refused, but what the pusher was shown doesn't name the rule and the commit"
  else
    note secret-refused ok
  fi
  back

  # 3. A secret added by a middle commit and taken out by the last.
  printf 'token: %s\n' "$hub" | put "ci.yaml"
  commit "Add the CI settings"
  added=$(as_learner git rev-parse HEAD)
  printf 'token: from the CI system\n' | put "ci.yaml"
  commit "Take the token out"
  echo "more" | put -a "README.md"
  commit "Tidy the README"
  if push main || [ "$(at_server main)" != "$before" ]; then
    note buried-refused "a push was accepted though one of its commits adds a token that a later commit removes"
  elif ! grep "${added:0:7}" "$work/push.$n" > /dev/null; then
    note buried-refused "the push was refused, but what the pusher was shown doesn't name the commit that added the token"
  else
    note buried-refused ok
  fi
  back

  # 4. A secret on a branch the server has never seen.
  as_learner git checkout -q -b "keys-$odd"
  echo "$pem" | put "signing.pem"
  commit "Add the signing key"
  if push "keys-$odd" || [ -n "$(at_server "keys-$odd")" ]; then
    note new-branch "a new branch whose commit adds a private key was accepted"
  else
    note new-branch ok
  fi
  back

  # 5. The shop's own key format, on a line with no word a general rule
  # looks for.
  printf 'charge with %s\n' "$pay" | put "notes-$odd.txt"
  commit "Notes"
  if push main || [ "$(at_server main)" != "$before" ]; then
    note own-rule "a push that adds a payment gateway key (pg_live_ and 32 letters and digits) was accepted"
  elif ! grep 'paygate-key' "$work/push.$n" > /dev/null; then
    note own-rule "the gateway key was refused, but not by a rule called paygate-key"
  else
    note own-rule ok
  fi
  back

  # 6. The allowance for test fixtures: tests/fixtures/ and nowhere else.
  printf 'charge with %s\n' "$pay2" | put "tests/fixtures/$odd/gateway.txt"
  commit "A fixture"
  if ! push main; then
    note fixtures-only "a key-shaped value under tests/fixtures/ was refused"
  else
    before=$(at_server main)
    printf 'charge with %s\n' "$pay3" | put "tests/$odd/gateway.txt"
    commit "Not a fixture"
    if push main; then
      note fixtures-only "a gateway key under tests/, outside tests/fixtures/, was accepted"
    fi
    back
    printf 'charge with %s\n' "$pay3" | put "$odd/fixtures/gateway.txt"
    commit "Not a fixture either"
    if push main; then
      note fixtures-only "a gateway key in a folder called fixtures, outside tests/fixtures/, was accepted"
    fi
    note fixtures-only ok
  fi
  back
  before=$(at_server main)

  # 7. A push that brings scanner settings of its own.
  printf '[allowlist]\nregexes = [%s]\npaths = [%s]\n' "'''.*'''" "'''.*'''" | put ".gitleaks.toml"
  printf 'export AWS_ACCESS_KEY_ID=%s\n' "$aws" | put "env.sh"
  commit "Scanner settings"
  if push main || [ "$(at_server main)" != "$before" ]; then
    note pushed-config-ignored "a push that brings its own .gitleaks.toml, allowing everything, got a cloud access key through"
  else
    note pushed-config-ignored ok
  fi
  back

  # 8. Nothing the pusher was shown holds a secret.
  if grep -F -f "$work/secrets" "$work"/push.* > /dev/null 2>&1; then
    note no-secret-printed "a refused push's output shows the secret itself"
  else
    note no-secret-printed ok
  fi
}

# guard_finding ASPECT: prints "ok", or what the trial found wrong.
guard_finding() {
  local sum now
  sum=$(cat "$hook" "$settings" 2> /dev/null | sha256sum | cut -d' ' -f1)
  now=$(date +%s)
  if ! [ -s "$findings" ] \
    || [ "$(sed -n 's/^files: //p' "$findings")" != "$sum" ] \
    || [ $((now - $(sed -n 's/^at: //p' "$findings"))) -gt 60 ]; then
    (run_trial)
    {
      echo "files: $sum"
      echo "at: $now"
    } >> "$findings.new"
    mv "$findings.new" "$findings"
  fi
  sed -n "s/^$1: //p" "$findings"
}
