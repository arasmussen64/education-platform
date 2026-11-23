# The identity labs' check helpers. A check starts with
#   . /usr/local/lib/idlab/idlib.sh
# which also brings the network base's helpers (wait_for, json, intact ...).
# Checks run as root on the lab machine. The base's README
# (content/lab-bases/id/README.md) lists them all, with the rules.
. /usr/local/lib/netlab/checklib.sh
. /etc/idlab/idp

# kc VERB PATH: Keycloak's admin API, on the identity provider's machine.
#   kc get shop/clients?clientId=shop-web   kc post shop/users < user.json
kc() { on "$IDP_MACHINE" python3 /usr/local/lib/idlab/kcapi.py "$@"; }

# kc_saved REALM: prints "saved" when the running realm equals a fresh
# build of its file (so a reload or a rebuild changes nothing), otherwise
# how it differs. A change made only with kcadm.sh or the admin console
# fails it. It takes a realm, not a machine: kc_saved shop. Never run it
# while a check holds something of its own in the realm (a person made with
# idp-user is the one exception it ignores; the rule is still to remove
# them first).
kc_saved() { kc saved "$@"; }

# kc_ready: exit 0 once Keycloak answers. The boot already waits for it;
# this is for a check that has restarted or reloaded it.
kc_ready() { kc ready; }

# password_of USER: the password made for USER at image build.
password_of() { awk -v u="$1" '$1 == u { print $2 }' /etc/idlab/accounts; }

# secret_of NAME: a value from the realm's secrets.env (a client's secret,
# say), as the identity provider's machine has it.
secret_of() { on "$IDP_MACHINE" awk -F= -v n="$1" '$1 == n { print substr($0, length(n) + 2) }' /etc/keycloak/secrets.env; }

# clock_offset MACHINE: MACHINE's clock minus the real time, in seconds.
clock_offset() { /usr/local/lib/idlab/machine-clock offset "$1"; }

# clock_synced MACHINE: prints "in sync with time server NAME" and exits 0
# when a server MACHINE's /etc/chrony/chrony.conf names answers right now
# and MACHINE's clock agrees with it; otherwise prints why not and exits 1.
# It asks the server itself, so a clock set right by hand beside a time
# sync that can't reach its server fails.
clock_synced() {
  NETLAB_REAL_CLOCK=1 ip netns exec "$1" /usr/local/lib/netlab/lab-enter "$1" /usr/local/lib/idlab/timesync --check
}

# client_field REALM CLIENT EXPR: a field of a client as the running server
# has it; EXPR is Python over the client as d ("d['redirectUris']").
client_field() { kc get "$1/clients?clientId=$2" | json "(lambda d: $3)(d[0])"; }
