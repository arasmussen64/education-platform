#!/usr/bin/env python3
"""Keycloak's admin API for the identity labs: apply a realm's file, say
whether the running realm equals its file, and plain reads and writes for
checks. Runs on the identity provider's machine (the wrappers in
/usr/local/bin enter it first), as root.

  kcapi.py apply [REALM...]     rebuild each realm from /etc/keycloak/realms/REALM.json
  kcapi.py apply-if-changed     the same, only for files changed since they were applied;
                                a file that can't be applied is reported and left
  kcapi.py saved [REALM]        "saved", or how the running realm differs from its file
  kcapi.py get|delete PATH      /admin/realms/PATH, the answer as JSON
  kcapi.py post|put PATH        the same, with a JSON body on standard input
  kcapi.py ready                exit 0 once Keycloak answers
  kcapi.py flows REALM [FLOW] [--file]   a sign-in flow as a tree (kc-flows)
  kcapi.py user-add REALM NAME PASSWORD [--otp] [--key] [GROUP...]
                                a check's own person (idp-user)
  kcapi.py user-disable REALM NAME | user-del REALM NAME
"""

import base64
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

ETC = os.environ.get("KC_ETC", "/etc/keycloak")
APPLIED = "/opt/keycloak/data/applied"
CHK = "chk-"
# Keycloak's log inside an image build (lib/kc-build-run), where there is no journal.
BUILD_LOG = "/tmp/keycloak-build.log"


class FileProblem(SystemExit):
    """A realm file that can't be applied; its text says which file, where
    and why. Left uncaught it ends the command as sys.exit(text) does: the
    text on standard error, exit status 1."""


def settings(path):
    """NAME=value lines of a file, as a dict."""
    found = {}
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                name, value = line.split("=", 1)
                found[name.strip()] = value.strip()
    return found


BASE = os.environ.get("KC_URL") or settings("/etc/idlab/idp").get("IDP_URL", "")
_token = None


def call(method, url, body=None, form=None, token=None):
    """One request; returns (status, bytes). Never raises on an HTTP status."""
    data, headers = None, {}
    if form is not None:
        data = urllib.parse.urlencode(form).encode()
    elif body is not None:
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=25) as answer:
            return answer.status, answer.read()
    except urllib.error.HTTPError as error:
        return error.code, error.read()


def admin_token():
    global _token
    if _token is None:
        admin = settings("/etc/idlab/admin.env")
        status, raw = call(
            "POST",
            BASE + "/realms/master/protocol/openid-connect/token",
            form={
                "grant_type": "password",
                "client_id": "admin-cli",
                "username": admin.get("KC_ADMIN", "admin"),
                "password": admin.get("KC_ADMIN_PASSWORD", ""),
            },
        )
        if status != 200:
            sys.exit(f"keycloak: the admin sign-in was refused ({status}): {raw[:200]!r}")
        _token = json.loads(raw)["access_token"]
    return _token


def admin(method, path, body=None):
    return call(method, BASE + "/admin/realms" + path, body=body, token=admin_token())


def realm_file(realm):
    return f"{ETC}/realms/{realm}.json"


def read_realm(realm):
    """The realm's file as Keycloak takes it: ${NAME} filled in from
    secrets.env, and the realm's signing keys (made at image build) added."""
    path = realm_file(realm)
    text = open(path, encoding="utf-8").read()
    for number, line in enumerate(text.splitlines(), 1):
        if '"..."' in line:
            raise FileProblem(f'{path}, line {number}: a gap ("...") is still to be filled in')
    secrets = settings(f"{ETC}/secrets.env")

    def fill(match):
        name = match.group(1)
        if name not in secrets:
            number = text.count("\n", 0, match.start()) + 1
            raise FileProblem(f"{path}, line {number}: ${{{name}}} is not in {ETC}/secrets.env")
        # A value never adds a line, so a line number below is the file's own.
        return json.dumps(secrets[name])[1:-1]

    filled = re.sub(r"\$\{([A-Z0-9_]+)\}", fill, text)
    try:
        data = json.loads(filled)
    except json.JSONDecodeError as error:
        raise FileProblem(f"{path}, line {error.lineno}: not valid JSON: {error.msg}") from None
    if not isinstance(data, dict) or data.get("realm") != realm:
        raise FileProblem(f'{path}: "realm" must be "{realm}", the file\'s name')
    keys = sorted(glob.glob(f"{ETC}/keys/{realm}/*.key"))
    if keys and "components" not in data:
        # Later names win: the last key signs, the others stay published.
        # A file NAME.passive beside a key keeps it for checking only.
        providers = []
        for priority, key in enumerate(keys, 100):
            name = os.path.basename(key)[:-4]
            passive = os.path.exists(key[:-4] + ".passive")
            providers.append(
                {
                    "name": name,
                    "providerId": "rsa",
                    "config": {
                        "privateKey": [open(key).read()],
                        "certificate": [open(key[:-4] + ".crt").read()],
                        "priority": [str(priority)],
                        "algorithm": ["RS256"],
                        "keyUse": ["SIG"],
                        "active": ["false" if passive else "true"],
                    },
                }
            )
        data["components"] = {"org.keycloak.keys.KeyProvider": providers}
    return data


def reason_in(log):
    """Keycloak's own reason for a refusal, from its log: the text of the
    last "Uncaught server error" line without the Java class, or ""."""
    found = re.findall(r"Uncaught server error: (?:[\w.$]+: )?(.+)", log)
    return found[-1].strip() if found else ""


def keycloaks_reason(since):
    """Some files Keycloak refuses with no more than "unknown error" (a
    person in a group that isn't there is one) and writes the reason in
    its log. This reads it there: in the unit's journal from `since`
    (seconds since 1970) on, or, inside an image build, in the build's log."""
    machine = settings("/etc/idlab/idp").get("IDP_MACHINE", "idp")
    journal = ["journalctl", "-u", f"keycloak@{machine}", "--since", f"@{int(since)}", "-o", "cat", "--no-pager"]
    for _ in range(5):  # the line reaches the journal a moment after the answer
        try:
            if os.path.exists(BUILD_LOG):
                log = open(BUILD_LOG, encoding="utf-8", errors="replace").read()
            else:
                log = subprocess.run(journal, capture_output=True, text=True, timeout=10).stdout
            if reason_in(log):
                return reason_in(log)
            time.sleep(0.3)
        except (OSError, subprocess.SubprocessError):
            return ""
    return ""


def create(data, path):
    """Makes the realm `data` describes; `path` is the file it came from,
    for the message when Keycloak won't have it."""
    asked = time.time()
    status, raw = call("POST", BASE + "/admin/realms", body=data, token=admin_token())
    if status != 201:
        try:
            message = json.loads(raw).get("errorMessage") or raw.decode()
        except (ValueError, AttributeError):
            message = raw.decode(errors="replace")
        if status >= 500:
            message = keycloaks_reason(asked) or message
        raise FileProblem(f"{path}: Keycloak refused it ({status}): {message[:300]}")


def build_copy(realm, data):
    """The throwaway realm chk-REALM, built from the file's data beside the
    running realm: to try a file out before the running realm is touched,
    and to compare the running realm with. It is the whole file, people
    and service accounts too, so a file Keycloak would refuse is refused
    here; only the ids are left out (a person's id can be used once in a
    Keycloak). Raises FileProblem; the caller removes the copy."""
    copy = strip_ids(data)
    copy["realm"] = CHK + realm
    admin("DELETE", f"/{CHK}{realm}")
    create(copy, realm_file(realm))


def sha(realm):
    digest = hashlib.sha256()
    paths = [realm_file(realm), f"{ETC}/secrets.env"]
    for path in paths + sorted(glob.glob(f"{ETC}/keys/{realm}/*")):
        if os.path.exists(path):
            # By its name under /etc/keycloak, so the checksum taken at image
            # build (when the folder is /etc/netns/idp/keycloak) still matches.
            name = os.path.relpath(path, ETC).encode()
            digest.update(name + b"\0" + open(path, "rb").read())
    return digest.hexdigest()


def realms():
    return sorted(os.path.basename(p)[:-5] for p in glob.glob(f"{ETC}/realms/*.json"))


def apply(realm):
    """Rebuilds the realm from its file. A file that can't be applied
    raises FileProblem before the running realm is touched: one this script
    can see is wrong stops in read_realm, and one only Keycloak can judge (a
    person in a group that isn't there) stops in a throwaway copy, built
    first."""
    data = read_realm(realm)
    status, _ = admin("GET", f"/{realm}")
    if status == 200:
        try:
            build_copy(realm, data)
        finally:
            admin("DELETE", f"/{CHK}{realm}")
        admin("DELETE", f"/{realm}")
    try:
        create(data, realm_file(realm))
    except FileProblem as problem:
        if status != 200:
            raise
        # The copy was taken and the realm was not (the copy is built
        # without the file's ids, so a fault in those shows only here).
        raise FileProblem(f"{problem}. Realm {realm} is gone until the file is mended and applied") from None
    os.makedirs(APPLIED, exist_ok=True)
    open(f"{APPLIED}/{realm}.sha256", "w").write(sha(realm))
    print(f"keycloak: realm {realm} rebuilt from {realm_file(realm)}")


def changed(realm):
    try:
        return open(f"{APPLIED}/{realm}.sha256").read() != sha(realm)
    except OSError:
        return True


def not_applied(realm, problem, there):
    """The one message for a realm file that couldn't be applied when
    Keycloak started: which file, where and why (`problem`), what Keycloak
    serves meanwhile (`there`: the realm exists) and what to type."""
    if there:
        serves = f"Realm {realm} was not rebuilt: Keycloak serves it as it was before the file changed"
    else:
        serves = f"There is no realm {realm}"
    return f"keycloak: {problem}. {serves}. Mend the file, then: sudo realm-apply {realm}"


def apply_changed():
    """Applies every realm file changed since it was last applied. A file
    that can't be applied is reported and left as it is, and the other
    realms' files are still applied. Returns 3 when any was left."""
    # Under systemd, "<4>" makes the line a warning in the journal.
    mark = "<4>" if os.environ.get("JOURNAL_STREAM") else ""
    left = 0
    for realm in realms():
        if not changed(realm):
            continue
        try:
            apply(realm)
        except FileProblem as problem:
            left = 3
            status, _ = admin("GET", f"/{realm}")
            print(mark + not_applied(realm, problem, status == 200), file=sys.stderr, flush=True)
    return left


def strip_ids(x):
    if isinstance(x, dict):
        return {k: strip_ids(v) for k, v in x.items() if k not in ("id", "containerId")}
    if isinstance(x, list):
        return [strip_ids(v) for v in x]
    return x


# What realm-saved leaves out wherever it appears: values Keycloak makes
# for itself, never the same in two builds of one file, which nobody can
# set to any effect. The base's README gives the reason for each.
STAMPED = (
    "createdTimestamp",  # the moment a service account was made
    "client.secret.creation.time",  # the moment a client's secret was made
    "internalId",  # an identity provider's id
)
DROPPED = ("id", "containerId", "subComponents", *STAMPED)
THE_FILES = "(the file's secret)"
NOT_THE_FILES = "(not the file's secret)"


def file_secrets(data):
    """The secret of each client the realm file gives one, by client."""
    return {c.get("clientId"): c["secret"] for c in data.get("clients", []) if "secret" in c}


def comparable(export, fresh, secrets, filed):
    """One of Keycloak's exports as realm-saved compares it.

    Of its users only the service accounts stay: they are settings (a
    client's own roles and groups), and an export lists no other user.
    An export hides every secret, so where the file gives a client its
    secret (`filed`), the hidden value is replaced by a word saying whether
    the realm's real one (`secrets`, from the list of clients) is the
    file's. Then normal() takes out what differs between any two builds."""
    export = dict(export)
    if "users" in export:
        export["users"] = [u for u in export["users"] if u.get("serviceAccountClientId")]
    clients = []
    for client in export.get("clients", []):
        name = client.get("clientId")
        if name in filed:
            client = dict(client, secret=THE_FILES if secrets.get(name) == filed[name] else NOT_THE_FILES)
        clients.append(client)
    if clients:
        export["clients"] = clients
    return normal(export, fresh)


def shown(path, value):
    """A value as a difference's line prints it: cut short, and never a
    secret (a setting whose name says "secret", but for the two words
    above, which hold none)."""
    setting = path.rsplit("]", 1)[-1].lower()  # what follows the last [name]
    if "secret" in setting and value not in (THE_FILES, NOT_THE_FILES, "(not set)"):
        return '"(a secret, not shown)"'
    return json.dumps(value)[:120]


def normal(x, fresh):
    """An export with what differs between any two builds of one file taken
    out: ids, the moments Keycloak stamps (STAMPED), the copy's name, and
    the keys Keycloak makes for itself."""
    if isinstance(x, dict):
        return {k: normal(v, fresh) for k, v in sorted(x.items()) if k not in DROPPED}
    if isinstance(x, list):
        items = [
            normal(v, fresh)
            for v in x
            if not (isinstance(v, dict) and str(v.get("name", "")).startswith("fallback-"))
        ]
        return sorted(items, key=lambda v: json.dumps(v, sort_keys=True))
    if isinstance(x, str) and fresh:
        return x.replace(CHK, "")
    return x


def name_of(x):
    if isinstance(x, dict):
        # flowAlias: a flow's step that is a sub-flow has no authenticator.
        for key in ("clientId", "alias", "name", "username", "providerId", "authenticator", "flowAlias"):
            if isinstance(x.get(key), str):
                return x[key]
    return None


def differences(live, fresh, path=""):
    if type(live) is not type(fresh):
        return [(path, live, fresh)]
    out = []
    if isinstance(live, dict):
        for key in sorted(set(live) | set(fresh)):
            if key not in live or key not in fresh:
                pair = (live.get(key, "(not set)"), fresh.get(key, "(not set)"))
                out.append((f"{path}.{key}", *pair))
            else:
                out += differences(live[key], fresh[key], f"{path}.{key}")
    elif isinstance(live, list):
        names = [name_of(v) for v in live + fresh]
        if names and all(names) and len(set(names)) >= max(len(live), len(fresh)):
            a, b = {name_of(v): v for v in live}, {name_of(v): v for v in fresh}
            for key in sorted(set(a) | set(b)):
                if key not in a:
                    out.append((f"{path}[{key}]", "(not there)", "there"))
                elif key not in b:
                    out.append((f"{path}[{key}]", "there", "(not there)"))
                else:
                    out += differences(a[key], b[key], f"{path}[{key}]")
        elif live != fresh:
            out.append((path, live, fresh))
    elif live != fresh:
        out.append((path, live, fresh))
    return out


def export(realm):
    status, raw = admin(
        "POST", f"/{realm}/partial-export?exportClients=true&exportGroupsAndRoles=true"
    )
    if status != 200:
        sys.exit(f"realm {realm} isn't there ({status})")
    return json.loads(raw)


def client_secrets(realm):
    """Each client's real secret, by client: the list of clients gives it,
    where an export prints stars."""
    status, raw = admin("GET", f"/{realm}/clients")
    if status != 200:
        sys.exit(f"realm {realm} isn't there ({status})")
    return {c.get("clientId"): c.get("secret") for c in json.loads(raw)}


def saved(realm):
    """Builds a throwaway copy of the realm from its file, beside the running
    one, compares what Keycloak says about each, and removes the copy: the
    same idea as netlab verify. People aren't compared (checks and
    provisioning make and change them at run time); service accounts and
    everything else are."""
    data = read_realm(realm)
    filed = file_secrets(data)
    try:
        build_copy(realm, data)
        fresh = comparable(export(CHK + realm), True, client_secrets(CHK + realm), filed)
    finally:
        admin("DELETE", f"/{CHK}{realm}")
    live = comparable(export(realm), False, client_secrets(realm), filed)
    found = differences(live, fresh)
    if not found:
        print("saved")
        return 0
    print(f"realm {realm} differs from a fresh build of {realm_file(realm)}:")
    for path, now, file in found[:3]:
        print(f"  {path.lstrip('.')}: now {shown(path, now)}, from its file {shown(path, file)}")
    return 1


# --- kc-flows: a sign-in flow as a tree -------------------------------------------


def flow_line(depth, requirement, name, is_flow, config):
    text = "  " * depth + f"{requirement:<11} {name}"
    if is_flow:
        text += "  (a sub-flow: its steps are indented below)"
    if config:
        text += "  [" + ", ".join(f"{k}={v}" for k, v in sorted(config.items())) + "]"
    return text


def flow_lines_from_file(data, alias, depth=0):
    """A flow written in a realm file, as lines: one per step, indented by
    its depth, with its requirement and, for a step that has settings, the
    settings. Returns None when the file doesn't define the flow."""
    flows = {f.get("alias"): f for f in data.get("authenticationFlows", [])}
    configs = {c.get("alias"): c.get("config", {}) for c in data.get("authenticatorConfig", [])}
    if alias not in flows:
        return None
    lines = []
    steps = sorted(flows[alias].get("authenticationExecutions", []), key=lambda s: s.get("priority", 0))
    for step in steps:
        requirement = step.get("requirement", "?")
        # Keycloak's own exports spell the field "autheticatorFlow" too.
        if step.get("authenticatorFlow") or step.get("autheticatorFlow"):
            name = step.get("flowAlias", "?")
            lines.append(flow_line(depth, requirement, name, True, None))
            inner = flow_lines_from_file(data, name, depth + 1)
            lines += inner if inner is not None else [flow_line(depth + 1, "?", "(not in the file)", False, None)]
        else:
            config = configs.get(step.get("authenticatorConfig"))
            lines.append(flow_line(depth, requirement, step.get("authenticator", "?"), False, config))
    return lines


def flow_lines_from_server(executions, config_of):
    """The same lines from the admin API's list of a flow's steps (each
    carries its depth as "level"); config_of(ID) fetches a step's settings."""
    lines = []
    for step in executions:
        is_flow = bool(step.get("authenticationFlow"))
        config = config_of(step["authenticationConfig"]) if step.get("authenticationConfig") else None
        name = step.get("displayName") if is_flow else step.get("providerId")
        lines.append(flow_line(step.get("level", 0), step.get("requirement", "?"), name or "?", is_flow, config))
    return lines


def flows(argv):
    from_file = "--file" in argv
    rest = [a for a in argv if a != "--file"]
    if not rest:
        sys.exit("usage: kc-flows REALM [FLOW] [--file]")
    realm = rest[0]
    if from_file:
        data = read_realm(realm)
        alias = rest[1] if len(rest) > 1 else data.get("browserFlow", "browser")
        lines = flow_lines_from_file(data, alias)
        if lines is None:
            print(
                f"{realm_file(realm)} doesn't define a flow called {alias!r}: the realm uses "
                f"Keycloak's built-in one (kc-flows {realm} shows it, from the running server)"
            )
            return 1
        print(f"flow {alias!r}, from {realm_file(realm)}:")
    else:
        status, raw = admin("GET", f"/{realm}")
        if status != 200:
            sys.exit(f"realm {realm} isn't there ({status})")
        alias = rest[1] if len(rest) > 1 else json.loads(raw).get("browserFlow", "browser")
        status, raw = admin("GET", f"/{realm}/authentication/flows/{urllib.parse.quote(alias)}/executions")
        if status != 200:
            sys.exit(f"realm {realm} has no flow called {alias!r}")

        def config_of(config_id):
            status, raw = admin("GET", f"/{realm}/authentication/config/{config_id}")
            return json.loads(raw).get("config", {}) if status == 200 else None

        lines = flow_lines_from_server(json.loads(raw), config_of)
        print(f"flow {alias!r}, as realm {realm} runs it now:")
    print("\n".join(lines))
    return 0


# --- idp-user: a check's own person -----------------------------------------------


def person(name, password, groups, user_id, otp_secret=None, key_data=None):
    """A throwaway person as Keycloak imports one: a password, and when asked
    an authenticator app's secret or a security key's public half."""
    credentials = [{"type": "password", "value": password, "temporary": False}]
    if otp_secret:
        totp = {"subType": "totp", "digits": 6, "counter": 0, "period": 30, "algorithm": "HmacSHA1"}
        credentials.append(
            {
                "type": "otp",
                "userLabel": "made by a check",
                "secretData": json.dumps({"value": otp_secret}),
                "credentialData": json.dumps(totp),
            }
        )
    if key_data:
        credentials.append(
            {"type": "webauthn", "userLabel": "made by a check", "credentialData": key_data, "secretData": "{}"}
        )
    return {
        "id": user_id,
        "username": name,
        "enabled": True,
        "firstName": name.capitalize(),
        "lastName": "Check",
        "email": f"{name}@check.test",
        "emailVerified": True,
        "groups": ["/" + g for g in groups],
        "credentials": credentials,
    }


def user_files_gone(name):
    for path in (f"/etc/idlab/otp/{name}", f"/etc/idlab/keys/{name}.key"):
        if os.path.exists(path):
            os.remove(path)


def user_add(rest):
    """user-add REALM NAME PASSWORD [--otp] [--key] [GROUP...]. With --otp
    the person has an authenticator app, its secret in /etc/idlab/otp/NAME;
    with --key a security key, in /etc/idlab/keys/NAME.key. user-del removes
    both files with the person."""
    flags = {a for a in rest if a in ("--otp", "--key")}
    rest = [a for a in rest if a not in flags]
    if len(rest) < 3:
        sys.exit("usage: idp-user add REALM NAME PASSWORD [--otp] [--key] [GROUP...]")
    realm, name, password, groups = rest[0], rest[1], rest[2], rest[3:]
    user_id = str(uuid.uuid4())
    otp_secret = key_data = None
    if "--otp" in flags:
        otp_secret = os.urandom(10).hex()
        os.makedirs("/etc/idlab/otp", exist_ok=True)
        with open(f"/etc/idlab/otp/{name}", "w") as out:
            out.write(base64.b32encode(otp_secret.encode()).decode().rstrip("="))
    if "--key" in flags:
        os.makedirs("/etc/idlab/keys", exist_ok=True)
        host = urllib.parse.urlsplit(settings("/etc/idlab/idp").get("IDP_URL", "")).hostname or ""
        made = subprocess.run(
            ["/usr/local/lib/idlab/make-key", user_id, host, f"/etc/idlab/keys/{name}.key"],
            capture_output=True,
            text=True,
            check=True,
        )
        key_data = made.stdout.strip()
    body = {
        "ifResourceExists": "FAIL",
        "users": [person(name, password, groups, user_id, otp_secret, key_data)],
    }
    status, raw = admin("POST", f"/{realm}/partialImport", body=body)
    if status != 200:
        user_files_gone(name)
        sys.exit(f"couldn't make {name} ({status}): {raw[:200]!r}")
    return 0


def main(argv):
    if not argv:
        sys.exit(__doc__)
    verb, rest = argv[0], argv[1:]
    if verb == "ready":
        status, _ = call("GET", BASE + "/realms/master")
        return 0 if status == 200 else 1
    if verb == "apply":
        for realm in rest or realms():
            apply(realm)
        return 0
    if verb == "apply-if-changed":
        return apply_changed()
    if verb == "saved":
        return max([saved(realm) for realm in rest or realms()] or [0])
    if verb == "flows":
        return flows(rest)
    if verb == "user-add":
        return user_add(rest)
    if verb in ("user-disable", "user-del"):  # user-disable REALM NAME
        realm, name = rest[0], rest[1]
        query = urllib.parse.urlencode({"username": name, "exact": "true"})
        status, raw = admin("GET", f"/{realm}/users?{query}")
        found = json.loads(raw) if status == 200 else []
        if not found:
            sys.exit(f"no user called {name} in {realm}")
        path = f"/{realm}/users/{found[0]['id']}"
        if verb == "user-del":
            status, _ = admin("DELETE", path)
            user_files_gone(name)
        else:
            status, _ = admin("PUT", path, body=dict(found[0], enabled=False))
        return 0 if status < 300 else 1
    if verb in ("get", "delete", "post", "put"):
        body = sys.stdin.buffer.read() if verb in ("post", "put") else None
        status, raw = admin(verb.upper(), "/" + rest[0].lstrip("/"), body=body)
        sys.stdout.write(raw.decode(errors="replace"))
        if raw and not raw.endswith(b"\n"):
            sys.stdout.write("\n")
        return 0 if status < 300 else 1
    sys.exit(__doc__)


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except urllib.error.URLError as error:
        sys.exit(f"keycloak isn't answering at {BASE}: {error.reason}")
