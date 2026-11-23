# sealcheck.sh: what the checks of the seal-order and open-order labs share.
# A check starts with:   . /usr/local/lib/lab/sealcheck.sh
#
# Every check makes an order file of its own, with a marker and a length
# made up on the spot, and runs the learner's two scripts on it as the
# learner, each with a token that has only the policy its job should need
# (order-writer to seal, order-reader to open). The root token then looks
# at what the scripts left. Nothing the learner made is changed.
. /usr/local/lib/lab/checklib-sec.sh

bin=/home/learner/bin

# as_learner TOKEN COMMAND...: COMMAND as the learner, with TOKEN as its
# only way in to OpenBao, stopped after 15 seconds.
as_learner() {
  local token=$1
  shift
  runuser -u learner -- env HOME=/home/learner BAO_TOKEN="$token" timeout 15 "$@"
}

# seal_setup: the check's own folder, order and tokens. Prints why and is
# false when there is nothing to try.
seal_setup() {
  bao_root || {
    echo "OpenBao was never set up on this machine"
    return 1
  }
  [ -x "$bin/seal-order" ] && [ -x "$bin/open-order" ] || {
    echo "~/bin/seal-order or ~/bin/open-order is missing, or isn't executable"
    return 1
  }
  work=$(mktemp -d /var/tmp/seal-check.XXXXXX)
  trap 'rm -rf "$work"' EXIT
  marker="marker-$(openssl rand -hex 8)"
  {
    echo "order,$marker"
    echo "card,4111-0000-0000-$((RANDOM % 9000 + 1000))"
    head -c $((RANDOM % 400 + 100)) /dev/urandom | base64
  } > "$work/order.txt"
  cp "$work/order.txt" "$work/again.txt"
  chown -R learner:learner "$work"
  writer=$(token_for order-writer 2> /dev/null)
  reader=$(token_for order-reader 2> /dev/null)
  [ -n "$writer" ] && [ -n "$reader" ] || {
    echo "OpenBao wouldn't make a token for order-writer or order-reader"
    return 1
  }
}

# seal_one FILE: seals FILE with the writer's token. Prints why and is
# false when no sealed file and wrapped key came of it.
seal_one() {
  as_learner "$writer" "$bin/seal-order" "$1" > /dev/null 2>&1 || {
    echo "seal-order failed, run with a token that has only the order-writer policy"
    return 1
  }
  [ -s "$1.sealed" ] && [ -s "$1.key" ] || {
    echo "seal-order didn't leave both FILE.sealed and FILE.key"
    return 1
  }
}

# data_key FILE: the data key wrapped in FILE.key, unwrapped with the root
# token. False when FILE.key isn't a key the orders key wrapped.
data_key() {
  case "$(cat "$1.key" 2> /dev/null)" in
    vault:v*) ;;
    *) return 1 ;;
  esac
  bao write -field=plaintext transit/decrypt/orders ciphertext="$(cat "$1.key")" 2> /dev/null
}

check_roundtrip() {
  seal_setup || return 0
  seal_one "$work/order.txt" || return 0
  as_learner "$reader" "$bin/open-order" "$work/order.txt.sealed" > "$work/opened" 2> /dev/null || {
    echo "open-order failed, run with a token that has only the order-reader policy"
    return 0
  }
  cmp -s "$work/opened" "$work/order.txt" || {
    echo "open-order didn't print the order that seal-order sealed"
    return 0
  }
  echo "sealed and opened"
}

check_envelope() {
  local key size
  seal_setup || return 0
  seal_one "$work/order.txt" || return 0
  grep -a "$marker" "$work/order.txt.sealed" > /dev/null && {
    echo "FILE.sealed holds the order where anyone can read it"
    return 0
  }
  key=$(data_key "$work/order.txt") || {
    echo "FILE.key isn't a data key wrapped by the orders key"
    return 0
  }
  echo "$key" | gcm open "$work/order.txt.sealed" - 2> /dev/null | cmp -s - "$work/order.txt" || {
    echo "FILE.sealed isn't the order encrypted by gcm under the data key wrapped in FILE.key"
    return 0
  }
  # A sealed file with one byte changed must be refused, not opened.
  cp "$work/order.txt.sealed" "$work/bent.txt.sealed"
  cp "$work/order.txt.key" "$work/bent.txt.key"
  size=$(stat -c %s "$work/bent.txt.sealed")
  printf '\377' | dd of="$work/bent.txt.sealed" bs=1 seek=$((size / 2)) conv=notrunc status=none
  cmp -s "$work/bent.txt.sealed" "$work/order.txt.sealed" \
    && printf '\000' | dd of="$work/bent.txt.sealed" bs=1 seek=$((size / 2)) conv=notrunc status=none
  chown learner:learner "$work"/bent.txt.*
  as_learner "$reader" "$bin/open-order" "$work/bent.txt.sealed" > /dev/null 2>&1 && {
    echo "open-order opened a sealed file that had been changed"
    return 0
  }
  echo "an envelope"
}

check_fresh_key() {
  local first second
  seal_setup || return 0
  seal_one "$work/order.txt" || return 0
  seal_one "$work/again.txt" || return 0
  first=$(data_key "$work/order.txt") && second=$(data_key "$work/again.txt") || {
    echo "FILE.key isn't a data key wrapped by the orders key"
    return 0
  }
  [ "$first" != "$second" ] || {
    echo "two files were sealed under one data key"
    return 0
  }
  echo "a key each"
}

check_no_key_on_disk() {
  local key found
  seal_setup || return 0
  seal_one "$work/order.txt" || return 0
  key=$(data_key "$work/order.txt") || {
    echo "FILE.key isn't a data key wrapped by the orders key"
    return 0
  }
  found=$(on_disk "$key") && {
    echo "the data key is in a file, unwrapped: $(echo "$found" | head -n 1)"
    return 0
  }
  echo clean
}

check_policies() {
  local policy
  bao_root || {
    echo "OpenBao was never set up on this machine"
    return 0
  }
  for policy in order-writer order-reader; do
    bao policy read "$policy" > /dev/null 2>&1 || {
      echo "there is no policy called $policy"
      return 0
    }
  done
  writer=$(token_for order-writer)
  reader=$(token_for order-reader)
  [ "$(caps "$writer" transit/datakey/plaintext/orders)" = update ] || {
    echo "order-writer can't make a data key"
    return 0
  }
  [ "$(caps "$reader" transit/decrypt/orders)" = update ] || {
    echo "order-reader can't unwrap"
    return 0
  }
  for path in transit/decrypt/orders transit/encrypt/orders transit/rewrap/orders transit/keys/orders \
    transit/keys/orders/config transit/keys/orders/rotate transit/export/encryption-key/orders \
    transit/datakey/plaintext/other sys/policies/acl/order-writer; do
    [ "$(caps "$writer" "$path")" = deny ] || {
      echo "order-writer may do more than make data keys from the orders key"
      return 0
    }
  done
  for path in transit/datakey/plaintext/orders transit/datakey/wrapped/orders transit/encrypt/orders \
    transit/rewrap/orders transit/keys/orders transit/keys/orders/config transit/keys/orders/rotate \
    transit/export/encryption-key/orders transit/decrypt/other sys/policies/acl/order-reader; do
    [ "$(caps "$reader" "$path")" = deny ] || {
      echo "order-reader may do more than unwrap with the orders key"
      return 0
    }
  done
  echo "least privilege"
}
