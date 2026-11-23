# shopcheck.sh: what the checks of the no-static-secrets build share.
# A check starts with:   . /usr/local/lib/lab/shopcheck.sh
# Every check reads real state: what the API answers, what the database
# says of the account the API is using, what OpenBao does with tokens the
# check signs itself with the platform's key, what a token from a good
# sign-in may do. The truth is under /usr/local/lib/lab/build, which only
# root reads: the two passwords the lab began with.
. /usr/local/lib/lab/checklib-sec.sh

truth=/usr/local/lib/lab/build
api=http://127.0.0.1:8080

# need_bao: the root token, or the reason there is none.
need_bao() {
  bao_root || {
    echo "OpenBao was never set up on this machine"
    return 1
  }
}

# api_user: the database account the API is connected as right now, or
# "none" when it has no answer that reads as an account's name (the name
# goes into the checks' own SQL).
api_user() {
  local user
  user=$(curl -s -m 8 "$api/whoami")
  case "$user" in
    "" | *[!A-Za-z0-9_-]*) echo none ;;
    *) echo "$user" ;;
  esac
}

# logs_in USER PASSWORD: true when the database lets that account in.
logs_in() {
  PGPASSWORD="$2" PGCONNECT_TIMEOUT=3 psql -X -A -t -q --host=127.0.0.1 --username="$1" --dbname=shop -c 'SELECT 1' > /dev/null 2>&1
}

# signed ARGS...: a platform token with claims of the check's choosing.
signed() {
  /usr/local/bin/platform-token sign "$@"
}

# sign_in ROLE JWT: the OpenBao token that sign-in gives, or nothing.
sign_in() {
  bao write -field=token auth/jwt/login role="$1" jwt="$2" 2> /dev/null
}

check_api() {
  local wanted user state template
  need_bao || return 0
  for unit in shop-api shop-api-agent; do
    state="$(systemctl is-enabled "$unit" 2> /dev/null) $(systemctl is-active "$unit" 2> /dev/null)"
    [ "$state" = "enabled active" ] || {
      echo "$unit.service is $state, not enabled and running"
      return 0
    }
  done
  wanted="$(pg 'SELECT count(*) FROM orders' shop) orders"
  answers() { [ "$(curl -s -m 8 "$api/orders")" = "$wanted" ]; }
  wait_for 12 answers || {
    echo "GET /orders doesn't answer with the number of orders: $(curl -s -m 8 "$api/orders" | cut -c 1-120)"
    return 0
  }
  # An account's name says who asked for it ("v-", the start of the asking
  # token's name, the role), unless the connection was given a name
  # pattern of its own. A token from a sign-in at auth/jwt as
  # "workload:..." is called "jwt-workload:...".
  template=$(bao read -format=json database/config/shop 2> /dev/null | json "d['data']['connection_details'].get('username_template', '')")
  [ -z "$template" ] || {
    echo "the database connection shop has a username_template of its own, so an account's name no longer says who asked for it"
    return 0
  }
  user=$(api_user)
  case "$user" in
    v-jwt-work-*) ;;
    *)
      echo "the API's database account, $user, isn't one OpenBao made for a workload that signed in at auth/jwt with its platform token"
      return 0
      ;;
  esac
  [ "$(pg "SELECT count(*) FROM pg_roles WHERE rolname = '$user'")" = 1 ] || {
    echo "the database has no account called $user"
    return 0
  }
  echo "serving, as a dynamic account"
}

check_short() {
  local role default longest user left
  need_bao || return 0
  role=$(bao read -format=json database/roles/shop-api 2> /dev/null) || {
    echo "OpenBao has no database role called shop-api"
    return 0
  }
  default=$(echo "$role" | json "d['data']['default_ttl']")
  longest=$(echo "$role" | json "d['data']['max_ttl']")
  [ "$default" -gt 0 ] && [ "$default" -le 3600 ] || {
    echo "an account from the role lasts $default seconds unless renewed (0 means OpenBao's own default of 32 days), not at most an hour"
    return 0
  }
  [ "$longest" -gt 0 ] && [ "$longest" -le 86400 ] || {
    echo "an account from the role can be renewed up to $longest seconds (0 means OpenBao's own default of 32 days), not at most a day"
    return 0
  }
  user=$(api_user)
  left=$(pg "SELECT coalesce(round(extract(epoch FROM rolvaliduntil - now())), 999999999) FROM pg_roles WHERE rolname = '$user'")
  [ -n "$left" ] && [ "$left" -le 3660 ] || {
    echo "the account the API is using has no end within the hour"
    return 0
  }
  echo "an hour, a day"
}

# least USER: prints what is wrong with the account's rights, or nothing.
least() {
  local user=$1 can more
  can=$(pg "SELECT has_table_privilege('$user', 'orders', 'SELECT') AND has_table_privilege('$user', 'orders', 'INSERT')" shop)
  [ "$can" = t ] || {
    echo "can't read and add orders"
    return
  }
  more=$(pg "SELECT has_table_privilege('$user', 'orders', 'UPDATE') OR has_table_privilege('$user', 'orders', 'DELETE')
      OR has_table_privilege('$user', 'orders', 'TRUNCATE') OR has_table_privilege('$user', 'orders', 'REFERENCES')
      OR has_table_privilege('$user', 'customers', 'SELECT') OR has_table_privilege('$user', 'customers', 'INSERT')
      OR has_database_privilege('$user', 'shop', 'CREATE') OR has_schema_privilege('$user', 'public', 'CREATE')
      OR (SELECT rolsuper OR rolcreaterole OR rolcreatedb OR rolbypassrls FROM pg_roles WHERE rolname = '$user')
      OR EXISTS (SELECT 1 FROM pg_auth_members m JOIN pg_roles r ON r.oid = m.member WHERE r.rolname = '$user')" shop)
  [ "$more" = f ] || echo "can do more in the database than read and add orders"
}

check_db_least() {
  local user made lease wrong
  need_bao || return 0
  user=$(api_user)
  case "$user" in
    v-*) ;;
    *)
      echo "the API isn't using an account that OpenBao made"
      return 0
      ;;
  esac
  wrong=$(least "$user")
  [ -z "$wrong" ] || {
    echo "the account the API is using $wrong"
    return 0
  }
  made=$(bao read -format=json database/creds/shop-api 2> /dev/null) || {
    echo "OpenBao can't make an account from the role shop-api"
    return 0
  }
  lease=$(echo "$made" | json "d['lease_id']")
  # shellcheck disable=SC2064
  trap "bao lease revoke '$lease' > /dev/null 2>&1" EXIT
  wrong=$(least "$(echo "$made" | json "d['data']['username']")")
  [ -z "$wrong" ] || {
    echo "a new account from the role $wrong"
    return 0
  }
  echo "orders: read and add"
}

check_static_gone() {
  local old found b64 hex role
  old=$(cat "$truth/app-password")
  logs_in shop_app "$old" && {
    echo "shop_app still logs in with its old password"
    return 0
  }
  [ "$(pg "SELECT count(*) FROM pg_roles WHERE rolname = 'shop_app' AND rolcanlogin")" = 0 ] || {
    echo "shop_app can still log in to the database"
    return 0
  }
  # The old password under any other name: an account that was renamed
  # keeps its password.
  while IFS= read -r role; do
    [ -n "$role" ] || continue
    logs_in "$role" "$old" && {
      echo "the old password still logs in to the database, as $role"
      return 0
    }
  done < <(pg "SELECT rolname FROM pg_roles WHERE rolcanlogin AND rolname <> 'postgres'")
  [ -e /etc/shop/db.conf ] && {
    echo "/etc/shop/db.conf is still there"
    return 0
  }
  b64=$(printf '%s' "$old" | base64 -w 0)
  hex=$(printf '%s' "$old" | xxd -p -c 256)
  found=$(on_disk "$old") || found=$(on_disk "$b64") || found=$(on_disk "$hex") && {
    echo "the old password is still in a file: $(echo "$found" | head -n 1)"
    return 0
  }
  echo gone
}

check_root_rotated() {
  local made
  need_bao || return 0
  bao read database/config/shop > /dev/null 2>&1 || {
    echo "OpenBao has no database connection called shop"
    return 0
  }
  logs_in bao_admin "$(cat "$truth/admin-password")" && {
    echo "the admin password that was in secret/db/admin still logs in as bao_admin"
    return 0
  }
  made=$(bao read -format=json database/creds/shop-api 2> /dev/null) || {
    echo "OpenBao can no longer make an account from the role shop-api"
    return 0
  }
  bao lease revoke "$(echo "$made" | json "d['lease_id']")" > /dev/null 2>&1
  echo "only OpenBao knows it"
}

check_identity() {
  local roles role odd other good others
  need_bao || return 0
  roles=$(bao list -format=json auth/jwt/role 2> /dev/null | json "' '.join(d)") || roles=""
  case " $roles " in
    *" shop-api "*) ;;
    *)
      echo "OpenBao has no JWT sign-in role called shop-api at auth/jwt"
      return 0
      ;;
  esac
  good=$(sign_in shop-api "$(signed --sub workload:shop-api)")
  [ -n "$good" ] || {
    echo "the order API's own platform token can't sign in with the role shop-api"
    return 0
  }
  # Any other sign-in method that is switched on is another way in, which
  # these trials would never see: there must be none (auth/token is
  # OpenBao's own, and always there).
  others=$(bao auth list -format=json 2> /dev/null | json "' '.join(sorted(k for k in d if k not in ('token/', 'jwt/')))")
  [ -z "$others" ] || {
    others=${others%% *}
    echo "another way of signing in is switched on, at auth/${others%/}: the order API needs auth/jwt alone"
    return 0
  }
  # A key of the check's own: a token it signs has the right claims and
  # the wrong signer.
  other=$(mktemp /var/tmp/identity-check.XXXXXX)
  # shellcheck disable=SC2064
  trap "rm -f '$other'" EXIT
  openssl ecparam -name prime256v1 -genkey -noout 2> /dev/null | openssl pkcs8 -topk8 -nocrypt -out "$other" 2> /dev/null
  odd="x$(openssl rand -hex 4)"
  # Every role at auth/jwt is tried, with names made up on the spot beside
  # the ones the lab has: a role that takes any workload, or any name
  # that begins the right way, lets these in.
  for role in $roles; do
    for subject in workload:report-job "workload:shop-api-$odd" "workload:$odd" workload:shop-ap "workload:shop-api$odd" "$odd"; do
      [ -z "$(sign_in "$role" "$(signed --sub "$subject")")" ] || {
        echo "a platform token for another workload can sign in"
        return 0
      }
    done
    [ -z "$(sign_in "$role" "$(signed --sub workload:shop-api --aud "$odd")")" ] \
      && [ -z "$(sign_in "$role" "$(signed --sub workload:shop-api --aud other)")" ] || {
      echo "a platform token meant for another audience can sign in"
      return 0
    }
    [ -z "$(sign_in "$role" "$(signed --sub workload:shop-api --ttl=-600)")" ] || {
      echo "a platform token that ran out ten minutes ago can sign in"
      return 0
    }
    [ -z "$(sign_in "$role" "$(signed --sub workload:shop-api --iss "https://$odd.shop.test")")" ] || {
      echo "a token from another issuer can sign in"
      return 0
    }
    [ -z "$(sign_in "$role" "$(signed --sub workload:shop-api --key "$other")")" ] || {
      echo "a token signed with a key that isn't the platform's can sign in"
      return 0
    }
  done
  echo "the order API only"
}

check_token_least() {
  local token odd path
  need_bao || return 0
  token=$(sign_in shop-api "$(signed --sub workload:shop-api)")
  [ -n "$token" ] || {
    echo "the order API's own platform token can't sign in with the role shop-api"
    return 0
  }
  [ "$(caps "$token" database/creds/shop-api)" = read ] || {
    echo "a token from that sign-in can't read database/creds/shop-api, or can do more there than read"
    return 0
  }
  # Paths with a name made up on the spot stand for everything a policy
  # doesn't list: one that allows everything and then denies the paths it
  # expects to be asked about allows these.
  odd="x$(openssl rand -hex 4)"
  for path in secret/data/db/admin secret/metadata/db/admin "secret/data/$odd" database/config/shop \
    database/roles/shop-api database/rotate-root/shop "database/creds/$odd" database/creds/report \
    "database/creds/shop-api$odd" "database/creds/shop-api-$odd" "database/creds/shop-api/$odd" \
    "database/$odd" sys/policies/acl/shop-api "sys/policies/acl/$odd" sys/auth sys/mounts \
    auth/token/create "auth/jwt/role/$odd" auth/jwt/config "$odd/creds/shop-api" "$odd"; do
    [ "$(caps "$token" "$path")" = deny ] || {
      echo "a token from that sign-in may do more than read its own database credentials"
      return 0
    }
  done
  echo "its own credentials only"
}

check_no_standing() {
  local file token where pid found
  need_bao || return 0
  # Any live OpenBao token in a file outside the learner's and root's own
  # token files must have come from a platform sign-in. Every folder a
  # file can be kept in is searched, not only the usual ones.
  while IFS= read -r file; do
    for token in $(grep -a -o -E 's\.[A-Za-z0-9]{24}' "$file" 2> /dev/null | sort -u); do
      where=$(bao token lookup -format=json "$token" 2> /dev/null | json "d['data']['path']") || continue
      case "$where" in
        auth/jwt/login | "" | json:*) ;;
        *)
          echo "a token that wasn't given for a platform sign-in is kept in $file"
          return 0
          ;;
      esac
    done
  done < <(grep -rlaE 's\.[A-Za-z0-9]{24}' /etc /home /srv /run /tmp /var /usr/local /opt /root /mnt /media /dev/shm 2> /dev/null \
    | grep -v -e '^/home/learner/\.vault-token$' -e '^/root/\.bao-root-token$' -e '^/var/lib/lab/' -e '^/opt/openbao/' \
      -e '^/var/lib/postgresql/' -e '^/var/lib/containers/' -e '^/var/log/journal/' -e '^/var/log/openbao/' \
      -e '^/run/lab-' -e '^/run/log/' -e '^/etc/openbao/unseal.key$' -e '^/usr/local/lib/lab/')
  # No token handed to a unit or a running program through its environment.
  found=$(systemctl show shop-api shop-api-agent -p Environment 2> /dev/null | grep -E 'TOKEN|s\.[A-Za-z0-9]{24}')
  [ -z "$found" ] || {
    echo "a unit's Environment= holds an OpenBao token"
    return 0
  }
  for pid in $(pgrep -u shop); do
    if tr '\0' '\n' < "/proc/$pid/environ" 2> /dev/null | grep -E '^(BAO|VAULT)_TOKEN=|s\.[A-Za-z0-9]{24}' > /dev/null; then
      echo "a program running as shop has an OpenBao token in its environment"
      return 0
    fi
  done
  echo "nothing standing"
}

check_private() {
  local file owner mode password found
  file=$(sed -n 's/^credentials *= *//p' /etc/shop/shop-api.conf | head -n 1)
  [ -n "$file" ] && [ -f "$file" ] || {
    echo "/etc/shop/shop-api.conf names no credentials file that is there"
    return 0
  }
  owner=$(stat -c %U "$file")
  mode=$(stat -c %a "$file")
  [ "$owner" = shop ] || {
    echo "$file belongs to $owner, not to shop"
    return 0
  }
  case "$mode" in
    400 | 600) ;;
    *)
      echo "$file has the mode $mode: users other than shop can read the database password in it"
      return 0
      ;;
  esac
  # Another workload's user tries.
  as_user report cat "$file" > /dev/null 2>&1 && {
    echo "the user report can read $file"
    return 0
  }
  password=$(sed -n 's/^password=//p' "$file" | head -n 1)
  [ -n "$password" ] || {
    echo "$file has no password= line"
    return 0
  }
  found=$(on_disk "$password" | grep -vxF "$file" | head -n 1)
  [ -z "$found" ] || {
    echo "the API's database password is in another file as well: $found"
    return 0
  }
  echo "shop alone"
}
