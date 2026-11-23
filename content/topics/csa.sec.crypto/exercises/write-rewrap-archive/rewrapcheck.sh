# rewrapcheck.sh: the trial behind the checks of the rewrap-archive lab.
# A check starts with:   . /usr/local/lib/lab/rewrapcheck.sh
# and asks for one finding:   rewrap_finding all-current
#
# The trial makes everything it needs on the spot, so nothing can be
# hard-coded: a transit key with a made-up name, rotated three or four
# times; a tree of 5 to 12 sealed orders in folders of several depths (one
# folder's name has a space), their keys wrapped by versions picked at
# random; and a token that may rewrap with that key and read its
# description, and nothing else. It runs the learner's script on the tree
# twice, as the learner, and writes down what it found. It then removes its
# key, its policy and its tree: nothing of the learner's is changed.
#
# All five checks ask about one script, so the trial runs once for the five:
# its findings are kept for a minute in /run/lab-rewrap, under the
# checksum of the script they are about. A changed script, or a minute
# gone by, means a new trial.
. /usr/local/lib/lab/checklib-sec.sh

script=/home/learner/bin/rewrap-archive
findings=/run/lab-rewrap

as_learner() {
  local token=$1
  shift
  (cd /home/learner && runuser -u learner -- env HOME=/home/learner BAO_TOKEN="$token" timeout 20 "$@")
}

# note ASPECT TEXT: the trial's finding for one check; the first one said
# for an aspect is the one that counts.
note() {
  grep "^$1: " "$findings.new" > /dev/null 2>&1 || echo "$1: $2" >> "$findings.new"
}

all_aspects() {
  local aspect
  for aspect in all-current sealed-untouched counts idempotent no-unwrap; do
    note "$aspect" "$1"
  done
}

run_trial() {
  local key work tree truth latest rotations n i v dir dk token old current expected file name

  : > "$findings.new"
  chmod 600 "$findings.new"
  bao_root || {
    all_aspects "OpenBao was never set up on this machine"
    return
  }
  [ -x "$script" ] || {
    all_aspects "~/bin/rewrap-archive is missing, or isn't executable"
    return
  }

  key="chk-$(openssl rand -hex 4)"
  work=$(mktemp -d /var/tmp/rewrap-check.XXXXXX)
  tree="$work/tree"
  truth="$work/truth"
  mkdir -p "$tree/first" "$tree/second half/2026" "$tree/third/a/b" "$truth"
  # shellcheck disable=SC2064
  trap "bao write transit/keys/$key/config deletion_allowed=true > /dev/null 2>&1
        bao delete transit/keys/$key > /dev/null 2>&1
        bao policy delete $key > /dev/null 2>&1
        rm -rf '$work'" EXIT

  bao write -f "transit/keys/$key" > /dev/null
  rotations=$((RANDOM % 2 + 3))
  for ((i = 0; i < rotations; i++)); do
    bao write -f "transit/keys/$key/rotate" > /dev/null
  done
  latest=$((rotations + 1))
  bao policy write "$key" - > /dev/null << EOF
path "transit/rewrap/$key" {
  capabilities = ["update"]
}
path "transit/keys/$key" {
  capabilities = ["read"]
}
EOF
  token=$(token_for "$key")

  # The orders. The first is already at the latest version and the second
  # at the oldest, so both kinds are always there; the rest are random.
  n=$((RANDOM % 8 + 5))
  old=0
  current=0
  dirs=("$tree/first" "$tree/second half/2026" "$tree/third/a/b" "$tree")
  for ((i = 1; i <= n; i++)); do
    case $i in
      1) v=$latest ;;
      2) v=1 ;;
      *) v=$((RANDOM % latest + 1)) ;;
    esac
    dir=${dirs[$((i % 4))]}
    name="order-$((4000 + i)).txt"
    head -c $((RANDOM % 300 + 60)) /dev/urandom | base64 > "$truth/$name"
    dk=$(openssl rand -base64 32)
    echo "$dk" | gcm seal "$truth/$name" "$dir/$name.sealed"
    bao write -field=ciphertext "transit/encrypt/$key" key_version="$v" plaintext="$dk" > "$dir/$name.key"
    if [ "$v" = "$latest" ]; then current=$((current + 1)); else old=$((old + 1)); fi
  done
  (cd "$tree" && find . -name '*.sealed' -print0 | sort -z | xargs -0 sha256sum) > "$truth/sealed.sums"
  chown -R learner:learner "$tree"
  chmod 755 "$work"

  # First run.
  as_learner "$token" "$script" "$tree" "$key" > "$truth/out1" 2> "$truth/err1"
  echo $? > "$truth/status1"
  (cd "$tree" && find . -name '*.key' -print0 | sort -z | xargs -0 sha256sum) > "$truth/keys.after1"

  # Did anything ask OpenBao to unwrap with the trial's key? Read before
  # the trial's own unwrapping, below.
  if grep -F "\"path\":\"transit/decrypt/$key\"" /var/log/openbao/audit.log > /dev/null; then
    note no-unwrap "a data key was unwrapped on the way: the script asked OpenBao to decrypt"
  else
    note no-unwrap "ok"
  fi

  # Second run.
  as_learner "$token" "$script" "$tree" "$key" > "$truth/out2" 2> "$truth/err2"
  (cd "$tree" && find . -name '*.key' -print0 | sort -z | xargs -0 sha256sum) > "$truth/keys.after2"

  if [ "$(cat "$truth/status1")" != 0 ]; then
    note counts "the script ended with an error (exit status $(cat "$truth/status1")), run with a token that may only rewrap with the key and read its description"
  fi

  # Every wrapped key at the latest version, and still the key that opens
  # its order.
  while IFS= read -r -d '' file; do
    case "$(cat "$file")" in
      "vault:v$latest:"*) ;;
      *)
        note all-current "a .key file isn't wrapped by the key's latest version"
        continue
        ;;
    esac
    dk=$(bao write -field=plaintext "transit/decrypt/$key" ciphertext="$(cat "$file")" 2> /dev/null)
    name=$(basename "${file%.key}")
    echo "$dk" | gcm open "${file%.key}.sealed" - 2> /dev/null | cmp -s - "$truth/$name" \
      || note all-current "a rewrapped .key file no longer opens its order"
  done < <(find "$tree" -name '*.key' -print0)
  [ "$(find "$tree" -name '*.key' | wc -l)" = "$n" ] || note all-current "a .key file is gone"
  note all-current "ok"

  if (cd "$tree" && sha256sum --check --quiet "$truth/sealed.sums" > /dev/null 2>&1); then
    note sealed-untouched "ok"
  else
    note sealed-untouched "a .sealed file changed or is gone"
  fi

  expected="rewrapped $old, already current $current"
  if [ "$(tail -n 1 "$truth/out1")" = "$expected" ]; then
    note counts "ok"
  else
    note counts "with $old keys to rewrap and $current current, the last line printed wasn't \"$expected\""
  fi

  expected="rewrapped 0, already current $n"
  if [ "$(tail -n 1 "$truth/out2")" != "$expected" ]; then
    note idempotent "a second run over the same archive didn't end \"$expected\""
  elif ! cmp -s "$truth/keys.after1" "$truth/keys.after2"; then
    note idempotent "a second run changed .key files that were already current"
  else
    note idempotent "ok"
  fi
}

# rewrap_finding ASPECT: prints "ok", or what the trial found wrong.
rewrap_finding() {
  local sum now
  sum=$(sha256sum "$script" 2> /dev/null | cut -d' ' -f1)
  now=$(date +%s)
  if ! [ -s "$findings" ] \
    || [ "$(sed -n 's/^script: //p' "$findings")" != "$sum" ] \
    || [ $((now - $(sed -n 's/^at: //p' "$findings"))) -gt 60 ]; then
    (run_trial)
    {
      echo "script: $sum"
      echo "at: $now"
    } >> "$findings.new"
    mv "$findings.new" "$findings"
  fi
  sed -n "s/^$1: //p" "$findings"
}
