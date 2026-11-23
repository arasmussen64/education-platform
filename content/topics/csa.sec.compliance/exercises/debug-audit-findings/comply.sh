# comply.sh: what the checks of Compliance basics' server labs share. A
# check reads it with ". /usr/local/lib/lab-comp/comply.sh". Nothing here
# changes the learner's work; the same file is in each of those labs'
# folders. Each function prints one word when all is well, or one sentence
# about what the machine does, never about where to look.
#
# root_login_off, passwords_met and journal_on_disk each run their rule of
# the benchmark and then look at what the machine does. With the word
# "behaviour" they skip the rule: for a lab whose "pack-check met" already
# runs every rule in scope, so that each OpenSCAP run (a second or two) is
# made once in a round of checks and not twice.
# shellcheck shell=bash

lib=/usr/local/lib/lab-pay
comp=/usr/local/lib/lab-comp

# A fresh marker: hex, so it is safe after "=" and as a journal tag.
marker() { echo "chk$(od -An -N6 -tx1 /dev/urandom | tr -d ' \n')"; }

# rule NAME: the benchmark's result for one rule now.
rule() { "$lib/oscap-rules" "$1" 2> /dev/null | awk '{ print $2 }'; }

# setting CONFIG KEY: the value of a systemd setting as the files that
# outlast a reboot give it (the main file and every drop-in, the last one
# winning). A file under /run is left out: a reboot empties /run. CONFIG is
# as systemd-analyze names it: systemd/journald.conf.
setting() {
  systemd-analyze cat-config "$1" 2> /dev/null | awk -v key="$2" '
    /^# \// { lasting = ($2 !~ /^\/run\//); next }
    /^[[:space:]]*[#;]/ { next }
    lasting {
      line = $0
      sub(/^[[:space:]]+/, "", line)
      eq = index(line, "=")
      if (eq) {
        name = substr(line, 1, eq - 1)
        gsub(/[[:space:]]+$/, "", name)
        if (name == key) {
          value = substr(line, eq + 1)
          gsub(/^[[:space:]]+|[[:space:]]+$/, "", value)
        }
      }
    }
    END { print value }'
}

# seconds VALUE: a time span as systemd reads it, in whole seconds.
seconds() {
  systemd-analyze timespan -- "$1" 2> /dev/null | awk '/μs:/ { printf "%d\n", $2 / 1000000 }'
}

# sshd_started_plainly: do the unit files that outlast a reboot start the
# SSH server with nothing but its files to read? Its start line may hold
# the program, -D, -e and $SSHD_OPTS, and SSHD_OPTS must be empty.
sshd_started_plainly() {
  local starts opts
  starts=$(systemctl cat ssh.service 2> /dev/null | awk '
    /^# \// { lasting = ($2 !~ /^\/run\//); next }
    lasting && /^ExecStart=/ {
      value = substr($0, 11)
      if (value == "") { n = 0 } else { list[++n] = value }
    }
    END { for (i = 1; i <= n; i++) print list[i] }')
  [ "$(echo "$starts" | grep -c .)" = 1 ] || return 1
  for word in $starts; do
    case $word in
      /usr/sbin/sshd | -D | -e | '$SSHD_OPTS') ;;
      *) return 1 ;;
    esac
  done
  opts=$(. /etc/default/ssh 2> /dev/null; echo "$SSHD_OPTS")
  [ -z "$opts" ]
}

# root_login_off: prints "off" when the benchmark's rule passes, a real
# login as root with an authorised key is turned away, and it would be
# after a reboot too.
root_login_off() {
  local live
  if [ "$1" != behaviour ]; then
    [ "$(rule sshd_disable_root_login)" = pass ] || { echo "the benchmark's rule for root logging in over SSH doesn't pass"; return; }
  fi
  live=$("$lib/root-login")
  case $live in
    refused) ;;
    allowed) echo "root can still log in over SSH"; return ;;
    "key removed") echo "the test key has gone from root's authorized_keys, so nothing shows whether root could log in"; return ;;
    *) echo "the SSH server isn't answering, and people still need it: $live"; return ;;
  esac
  sshd_started_plainly || { echo "root is turned away now, but the SSH server isn't started with only its own files to go by, as it must be now and after a reboot"; return; }
  echo off
}

# passwords_met: prints "met" when the three password rules pass and the
# password library, read the way the sign-in programs read it, asks for at
# least 14 characters with a digit and a lower-case letter.
passwords_met() {
  local results values
  if [ "$1" != behaviour ]; then
    results=$("$lib/oscap-rules" accounts_password_pam_minlen accounts_password_pam_dcredit accounts_password_pam_lcredit 2> /dev/null | awk '{ print $2 }' | sort -u)
    [ "$results" = pass ] || { echo "a password rule of the benchmark doesn't pass"; return; }
  fi
  values=$(python3 - 2> /dev/null << 'PY'
import ctypes

lib = ctypes.CDLL("libpwquality.so.1")
lib.pwquality_default_settings.restype = ctypes.c_void_p
lib.pwquality_read_config.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_void_p)]
lib.pwquality_get_int_value.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
settings = lib.pwquality_default_settings()
aux = ctypes.c_void_p()
if lib.pwquality_read_config(settings, None, ctypes.byref(aux)) != 0:
    raise SystemExit("unreadable")
# 3 is the minimum length, 4 the digit credit, 6 the lower-case credit,
# and 17 "enforcing": 0 there means a weak password only gets a warning.
found = []
for number in (3, 4, 6, 17):
    value = ctypes.c_int()
    lib.pwquality_get_int_value(settings, number, ctypes.byref(value))
    found.append(value.value)
print(*found)
PY
  )
  # shellcheck disable=SC2086
  set -- $values
  [ $# = 4 ] || { echo "the password library can't read its settings"; return; }
  if [ "$1" -lt 14 ] || [ "$2" -ge 0 ] || [ "$3" -ge 0 ]; then
    echo "the password library doesn't ask for what the shop's policy asks"
    return
  fi
  [ "$4" -ne 0 ] || { echo "the password library only warns about a weak password, and lets it through"; return; }
  if ! grep -E '^password[[:space:]].*pam_pwquality\.so' /etc/pam.d/common-password > /dev/null \
    || grep -E '^password[[:space:]].*pam_pwquality\.so' /etc/pam.d/common-password | grep -E '(minlen|dcredit|lcredit)=' > /dev/null; then
    echo "the sign-in programs don't apply the password library's settings as written"
    return
  fi
  echo met
}

# journal_on_disk: prints "on disk" when the benchmark's rule passes, the
# settings that outlast a reboot say persistent, and a line logged now can
# be read from the journal's folder under /var/log/journal.
journal_on_disk() {
  local mark try folder
  if [ "$1" != behaviour ]; then
    [ "$(rule journald_storage)" = pass ] || { echo "the benchmark's rule for the journal's storage doesn't pass"; return; }
  fi
  [ "$(setting systemd/journald.conf Storage)" = persistent ] || { echo "the journal's settings that outlast a reboot don't keep it on disk"; return; }
  # The journal's folder has to be on the disk itself: a folder that is
  # really in memory (a link into /run, a tmpfs mounted over it) is emptied
  # by a reboot whatever its name says.
  folder=/var/log/journal/$(cat /etc/machine-id)
  if [ "$(stat -f -c %T "$(readlink -f "$folder")" 2> /dev/null)" = tmpfs ]; then
    echo "the journal's folder under /var/log/journal is kept in memory, not on the disk"
    return
  fi
  mark=$(marker)
  logger -t "$mark" "a line for the check"
  for try in 1 2 3 4 5 6 7 8 9 10; do
    journalctl --directory="$folder" -t "$mark" -o cat 2> /dev/null | grep -F "a line for the check" > /dev/null && { echo "on disk"; return; }
    sleep 0.5
  done
  echo "a line logged a moment ago isn't in the journal's files on disk"
}

# sync_kept: prints "kept" when the bank's settlement sync is as the lab
# shipped it: rsync installed, the shop's unit enabled, running and
# answering on port 873, and its settings untouched.
sync_kept() {
  local try ok=no
  [ "$(dpkg-query -W -f '${db:Status-Status}' rsync 2> /dev/null)" = installed ] || { echo "rsync is no longer installed, and the bank's settlement sync needs it"; return; }
  [ "$(systemctl is-enabled shop-sync 2> /dev/null)" = enabled ] || { echo "the settlement sync is no longer enabled"; return; }
  # The daemon greets first ("@RSYNCD: 31.0 ..."), so one line is read and
  # the connection dropped: nothing waits for the daemon to hang up.
  answers() {
    timeout 3 bash -c 'exec 3<> /dev/tcp/127.0.0.1/873 && IFS= read -r -t 2 line <&3 && [[ $line == @RSYNCD:* ]]' 2> /dev/null
  }
  for try in 1 2 3 4 5; do
    if systemctl is-active --quiet shop-sync && answers; then ok=yes; break; fi
    sleep 1
  done
  [ "$ok" = yes ] || { echo "the settlement sync isn't answering on port 873"; return; }
  cmp -s /etc/shop/rsyncd.conf "$comp/rsyncd.conf" || { echo "the settlement sync's settings have changed"; return; }
  echo kept
}

# earlier_work_stands: prints "stands" when what the audit and the
# vulnerability work left is still so: the audit policy untouched, the
# audit writer running, the trail on disk and sealed with the auditors'
# key where it was left, kept 365 to 400 days by settings that outlast a
# reboot, and a fresh scan of the server finding nothing.
earlier_work_stands() {
  local value kept
  cmp -s /etc/shop/audit.conf "$comp/audit.conf" || { echo "the audit policy has changed"; return; }
  systemctl is-active --quiet shop-audit || { echo "the audit writer is no longer running"; return; }
  if [ "$(setting systemd/journald@audit.conf Storage)" != persistent ] || [ "$(setting systemd/journald@audit.conf Seal)" != yes ] || [ ! -s /srv/auditors/verify-key ]; then
    echo "the audit trail is no longer on disk and sealed, with the auditors' key where it was left"
    return
  fi
  value=$(setting systemd/journald@audit.conf MaxRetentionSec)
  kept=$(seconds "${value:-0}")
  if [ -z "$kept" ] || [ "$kept" -lt $((365 * 86400)) ] || [ "$kept" -gt $((400 * 86400)) ]; then
    echo "the audit trail is no longer kept for 365 to 400 days"
    return
  fi
  [ -z "$("$lib/scan-tsv" 2> /dev/null)" ] || { echo "a fresh scan of the server finds a vulnerability"; return; }
  echo stands
}

# lab_intact: prints "intact" when the benchmark, the crosswalk, the
# scanners and this lab's own lists are as the image shipped them.
lab_intact() {
  local said
  said=$("$lib/base-intact" 2>&1 | head -n 3)
  [ "$said" = intact ] || { echo "$said"; return; }
  sha256sum --quiet -c "$comp/SHA256SUMS" > /dev/null 2>&1 || { echo "one of the files this lab gave you to read has changed"; return; }
  echo intact
}
