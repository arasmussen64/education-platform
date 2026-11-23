# The identity-lab base

Every identity lab (the Cloud Solutions Architect track's Module 4: federation, strong authentication, zero trust, Checkpoint 4's second part) starts `FROM lab-base-id`. This folder is that image. It starts `FROM lab-base-net` itself, so an identity lab's machines are the network base's machines, and everything in [the network base's README](../net/README.md) holds here: read that first. `tools/labcheck.py` builds `lab-base-net`, then `lab-base-id`, then the lab ([ADR-0018](../../../docs/decisions/0018-lab-checker-local-mode.md), fourth amendment).

Read this before writing an identity lab. The plan behind it is [docs/plans/cloud-module-4/MODULE-4-BRIEF.md](../../../docs/plans/cloud-module-4/MODULE-4-BRIEF.md), sections 3.3, 3.4 and 4.1, and the designer's brief beside it, `identity-lab-base.md`. Where a number below says "measured", it was measured on the owner's PC on 2026-11-22 (Docker Desktop 29.8.2, 8 CPUs, 15.5 GiB), with other sessions' containers running.

## What's in the image

| Layer | What | Notes |
| --- | --- | --- |
| 0 | `FROM lab-base-net` | The network base, unchanged: 659 MB as Docker Desktop reports it. |
| 1 | Java 21 (headless), Apache 2.4 with mod_auth_openidc, mod_auth_mellon and mod_oauth2, xmlsec1, jq, libfaketime, chrony, python3-fido2, oathtool, ca-certificates | All from Ubuntu 24.04's archive. Apache's and chrony's own services are switched off and replaced by units that say what to type (below). |
| 2 | Keycloak, unpacked in `/opt/keycloak` | The one download from outside the archive, pinned (below). |
| 3 | The base's files; Keycloak built for its file database and started once, so the image holds its master realm and an administrator | The administrator's password is made at this build (`/etc/idlab/admin.env`, readable by root only), so it is in no repository and differs in every build. |

The whole image is 1.35 GB as Docker Desktop reports it. Its three layers build in about 100 s on top of an existing `lab-base-net` (measured, nothing cached), and layer 3 alone, after a helper changes, in about 35 s (Keycloak's own build step is 18 s of it).

**The pin.** Keycloak 26.8.2, Apache-2.0, released 2026-11-05: the newest release at least two weeks old on 2026-11-22, the day the base was built (GitHub's release list, read that day; 26.8.1 is of 2026-10-13).

| | |
| --- | --- |
| URL | `https://github.com/keycloak/keycloak/releases/download/26.8.2/keycloak-26.8.2.tar.gz` |
| Size | 173,550,645 bytes |
| SHA-256 | `dd124787283918bc597628887168333465ee2a811a389e0003569e52be7e487f` (GitHub's digest for the release asset; the `Dockerfile` checks it) |

Move the pin only on purpose. A new Keycloak can rename a form that `signin` reads, or stamp a new field that `realm-saved` must leave out, so: change the version and checksum, save Keycloak's pages again into `tools/tests/keycloak_pages/` (`tools/tests/test_idlab_signin.py` says how they were saved) and its exports into `tools/tests/keycloak_exports/` (`tools/tests/test_idlab_kcapi.py` says how), run those tests, and read one full Labs run. The weekly Labs run rebuilds from whatever apt serves, so a new Java or Apache arrives without a pull request; Keycloak itself moves only with the pin.

**The packages,** with the licence each one's `/usr/share/doc/PACKAGE/copyright` states (read in the image on 2026-11-22):

| Package | Version | Licence | For |
| --- | --- | --- | --- |
| openjdk-21-jre-headless | 21.0.13.1+2 | GPL-2 with the Classpath exception | Keycloak |
| apache2 | 2.4.58 | Apache-2.0 | a site or an API that relies on the identity provider |
| libapache2-mod-auth-openidc | 2.4.15.1 | Apache-2.0 | signing people in with OpenID Connect |
| libapache2-mod-auth-mellon | 0.19.0 | GPL-2+ with an OpenSSL exception | signing people in with SAML |
| libapache2-mod-oauth2 | 3.3.1 (liboauth2 1.6.0) | AGPL-3.0+ | an API that checks access tokens, where the learner builds or repairs the API (run once here, below) |
| xmlsec1 | 1.2.39 | MIT (upstream's; the package's file isn't in the form that names one) | checking a SAML signature by hand |
| jq | 1.7.1 | MIT | reading JSON, for learners (Module 1 taught it) |
| faketime, libfaketime | 0.9.10 | GPL-2 | a machine's own clock; certificates dated two days back |
| chrony | 4.5 | GPL-2 | a lab's time server, always with `-x` |
| python3-fido2 | 1.1.2 | BSD-2-Clause | the software security key in `signin`; it brings python3-cryptography (Apache-2.0 or BSD), which `mint-token` and `make-key` use |
| oathtool | 2.6.11 | GPL-3+ | one-time codes on the command line |
| ca-certificates | 20260816 | MPL-2.0 | the download; and the bundle the lab's own CA joins |

`jq` is here for learners. Checks still read JSON with `python3`, through the network base's `json`, and `predict_shell` items never use it.

## A lab's folder and Dockerfile

```text
exercises/<lab>/
├── exercise.yaml      runtime: lab, lab: { init: systemd, restart_trial: true }
├── Dockerfile         below
├── topology           netlab's words, with: run idp keycloak / run app apache2 timesync / run api stock-api / run ntp chrony
├── machines/idp/keycloak/realms/shop.json           the realm (no secret in it: ${NAME} placeholders)
├── machines/app/apache2/sites-available/orders.conf
├── machines/app/chrony/chrony.conf                  where app gets its time (a machine that runs timesync)
├── machines/app/clock/hwclock                       how far off app's hardware clock is: +480
├── machines/api/stock-api/api.conf
├── machines/ntp/chrony/chrony.conf                  the time server's own file
├── checks.yaml  solution.sh  wrong/*.sh
```

```dockerfile
FROM lab-base-id
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
RUN netlab enable \
 && idlab idp idp https://login.shop.test \
 && idlab names login.shop.test=10.0.5.10 app.shop.test=10.0.5.20 api.shop.test=10.0.5.30 time.shop.test=10.0.5.40 \
 && idlab cert app app.shop.test && idlab cert api api.shop.test \
 && idlab secret SHOP_WEB_SECRET \
 && idlab account ana ben \
 && idlab key shop 2025 passive && idlab key shop 2026 \
 && idlab a2 app mod auth_openidc && idlab a2 app site orders \
 && (umask 077; printf 'OIDCClientSecret %s\nOIDCCryptoPassphrase %s\n' "$(idlab secret-of SHOP_WEB_SECRET)" "$(openssl rand -hex 16)" > /etc/netns/app/apache2/oidc-secret.conf) \
 && idlab bake \
 && netlab seal /etc/netlab/topology /etc/netns/api/stock-api/api.conf /etc/netns/app/clock/hwclock /etc/netns/ntp/chrony/chrony.conf
```

The draft topic `csa.sec.base-probes` has one whole lab in this shape, while it exists.

`idlab` is what makes "no secrets in the repository" true. Everything it makes is made at image build, so it differs in every build and is in no commit:

| Command | Makes |
| --- | --- |
| `idlab idp idp https://login.shop.test` | records which machine is the provider (`/etc/idlab/idp`), its certificate, and its `keycloak.conf` (host name, HTTPS on 443, `cache=local`, sign-in events to the journal) |
| `idlab names NAME=ADDRESS...` | the names in every machine's `/etc/hosts`. There is no resolver to boot, warm or break; a name that isn't listed fails to resolve at once |
| `idlab cert MACHINE NAME...` | a certificate from the lab's CA (made on first use, trusted by every machine through the shared bundle) in MACHINE's `/etc/tls/NAME.crt` and `.key`; the key is readable by root and the `tlskey` group (Keycloak, Apache) only. Certificates start two days in the past, so a machine whose clock is behind still accepts them, even on a CI runner where the image is seconds old |
| `idlab secret NAME...` | a random value in the provider's `/etc/keycloak/secrets.env` (root only), which the realm file names as `${NAME}`; `idlab secret-of NAME` prints it, for an app's own file |
| `idlab account USER...` | a random password: `USER_PASSWORD` in `secrets.env`, and `USER PASSWORD` in `/etc/idlab/accounts`, which the learner may read (these are the people they sign in as) |
| `idlab key REALM NAME [passive]` | an RSA signing key for the realm. Names sort, the last active one signs, the others stay published. Labs start with two real keys, `idlab key shop 2025 passive` and `idlab key shop 2026`, so a check can read which key a fresh token names and what an API accepts |
| `idlab seckey USER USER-ID` | a software security key USER already has: `/etc/idlab/keys/USER.key` for `signin --key`, and `USER_KEY` for the realm file's `webauthn` credential. USER-ID is the person's `"id"` in the realm file |
| `idlab otp USER...` | an authenticator-app secret: `USER_OTP` for the realm file's `otp` credential, and its base32 form in `/etc/idlab/otp/USER` for `signin --otp-secret` and `oathtool` |
| `idlab a2 MACHINE mod\|site NAME...` | what `a2enmod` and `a2ensite` do, in MACHINE's own Apache |
| `idlab bake` | starts Keycloak inside the build (plain HTTP on the build's own 127.0.0.1), builds every realm from its file, and stops it cleanly; the image then boots with the realm already there |

## Names every identity lab uses

The provider's machine is always **`idp`**, Keycloak is always at **`https://login.shop.test`** (port 443), and the realm is **`shop`**. The business is the shop of Modules 1 to 3 in every topic. `office` is a staff laptop and `signin` its browser; `app` is a site (Apache) and `api` an API; `ntp` is the time server, `time.shop.test`. People: `ana` (staff), `ben` (warehouse), and whoever a lab adds. A checkpoint's unfamiliarity comes from its machines and its story, not from another name for the provider.

The name is fixed for two reasons. Strong authentication's lookalike (`login.shop-help.test`) only teaches if the real name is one the learner has typed for weeks. And `apache2@.service` and `stock-api@.service` start after `keycloak@idp.service` by name, so a provider on a machine with another name would need a drop-in.

The lab machine itself is the console and is on no network, so checks act from `office`.

## Keycloak on a machine

**The unit** is `keycloak@idp`. It runs through `lab-enter` like every per-machine service, as the user `keycloak`, not root (the unit sets `net.ipv4.ip_unprivileged_port_start=0` in the machine so it can serve port 443), with the JVM's fast compiler only (`-XX:TieredStopAtLevel=1`) and a heap of at most 384 MB. Its `ExecStartPost` waits until Keycloak answers and then applies any realm file that changed since it was last applied (one that can't be applied is reported and left: "A realm file that can't be applied", below). So **"booted" means "the provider answers"**: `labcheck`'s wait for the boot covers it, and no check waits for Keycloak. Its log is `journalctl -u keycloak@idp`, with a line for every sign-in and token request (`type="LOGIN"`, `type="CODE_TO_TOKEN"`, `type="LOGIN_ERROR" ... error="..."`).

**`cache=local` is not optional.** Without it Keycloak 26 looks in its database for the other members of a cluster. After a restart that killed it (which `docker restart` is), it waits for the instance it used to be: the designer measured 25 s and then 44 s for the restart trial's boots, against 7 to 8 s with `cache=local`. It is a setting of the running server, so it lives in `keycloak.conf` (`idlab idp` writes it) and in the build-time start. Keycloak's own guide says local mode "is intended only for development and testing purposes", which a lab is; the file database (H2) is not for production either. A lesson that shows `keycloak.conf` says both in a sentence.

**One Keycloak per lab.** Its database is one folder in the container. Two organisations are two realms on it.

### The realm file is the configuration

`/etc/keycloak/realms/shop.json` on `idp` is short: only what the lab sets (the probe's is 71 lines for a realm, two groups, two people and one client with two mappers). Keycloak fills in the rest.

- **`sudo realm-apply [REALM]`**, or `sudo systemctl reload keycloak@idp`: fills in each `${NAME}` from `secrets.env`, adds the realm's signing keys, builds the file once as a throwaway copy (`chk-shop`) to see that Keycloak takes it, then deletes the running realm and creates it again from the file. It refuses a file **before touching the running realm**, whatever is wrong with it: "A realm file that can't be applied", below, has the messages.
- **`realm-saved [REALM]`**, `kc_saved REALM` in checks: builds a throwaway copy of the realm (`chk-shop`) from the file beside the running one, asks Keycloak to export both, removes the copy, and compares them. It prints `saved`, or up to three differences:

  ```text
  realm shop differs from a fresh build of /etc/keycloak/realms/shop.json:
    authenticationFlows[Browser - Conditional 2FA].authenticationExecutions[webauthn-authenticator].requirement: now "ALTERNATIVE", from its file "DISABLED"
    clients[scanner]: now "there", from its file "(not there)"
    clients[shop-web].secret: now "(not the file's secret)", from its file "(the file's secret)"
  ```

  This is `netlab verify`'s idea applied to an identity provider. It keeps no list of the fields it compares, so a change to a flow, a mapper, a client, a role, a lifetime or a service account is caught alike; "What `realm-saved` compares", below, lists the few things it leaves out. **`kc_saved` takes a realm, not a machine:** `kc_saved shop`. With a file that can't be applied it prints the file's fault instead (on standard error, exit 1), so a check that expects `saved` fails.
- **At a boot** the realm is left as the database has it, unless its file (or `secrets.env`, or a key) changed since the last apply. A reload always rebuilds; a boot rebuilds only when the file changed. So a restart keeps what was made at run time, and a file edited but never applied takes effect at the next boot, as a daemon's configuration does. A file that can't be applied never stops Keycloak starting (below).
- **`kcadm.sh` is for looking.** `kc get shop/clients?clientId=shop-web` is the same through the base's helper, in a fraction of a second. A change made with either is real until the next apply, and `realm-saved` shows it. The lesson's word for that is **drift**; the cloud parallel is a console change to something Terraform or Bicep owns.
- **`kc-flows REALM [FLOW] [--file]`** shows a sign-in flow as a tree, one step a line with its requirement and its settings: as the running realm has it, or with `--file` as the realm file writes it. A realm file that sets no flow gets Keycloak's built-in ones, and `kc-flows shop --file` says so.

### What `realm-saved` compares

Everything Keycloak exports for the realm (`partial-export`, with clients, groups and roles), and each client's secret where the file gives one. Found by building a realm with one of each kind of client the base supports (a site with a secret, a public client, a device client, two service accounts, a client that signs its own tokens, a bearer-only API, a SAML client, an identity provider) and people with a password, an authenticator app and a security key; applying it; and reading what differs between the running realm and a fresh copy when nobody has changed anything. That pair of exports is saved in `tools/tests/keycloak_exports/one-of-each.json`, and `tools/tests/test_idlab_kcapi.py` holds the list below to it.

**Left out, wherever it appears** (`STAMPED` and `DROPPED` in `lib/kcapi.py`):

| Field | Where Keycloak 26.8.2 writes it | Why leaving it out is safe |
| --- | --- | --- |
| `id`, `containerId` | everything | Keycloak makes them up, new in every build. A realm file names things by name (a flow's alias, a client's `clientId`); the one id it sets is a person's, and people aren't compared. |
| `internalId` | an identity provider | The same: an id under another name. |
| `createdTimestamp` | each user; the only users in an export are service accounts | The millisecond the account was made. No sign-in, token or permission reads it. A file can't usefully set it, and everything else about a service account (enabled, groups, realm and client roles) is compared. |
| `client.secret.creation.time` (a client attribute) | a client whose secret Keycloak made itself: a SAML client, a bearer-only API, a client that signs its own tokens, any client after "regenerate secret" | The second the secret was made. It matters only to a secret-rotation policy, which no lab sets. The secret itself is compared, below, so a regenerated secret is still caught. |
| `subComponents`, and key providers named `fallback-…` | components | Empty, and the keys Keycloak makes for itself when asked for an algorithm the realm has no key for. The realm's own keys are compared by certificate. |

**Compared in a way of its own:**

- **A client's secret.** An export prints every secret as `**********`, so two exports can't tell a changed secret (before this was added, a secret set through the admin API passed, and a regenerated one was caught only by its creation time). Where the realm file gives a client a `"secret"`, `realm-saved` reads the running realm's real one from the list of clients and compares it with the file's. The difference is printed as `now "(not the file's secret)", from its file "(the file's secret)"`: no secret is ever printed, and any other setting with "secret" in its name prints as `"(a secret, not shown)"`. Where the file gives a client no secret (a SAML client, a bearer-only API), Keycloak makes one up in every build; it is no setting of the file's, so it isn't compared. A confidential client that signs in with a secret always has it in the file (`${NAME}`), or every `realm-apply` would change it.
- **Service accounts.** A client with `"serviceAccountsEnabled": true` has a user, `service-account-CLIENT`, which Keycloak's export lists. It is a setting, so it is compared: enabled, groups, realm roles, client roles. The copy is built from the whole file, so a service account the file writes out (with `"serviceAccountClientId"`, to give it roles) is in it. One trap: a client whose service account the file writes out does not get the `service_account` client scope, and one Keycloak makes by itself does; both forms are `saved`, each compared with a copy built the same way.

**Not compared:**

- **People:** who exists, their groups, roles, passwords, keys and whether they are switched off. Checks make people of their own (`idp-user`), and provisioning changes the file's own people while a lab runs: federation's HR connector moves them between groups and switches leavers off, and its check then expects `saved`. A lab that must prove a person's group lasts reads the file (and that the file was applied, with `realm-saved`), or signs in after a `realm-apply`. An export lists no people in 26.8.2; `realm-saved` drops them if a later one does.
- **Values Keycloak never gives back:** an identity provider's client secret (`identityProviders[].config.clientSecret`: changed through the admin API, it still reads `**********` everywhere, tried here) and a key's private half (the key is still caught by its certificate). A lab whose learner sets an identity provider's secret proves it by signing in through that provider.

Each of these was changed in the running realm alone, through the admin API, on the one-of-each realm, and `realm-saved` named it: a redirect address, a client's secret (set, and regenerated), a mapper's setting, a new role, a service account's group, role and "enabled", a step of the browser flow, a new client (with and without a service account) and the token lifetime. The tests make the same changes to the saved export, and a SAML setting, a grant switched on and an identity provider's address as well.

### A realm file that can't be applied

A learner's realm file is unfinished for a while: a gap still to fill in, a comma missing, a name with no value, something Keycloak won't take. The rule is that **the running realm stays as it was until a file is applied that Keycloak takes whole**, and Keycloak itself always runs.

| What's wrong | Who finds it | `sudo realm-apply` says (and exits 1) |
| --- | --- | --- |
| a gap | `kcapi.py`, before Keycloak is asked | `/etc/keycloak/realms/shop.json, line 17: a gap ("...") is still to be filled in` |
| invalid JSON, an empty file | the same | `/etc/keycloak/realms/shop.json, line 6: not valid JSON: Expecting ',' delimiter` (the line is where Python noticed, often the line after the slip) |
| `${NAME}` with no value | the same | `/etc/keycloak/realms/shop.json, line 89: ${NO_SUCH_SECRET} is not in /etc/keycloak/secrets.env` |
| `"realm"` isn't the file's name | the same | `/etc/keycloak/realms/shop.json: "realm" must be "shop", the file's name` |
| valid JSON that Keycloak refuses (a person in a group that isn't there) | Keycloak, building the throwaway copy | `/etc/keycloak/realms/shop.json: Keycloak refused it (500): Unable to find group specified by path: /no-such-group` |

The last row is why `realm-apply` builds a copy first. Keycloak can only say whether it takes a file by building it, and the old `realm-apply` had deleted the running realm by then: one slip left the lab with no realm at all. Keycloak answers some such files with no more than `unknown_error`; the reason is in its log, and `kcapi.py` reads it from there (`keycloaks_reason`). Keycloak has no line numbers to give; its sentence usually names the thing. It does not check everything: a mapper whose type doesn't exist (`"protocolMapper": "no-such-mapper"`) was accepted here, so what a realm does is still a lab's checks' business.

**At a start** (a boot, the restart trial, `sudo systemctl restart keycloak@idp`, `sudo netlab restart`), with a file that changed and can't be applied:

- **Keycloak starts and the unit is `active`.** `lib/kc-wait`, the unit's `ExecStartPost`, never fails because of a realm file. Before this, it did: systemd started Keycloak again, found the same file, and went round for ever (a new start about every 30 seconds, counted here on the base as it was, and never a provider that answered).
- **Keycloak serves each such realm as its database has it:** the realm as it last was, from the last file that was applied, with everything made at run time since. Sign-ins go on working against that. Nothing of the new file is in effect, as with any file that was edited and not applied. If the realm was never built, there is no such realm (a lab's image is baked from a file that applies, so this needs a file added by hand). The other realms' files are still applied: one bad file doesn't hold back the rest.
- **One warning in the unit's journal says what and what to do,** once per start:

  ```text
  $ journalctl -u keycloak@idp -p warning -o cat
  keycloak: /etc/keycloak/realms/shop.json, line 17: a gap ("...") is still to be filled in. Realm shop was not rebuilt: Keycloak serves it as it was before the file changed. Mend the file, then: sudo realm-apply shop
  ```

  `realm-saved` and `sudo realm-apply` say the first sentence again whenever they are run, so a learner who never opens the journal still meets it at the first thing they type about the realm.
- **Mending it:** fix the file, then `sudo realm-apply` (a second or two), or restart; the next start applies a file that changed. Nothing needs `reset-failed`, because nothing failed.

So a fill-in lab may ship a realm file with gaps: bake the image from the file with the unfinished part left out, then put the file with the gaps in place (`csa.sec.federation`'s first fill-in does it with `jq 'del(.clients)'`). The lab boots with the baked realm and the warning above, which is true and points at nothing but the gap the prompt already names.

The start still fails, and systemd still tries again, when Keycloak doesn't answer within 280 seconds: that is Keycloak itself not coming up, not a realm file, and `journalctl -u keycloak@idp` has its own words. That case was not run here.

### Rules for realm files

1. **Applying rebuilds the realm, so what was made at run time and isn't in the file goes:** accounts made through SCIM, a security key someone registered, a check's own people, every session. A lab whose learner both makes such things and applies orders its steps so nothing is applied afterwards, and says so in its prompt.
2. **People in the file carry an `"id"`,** so their `sub` is the same after every apply.
3. **Write the file as Keycloak would store it.** A group mapper without `"multivalued": "true"` gained that setting in the running realm the first time a token was issued, and `realm-saved` then reported a difference nobody made. The rule is the network base's "seed files written by FRR": before a lab is done, sign in once and run `realm-saved`; whatever it reports goes into the file.
4. **Keys and secrets never go in the file:** `${SHOP_WEB_SECRET}`, `${ANA_PASSWORD}`, `${BEN_KEY}`. Signing keys are files in `/etc/keycloak/keys/REALM/`, added at apply, so they are the same after every apply.
5. **Everything a person needs to pass Keycloak's profile check** (`firstName`, `lastName`, `email`, `emailVerified`), or the first sign-in stops at an "update your profile" page.
6. **`"sslRequired": "all"`** costs nothing: every lab address is HTTPS from the lab's CA. No lab has a plain HTTP issuer.
7. **`"eventsEnabled": true`,** as the probe's file has. The journal's sign-in lines were seen with it; whether they appear without it was not tried.

## Sites and APIs that rely on the provider

**Apache with mod_auth_openidc** (`run app apache2`, the unit `apache2@app`): the code flow with PKCE (`OIDCPKCEMethod S256`), the client secret in an included file only root reads, `Require claim groups:staff`. What a check reads: a CGI page that prints `user=$REMOTE_USER` and `groups=$OIDC_CLAIM_groups`, and Apache's error log on the machine (`on app tail /var/log/apache2/error.log`), which names each failure. Three things found by running: it answers `401`, not a redirect to the sign-in, to a client that doesn't ask for HTML, so `signin` sends a browser's `Accept` header; the unit's start script makes the run and lock folders a machine's empty `/run` lacks; and the signed-in person's access token reaches a CGI script as `$OIDC_access_token`, so "the site calls the API as the person" is three lines of shell. Apache starts after Keycloak, a moment after the boot counts as finished, so a lab's first check waits a few seconds for it (`wait_for 10 on office curl -s -m 2 -o /dev/null https://app.shop.test/`).

**Apache with a configuration file it can't read never starts, and never gives up.** The unit tests the configuration first (`apache2 -t`) and has `Restart=on-failure` with `RestartSec=2`, slow enough that systemd's start limit is never reached: with a bad line in a site file, 12 restarts in 32 seconds were counted here, and it goes on for as long as the file is wrong. What a learner sees: `sudo systemctl restart apache2@app` answers `Job for apache2@app.service failed because the control process exited with error code`; `systemctl status apache2@app` says `activating (auto-restart) (Result: exit-code)`; the site doesn't answer (`curl` can't connect); the lab machine as a whole still counts as booted (`systemctl is-system-running` says `running`), so the checker's wait for a boot isn't held up. Why: `on app apache2ctl -t`, or `journalctl -u apache2@app -n 5`, gives Apache's own line (`AH00526: Syntax error on line 28 of /etc/apache2/sites-enabled/orders.conf: Invalid command ...`). What they do: mend the file. Apache then starts by itself within two seconds; `sudo systemctl restart apache2@app` does no harm and `reset-failed` is never needed, because the unit never reaches `failed`. So a fill-in lab may ship an unfinished site file, and its prompt says the site is down until the file is done.

**`stock-api`** (`run api stock-api`, the unit `stock-api@api`) is the base's stand-in API, for labs where the API is scenery: HTTPS on 443, `GET /stock/level`, a bearer token required. Its settings are seven lines in the machine's `/etc/stock-api/api.conf` (`name`, `issuer`, `audience`, `jwks_uri`, `leeway`, and the two switches a hurried fix reaches for, `check_audience` and `check_expiry`), and its journal gives the reason in plain words: `10.0.5.20 refused: audience 'https://apis.shop.test' doesn't include 'https://api.shop.test'`. It fetches the keys by address, and once more when a token names a key it doesn't have.

**mod_oauth2** is for labs where the learner builds or repairs the API (federation's build and debug, Checkpoint 4's second part). It is installed and switched off; `idlab a2 api mod oauth2` switches it on for a machine whose topology line says `run api apache2`. It was run once on this base, by hand in the probe lab, in place of the stand-in API:

```apache
<Location /stock/>
  AuthType oauth2
  OAuth2TokenVerify jwks_uri https://login.shop.test/realms/shop/protocol/openid-connect/certs
  <RequireAll>
    Require oauth2_claim iss:https://login.shop.test/realms/shop
    Require oauth2_claim aud:https://api.shop.test
  </RequireAll>
</Location>
```

It served the provider's access token (`200`) and refused the ID token (its audience is the site), a token signed by another key and an unsigned one (`401` each). Three things found:

- **Two `Require` lines without `<RequireAll>` mean "either":** the issuer line alone granted a token for any audience.
- **It answers a token it has already accepted from its cache, past the token's expiry.** With 20-second tokens, a token it had served was still served 46 s after it expired, while one it had never seen was refused 6 s after its expiry (`_oauth2_jose_jwt_validate_exp: "exp" validation failure (1795396087): JWT expired 7 seconds ago`, in the machine's `error.log`). So a check of expiry shows the API a token it has never seen, and the federation lesson says why.
- **An option it doesn't know makes it refuse every token** (`error_description="Token could not be verified."`): `verify.iss=required&verify.exp=required&verify.iat.slack_after=60` after the address did that here. The plain line above checks signature and expiry; the first lab that needs more reads liboauth2's own list of options.
- **It logs nothing when a signature doesn't verify.** A token signed by another key and an unsigned one each got `401` and left not one byte in the machine's `error.log`, with `LogLevel warn oauth2:info` (federation's debug lab, 2026-11-23). Text that isn't a token at all does leave a line (`oauth2_jose_jwt_verify: cjose_jws_import failed`), and so does an expired token, below. So the log can't tell a learner "wrong key": a `401` with a silent log, for a token whose issuer, audience and expiry are right (`jwt show`, `jwt verify`), is the evidence, and a lesson says so. `stock-api`, the stand-in, does name the reason.
- **It allows no slack on expiry.** A token it had never seen was served 1.7 s before its `exp` and refused 0.6 s after it (`"exp" validation failure (1795420622): JWT expired 1 seconds ago`). `stock-api`, by contrast, forgives 60 s both ways. So an API on mod_oauth2 whose clock runs a few seconds ahead refuses tokens early, and a check that shows it an expired token needs no margin beyond a second.

**mod_auth_mellon** (SAML) is installed and switched off. The designer ran one sign-on through it with the provider's metadata fetched from the running Keycloak. Not tried: metadata written at image build, and a NameID that is the user name.

## What the learner types

| Tool | Does |
| --- | --- |
| `on office signin URL USER [-v]` | Opens a page as the person's browser: follows redirects, keeps cookies (`--jar FILE` between runs), fills the provider's sign-in form, types a one-time code (`--otp-secret`), uses or registers a security key (`--key`, `--register-key`), posts the forms single sign-on sends through the browser. Prints each thing the person did, then `signed in: 200 URL` and the page, or `refused: WHY`. `-v` shows every request and redirect, long values cut |
| `signin --code CLIENT REDIRECT_URI ISSUER USER [--secret=S]` | Is the app: runs the code flow with its own PKCE pair, state and nonce, and prints the token response. `signin --code ... \| jwt show` is how to see a sign-in's claims |
| `signin --approve-device CODE USER` | Is the person a device showed a code to: opens the provider's device page, types the code, signs in as USER and answers yes. Prints `approved: ...`, or `refused: Invalid code, please try again.` |
| `jwt show [FILE]` | Header and payload as JSON, and `iat`, `nbf`, `exp` as dates "by this machine's clock" |
| `jwt verify --issuer=URL --audience=AUD [--nonce=N] [--leeway=S]` | `valid sub=...`, or `invalid:` and the first of `format alg key signature issuer audience expired not-yet-valid nonce` |
| `sudo realm-apply`, `realm-saved`, `kc get PATH`, `kc-flows REALM` | the realm, above |
| `on app clock` | `app's clock reads 2026-11-23 00:28:50 UTC: 8 min 0 s ahead of the real time`, then its time sync's state, the servers its file names, and the time sync's last line |
| `kcadm.sh`, `jq`, `xmlsec1`, `oathtool`, `openssl` | the real tools |

`signin` is honest about what it is. The first lab that uses it says it is the lab's scripted browser and shows a sign-in with `-v` beside the same flow done by hand with `curl`; from then on it is a tool. Its "refused" lines are the browser's or the page's own words where there are any (`refused: Invalid parameter: redirect_uri` is Keycloak's error page; `refused: Account is disabled, contact your administrator.`).

There is no admin console for the learner: `labcheck` publishes no ports. Files, `kc get`, `kcadm.sh` and `signin -v` show every message, which a console hides, and the console is where drift comes from.

## Security keys

`signin` holds a software authenticator: a P-256 key, attestation `none`, the flags and counter a real key sends. No real browser and no hardware take part.

- **Registration** at Keycloak's own page (`--register-key FILE`), and **sign-in** with the key once the flow asks (`--key FILE`).
- **A key made at image build** (`idlab seckey`) and carried by the realm file as a `webauthn` credential, so a lab can start with people who already have keys. A key registered at run time is lost at the next `realm-apply` (rule 1), so labs that need people with keys use `idlab seckey`.
- **The three refusals,** each by the party that makes it in real life: the browser (`refused by the browser: the page on login.shop-help.test asked for a key for login.shop.test`: a page may ask for a key only for its own host or a parent of it); the key (`refused by the key: the security key has no credential for ...`); and the server, when a browser lies with `--origin` (`refused: Passkey origin mismatch.`, Keycloak's own page).
- A person with a key and no `--key` is stopped: `refused: the page asks for a security key, and this person has none`.

What the lab proves is what the **server** enforces: challenge, origin, relying-party id, signature, counter. It models the browser's and the key's rules in forty readable lines of `signin`. It does not prove user verification (a PIN or a fingerprint: the flag is simply set), attestation (which make of key), or anything about synced passkeys. The lesson says so in two sentences.

## Clocks

Every machine in a lab is a network namespace in one container, and all of them share the kernel's one clock. In a privileged container that clock is the real clock of Docker's whole machine. So **nothing in a lab ever sets it** (the network base's `date` refuses `-s`; chrony only ever runs with `-x`), and a machine that needs a time of day of its own gets one made of three small parts:

- **The machine's clock is an offset.** A machine whose topology line says `run app timesync` has its own `/etc/faketimerc`, holding how far its clock is from the real time, in seconds (`+480`). `lab-enter`, the one door every command and daemon on a machine comes through, gives everything started there libfaketime, which adds that offset and reads the file again every second. So `on app date`, Apache's log times and its token checks all read app's clock, and a daemon already running takes a correction within a second, with no restart.
- **Its hardware clock is scenery.** `/etc/clock/hwclock` (`machines/app/clock/hwclock` in the lab's folder; sealed) holds how far off the machine's hardware clock is: `+480`, `-1200`, or `+8m`. At every boot, `machine-clocks.service` sets each such machine's clock from it, as a server's is before its time sync has spoken.
- **Its time sync sets it right, if it can.** `timesync@app` is a small SNTP client. It reads the `server` lines of the machine's `/etc/chrony/chrony.conf`, the file chrony's own client reads, asks the first server that answers, and steps the machine's clock to it. Its journal says what a real client's would:

  ```text
  time server time-old.shop.test: the name doesn't resolve; the clock is not synchronized
  synchronized to time server 10.0.5.40:123 (time.shop.test): clock stepped by -480.0 s
  ```

  The server is real: `run ntp chrony` runs `chronyd` on a machine, as `chrony@ntp`, from the machine's own `/etc/chrony/chrony.conf` (two lines: `local stratum 8` and `allow 10.0.5.0/24`). The `-x` that stops it setting a clock is written in the unit, never left to the lab's file.

So a clock fault has a cause to find (a server name that no longer resolves, a time server that won't answer this network, a time sync that isn't enabled), it lasts across the restart trial (the hardware clock is still wrong at the next boot), and the fix is at the cause: mend the file, `sudo systemctl restart timesync@app`. Setting the clock right by hand (writing `+0` into the machine's `faketimerc`) is lost at the next boot, and `clock_synced` fails it at once. `timesync@M` counts as started once it has had its chance (up to ten seconds for a server that is still starting, no wait when its file names none that resolves), so the boot covers the clock, and `systemctl restart timesync@app` returns with the clock set.

The lesson says once that this time sync is a stand-in, because the lab's machines share one real clock.

**Which way to skew** is the lab's choice. Both ways were run on this base, with five-minute tokens, and Apache's error log on `app` said:

| app's clock | What happens | mod_auth_openidc's line |
| --- | --- | --- |
| **ahead** by more than the token's life (`+480`) | the site sees every token as expired; the browser gets `400 Bad Request` at the callback | `oidc_proto_validate_exp: "exp" validation failure (1795393550): JWT expired 180 seconds ago` |
| **behind** by more than 600 s (`-1200`) | the site sees every token as issued in the future; `400` at the callback | `oidc_proto_validate_iat: "iat" validation failure (1795393253): JWT was issued more than 600 seconds in the future` |
| behind by less than 600 s (`-500`) | nothing: the sign-in works | none (600 s is mod_auth_openidc's default slack for `iat`) |

`stock-api` forgives 60 s either way. In both failing cases the two logs disagree about when the same sign-in happened, by the size of the skew (app's `error.log` against `journalctl -u keycloak@idp`), and `on app clock` and `jwt show` ("exp: ... 181 s ago by this machine's clock") say it outright. Federation's worked example uses ahead, Checkpoint 4's second part behind.

**Skew the site or the API, never the provider.** Keycloak was not tried under libfaketime, and no lab needs it.

**What libfaketime can't do** (Ubuntu 24.04's is 0.9.10):

- **Python's `time.sleep` fails** on a machine with a clock of its own: `OSError: [Errno 22] Invalid argument` (found building this base: Python sleeps until a time on the steady clock, and 0.9.10 moves that time though it was told to leave the steady clock alone; upstream fixed it later, and 0.9.13 has the fix). A Python program there that only reads the time, waits on a socket or serves requests is fine: `signin`, `jwt` and `stock-api` all are. The base's own `timesync` steps outside libfaketime for this reason. So: no lab runs a Python program that sleeps on a machine that runs `timesync`; a shell script's `sleep` works.
- **Go programs read the real time** (they don't use the C library's clock: libfaketime's own README, not tried here), so oauth2-proxy can't be skewed.
- **It is kept away from `/dev/shm`.** Left alone, libfaketime 0.9.10 makes a semaphore and a shared-memory file in `/dev/shm` for the first program of every command (named after its process number, mode 600, never removed: 8 kB a command), names them in `FAKETIME_SHARED`, and every program started from there must open them or make its own; one that can do neither exits (`ft_shm_init`: `sem_open failed and recreation attempts failed`). On GitHub's runner every command on `app` exited that way, with `Permission denied`, which Docker Desktop never showed; why the runner refuses was not found. The files only let one command's processes agree on when it began, which a fixed offset doesn't need, and the library carries on without them where it can't make its semaphore. So `lib/faketime-noshm.c`, twenty lines of C built in the `Dockerfile` and preloaded just before the library, fails that one call (`sem_open` for a name starting `/faketime_sem_`): no file is made, no program is told to open one, and nothing piles up. Every other semaphore goes through untouched: Apache with mod_auth_openidc makes its own in `/dev/shm`, so that folder must stay writable.
- **`timesync` itself never loads it.** Its unit sets `NETLAB_REAL_CLOCK=1`, which makes `lab-enter` leave libfaketime out, and `clock_synced` asks the same way.

## Check helpers

Checks source `. /usr/local/lib/idlab/idlib.sh`, which brings the network base's helpers too (`wait_for`, `json`, `intact` ...), and run as root on the lab machine.

| Helper | What it reads |
| --- | --- |
| `kc get PATH`, `kc post\|put PATH < body.json`, `kc delete PATH` | Keycloak's admin API, as JSON; PATH is what follows `/admin/realms/` |
| `kc_saved REALM` | `saved` when the running realm equals a fresh build of its file; the differences otherwise |
| `kc_ready` | exit 0 once Keycloak answers (for a check that restarted or reloaded it; the boot already waits) |
| `client_field REALM CLIENT EXPR` | a field of a client as the running server has it: `client_field shop shop-web "' '.join(d['redirectUris'])"` |
| `password_of USER`, `secret_of NAME` | a person's password; a value from the realm's `secrets.env` |
| `clock_offset M` | M's clock minus the real time, in seconds |
| `clock_synced M` | `in sync with time server NAME` and exit 0 when a server M's file names answers now and M's clock agrees with it; why not, and exit 1, otherwise. It asks the server itself |
| `on office signin ...`, `signin --code ...`, `jwt verify ...` | a real sign-in, and the check's own verdict on the tokens |
| `mint-token --iss=URL --aud=AUD [--alg=none] [--exp-in=S] [--claims=JSON]` | a token the check makes, signed with a key made on the spot or not signed, to prove an API refuses what it should |
| `idp-user add REALM NAME PASSWORD [--otp] [--key] [GROUP...]`, `idp-user disable\|del REALM NAME` | a person the check makes at the provider, switches off, or removes; `--otp` gives them an authenticator app (`/etc/idlab/otp/NAME`), `--key` a security key (`/etc/idlab/keys/NAME.key`) |

## Rules for checks and labs on the base

From the Module 4 brief, section 3.3, and from running the probe.

- **A check's own verdict on a token.** The check signs in itself, as the app (`signin --code`, with its own PKCE pair, state and nonce), and runs `jwt verify`: signature against the provider's published keys, issuer, audience, expiry, nonce. It never trusts the app's word.
- **A check may make people and devices of its own at the identity provider, and removes them** (ADR-0018, fourth amendment): `idp-user add shop chk-u$r ...` with the removal in an `EXIT` trap, a name starting `chk-`, and never `kc_saved` or `realm-apply` while they exist. It changes nothing the learner made. Random people are what make an allow list of the lab's own people fail.
- **Random values go after `=`, and are hex.** `--nonce="$n"`, `--secret="$s"`, `--iss=$iss`. A random value that began with `-` was read as an option and failed one right answer in four parallel runs (the designer's finding). `signin` makes hex state and nonce values; a check makes its own with `od -An -N4 -tx1 /dev/urandom | tr -d ' \n'`.
- **One sign-in with a one-time code per person per 30 seconds.** Keycloak refuses a code it has already accepted (`refused: Invalid authenticator code.`, seen on this base). A check that needs two sign-ins with a code makes two people, or keeps the first session with `--jar`.
- **A file a check hands to `on M` goes under `/srv`, never `/run`.** Every machine has a `/run` of its own (`lab-enter` gives it one, and it starts empty at every boot), so a file the check writes to the lab machine's `/run` isn't there for a command run with `on M` (`cat: /run/x: No such file or directory`, tried here). `/srv` is one folder for the lab machine and every machine (so is `/tmp`, which is everybody's to write in). A check removes what it wrote.
- **`json` prints a bare value as Python does:** `json "d['enabled']"` prints `False`, `True` or `None`, not `false`, `true` or `null` (a list or an object is printed as JSON; a string or a number as itself). Compare with `False`, or ask for the word: `json "str(d['enabled']).lower()"`.
- **Allowlists, not denylists,** where a check must read a configuration: "the only verify line is `jwks_uri` with the realm's HTTPS address", not "no `pem` line".
- **Never file times.** Docker Desktop and a fresh CI checkout disagree about them. "Written after the fix" is proved by comparing content with a fresh run.
- **Read every included file** when a setting can live in more than one (`apachectl -t -D DUMP_INCLUDES`).
- **Fixes last.** The realm's lasting place is its file (`kc_saved`); a clock's is the machine's time sync and its file (`clock_synced`, and `systemctl is-enabled timesync@M`); Apache's is its site file. Write a `wrong/*.sh` that makes each fix live only: through the admin API, with a hand-written `faketimerc`.
- **The scenery is sealed:** the topology, the API's settings where they aren't the learner's, the time server's file, every `clock/hwclock`.
- **A machine's own file that sits straight in `/etc`** can't be replaced, only written into (the network base's README): `faketimerc` is one, which is why `timesync` writes it in place.
- **A debug lab's untouched state may pass a check or two** (the probe's API strictness and `realm-saved` pass before any work): "nothing passes before work" is not a rule, but those are availability-free checks.
- **Say what a laptop needs** in the first identity lab's "before you start": about 0.8 GB of memory and 1.4 GB of disk.

## Kernel and runner needs

Everything the network base needs, and three things of this base's own. "Works" for Docker Desktop means seen on Docker Desktop 29.8.2 on 2026-11-22. **Nothing here has run on a GitHub runner yet:** the probe lab in `csa.sec.base-probes` is there so the Labs job shows each row.

| Need | Who | Docker Desktop | GitHub's runner |
| --- | --- | --- | --- |
| Keycloak's boot, which is CPU-bound, with four labs at once on four CPUs | every identity lab | works: see "Size and time" | **untried; the main risk** |
| `net.ipv4.ip_unprivileged_port_start` set inside a namespace | `keycloak@idp` | works | untried |
| libfaketime preloaded, behind `faketime-noshm` (it makes no semaphore of its own) | a machine that runs `timesync` | works for Apache, curl, openssl, `date`, a shell's `sleep`; not Python's `time.sleep`, not Go | untried |
| `chronyd -x` serving NTP on a machine (UDP 123 in a namespace) | `chrony@M` | works | untried |

## Still untried on this base

Each is small, and belongs to the first writer who needs it (Module 4 brief, section 4.1):

- a sign-in flow written in a realm file that requires a security key by role, and the `amr` claim. A sign-in here carries `"acr": "1"` and no `amr`: the mapper (`oidc-amr-mapper`) needs each flow step's reference value, which lives in a flow in the realm file, so the two arrive together. There is no "starting realm" in the base for the mapper to go into; a realm is always a lab's own file;
- mod_oauth2 beyond the one trial above: its options, how long its cache keeps a verdict, and a learner's-eye lab on it;
- SAML's NameID as the user name, and the provider's metadata written at image build;
- a SCIM token for a service client (the designer's admin token got `401` at the SCIM endpoint);
- `signin` through oauth2-proxy, and the size of its cookie;
- Keycloak's sign-in events as a watching unit reads them;
- a page on a second host asking for a key (the relay): `signin`'s refusal is written and was not run against one;
- `realm-saved` on a realm whose file writes a sign-in flow of its own, LDAP or a client policy: the one-of-each realm had none, so a value Keycloak stamps there would show as a difference nobody made, and joins `STAMPED` with its reason;
- a Keycloak that doesn't answer within 280 seconds at a start;
- `ca-whatif`: it has one source, in the policy-lab base (`content/lab-bases/policy/bin/ca-whatif`), and a byte-identical copy here in `bin/`. Change the policy base's, then copy it over this one; `tools/tests/test_idlab_helpers.py` fails if the two differ.

## Files here

| File | What it is |
| --- | --- |
| `Dockerfile` | the image: three layers on `lab-base-net` |
| `bin/idlab` | what a lab's Dockerfile runs: names, certificates, secrets, accounts, keys, the bake |
| `bin/signin` | the scripted browser, with the software security key (its reading of Keycloak's pages is tested in `tools/tests/test_idlab_signin.py`) |
| `bin/jwt` | `jwt show`, `jwt verify` |
| `bin/realm-apply`, `bin/realm-saved`, `bin/kc`, `bin/kc-flows`, `bin/idp-user` | the realm and the admin API, each a line that goes to the provider's machine and runs `lib/kcapi.py` |
| `bin/clock` | `on M clock` |
| `bin/mint-token` | a check's forged token |
| `bin/stock-api` | the stand-in API |
| `lib/kcapi.py` | Keycloak's admin API: apply, saved, flows, a check's people, plain reads and writes (`tools/tests/test_idlab_kcapi.py`, on exports saved in `tools/tests/keycloak_exports/`) |
| `lib/jwtlib.py` | reading and checking tokens, RS256 only, standard library only (`tools/tests/test_idlab_jwtlib.py`) |
| `lib/idlib.sh` | the check helpers |
| `lib/timesync` | the time sync client (`tools/tests/test_idlab_helpers.py`) |
| `lib/machine-clock` | each machine's clock from its hardware clock at boot; `clock_offset` |
| `lib/make-key` | a security key made at image build, or for a check's person |
| `lib/kc-build-run`, `lib/first-start`, `lib/kc-wait` | Keycloak inside an image build; its first start; the wait that makes "started" mean "answering", and that keeps a realm file that can't be applied from failing the start (`tools/tests/test_idlab_helpers.py`) |
| `lib/faketime-noshm.c` | keeps libfaketime from making a semaphore and shared memory in `/dev/shm`; the `Dockerfile` compiles it in a stage of its own |
| `lib/apache2-run` | Apache inside a machine, whose `/run` starts empty |
| `lib/plain-units` | the plain `apache2` and `chrony` units, replaced by ones that say what to type |
| `units/` | `keycloak@`, `apache2@`, `stock-api@`, `timesync@`, `chrony@` and `machine-clocks.service` |
| `.dockerignore` | keeps a stray `__pycache__` out of the image |

Three things this base needs live in the network base, because they are shared plumbing: `netlab` knows the five services above, `lab-enter` gives a machine its own Apache and chrony folders and its own clock, and `date` refuses to set one.

## Size and time

Measured on the owner's PC on 2026-11-22 (Docker Desktop 29.8.2, 8 CPUs, 15.5 GiB for Docker). Keycloak's start is CPU-bound, so the times depend on what else the machine is doing. Each was measured twice: **quiet**, with nothing else running in Docker, and **busy**, while other sessions' lab containers used two CPUs or more throughout.

| What | Measured |
| --- | --- |
| Image | 1.35 GB as Docker Desktop reports it (the network base is 659 MB of it; Java is 194 MB of files and Keycloak 184 MB) |
| Base build, on an existing `lab-base-net`, nothing cached | about 100 s: the packages 43 s, the download 13 s, layer 3 33 s |
| A lab's own image | 13 s by the designer's measure, 9 s of it baking the realm (Keycloak starts once inside the build) |
| Container start to booted, Keycloak answering, one lab | quiet: 8.0 to 13.1 s, median 8.8 s (nine boots of a contract). Busy: 14 to 32 s, median 24.5 s |
| The same, four labs at once | quiet: 20.3 to 23.9 s, median 22.1 s (36 boots). Busy: 34 to 77 s, median 46 s |
| Memory, one lab | 550 to 620 MiB for the container (621 MiB at most over a whole contract); Keycloak's heap is capped at 384 MB |
| Memory, four labs at once | 2.4 GiB at most between them (sampled every 4 s); the largest single container 640 MiB |
| `realm-apply` | 1 to 2 s when it was delete-and-create (2026-11-22). Since it builds a copy first (2026-11-23) it makes two realms and removes two: 3.8 to 5.0 s for the probe's realm and 4.9 to 6.5 s for a realm with fourteen clients, both measured on a very busy machine (load average 13 to 20 on 8 CPUs), where delete-and-create alone took 1.5 s. Not measured quiet |
| `realm-saved` | 2.8 to 3.2 s for the probe's realm, 3.9 to 4.6 s for the fourteen-client one, on the same busy machine; the first run after a boot took 12 to 15 s there (Keycloak's code is cold) |
| The probe lab's eight checks, one run | 7 s through `labcheck check` |
| **The probe lab's contract, alone** (pristine, solution, restart trial, six wrong fixes: nine boots, ten runs of the checks) | **174 s** quiet, 439 s busy |
| **Four such labs at once** (`labcheck test --all --jobs 4`) | **366 s each** quiet, 783 to 793 s busy; all four kept, both times |

Four at once on eight CPUs already makes a boot two and a half times as long as one alone. What a contract costs is about (wrong fixes + 3) boots and as many runs of the checks, and the boot is the larger part. **A GitHub runner has four CPUs, and nothing here has run on one.** The plan's CI spike reads the boot with four labs at once there; if it is over 45 s, an identity lab counts as two of a machine's four jobs (the plan's P6, not built).
