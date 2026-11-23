# buildcheck.sh: the trial behind the checks of the build-without-secrets
# lab. A check starts with:   . /usr/local/lib/lab/buildcheck.sh
# and asks for one finding:   build_finding token-in-no-layer
#
# The trial changes the package server's token to one made on the spot,
# puts the same token in OpenBao, changes the library's version number,
# removes the image, and runs the learner's ~/bin/build-shop as the
# learner, with a token for OpenBao that may only read that one secret.
# So nothing can be hard-coded: the build has to fetch this run's token
# from OpenBao and this run's library from the server. Then it looks for
# the token everywhere a build can leave one. The package token and the
# library stay as the trial set them, which is what a rotated token looks
# like; the image is the one the learner's own script built.
#
# All six checks ask about one script and one recipe, so the trial runs
# once for the six: its findings are kept for a minute in /run/lab-build,
# under the checksum of the two files. A changed file, or a minute gone
# by, means a new trial.
. /usr/local/lib/lab/checklib-sec.sh

script=/home/learner/bin/build-shop
recipe=/home/learner/shop-export/Containerfile
image=shop-export:2
state=/var/lib/pkg-server
findings=/run/lab-build

# note ASPECT TEXT: the trial's finding for one check; the first one said
# for an aspect is the one that counts.
note() {
  grep "^$1: " "$findings.new" > /dev/null 2>&1 || echo "$1: $2" >> "$findings.new"
}

all_aspects() {
  local aspect
  for aspect in image-built token-in-no-layer secret-mount token-not-left given-token; do
    note "$aspect" "$1"
  done
}

# spellings VALUE: the value as it is, as base64 and as hex, one a line.
# Another spelling of a secret is the secret all the same.
spellings() {
  printf '%s\n' "$1"
  printf '%s' "$1" | base64 -w 0
  echo
  printf '%s\n' "$1" | base64 -w 0
  echo
  printf '%s' "$1" | xxd -p -c 256
}

run_trial() {
  local token version job lines said steps spelled found

  : > "$findings.new"
  chmod 600 "$findings.new"
  bao_root || {
    all_aspects "OpenBao was never set up on this machine"
    return
  }
  [ -x "$script" ] && [ -f "$recipe" ] || {
    all_aspects "~/bin/build-shop or ~/shop-export/Containerfile is missing"
    return
  }
  ready() { curl -s -m 3 -o /dev/null http://127.0.0.1:8081/; }
  wait_for 10 ready || {
    all_aspects "the package server isn't answering"
    return
  }

  # This run's token and library.
  token="pkg-$(openssl rand -hex 16)"
  version="shop-lib 2.4.$((RANDOM % 900 + 100))"
  echo "$token" > "$state/token"
  echo "$version" > "$state/library"
  bao kv put secret/ci/pkg-token token="$token" > /dev/null
  job=$(token_for ci-build)
  lines=$(wc -l < /var/log/openbao/audit.log)

  # A build must really happen: nothing of an earlier one may be reused.
  podman rmi -f "$image" > /dev/null 2>&1
  podman image prune -f > /dev/null 2>&1

  said=$(cd /home/learner && runuser -u learner -- env HOME=/home/learner BAO_TOKEN="$job" timeout 90 "$script" 2>&1) || {
    all_aspects "build-shop failed, run with a token that may only read secret/ci/pkg-token: $(echo "$said" | tail -n 1 | cut -c 1-150)"
    return
  }
  podman image exists "$image" || {
    all_aspects "build-shop ran, and there is no image called $image"
    return
  }
  if [ "$(podman run --rm "$image" 2> /dev/null)" = "shop-export, with $version" ]; then
    note image-built ok
  else
    note image-built "the image doesn't run and print the library the package server has now"
  fi

  # The token, in any spelling, anywhere in the image: a layer, the
  # history, the settings.
  spelled=$(spellings "$token")
  found=""
  while IFS= read -r value; do
    found=$(image_has "$image" "$value" | head -n 1)
    [ -n "$found" ] && break
  done <<< "$spelled"
  if [ -n "$found" ]; then
    note token-in-no-layer "the package token is in the image ($found)"
  else
    note token-in-no-layer ok
  fi

  # How the fetching step got the token: as a secret mount, and with no
  # build argument anywhere in the history.
  steps=$(podman history --no-trunc --format '{{.CreatedBy}}' "$image")
  if echo "$steps" | grep -E '^\|[0-9]+ ' > /dev/null; then
    note secret-mount "a build step was handed a build argument"
  elif ! echo "$steps" | grep 'shop-lib.txt' | grep -e '--mount=type=secret' > /dev/null; then
    note secret-mount "the step that fetches the library isn't shown the token the way the recipe's comment describes"
  else
    note secret-mount ok
  fi

  # The token, in any spelling, in any file the build left: the usual
  # places, and podman's own storage.
  found=$(grep -rlF -f <(echo "$spelled") /home /tmp /var/tmp /srv /etc /run /var/log /var/lib/containers 2> /dev/null | head -n 1)
  if [ -n "$found" ]; then
    note token-not-left "the package token is in a file after the build: $found"
  else
    note token-not-left ok
  fi

  # Whose token asked OpenBao for the secret? Every read of it since the
  # trial began is in the audit log with the policies of the token that
  # asked.
  found=$(tail -n "+$((lines + 1))" /var/log/openbao/audit.log \
    | grep -F '"type":"request"' | grep -F '"path":"secret/data/ci/pkg-token"' | grep -F '"operation":"read"')
  if [ -z "$found" ]; then
    note given-token "build-shop never asked OpenBao for secret/ci/pkg-token"
  elif echo "$found" | grep -vF '"token_policies":["ci-build","default"]' > /dev/null; then
    note given-token "OpenBao was asked for the secret with another token than the one build-shop was given"
  else
    note given-token ok
  fi
}

# build_finding ASPECT: prints "ok", or what the trial found wrong.
build_finding() {
  local sum now
  sum=$(cat "$script" "$recipe" 2> /dev/null | sha256sum | cut -d' ' -f1)
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
