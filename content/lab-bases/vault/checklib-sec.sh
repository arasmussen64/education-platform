# checklib-sec.sh: helpers for the checks of labs on the vault base.
# A check starts with:   . /usr/local/lib/lab/checklib-sec.sh
# Checks run as root on the lab machine. Every helper reads real state:
# what OpenBao answers, what its audit log holds, what the database says,
# what is inside a built image. The base's README
# (content/lab-bases/vault/README.md) lists them all.

export BAO_ADDR=http://127.0.0.1:8200

# Git refuses to read a repository that belongs to someone else ("dubious
# ownership"), and a check is root reading the learner's. These three
# settings lift that for the check's own commands only (and for gitleaks,
# which runs git itself); nothing on the machine changes.
export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=safe.directory GIT_CONFIG_VALUE_0='*'

# wait_for TRIES COMMAND...: tries COMMAND up to TRIES times, a second
# apart, until it succeeds. For something that needs a moment after a boot;
# never to wait out a race. (The same helper as the network base's.)
wait_for() {
  local limit=$1 i
  shift
  for ((i = 0; i < limit; i++)); do
    "$@" > /dev/null 2>&1 && return 0
    sleep 1
  done
  "$@" > /dev/null 2>&1
}

# json PYTHON-EXPRESSION: reads JSON on stdin as d, prints the expression
# (the lab images have no jq). bao read -format=json transit/keys/orders | json "d['data']['type']"
json() {
  python3 -c 'import json, sys
try:
    d = json.load(sys.stdin)
    r = eval(sys.argv[1], {"d": d})
except Exception as e:
    print("json: " + type(e).__name__)
    sys.exit(0)
print(r if not isinstance(r, (dict, list)) else json.dumps(r, sort_keys=True))' "$1"
}

# bao_root: from here on, the check's own bao commands use the root token,
# which sees everything. Fails when OpenBao has no root token yet.
bao_root() {
  BAO_TOKEN=$(cat /root/.bao-root-token 2> /dev/null) || return 1
  export BAO_TOKEN
}

# token_for POLICY [TTL]: prints a new token that has only POLICY (and
# "default"), for trying what that policy allows. It lasts TTL (5m unless
# given) and has no parent, so it can't outlive the check by much. Call
# bao_root first.
token_for() {
  bao token create -orphan -policy="$1" -ttl="${2:-5m}" -field=token
}

# caps TOKEN PATH: what TOKEN may do at PATH, as OpenBao works it out from
# the token's policies, sorted on one line: "create read update", or "deny".
caps() {
  bao token capabilities "$1" "$2" | tr ', ' '\n\n' | grep . | sort | tr '\n' ' ' | sed 's/ $//'
}

# audit_saw PATH VALUE: true when the audit log holds a request to PATH that
# carried VALUE, in what was sent or in what came back. The log never holds
# a secret value itself: it holds an HMAC of it, under a key only OpenBao
# has, and OpenBao works out the same HMAC for VALUE when asked. Call
# bao_root first.
audit_saw() {
  local hash
  hash=$(bao write -field=hash sys/audit-hash/file input="$2" 2> /dev/null) || return 1
  [ -n "$hash" ] || return 1
  python3 -c 'import json, sys
path, wanted = sys.argv[1].strip("/"), sys.argv[2]
for line in open("/var/log/openbao/audit.log", errors="replace"):
    if wanted not in line:
        continue
    try:
        entry = json.loads(line)
    except ValueError:
        continue
    if entry.get("request", {}).get("path", "").strip("/") == path:
        sys.exit(0)
sys.exit(1)' "$1" "$hash"
}

# on_disk VALUE [SKIP-DIR]: prints every file that holds VALUE under the
# places a secret gets left (/home /tmp /srv /var/tmp /etc /run
# /var/log), and is true when there is one. SKIP-DIR is the check's own
# scratch folder, which it leaves out. OpenBao's own store (/opt/openbao)
# isn't searched: it is encrypted.
on_disk() {
  local found
  found=$(grep -rlF --exclude-dir="$(basename "${2:-.no-such-folder}")" -e "$1" \
    /home /tmp /srv /var/tmp /etc /run /var/log 2> /dev/null | sort)
  [ -n "$found" ] && echo "$found"
}

# sealed_ok: "intact", or the scenery files that changed since the lab's
# image was built (and then it is false). A lab records them at build with
# "RUN lab-seal FILE...".
sealed_ok() {
  local changed
  [ -s /root/lab-sums ] || {
    echo "no file was sealed in this lab"
    return 1
  }
  changed=$(sha256sum --check --quiet /root/lab-sums 2>&1 | grep -v '^sha256sum: WARNING')
  if [ -z "$changed" ]; then
    echo intact
  else
    echo "$changed"
    return 1
  fi
}

# pg SQL [DATABASE]: runs SQL as the database's own superuser and prints the
# bare answer: no headings, columns separated by "|".
pg() {
  runuser -u postgres -- psql -X -A -t -q -d "${2:-postgres}" -c "$1"
}

# as_user USER COMMAND...: runs COMMAND as USER, with that user's home
# folder, for "who can read this?" checks.
as_user() {
  local user=$1
  shift
  runuser -u "$user" -- env HOME="$(getent passwd "$user" | cut -d: -f6)" "$@"
}

# image_has IMAGE VALUE: saves the podman image and prints every place VALUE
# is in it (a file in a layer, a file's name, a build step's command in the
# history, the settings); true when it is anywhere. A value that a later
# build step deleted is still found, in the layer that added it.
image_has() {
  local dir status
  dir=$(mktemp -d /var/tmp/image-has.XXXXXX)
  if ! podman save -q -o "$dir/image.tar" "$1" > /dev/null 2>&1; then
    rm -rf "$dir"
    echo "no image called $1"
    return 2
  fi
  /usr/local/lib/lab/image-search "$dir/image.tar" "$2"
  status=$?
  rm -rf "$dir"
  return $status
}
