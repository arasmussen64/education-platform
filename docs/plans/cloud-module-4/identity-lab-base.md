# Shared design: the identity-lab base, `lab-base-id` (topics 41, 44, 47 and Checkpoint 4 part 2)

Design only, by the `identity-lab-base` designer, 2026-11-22. Nothing here is in the repository. Every mechanism marked **tried** ran on 2026-11-22 on the owner's PC (Docker Desktop 29.8.2, kernel 6.18.33.2-microsoft-standard-WSL2, 8 CPUs, 15.5 GiB for Docker), in privileged systemd containers started by a copy of `tools/labcheck.py` (`--privileged --cgroupns=private --tmpfs /run --tmpfs /run/lock`, `/sbin/init`). **Nothing has run on a GitHub runner.** The working prototype is `prototypes/identity-lab-base/` (its `README.md` lists the files and how to run it again); every container and image it made was removed afterwards.

An earlier design of this base (2026-11-12) left no file behind, only the names the other briefs quote from it (`keycloak@idp`, a realm file, `kc_saved`, `signin`, `jwt show`, `/etc/idlab/accounts`). This one was written to fit those briefs; section 13 lists every place it does not.

## 1. The decisions, in one place

| Question | Decision | Why, in a line |
| --- | --- | --- |
| Which identity provider | **Keycloak 26.8.2** (Apache-2.0), pinned by sha256 | The only candidate that does OIDC, SAML, SCIM, WebAuthn, one-time codes and conditional sign-in flows in one program, with no database server beside it (section 2) |
| Where it runs | On a machine of the network-lab base: `FROM lab-base-net`, as the unit `keycloak@idp` | The learner already knows machines, `on`, `name@machine` units and `journalctl -u`; every message crosses a network a check can read |
| What lasts | **The realm's file**, `/etc/keycloak/realms/REALM.json` on the identity provider's machine. `sudo realm-apply` (or `sudo systemctl reload keycloak@idp`) rebuilds the realm from it; `realm-saved` says whether the running realm equals a fresh build of the file | A change made only in the admin console or with `kcadm.sh` is drift, caught the way `frr_saved` and `netlab verify` catch it in Module 3 |
| The relying party | Apache 2.4 with mod_auth_openidc (OIDC) and mod_auth_mellon (SAML), as `apache2@M`; and `stock-api@M`, a 120-line stand-in API whose settings file and log a check can read | Real modules where the protocol is the lesson; a stand-in where the API is scenery |
| Reading tokens | `jwt show` and `jwt verify` (python3, RS256 only); `jq` and `xmlsec1` in the image | A decoder a beginner can run; the same code is what checks verify with |
| A check's own verdict on a token | The check signs in itself, as the app (`signin --code`, with its own PKCE pair, state and nonce), and runs `jwt verify`: signature against the provider's published keys, issuer, audience, expiry, nonce | Never trusts the app's word |
| Security keys | A **software authenticator inside `signin`** (python3-fido2): registers and signs in at Keycloak's real WebAuthn pages over HTTPS. Works; no browser needed | Section 8 |
| Clock skew | **libfaketime**, switched on per machine by `lab-enter`; a machine's clock starts from its "hardware clock" at every boot and is set right by a stand-in time service, `timesync@M`. Time namespaces can't do it | Section 9 |
| What `labcheck` needs | One change: build a base's own base first. No memory budget, no longer boot wait | Section 12 |

Measured, all on the owner's PC: image 1.34 GB as Docker reports it (the network base is 659 MB; 871 MB of files against 467 MB); one running lab 550 to 640 MiB; four at once 2.4 GiB at most; container start to "booted, Keycloak answering" 9.5 s; after a restart 7.4 to 7.9 s; a whole sign-in through the scripted browser 0.3 s; the prototype lab's full contract (pristine, solution, restart trial, six wrong fixes) 150 s alone and 241 to 244 s with four at once. Section 10 has the table.

## 2. Which identity provider

### The candidates

Versions, dates and licences are from GitHub's API for each repository, read 2026-11-22. "Confirmed" means read on the project's own page that day (section 15); "from memory" means it was not, and the writer must not repeat it as fact.

| | Keycloak | Dex | authentik | ZITADEL | Ory (Hydra + Kratos) | Authelia | Kanidm |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Latest release | 26.8.2, 2026-11-05 | v2.46.1, 2026-10-21 | 2026.8.6, 2026-11-20 | v4.20.5, 2026-11-18 | v26.2.0, 2026-03-20 | v4.39.28, 2026-09-17 | v1.12.1, 2026-11-13 |
| Licence | Apache-2.0 | Apache-2.0 | MIT, with a separately licensed `authentik/enterprise/` folder (its `LICENSE`, confirmed) | AGPL-3.0 (its `LICENSE`, confirmed) | Apache-2.0 | Apache-2.0 | MPL-2.0 |
| OIDC provider | yes (**tried**) | yes, the only protocol it speaks to apps ("uses OpenID Connect to drive authentication for other apps", confirmed; **tried**) | yes (provider list, confirmed) | yes | Hydra: yes, certified (confirmed); it has no users of its own ("a headless API") | yes, but "an open beta feature" (confirmed) | yes (OAuth shown on its front page; details from memory) |
| SAML identity provider for apps | yes (**tried** with mod_auth_mellon) | **no**: SAML only as a connector to an upstream provider (confirmed) | yes (provider list, confirmed) | from memory: yes | not in the open-source programs (not mentioned on the pages read) | **no** (not mentioned, confirmed) | from memory: no |
| SCIM | **a SCIM server**, feature `scim-api`, type DEFAULT in 26.8.2 (its own `/admin/serverinfo`, **tried**); switched on per realm (`"scimApiEnabled": true`), at `/realms/REALM/scim/v2/` (**tried**: 401 without a realm token, 404 until switched on) | no (confirmed: not mentioned) | "SCIM" is a provider type (confirmed); which direction was not confirmed | not confirmed | not confirmed | no | not confirmed |
| One-time codes, WebAuthn | both (**tried**: TOTP from the realm file; WebAuthn registered and used) | none of its own (confirmed: not mentioned) | from memory: both | passkeys (confirmed on a link card) | Kratos: TOTP and passkeys (confirmed) | security keys, passkeys, one-time passwords, Duo (confirmed in its navigation) | from memory: passkeys first |
| Conditional rules | sign-in flows with conditions by role, credential and more, in the realm (**tried**: the default flow's "Conditional 2FA"; a role condition was tried by the strong-auth designer) | no | flows and policies (from memory) | not confirmed | not confirmed | access-control rules per request (confirmed it has them; they belong to its proxy role) | not confirmed |
| Needs beside itself | **nothing**: a JVM and a file database (H2) in its own folder | nothing (in-memory, SQLite) | PostgreSQL, a server and a worker; "at least 2 CPU cores and 2 GB of RAM" (confirmed) | "A PostgreSQL instance" (confirmed); "1 CPU and 512MB" for tests (confirmed) | from memory: a database, and Hydra needs a login-and-consent app (Kratos plus a UI), so three programs | nothing | nothing |
| Configuration in files | the realm as JSON through its admin API or `kc.sh import`; this base makes the file the source (section 5) | **one YAML file is everything** (**tried**) | YAML "blueprints" in `/blueprints`, applied when a file changes (confirmed) | not confirmed | YAML per program | one YAML file | a CLI against a running server (from memory) |
| Size, memory, start | 184 MB of files plus a 194 MB JRE; 420 to 510 MB of memory; 7 to 10 s (**measured**) | image 218 MB (the `dex` program itself is 46.5 MB), 10.6 MiB, listening 0.17 s after start (**measured**) | not tried | not tried | not tried | not tried | not tried |
| Offline | yes (**tried**: no lab machine reaches the internet) | yes (**tried**) | not tried | not tried | not tried | not tried | not tried |

### The two tried

**Keycloak 26.8.2**: started on a network-base machine over HTTPS, configured from a file, issued tokens through the code flow with PKCE, signed a SAML assertion, registered and used a security key, checked a one-time code, survived restarts, and kept the contract of a whole lab four at a time (sections 5 to 11).

**Dex v2.46.1** (`prototypes/identity-lab-base/dex/config.yaml`): started from one YAML file with a static client and a static password, issued an ID token (822 characters) by the password grant, and restarted. It used 10.6 MiB. With `storage: memory` it made new signing keys at every start (`rotating signing keys reason="missing signing key"`), so every earlier token dies at a restart; SQLite storage would keep them (not tried). Its discovery document lists `authorization_code`, `password`, `refresh_token`, the device grant and token exchange.

### Why Keycloak

Dex is the better tool for one job: an OIDC-only lab that boots in a fifth of a second. It cannot carry this module. Topic 44 needs a SAML identity provider and a SCIM server; topic 41 needs WebAuthn, one-time codes and a flow that requires a key by role; topic 47 needs to disable a user and see the next refresh refused; none of those exists in Dex. authentik and ZITADEL cover the features but each needs a PostgreSQL server beside it (and authentik a worker), which is a second and third daemon in every container start of every wrong fix in CI, for no teaching gain; ZITADEL is AGPL-3.0, which is free to use here but is one more licence to explain. Ory is three programs and no SAML. Authelia's OIDC is "open beta" and it has no SAML or SCIM. Kanidm has no SAML.

Under the owner's rule (best learning, best retention, free): Keycloak is free, is the provider most open-source shops actually run, and one tool across four topics and a checkpoint is retrieval practice of the same commands in new settings. Its cost is weight (section 10), which the measurements show is affordable.

**Pin.** `https://github.com/keycloak/keycloak/releases/download/26.8.2/keycloak-26.8.2.tar.gz`, 173,550,645 bytes, sha256 `dd124787283918bc597628887168333465ee2a811a389e0003569e52be7e487f` (GitHub's release asset digest, read 2026-11-22; the download in the prototype's Dockerfile checked it). Released 2026-11-05, so older than two weeks. It is the repository's second download from outside Ubuntu's archive, after step-ca.

## 3. The image

`prototypes/identity-lab-base/base/Dockerfile`, proposed as `content/lab-bases/id/Dockerfile`:

| Layer | What | Size | From |
| --- | --- | --- | --- |
| 0 | `FROM lab-base-net` | 659 MB as Docker reports it | the network base, unchanged |
| 1 | `ca-certificates openjdk-21-jre-headless apache2 libapache2-mod-auth-openidc libapache2-mod-auth-mellon libapache2-mod-oauth2 xmlsec1 jq faketime python3-fido2 oathtool` | 234 MB | Ubuntu 24.04's archive |
| 2 | Keycloak 26.8.2, unpacked in `/opt/keycloak` | 193 MB | GitHub release, sha256 above |
| 3 | The base's files; `kc.sh build --db=dev-file`; Keycloak started once so its database holds the master realm and an administrator whose password is made then (`/etc/idlab/admin.env`, root only) | a few MB | the base's folder |

What each package is and its licence (versions are Ubuntu 24.04's candidates on 2026-11-22):

| Package | Version | Licence | For |
| --- | --- | --- | --- |
| openjdk-21-jre-headless | 21.0.13.1+2 | GPL-2.0 with the Classpath exception | Keycloak |
| apache2 | 2.4.58 | Apache-2.0 | the relying party |
| libapache2-mod-auth-openidc | 2.4.15.1 | Apache-2.0 | OIDC relying party (**tried**) |
| libapache2-mod-auth-mellon | 0.19.0 | GPL-2.0+ with an OpenSSL exception (the writer re-reads its copyright file) | SAML service provider (**tried**) |
| libapache2-mod-oauth2 | 3.3.1 | the federation brief read AGPL-3.0+ in its copyright file | resource server (installed; **not tried here**) |
| xmlsec1 | 1.2.39 | MIT | checking a SAML signature by hand |
| jq | 1.7.1 | MIT | reading JSON that isn't a token (section 13, question 4) |
| faketime (libfaketime) | 0.9.10 | GPL-2.0 (its README: "released under the GNU General Public License") | a machine's clock; backdating the lab's certificates |
| python3-fido2 | 1.1.2 | BSD-2-Clause | the software security key; it brings python3-cryptography (Apache-2.0 or BSD), which `jwt`, `stock-api` and `mint-token` use |
| oathtool | 2.6.11 | GPL-3.0+ | one-time codes on the command line |
| ca-certificates | archive | MPL-2.0 and others | the download; and the lab CA joins the same bundle |

Build times (**measured**): the base's own three layers from nothing, on top of an existing `lab-base-net`, 65 s (packages 15.5 s, the download 11 s, layer 3 30 s, of which `kc.sh build` is about 18 s); a rebuild after changing a helper 33 s (layer 3 again); a lab's own image 13 s, of which baking its realm into the database is 9 s. On a CI shard, add the network base's own cold build (about 45 s on this PC by its README).

**Why on top of the network base and not a base of its own.** A sign-in is four machines talking: a laptop, the provider, the app, the API. On the network base each is a machine with an address and a name, `on office ...` is the browser, `tcpdump` on the switch shows the front channel and the back channel as different conversations (the app's own request to the token endpoint never passes the laptop), and a firewall or a phishing machine is one more line of topology. The learner arrives from Module 3 knowing all of it. A single-machine base would save 467 MB of files and nothing else, and would cost that picture.

## 4. A lab on the base

```text
exercises/<lab>/
├── exercise.yaml      runtime: lab, lab: { init: systemd, restart_trial: true }
├── Dockerfile         below
├── topology           netlab's words, with: run idp keycloak / run app apache2 timesync / run api stock-api
├── machines/idp/keycloak/realms/shop.json       the realm (no secret in it: ${NAME} placeholders)
├── machines/app/apache2/sites-available/orders.conf
├── machines/api/stock-api/api.conf
├── checks.yaml  solution.sh  wrong/*.sh
```

```dockerfile
FROM lab-base-id
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
RUN netlab enable \
 && idlab idp idp https://idp.shop.test \
 && idlab names idp.shop.test=10.0.5.10 app.shop.test=10.0.5.20 api.shop.test=10.0.5.30 \
 && idlab cert app app.shop.test && idlab cert api api.shop.test \
 && idlab secret SHOP_WEB_SECRET \
 && idlab account ana ben \
 && idlab key shop 2026 \
 && idlab a2 app mod auth_openidc && idlab a2 app site orders \
 && (umask 077; printf 'OIDCClientSecret %s\nOIDCCryptoPassphrase %s\n' "$(idlab secret-of SHOP_WEB_SECRET)" "$(openssl rand -hex 16)" > /etc/netns/app/apache2/oidc-secret.conf) \
 && idlab bake \
 && netlab seal /etc/netlab/topology /etc/netns/api/stock-api/api.conf
```

`idlab` is what makes "no secrets in the repository" true. Everything it makes is made at image build, so it differs in every build and is in no commit:

| Command | Makes |
| --- | --- |
| `idlab idp MACHINE URL` | records which machine is the provider (`/etc/idlab/idp`), its certificate, and its `keycloak.conf` (host name, HTTPS on 443, `cache=local`, sign-in events to the journal) |
| `idlab names NAME=ADDRESS...` | the names in every machine's `/etc/hosts` (no resolver to boot, warm or break; a lab about DNS adds one) |
| `idlab cert MACHINE NAME...` | a certificate from the lab's CA (made on first use, trusted by every machine through the shared bundle) in MACHINE's `/etc/tls/NAME.crt` and `.key`; the key is readable by root and the `tlskey` group only. Certificates start two days in the past, so a machine whose clock is behind still accepts them |
| `idlab secret NAME...` | a random value in the provider's `/etc/keycloak/secrets.env` (root only), which the realm file names as `${NAME}`; `idlab secret-of NAME` prints it for an app's own file |
| `idlab account USER...` | a random password: `USER_PASSWORD` in `secrets.env` and `USER PASSWORD` in `/etc/idlab/accounts`, which the learner may read (these are the people they sign in as) |
| `idlab key REALM NAME [passive]` | an RSA signing key for the realm; names sort, the last active one signs, the others stay published (**tried**: `2026` active and `2025` passive both appeared in the JWKS with `x5c`, and tokens carried 2026's `kid`) |
| `idlab seckey USER USER-ID` | a software security key USER already has: `/etc/idlab/keys/USER.key` for `signin --key`, and `USER_KEY` for the realm file's `webauthn` credential (**tried**) |
| `idlab otp USER...` | an authenticator-app secret: `USER_OTP` for the realm file's `otp` credential, and its base32 form in `/etc/idlab/otp/USER` for `signin --otp-secret` and `oathtool` (**tried**) |
| `idlab a2 MACHINE mod\|site NAME...` | what `a2enmod` and `a2ensite` do, in MACHINE's own Apache |
| `idlab bake` | starts Keycloak inside the build (plain HTTP on the build's own 127.0.0.1), builds every realm from its file, stops it cleanly; the image then boots with the realm already there |

**Machines, the same in every identity lab unless it says otherwise** (the federation brief's table, kept): `office` (a staff laptop; `signin` is its browser), `idp` (Keycloak, realm `shop`), `app` (Apache), `api` (the stock API), on one lan. The lab machine itself is the console and is on no network, so checks act from `office`.

## 5. Keycloak on a machine

**The unit** (`keycloak@.service`, **tried**): runs through `lab-enter` like every per-machine service, as the user `keycloak` (not root; the unit sets `net.ipv4.ip_unprivileged_port_start=0` in the machine so it can serve 443), with `-XX:TieredStopAtLevel=1` and `-Xms64m -Xmx384m`. Its `ExecStartPost` waits until Keycloak answers and then applies any realm file that changed since it was last applied, so **"booted" means "the provider answers"**: `labcheck`'s boot wait covers it and no check has to wait for Keycloak. Logs: `journalctl -u keycloak@idp`, with a line per sign-in and token request (`type="LOGIN"`, `type="CODE_TO_TOKEN"`, `type="LOGIN_ERROR" ... error="..."`; **seen**).

**Finding: `cache=local` is not optional.** Without it Keycloak 26 starts a cluster stack (`jdbc-ping`) and looks in its database for the other members. After a restart that killed it (which `docker restart` is: systemd as PID 1 doesn't stop on Docker's signal), it waits for the instance it used to be: ten tries of two seconds, per dead instance. **Measured:** the restart trial's boot took 25.4 s after the first restart and 43.8 s after the second (`captured/restart-jdbc-ping.txt`: `JOIN(...) sent to idp-38123 timed out (after 2000 ms)` ... `too many JOIN attempts (10): becoming singleton`, `Bootstrap completed in 38.2 seconds`). With `cache=local` in `keycloak.conf`: 7.4, 7.7, 7.9 s, three restarts running. It is a runtime setting: `kc.sh build --cache=local` did not persist it (`kc.sh show-config` listed only the database), so it lives in `keycloak.conf` and in the build-time start. Keycloak's caching guide says local mode "is intended only for development and testing purposes", which a lab is; the lesson says so in a sentence, with the file database (H2, `--db=dev-file`), which is also not for production.

### The realm file is the configuration

`/etc/keycloak/realms/shop.json` on `idp` is short: only what the lab sets (the prototype's is 73 lines for a realm, two groups, two people, one client with two mappers). Keycloak fills in the rest.

- **`sudo realm-apply [REALM]`**, or `sudo systemctl reload keycloak@idp` (**tried**): fills in `${NAME}` from `secrets.env`, adds the realm's signing keys, deletes the running realm and creates it again from the file through the admin API. **0.9 to 2.4 s.** It refuses a file before touching anything when the JSON is invalid (`line 17: not valid JSON`), a placeholder has no value, or a fill-in gap is still there (`shop.json, line 17: a gap ("...") is still to be filled in`, which is what the strong-auth fill-in asks for).
- **`realm-saved [REALM]`**, `kc_saved [REALM]` in checks (**tried**): builds a throwaway copy of the realm (`chk-shop`) from the file beside the running one, asks Keycloak to export both, removes the copy, and compares everything except ids and users. **0.8 to 1.0 s.** It prints `saved`, or up to three differences:

  ```text
  realm shop differs from a fresh build of /etc/keycloak/realms/shop.json:
    clients[shop-web].redirectUris: now ["https://app.shop.test/*"], from its file ["https://app.shop.test/oidc/callback"]
  ```

  This is `netlab verify`'s idea applied to an identity provider: no list of fields to keep up to date, so a change to a flow, a mapper, a client, a role or a lifetime is caught alike. **Tried against:** a redirect URI changed with `kcadm.sh`; a client added with `kcadm.sh`; a flow step's requirement changed through the admin API; the prototype's `wrong/console-only.sh`, which makes both realm fixes through the admin API and leaves the file alone (the contract fails it on `realm-saved` and nothing else).
- **At a boot** the realm is left as the database has it, unless its file (or `secrets.env`, or a key) changed since the last apply. So a restart keeps what was made at run time, and a file edited but never applied takes effect at the next boot, as a daemon's config does.
- **`kcadm.sh` is for looking** (`kcadm.sh get clients -r shop -q clientId=shop-web`; 1.5 s a command here), `kc get shop/clients?clientId=shop-web` is the same through the base's helper in a fraction of a second. A change made with either is real until the next apply, and `realm-saved` shows it: the lesson's word for it is **drift**, and the cloud parallel is a console change to something Terraform or Bicep owns.

### Rules for realm files (each found by running)

1. **Applying rebuilds the realm, so what was made at run time and isn't in the file goes**: accounts made through SCIM, a security key someone registered, a check's own users, every session. A lab whose learner both makes such things and applies says so in its prompt. (For the federation brief's `fill-hr-sync`: the learner never changes the realm there, a boot doesn't re-apply an unchanged file, and `realm-saved` ignores users, so SCIM-made accounts survive the restart trial and don't count as a live change. The mechanism was tried; that lab was not.)
2. **People in the file carry an `"id"`**, so their `sub` is the same after every apply.
3. **Write the file as Keycloak would store it.** A group mapper without `"multivalued": "true"` gained that setting in the running realm the first time a token was issued, and `realm-saved` then reported a difference that no one made (**seen**; fixed by putting the line in the file). The rule is Module 3's "seed files written by FRR": before a lab is done, sign in once and run `realm-saved`; whatever it reports goes into the file.
4. **Keys and secrets never go in the file**: `${SHOP_WEB_SECRET}`, `${ANA_PASSWORD}`, `${BEN_KEY}`. Signing keys are files in `/etc/keycloak/keys/REALM/`, added at apply, so the keys are the same after every apply (a SAML service provider's copy of the provider's metadata, and anything that pinned a key, stay true).
5. **Everything a person needs to pass Keycloak's profile check** (`firstName`, `lastName`, `email`, `emailVerified`), or the first sign-in stops at an "update your profile" page.
6. **`"sslRequired": "all"`** costs nothing here: every lab URL is HTTPS from the lab's CA.

## 6. Relying parties

**Apache with mod_auth_openidc 2.4.15** (`apache2@M`, **tried** end to end): the code flow with PKCE (`OIDCPKCEMethod S256`), the client secret in a root-only included file, `Require claim groups:staff`. What a check reads: a CGI page that prints `user=$REMOTE_USER` and `groups=$OIDC_CLAIM_groups`, and Apache's error log on the machine (`on app tail /var/log/apache2/error.log`), which names each failure (`oidc_proto_validate_exp: "exp" validation failure (...): JWT expired 180 seconds ago`). Three things found: it answers `401`, not a redirect to the sign-in, to a client that doesn't ask for HTML, so `signin` sends a browser's `Accept` header; the unit's start script makes `/run/lock`, `/var/run/apache2` and its `socks` folder, which a machine's empty `/run` lacks (without them Apache fails with `mkdir: cannot create directory '/var/lock'` and CGI with `Couldn't bind unix domain socket`); and the signed-in person's access token reaches a CGI script as `$OIDC_access_token`, so "the site calls the API as the person" is three lines of shell.

**Apache with mod_auth_mellon 0.19** (**tried** once, `captured/saml-mellon-trial.txt`): a `saml` client in the realm file and eight `Mellon...` lines on the site gave a working single sign-on: `303` to the provider with a `SAMLRequest`, the sign-in, and a `SAMLResponse` form that `signin` carried back (`carried a SAMLResponse form to https://app.shop.test`). The provider's metadata was fetched from the running Keycloak; **not tried:** writing that metadata at image build (the realm's certificate is known then, so it is a template), and a NameID that is the user name (the trial showed a transient one, `G-ecb31f77-...`; a client setting).

**`stock-api@M`**, the base's stand-in resource server (**tried**): HTTPS on 443, `GET /stock/level`, a bearer token required. Its settings are seven lines in the machine's `/etc/stock-api/api.conf` (`issuer`, `audience`, `jwks_uri`, `leeway`, and the two switches a hurried fix reaches for, `check_audience` and `check_expiry`), and its log gives the reason in plain words: `10.0.5.20 refused: audience 'https://apis.shop.test' doesn't include 'https://api.shop.test'`. It fetches the keys by URL and once more on an unknown `kid`. Where the API is the learner's to build with a real module, the federation brief's choice (mod_oauth2) stands; the package is in the image, and this prototype did not run it.

**oauth2-proxy** (topic 47) is that topic's own layer on this base, as its brief says. What this base adds for it: token sizes. A Keycloak sign-in for the prototype's client gave an access token of 1,158 characters, an ID token of 1,119 and a refresh token of 701 (**measured**), about 3 kB before oauth2-proxy encrypts and encodes them: more than one 4 kB cookie is likely, which is the zero-trust brief's I8. That brief's designer decides between Redis (in Ubuntu's archive, 7.0.15) and a smaller session; `"fullScopeAllowed": false` on the client would shrink the access token (not tried).

## 7. What the learner types

| Tool | Does | Tried |
| --- | --- | --- |
| `on office signin URL USER [-v]` | Opens a page as the person's browser: follows redirects, keeps cookies (`--jar FILE` between runs), fills the provider's sign-in form, types a one-time code (`--otp-secret`), uses or registers a security key (`--key`, `--register-key`), posts the forms single sign-on sends through the browser. Prints each thing the person did, then `signed in: 200 URL` and the page, or `refused: WHY`. `-v` shows every request and redirect, long values cut | yes |
| `signin --code CLIENT REDIRECT_URI ISSUER USER [--secret S]` | Is the app: runs the code flow with its own PKCE pair, state and nonce and prints the token response | yes |
| `jwt show [FILE]` | Header and payload as JSON, and `iat`, `nbf`, `exp` as dates "by this machine's clock" | yes |
| `jwt verify --issuer URL --audience AUD [--nonce=N] [--leeway S]` | `valid sub=...`, or `invalid:` and the first of `format alg key signature issuer audience expired not-yet-valid nonce` | yes |
| `sudo realm-apply`, `realm-saved`, `kc get PATH` | section 5 | yes |
| `on app clock` | `app's clock reads 2026-11-22 22:48:27 UTC: 8 min 0 s ahead of the time server` and `timesync@app: inactive (disabled)` | yes |
| `kcadm.sh`, `jq`, `xmlsec1`, `oathtool`, `openssl` | the real tools | `kcadm.sh` and `oathtool` yes |

`signin` is honest about what it is: the first lab that uses it says it is the lab's scripted browser, shows a sign-in with `-v` beside the same flow done by hand with `curl` (the federation brief's worked example does exactly that), and from then on it is a tool. Its "refused" lines are the browser's or the page's own words where there are any (`refused: Invalid parameter: redirect_uri` is Keycloak's error page; `refused: Account is disabled, contact your administrator.`).

## 8. WebAuthn and passkeys

**What works (tried).** `signin` holds a software authenticator written on python3-fido2's WebAuthn types: a P-256 key, attestation `none`, the flags and counter a real key sends.

- **Registration** at Keycloak's own page (the `webauthn-register` required action) over HTTPS: `registered a security key for idp.shop.test`; the key file is saved (mode 600); Keycloak stored the credential (`type webauthn`, read back through the admin API).
- **Sign-in** with it, once the flow asks: `touched the security key for idp.shop.test`, `signed in: 200`.
- **A key made at image build** (`idlab seckey`) and carried by the realm file as a `webauthn` credential signed in after an apply and a restart, so a lab can start with people who already have keys.
- **The three refusals the lesson is about**, each by the party that makes it in real life:
  - the browser: a page may ask for a key only for its own host or a parent of it (`refused by the browser: the page on login.shop-help.test asked for a key for login.shop.test`; the rule is in `signin`, the page-on-another-host case needs the strong-auth brief's relay machine and was not run);
  - the key: `refused by the key: the security key has no credential for idp.shop.test (it was registered with login.shop-help.test)` (**tried** with an edited key file);
  - the server: `signin --origin https://login.shop-help.test` (a browser that lies) is refused by Keycloak itself, `refused: Passkey origin mismatch.`, and its journal says `web_authn_authentication_error="webauthn-error-bad-origin"` (**tried**).
- A person with a key and no `--key` is stopped: `refused: the page asks for a security key, and this person has none`.

**What doesn't, and the honest wording.** No real browser and no hardware take part. A headless Chromium with its virtual authenticator would add about 400 MB and a browser-automation stack to prove the same server-side checks; python-fido2's own client needs a CTAP device and has no software one. So the lab proves what the **server** enforces (challenge, origin, relying-party id, signature, counter) and models the browser's and the key's rules in forty readable lines. It does not prove user verification (a PIN or a fingerprint; the flag is simply set), attestation (which make of key), or anything about synced passkeys. The lesson says that in two sentences; the strong-auth brief's own-hardware step (a real key on the learner's own accounts) belongs to Module 10, as that brief recommends.

**Not tried here:** the `amr` claim (the strong-auth brief's N8: a mapper and reference values in the realm file; that designer saw `pwd`, `otp`, `hwk` on 26.8.1); a flow that requires a key by role, written in a realm file (the default flow's WebAuthn step was switched on through the admin API for these trials).

## 9. Clock skew on purpose

Every machine in a lab is a network namespace in one container, and all share the kernel's one real clock.

| Way | Result |
| --- | --- |
| A time namespace (`unshare --time --boottime 600 --monotonic 600`) | **Can't.** **Tried:** inside it `date +%s` was unchanged and only `/proc/uptime` moved by 600 s. The manual says why: "time namespaces do not virtualize the CLOCK_REALTIME clock" (time_namespaces(7)) |
| Setting the real clock (`date -s`, chronyd) | **Must never happen.** A lab container is privileged, and `--cap-drop SYS_TIME` beside `--privileged` changes nothing (**tried**: the effective capabilities were `000001ffffffffff` both ways), so it would move the clock of Docker's whole machine and every other lab on it. No lab runs chrony, ntpd or `timedatectl set-time`; the lesson says why the lab's time service is a stand-in |
| **libfaketime 0.9.10**, preloaded for everything started on one machine | **Works** (**tried**) for programs that ask the C library for the time: Apache with mod_auth_openidc, `curl`, `openssl`, `python3`, `date`. Its README says it "cannot work with statically linked binaries" and is bypassed by "programs written in golang", so **oauth2-proxy can't be skewed**; "Java-/JVM-based applications work" with its don't-fake-monotonic setting (`java -version` ran under it here; **Keycloak under it was not tried**, and no lab needs it: skew the relying party, not the provider) |

**The design (tried, in the prototype lab).**

- A machine has a clock of its own when the topology says `run app timesync`. It then has two files of its own: `/etc/clock/hwclock`, how far off its hardware clock is, in libfaketime's words (`+8m`), which is scenery and sealed; and `/etc/faketimerc`, how far off its clock is right now.
- `lab-enter`, the one door every command and daemon on a machine comes through, preloads libfaketime when the machine has that file. So `on app date`, Apache's own log times and its token checks all read the machine's clock, re-read every second (`FAKETIME_CACHE_DURATION=1`): a daemon already running takes a correction within a second, with no restart (**seen**: Apache's log lines went from `22:49:01` to `22:41:42`).
- **At every boot** `machine-clocks.service` sets each such machine's clock from its hardware clock, as a server's is before its time service has spoken. **`timesync@M`**, a stand-in for chrony or systemd-timesyncd, sets it right when it starts. Enabled, it does so at every boot.
- So the fault "the clock is wrong" lasts across the restart trial (the hardware clock is still eight minutes fast), the fix at its cause is `sudo systemctl enable --now timesync@app`, and the tempting fixes fail: setting the clock right by hand is lost at the next boot (the prototype's `wrong/clock-by-hand.sh`), and lengthening every token's life at the provider leaves the clock wrong (`wrong/long-tokens.sh`).
- **The evidence is real.** With `app` eight minutes fast and five-minute tokens, mod_auth_openidc refused the ID token with `"exp" validation failure (1795387561): JWT expired 180 seconds ago`, the browser got `400 Bad Request` at `/oidc/callback`, and the two logs disagreed by eight minutes about when the same sign-in happened (`22:49:01` in app's `error.log`, `22:41:01` in Keycloak's journal line for the same code). `on app clock` and `jwt show` ("exp: ... 181 s ago by this machine's clock") say it outright.
- **Which way to skew.** mod_auth_openidc forgives an `iat` up to 600 seconds in the future by default, so a relying party whose clock is **behind** by less than ten minutes notices nothing; one whose clock is **ahead** by more than the token's life sees every token as expired. The prototype uses ahead by eight minutes with five-minute tokens. `stock-api` has a 60-second leeway both ways.
- The lab's certificates are made two days in the past (`faketime -f '-2d' openssl ...`), or a machine whose clock is behind would find them not yet valid on a CI runner, where the image is seconds old.

**One naming detail for the writer:** the prototype sets `DONT_FAKE_MONOTONIC=1` (it worked with Ubuntu's 0.9.10); the README's current name is `FAKETIME_DONT_FAKE_MONOTONIC`. Set both.

## 10. Timings and memory

All measured 2026-11-22 on the owner's PC, with other sessions' containers possibly running.

| What | Measured |
| --- | --- |
| Image | 1.34 GB as Docker Desktop reports it; 871 MB of files (network base 467 MB; the JRE 194 MB, Keycloak 184 MB) |
| Base build | 65 s from nothing on an existing `lab-base-net`; 33 s after a helper changes |
| Lab image build | 13 s (the realm bake 9 s) |
| Container start to booted, Keycloak answering | 9.5 s and 9.7 s (first boots) |
| `docker restart`, then booted | 3.6 s for the restart itself, then 7.4 to 7.9 s (with `cache=local`; 25 s, then 44 s, without) |
| Memory, one lab | 550 to 640 MiB for the container; Keycloak's own share 420 to 510 MB (heap capped at 384 MB) |
| Memory, four labs at once | 2.4 GiB at most between them (samples every 10 s, `captured/four-at-once-stats.txt`); the largest single container 637.5 MiB |
| A whole sign-in through `signin` (three redirects, the form, the callback, the page) | 0.27 s |
| `realm-apply` | 0.9 s on the provider's machine; 2.0 to 2.4 s as the learner types it |
| `realm-saved` | 0.8 to 1.0 s |
| The prototype lab's eight checks, one run | 6.2 s through `labcheck check` |
| Its `solution.sh` | 2.4 s |
| **Its full contract, alone, images built** (pristine, solution, restart trial, six wrong fixes: eight container starts, nine check runs) | **150 s** |
| The same including the base's layer 3 and the lab image | 189 s; 165 s through `run-contract.sh` from the prototype folder as it is kept (151 s of it the contract) |
| **Four such labs at once** (`labcheck test --all --jobs 4`, images built during the run) | **241 to 244 s each**, all four kept |
| Dex, for comparison | 10.6 MiB; listening 0.17 s after start (the 21 s first seen was Docker Desktop's published port, not Dex) |

**What a contract costs.** About 17 to 19 s per container start alone (boot 9.5 s, the script, one run of checks, removal) and about 27 to 30 s with four at once on this PC. So a lab with N wrong fixes costs about (N + 2) starts plus one restart: the federation brief's five identity labs (47 starts) come to about 15 minutes alone and 23 minutes four at a time, below its own estimate of 38; the strong-auth brief's four (32 starts) to about 10 and 16. **A GitHub runner has fewer cores than this PC and nothing here ran on one**: Keycloak's start is CPU-bound (the JVM used 12.6 s of CPU for a 9.5 s boot), so with four labs booting at once on a runner the boot may take two or three times as long. The first thing to do with this base is a CI spike with the prototype lab, as Module 3 did with its probes; until then the 20-minute aim per topic is plausible, not proved.

## 11. The prototype lab: a sign-in that fails three ways

`prototypes/identity-lab-base/lab/`. It has Checkpoint 4 part 2's shape (the wrong redirect, the wrong audience, clock skew) because that is the hardest thing this base must carry; the checkpoint's designer writes the real one and may use none of it.

| Fault | Where it lives, so it lasts | Evidence (all **seen**) |
| --- | --- | --- |
| The redirect address registered for the site has a typo (`/oidc/callbak`) | the realm file | Keycloak's page before any password is asked: `Invalid parameter: redirect_uri`; `signin -v` shows the `redirect_uri` the site sent |
| The site's server is eight minutes fast, its time service off | `app`'s `/etc/clock/hwclock` (sealed) and `timesync@app` disabled | after a good sign-in at the provider, `400 Bad Request` at the callback; app's log `JWT expired 180 seconds ago`; `on app clock`; the two logs eight minutes apart |
| The access token names an audience the API isn't (`https://apis.shop.test`) | an audience mapper in the realm file | the sign-in works, the stock page says `the stock API answered 401: {"error": "invalid_token", "reason": "audience"}`; the API's journal names both audiences |

Fixing one uncovers the next, in that order.

**Checks** (eight; 6.2 s a run): Ana signs in from `office` and the site knows her; Ben, who isn't staff, signs in at the provider and gets `401` from the site; the stock page shows the API's number; **a sign-in the check runs itself as the site** yields an ID token for the site with the check's own nonce and an access token for the API, both verified by `jwt verify` against the provider's published keys, valid for at most 300 s; the registered redirect is exactly the one address, **and** three other addresses the check makes up (a sub-path, another path, another host, each with a random part) are refused at the provider; the API still refuses a token signed with a key the check just made, an unsigned one, and the provider's own token for another audience, and the sealed scenery is intact; `app`'s clock is within 2 s and `timesync@app` is enabled; `kc_saved shop`.

**Wrong fixes, each failed by the contract** (`captured/contract-run-6-final-warm-alone.txt`):

| `wrong/` | The shortcut | Fails |
| --- | --- | --- |
| `wildcard-redirect.sh` | `https://app.shop.test/*` | `redirect-exact` |
| `audience-check-off.sh` | the API told `check_audience = no` | `tokens-right`, `api-strict` |
| `long-tokens.sh` | tokens made to last an hour so the fast clock no longer expires them | `tokens-right`, `clock-right` |
| `clock-by-hand.sh` | the clock set right once, nothing enabled | `clock-right` (and the restart trial would undo it) |
| `console-only.sh` | both realm fixes through the admin API, the file untouched | `realm-saved` only |
| `two-of-three.sh` | the audience left wrong | `stock-shown`, `tokens-right` |

The pristine lab passes two of eight (the API's strictness and `realm-saved`), which the checkpoint's designer should note: a debug lab's "nothing passes before work" is not a rule, but those two are availability-free checks.

**A flake the four-at-once run found** (`captured/contract-run-3-four-at-once.txt`): one lab of four failed after its solution because the check passed a random nonce that began with `-` to `jwt verify --nonce "$nonce"`, which read it as an option. Fixed twice over: `signin` now makes hex state and nonce values, and checks write `--nonce="$nonce"`. It is house rule 2's lesson again: a random input must not fail a right answer by chance, and it took a second, parallel run to see it.

## 12. Platform work the base needs

| # | What | Smallest version | Blocks |
| --- | --- | --- | --- |
| P1 | **`labcheck` builds a base's own base first.** `build_base` builds `content/lab-bases/id/` but doesn't look inside its Dockerfile, so on a machine with no `lab-base-net` image (every CI runner) the build fails. The prototype worked only because that image already existed here | in `build_base`: read the base's Dockerfile with `base_named_in` and build that base first (about six lines and a test) | every identity lab in CI |
| P2 | **`content/lab-bases/id/`**: the prototype's `base/` under its real name, with a README in the network base's style (sections 4 to 9 are its draft) | as prototyped | every identity lab |
| P3 | **Three edits to the network base**, done by `base/lib/patch-netlab` in the prototype so they can be read: `netlab` learns four services (`keycloak`, `apache2`, `stock-api`, `timesync`: eight lines in its two tables); `lab-enter` gives a machine its own `/var/log/apache2`, `/var/lib/apache2` and `/var/cache/apache2` (one line); `lab-enter` preloads libfaketime for a machine that has its own `/etc/faketimerc` (five lines, inert for every lab that doesn't, and guarded on the library being installed) | edit the two files in `content/lab-bases/net/`; the alternative, keeping the script in the identity base, hides a change to shared plumbing | every identity lab |
| P4 | **Tests for the helpers in `tools/tests/`**, as `cors-verdict` has: `jwtlib.verify`'s nine verdicts; `kcapi`'s `normal` and `differences`; `signin`'s form reading against saved Keycloak pages (a Keycloak upgrade that changes a form id then fails a unit test, not thirty labs) | three small test files | before the base is trusted |
| P5 | **ADR-0018 amendment lines** (Proposed, for the queue's "Decided for you"): a lab base may start from another lab base; Keycloak is the second pinned download from outside Ubuntu's archive; a check may make people of its own at the identity provider and removes them (`idp-user`, the same standing as a throwaway listener) | one paragraph | nothing technical |
| P6 | **`content/README.md`**: a short "Identity labs" section pointing at the base's README | ten lines | writers |
| P7 | **A CI spike**: the prototype lab (or the first real identity lab) on a GitHub runner, four at once, before a topic is written on the base; then its seconds in `tools/lab-seconds.json` | one pull request | confidence in section 10 |
| P8 | Still to build in the base, asked for by other briefs (section 13): approving a device code in `signin`; `kc-flows`; a throwaway person with a one-time code or a key; the provider's SAML metadata written at build | each under 60 lines | the labs that use them |

No app work, no new item type, no memory budget and no longer boot wait in `labcheck`: the unit makes "booted" mean "answering", and 9.5 s is far inside the 480 s limit.

**Docker Desktop against CI.** Keycloak, Apache and python need no kernel feature beyond the network base's namespaces and veth pairs, which its README records as working on both. Two things are particular to this base and untried on a runner: `net.ipv4.ip_unprivileged_port_start` set inside a namespace (a per-namespace `net.` setting, like the ones netlab already sets), and libfaketime's shared memory (`FAKETIME_SHARED`, a semaphore in `/dev/shm`). The weekly Labs run rebuilds from whatever apt serves, so a new OpenJDK or Apache arrives without a pull request; Keycloak itself moves only when the pin is changed.

## 13. Fit with the other briefs

What each brief asks of this base, and where they could not be made to agree.

**`csa.sec.federation` (F0 to F5).** Met and tried: Keycloak with OIDC, PKCE required per client (`"pkce.code.challenge.method": "S256"`, and requests without a challenge are the federation labs' to probe), discovery, an active and a passive key, the realm in a file applied at start and reload, secrets and keys made at build, a unit that counts as started when the realm answers, `-XX:TieredStopAtLevel=1`, events in the journal, `kcadm.sh`, the admin-API helper (`kc`), `signin`, the code flow as a helper (`signin --code`, its `oidc_login`), a token maker for forged tokens (`mint-token`), Apache with the three modules, `jq` and `xmlsec1`, SCIM switched on per realm in the file. **Differences:**

1. `kc_saved` takes a **realm**, not a machine: `kc_saved shop`, not `kc_saved idp`.
2. Its `keycloak-apply` is `realm-apply` (the strong-auth brief's name), and `sudo systemctl reload keycloak@idp` does the same; a reload **always** rebuilds, a boot only when the file changed. Nothing rebuilds because "the realm was changed live": a live change stays until the next apply, and `realm-saved` is what reports it.
3. **Not built:** approving a device code (its `device-approve.sh`; `signin` doesn't know the consent page), its `token-cases` (its own), a SCIM token for a service client (the admin's own token was refused at the SCIM endpoint with `401`, so the `hr-sync` client and its roles are that brief's to seed and were not tried here), and mod_oauth2.
4. Its F4 (a check that adds a signing key of its own to prove an API fetches keys by URL): **not needed.** `idlab key shop 2025 passive` and `idlab key shop 2026` give a lab two real keys from the start; a check can read which `kid` a fresh token carries and what the API accepts, and a debug lab can pin the old one. Recommend dropping the ADR line.

**`csa.sec.strong-auth` (N1 to N11).** Met and tried: N1 (WebAuthn, one-time codes, events, the admin API, HTTPS from the lab's CA with no cookie workaround), N2 (the realm in the file database at image build; boots in 9.5 s), N3 (`realm-apply` in seconds, refusing a `...` gap by line; `realm-saved`), N5 (`signin` with a software key over HTTPS; its `--report-origin` is `--origin` here), N6 (`idlab seckey`), N9's first half (sign-in events in the journal), N10's base part (a second name and certificate for a phishing machine is `idlab cert phish login.shop-help.test`). **Differences:**

5. `realm-apply` **rebuilds** the realm; it does not push changes into it. It is simpler and total, and it costs what section 5's rule 1 says. For that brief's worked example (Bob registers a key at run time and nothing is applied afterwards) nothing changes.
6. People's keys and app secrets are in `/etc/idlab/keys/USER.key` and `/etc/idlab/otp/USER`, not "in each person's folder". `/etc/idlab` is shared by every machine; a lab that wants them on `office` only can place them in `/etc/netns/office/` (not tried).
7. **Not built:** `kc-flows` (N4), a throwaway person with a one-time code or a key (N7; `idp-user add` makes one with a password and groups, **tried**; credentials of the other kinds work in a realm file, and were not tried through the users API), the AMR mapper (N8), `signin-watch`, the relay and `attacker-replay` (N10), `ca-whatif` (N11): all that brief's own.
8. `signin` doesn't print the token's claims after opening a page; `signin --code ... | jwt show` does.

**`csa.sec.zero-trust` (I1 to I9).** I1 (an OIDC provider on `idp` with HTTPS every machine trusts): met. I2 (groups in the ID token): a mapper in the realm file, **tried**. I3: a disabled person's refresh is refused (`invalid_grant`, `User disabled`, **tried**), and with `"revokeRefreshToken": true` a used refresh token is refused the second time (`Maximum allowed refresh token reuse exceeded`, **tried**). I4: `idlab secret` and `secret-of` (no trailing newline: `printf '%s'`). I5: `idp-user add|disable|del REALM NAME` (**tried**, effective at once: the disabled person's next sign-in read `Account is disabled`). I6: `signin URL USER --jar FILE` replaces its `zt-login` (**not tried through oauth2-proxy**). I7: 9.5 s to answering, which also brings its CI estimate down. I9: `oathtool` is in the image and `signin --otp-secret` types the code. **Open:** I8, the cookie (section 6).

9. Its prototype's issuer was `http://idp.corp.test`; on this base it is HTTPS, and the host name is whatever its `idlab idp` line says.
10. `apache2@.service` here is ordered after `keycloak@idp.service` by name; its `oauth2-proxy@.service` wants the same line, and a lab whose provider machine is not called `idp` needs a drop-in. Keeping the name `idp` in every lab avoids it.

**The module as a whole.**

11. **Host names differ between briefs**: `idp.shop.test` (federation), `login.shop.test` (strong-auth), `idp.corp.test` (zero trust). The base takes any. Section 14, question 6.
12. **Two designers used the name `lab-base-sec` for two different bases**: the payments server (audit, vulnerabilities, compliance; `lab-base-sec.md`) and, in the crypto brief's open question 5, a base for crypto and secrets with OpenBao. The critic names them apart. Neither needs anything from this base, and this base needs nothing from them.
13. **`jq`**: COMMON's rule 7 says lab images have no `jq`; this image has it, on the federation brief's argument. Section 14, question 4.
14. **Checkpoint 4 part 2** was designed without sight of this base. Section 11 is a working draft of it; what its designer must know is in section 9 (which way to skew, and that the relying party is the machine to skew) and section 5 (a fix made in the console fails `kc_saved`).

## 14. Open questions, each with a recommendation

1. **Keycloak, or something lighter?** Dex would cut 400 MB and nine seconds and lose SAML, SCIM, WebAuthn, one-time codes and flows. **Recommendation: Keycloak for the whole module**, one tool the learner meets five times. A learner's laptop needs about 0.65 GB of memory and 1.4 GB of disk for an identity lab; say so in the first identity lab's "before you start".
2. **Rebuild the realm on apply, or push changes into it?** Rebuilding is one second, total, and makes "the file is the configuration" literally true; it drops what was made at run time. Pushing changes keeps run-time accounts but needs code for every kind of setting and can leave a realm that no file describes. **Recommendation: rebuild**, with rule 1 stated in the two labs it touches.
3. **The API: the stand-in, or mod_oauth2?** **Recommendation:** `stock-api` wherever the API is scenery or the lesson is the five checks themselves (the checkpoint, zero trust, strong auth); the federation topic keeps mod_oauth2 for the API its learner builds, and runs it on this base before writing (this prototype did not).
4. **`jq` in the image.** Module 1 taught it (`csa.linux.shell` has a `jq` write lab), and a discovery document or a JWKS read with `grep` is fragile. **Recommendation: yes, for learners**; checks keep reading JSON with `python3` through `json`, and `predict_shell` items keep to tools Git Bash has.
5. **The clock: a model of a time service, or no clock lab at all.** The alternative is to teach skew from captured logs only. The model is small, its evidence is real (a real module refusing a real token for the real reason) and the fix is a habit worth having (find out why the clock is wrong; don't widen the tolerance). **Recommendation: keep it**, and say in one sentence that `timesync@M` stands in for chrony because the lab's machines share one real clock.
6. **One host name for the provider.** **Recommendation: machine `idp`, name `login.shop.test`, in every topic of the module.** The strong-auth topic's lookalike (`login.shop-help.test`) only teaches if the real name is one the learner has typed for weeks, and nothing is captured yet under the other names. The zero-trust brief's company can stay `corp.test` if its story needs another firm; the machine is still `idp`.
7. **One base on top of the network base (1.34 GB), or Keycloak as a topic layer.** A topic layer repeated in four topics and a checkpoint is the "900 copies" problem again, and the helpers must be in one place. **Recommendation: one base**, `content/lab-bases/id/`, with P1.
8. **No admin console for the learner.** `labcheck` publishes no ports, so Keycloak's web console can't be opened from the learner's own browser. **Recommendation: leave it so in Module 4.** Files, `kc get`, `kcadm.sh` and `signin -v` show every message, which a console hides, and the console is exactly where drift comes from. If the owner later wants to look, an optional "publish this port" switch in `labcheck start` is a small, separate piece of work.
9. **Keeping the pin fresh.** Keycloak ships fixes monthly (26.8.2 lists over thirty CVEs fixed). None matters to a provider that no network can reach, and every upgrade can change a form `signin` reads. **Recommendation:** move the pin only on purpose, with P4's tests and one full Labs run, and record the version in the base's README.
10. **Should a lab forbid `date -s`?** It can't (section 9), and a learner who types it moves the clock of Docker's whole machine until Docker Desktop corrects it. **Recommendation:** the clock lab's prompt says the machine's clock is set only by its time service and names `on app clock`; the debug prompt never suggests setting a date. Worth one line in the network base's README, since every systemd lab has had this exposure all along.

## 15. Sources (read 2026-11-22)

| Claim | Source |
| --- | --- |
| Releases, dates, licences of each candidate | GitHub's API: `repos/keycloak/keycloak`, `dexidp/dex`, `goauthentik/authentik`, `zitadel/zitadel`, `ory/hydra`, `ory/kratos`, `authelia/authelia`, `kanidm/kanidm`, `oauth2-proxy/oauth2-proxy` (v7.15.6, 2026-11-05, MIT), each with `/releases` |
| Keycloak 26.8.2's tarball size and sha256; its fixes | https://github.com/keycloak/keycloak/releases/tag/26.8.2 |
| Keycloak's features and their types in 26.8.2 (`SCIM_API`, `WEB_AUTHN`, `PASSKEYS`, `DEVICE_FLOW`, `STEP_UP_AUTHENTICATION`, `CLIENT_SECRET_ROTATION`, `DPOP`: all DEFAULT and enabled) | the running server's `/admin/serverinfo`, and `kc.sh build --help` |
| Keycloak's SCIM guide exists ("Managing users and groups through SCIM", "Enabling SCIM for a realm"); its body was not read (the page is 690,000 characters) | https://www.keycloak.org/docs/latest/server_admin/index.html |
| `jdbc-ping` is the default stack; local mode "is intended only for development and testing purposes" | https://www.keycloak.org/server/caching |
| Dex "uses OpenID Connect to drive authentication for other apps"; SAML only as a connector | https://dexidp.io/docs/ |
| authentik: "at least 2 CPU cores and 2 GB of RAM"; server, worker, PostgreSQL; provider types; blueprints | https://docs.goauthentik.io/install-config/install/docker-compose/ , https://docs.goauthentik.io/core/architecture/ , https://docs.goauthentik.io/add-secure-apps/providers/ , https://docs.goauthentik.io/customize/blueprints/ |
| authentik's licence | https://github.com/goauthentik/authentik/blob/main/LICENSE |
| ZITADEL needs "A PostgreSQL instance"; "1 CPU and 512MB memory" for tests; AGPL-3.0 | https://zitadel.com/docs/self-hosting/deploy/overview , https://github.com/zitadel/zitadel/blob/main/LICENSE |
| Ory Hydra: certified OIDC, "a headless API that doesn't force you to use a specific user management system"; Kratos: TOTP, passkeys | https://www.ory.com/docs/hydra/ , https://www.ory.com/docs/kratos/ory-kratos-intro |
| Authelia: OIDC provider "as an open beta feature"; its second factors | https://www.authelia.com/configuration/identity-providers/openid-connect/provider/ , https://www.authelia.com/overview/prologue/introduction/ |
| "time namespaces do not virtualize the CLOCK_REALTIME clock" | https://man7.org/linux/man-pages/man7/time_namespaces.7.html |
| libfaketime: static binaries, Go, Java, `/etc/faketimerc`, the 10-second cache, GPL | https://github.com/wolfcw/libfaketime |
| Package versions | `apt-cache policy` in `ubuntu:24.04` with the day's lists |

Pages that could not be read: ZITADEL's SCIM guide (404 at the address tried) and Kanidm's feature list (its front page names none), which is why those cells say "not confirmed".

## 16. Unverified

- **Anything on a GitHub runner**: boot time with four labs on fewer cores, the per-namespace port setting, libfaketime's shared memory. P7.
- **mod_oauth2** as the resource server (installed; the federation brief's own trial is the evidence).
- **Keycloak under libfaketime** (only `java -version` ran under it), and Go programs (the README says they bypass it).
- **A sign-in flow written in a realm file** that requires a key by role, and the `amr` claim; a flow change was tried through the admin API only.
- **The device grant, client credentials, token exchange and SCIM with a realm token**: the endpoints exist (discovery, and SCIM's `401`), none was driven here.
- **SAML**: one working sign-on; signature checking by hand with `xmlsec1`, the NameID format and build-time metadata were not tried.
- **`signin` through oauth2-proxy**, and the size of oauth2-proxy's cookie with Keycloak's tokens.
- **A browser's rule seen on a real second host**: `signin`'s refusal for a page on another host is coded and was not run against a relay machine.
- **Two Keycloak machines in one lab** (a broker and an upstream provider): the database folder is one per container, so the base runs one Keycloak; two realms on it are the way to model two organisations (not tried).
- **The licences in section 3's package table**, other than libfaketime's (read in its README): written from memory, and mod_oauth2's from the federation brief. The writer reads each package's copyright file (`/usr/share/doc/PACKAGE/copyright`) before the base's README repeats them.
- **Comparison cells marked "from memory" or "not confirmed"** in section 2.
- **Learner's-eye use**: nobody has yet done a lab on this base by hand from the prompt; the first written lab is the test of `signin`'s wording.
