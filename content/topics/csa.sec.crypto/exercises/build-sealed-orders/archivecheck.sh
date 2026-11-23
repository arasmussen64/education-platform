# archivecheck.sh: what the build's checks of the key and the archive share.
# A check starts with:   . /usr/local/lib/lab/archivecheck.sh
# The truth is under /usr/local/lib/lab/build, which only root reads: each
# order as it read before sealing (plain/), each wrapped key as it was
# when the lab started (keys/), and the sealed files' checksums.
. /usr/local/lib/lab/checklib-sec.sh

truth=/usr/local/lib/lab/build
archive=/srv/orders/archive

# key_field NAME: one field of the orders key's description.
key_field() {
  bao read -format=json transit/keys/orders 2> /dev/null | json "d['data']['$1']"
}

check_key() {
  bao_root || {
    echo "OpenBao was never set up on this machine"
    return 0
  }
  [ "$(key_field type)" = aes256-gcm96 ] || {
    echo "there is no AES-256-GCM key called orders"
    return 0
  }
  [ "$(key_field auto_rotate_period)" = 2592000 ] || {
    echo "the orders key doesn't rotate itself every 30 days"
    return 0
  }
  [ "$(key_field exportable)" = False ] && [ "$(key_field allow_plaintext_backup)" = False ] || {
    echo "the orders key can be taken out of OpenBao"
    return 0
  }
  echo "rotates, stays in"
}

check_archive_current() {
  local latest file name key
  bao_root || {
    echo "OpenBao was never set up on this machine"
    return 0
  }
  latest=$(key_field latest_version)
  [ "$latest" -ge 3 ] 2> /dev/null || {
    echo "the orders key hasn't been rotated since the archive was sealed"
    return 0
  }
  for name in $(cd "$truth/plain" && ls); do
    file="$archive/$name.key"
    case "$(cat "$file" 2> /dev/null)" in
      "vault:v$latest:"*) ;;
      *)
        echo "an archived order's key isn't wrapped by the latest version of the orders key"
        return 0
        ;;
    esac
    key=$(bao write -field=plaintext transit/decrypt/orders ciphertext="$(cat "$file")" 2> /dev/null)
    echo "$key" | gcm open "$archive/$name.sealed" - 2> /dev/null | cmp -s - "$truth/plain/$name" || {
      echo "an archived order no longer opens with the key beside it"
      return 0
    }
  done
  echo "all current"
}

check_archive_sealed() {
  (cd "$archive" 2> /dev/null && sha256sum --check --quiet "$truth/sealed.sums" > /dev/null 2>&1) || {
    echo "an archived .sealed file changed or is gone"
    return 0
  }
  echo untouched
}

# Every wrapped key the lab started with must have been sent to OpenBao's
# rewrap: the audit log holds each request, with an HMAC of the ciphertext
# it carried.
check_archive_rewrapped() {
  local file
  bao_root || {
    echo "OpenBao was never set up on this machine"
    return 0
  }
  for file in "$truth"/keys/*.key; do
    audit_saw transit/rewrap/orders "$(cat "$file")" || {
      echo "OpenBao's audit log shows no rewrap of an archived order's key"
      return 0
    }
  done
  echo "rewrapped by OpenBao"
}

check_old_retired() {
  local latest lowest
  bao_root || {
    echo "OpenBao was never set up on this machine"
    return 0
  }
  latest=$(key_field latest_version)
  lowest=$(key_field min_decryption_version)
  [ "$latest" -ge 3 ] 2> /dev/null || {
    echo "the orders key hasn't been rotated since the archive was sealed"
    return 0
  }
  [ "$lowest" = "$latest" ] || {
    echo "version $lowest of the orders key can still unwrap, and the latest is $latest"
    return 0
  }
  echo retired
}
