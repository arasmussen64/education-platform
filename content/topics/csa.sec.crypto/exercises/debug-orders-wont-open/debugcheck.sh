# debugcheck.sh: what the checks of the orders-won't-open lab share.
# A check starts with:   . /usr/local/lib/lab/debugcheck.sh
# The truth is under /usr/local/lib/lab/debug, which only root reads: each
# of the 16 orders as it read before sealing (plain/), and the sealed
# files' checksums as they were when the lab started.
. /usr/local/lib/lab/checklib-sec.sh

truth=/usr/local/lib/lab/debug
archive=/srv/orders/archive
incoming=/srv/orders/incoming

# denied TOKEN PATH...: true when the token may do nothing at any of them.
denied() {
  local token=$1 path
  shift
  for path in "$@"; do
    [ "$(caps "$token" "$path")" = deny ] || return 1
  done
}

# The report's own token, with the policy it has, opens every one of the
# 16 orders to what it was. The check does the opening itself, as the
# report does: unwrap with the orders key, then gcm.
check_report() {
  local token name key
  bao_root || {
    echo "OpenBao was never set up on this machine"
    return 0
  }
  token=$(cat /etc/shop/report.token 2> /dev/null)
  [ "$(caps "$token" transit/decrypt/orders)" = update ] || {
    echo "the report's token can't unwrap with the orders key"
    return 0
  }
  denied "$token" transit/decrypt/orders-test transit/datakey/plaintext/orders transit/encrypt/orders \
    transit/rewrap/orders transit/keys/orders transit/keys/orders/config transit/keys/orders/rotate \
    sys/policies/acl/reporting || {
    echo "the report's token may do more than unwrap with the orders key"
    return 0
  }
  for name in $(cd "$truth/plain" && ls); do
    key=$(BAO_TOKEN=$token bao write -field=plaintext transit/decrypt/orders \
      ciphertext="$(cat "$archive/$name.key" 2> /dev/null)" 2> /dev/null) || {
      echo "the report can't open every archived order"
      return 0
    }
    echo "$key" | gcm open "$archive/$name.sealed" - 2> /dev/null | cmp -s - "$truth/plain/$name" || {
      echo "the report can't open every archived order"
      return 0
    }
  done
  echo "16 of 16"
}

check_sealed() {
  (cd "$archive" 2> /dev/null && sha256sum --check --quiet "$truth/sealed.sums" > /dev/null 2>&1) || {
    echo "an archived .sealed file changed or is gone"
    return 0
  }
  echo untouched
}

check_old_retired() {
  local latest lowest
  bao_root || {
    echo "OpenBao was never set up on this machine"
    return 0
  }
  latest=$(bao read -field=latest_version transit/keys/orders 2> /dev/null)
  lowest=$(bao read -field=min_decryption_version transit/keys/orders 2> /dev/null)
  [ "${latest:-0}" -ge 3 ] || {
    echo "the orders key isn't the key the archive was sealed with"
    return 0
  }
  [ "$lowest" = "$latest" ] || {
    echo "version $lowest of the orders key can still unwrap, and the latest is $latest"
    return 0
  }
  echo retired
}

# The token the sealer really uses, whatever policies it has now.
check_front_end() {
  local token
  bao_root || {
    echo "OpenBao was never set up on this machine"
    return 0
  }
  token=$(cat /etc/shop/sealer.token 2> /dev/null)
  [ "$(caps "$token" transit/datakey/plaintext/orders)" = update ] || {
    echo "the front end's token can't make a data key from the orders key"
    return 0
  }
  denied "$token" transit/decrypt/orders transit/decrypt/orders-test transit/datakey/plaintext/orders-test \
    transit/datakey/wrapped/orders transit/encrypt/orders transit/rewrap/orders transit/keys/orders \
    transit/keys/orders/config transit/keys/orders/rotate transit/keys/new-key \
    transit/export/encryption-key/orders sys/policies/acl/web-front auth/token/create || {
    echo "the front end's token may do more than make data keys from the orders key"
    return 0
  }
  echo "data keys only"
}

# An order of the check's own, dropped where orders arrive: the running
# sealer must seal it, under the orders key. The check removes its order
# afterwards.
check_new_orders() {
  local name key
  bao_root || {
    echo "OpenBao was never set up on this machine"
    return 0
  }
  [ "$(systemctl is-enabled sealer 2> /dev/null)" = enabled ] || {
    echo "the sealer won't start at the next boot"
    return 0
  }
  name="order-check-$(openssl rand -hex 4).txt"
  # shellcheck disable=SC2064
  trap "rm -f '$incoming/$name' '$archive/$name.sealed' '$archive/$name.key' '/var/tmp/$name'" EXIT
  {
    echo "order check"
    echo "card 4111-0000-0000-$((RANDOM % 9000 + 1000))"
  } > "/var/tmp/$name"
  install -o web -g orders -m 664 "/var/tmp/$name" "$incoming/$name"
  sealed() { [ -s "$archive/$name.sealed" ] && [ -s "$archive/$name.key" ] && ! [ -e "$incoming/$name" ]; }
  wait_for 12 sealed || {
    echo "an order that arrived in $incoming wasn't sealed into the archive within 12 seconds"
    return 0
  }
  key=$(bao write -field=plaintext transit/decrypt/orders ciphertext="$(cat "$archive/$name.key")" 2> /dev/null) || {
    echo "a newly sealed order's key isn't wrapped by the orders key"
    return 0
  }
  echo "$key" | gcm open "$archive/$name.sealed" - 2> /dev/null | cmp -s - "/var/tmp/$name" || {
    echo "a newly sealed order doesn't open with the key beside it"
    return 0
  }
  echo "sealed under orders"
}
