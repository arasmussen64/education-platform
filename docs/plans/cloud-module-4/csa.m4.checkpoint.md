# Checkpoint 4: the threat model, the broken sign-in and the leak (`csa.m4.checkpoint`)

Designer's brief, 2026-11-22 (designer key `checkpoint`). The writing brief for Module 4's checkpoint, in the shape of Checkpoint 3's (`docs/plans/cloud-module-3/csa.m3.checkpoint.md`), whose decisions stand: parts in the slots `prove.build`, `prove.debug` and `prove.more` (ADR-0012 as amended 2026-11-11); the explain opens once part 1 passes; time targets are stated and self-timed; everything proven locally and for free.

Design only: nothing here is in the repository. Prototypes, captured output and the contract log are in `prototypes/checkpoint/` (its `README.md` lists the files). Everything marked **tried** ran on 2026-11-22 on the owner's PC (Docker Desktop 29.8.2, with other sessions' containers running). Everything made in Docker was removed.

I read the eleven topic briefs' skills tables and the parts of the threat-modeling, federation, secrets, PKI, audit and compliance briefs that this checkpoint leans on. I did not see an identity-lab base brief (none is in the folder), but the base designer's prototype image, `lab-base-idproto`, was on this machine, so part 2 was built `FROM` it. Section 8 lists what I assume of each topic and of the base, and every place the designs don't yet fit.

## 1. The plan in one screen

- **Three parts, not two.** Part 1, the threat model of a checkout that takes card payments, with its PCI DSS scope and a control for each high risk (a build, in a plain lab, a file the checker reads). Part 2, the staff sign-in that fails in three ways (a debug, in an identity lab). And a new **part 3, the leak** (a build, on the payments-server base): a repository with secrets in its history was public for six hours, and the learner finds what leaked, rotates the key, revokes and replaces the certificate, and reads the audit trail for what the leaked key did. The spec's two parts never touch secrets, certificates or the audit trail by hand; section 6 argues the third part and gives the spec text.
- **Part 1 uses the format the learner practised.** The threat-modeling topic's line format and `tm-check`, with one new line (`scope ELEMENT cde|impacting|out reason`) and one new part. The design's six weaknesses each come from a different Module 4 topic, so the model is the module's judgement retrieved in one place. **Tried:** a re-implementation of the checker passes the 64-line reference model, and each of 25 wrong models fails exactly the part aimed at it.
- **Part 2 is a real sign-in on five machines** (a staff laptop, Keycloak, the orders site, the orders API, a time server). The three faults sit in a chain, each hiding the next, so the symptom changes after every fix. **Tried, on the base designer's prototype image:** each fault planted, seen in the evidence and fixed; eleven checks; the solution passes, and passes again after a restart; each of 13 wrong fixes fails the check aimed at it; 15 container runs in 584 s.
- **Part 3 is designed on mechanisms the topic designers tried** (gitleaks over history, `openssl ca -revoke` and a CRL a client checks, a hash-chained trail). I did not prototype it (open question 2).
- **Support** (ADR-0012) for part 1: a solved sibling, four steps, two fresh versions. Part 3 has one fresh version. Part 2, a debug, has none.
- **Time:** part 1 75, part 2 60, part 3 60, explain 20; `estimated_minutes: 240` with labs' starts and re-checks. The generated outline says 480, which no count supports.
- **CI:** about 30 minutes of container time for the checkpoint's 11 labs (section 10).

## 2. Prerequisites, objectives and the proof block

**`prerequisites:`** the eleven Module 4 topics, as the outline has them.

**Objectives** (no fault of part 2 named; see open question 1 on the spec's wording):

- "Threat-model a shop's checkout that takes card payments: draw it, mark where trust changes, find and rank what can go wrong, say which parts are in PCI DSS scope, and choose a control that answers each high risk, aiming for 75 minutes on your own clock."
- "Find and fix a staff single sign-on that fails in three ways, from the evidence it leaves, without weakening any check it makes and with every fix lasting past a reboot, aiming for 60 minutes on your own clock."
- "Answer a leak: find every secret in a repository's history, rotate the key and revoke and replace the certificate without taking the service down, stop the next leak at the push, and read the audit trail for what the leaked key did, aiming for 60 minutes on your own clock."
- "Explain how a system's identity, keys, secrets, logs, patches and evidence fit together, and how the three clouds differ."

```yaml
prove:
  build: build-model-the-checkout          # part 1 (plain lab)
  debug: debug-the-staff-sign-in           # part 2 (identity lab)
  more:
    - id: build-answer-the-leak            # part 3 (systemd lab on lab-base-sec)
      versions: [build-answer-the-leak-clinic]
  explain: ...                             # opens once part 1 passes
unstuck:
  example: example-model-the-print-shop
  steps: [step-draw-and-scope, step-find-the-threats, step-rank-and-answer, step-the-whole-model]
  versions: [build-model-the-checkout-clinic, build-model-the-checkout-bakery]
```

One business runs through all three parts: the shop of Modules 1 to 3 (`shop.test`). The longest path this makes is `content/topics/csa.m4.checkpoint/exercises/build-model-the-checkout-bakery/wrong/only-backoffice-in-scope.sh`, 108 characters, inside the 150 limit.

## 3. Part 1: `build-model-the-checkout` (plain lab, 75 minutes)

### 3.1 What the learner gets

`~/design.md`, read-only (checksummed), and an empty `~/model.tm`. The prompt holds the format table (the topic's, plus the `scope` line), the control kinds, and the three scope words with their rule. `tm-check PART ~/model.tm`, run by the learner without a reference, checks format and arithmetic only (`reads`, `ranking`, `tree`), as in the topic.

**The design** (every sentence a fact; nothing is labelled a weakness). The shop is adding card payments through a payment provider, PayPoint.

| Part | What the design says |
| --- | --- |
| `customer` | A customer's browser, anywhere on the internet. |
| `staff` | A staff member's laptop on the shop's office network. |
| `psp` | PayPoint: its card form and its API. PayPoint runs both and is assessed against PCI DSS itself. |
| `web` | The storefront and checkout page: static files on the cloud's object storage behind its CDN, with no route into the shop's subnet. The checkout page shows PayPoint's card form in an inline frame, so the card goes from the browser straight to PayPoint. The page also loads `stats.js` from an analytics company's server by address; nothing pins its content, and the page's headers allow scripts from anywhere. |
| `orders-api` | Creates orders, asks PayPoint to take a payment, and refunds. It never receives a card number. Its PayPoint API key, which can refund, is in `config/prod.env` in its repository, which every contractor can read. Its hook `/hooks/payment` takes PayPoint's "paid" message from any caller: PayPoint signs each message, and checking the signature is not switched on. A "paid" message marks the order for dispatch. |
| `backoffice` | Staff pages: refunds and phone orders. Its address is public; staff sign in with a password. For a phone order a staff member types the customer's card number, expiry and code into a form, and the back office sends them to PayPoint. It logs every request's body. Refunds are recorded with the order and the amount, not with who made them. Every page checks the staff role. |
| `orders-db` | Orders, the last four digits of the card, and PayPoint's token. |
| `app-logs` | The log server. Every engineer can read it. |
| `stock-db` | Stock levels, on the warehouse network. A firewall lets only `orders-api` open connections to its database port; nothing on the warehouse network can open a connection to the shop's subnet, and no card data is sent there. |
| Networks | `orders-api`, `backoffice`, `orders-db` and `app-logs` are on one subnet, 10.20.1.0/24, with nothing filtering between them. |
| Already in place | HTTPS everywhere; the CDN absorbs floods; the load balancer rate-limits; PayPoint's API authenticates both ways. |
| Flows | `f1` customer to web; `f2` customer to psp (the card form); `f3` web to orders-api; `f4` orders-api to psp; `f5` psp to orders-api (the hook); `f6` staff to backoffice; `f7` backoffice to psp; `f8` orders-api to orders-db; `f9` backoffice to app-logs; `f10` orders-api to stock-db. |
| Scales | Likelihood 3: anyone on the internet, with no account and nothing stolen first. 2: it needs something first, such as a staff or contractor account, or control of a supplier's or the shop's own system. 1: an administrator's rights or physical access. Impact 3: card numbers exposed, or money paid out of the shop's account. 2: an order or one customer's details exposed or falsified (goods sent unpaid counts here). 1: a nuisance. |

**The task.** Write `~/model.tm`: zones (one zone is one owner and one network: two parts share a zone only when the same organisation runs both and nothing filters between them), elements, flows; a `scope` line for every process and store the shop runs; every flow that crosses a boundary reviewed for all six letters; ratings by the design's scales; the `top` line; a control for every risk of 6 or more, a control or an `accept` for the rest; an ATT&CK technique for the threat on the staff sign-in and for the threat on the API key; an attack tree for the highest risk.

**The scope words, as the prompt gives them** (from PCI DSS v4.0.1 section 4, facts P1 and P2): `cde`: card numbers or codes are stored on it, pass through it, or it sits on a network with something they do and nothing filters between them. `impacting`: no card data reaches it, but if it were taken over it could change what happens to card data (it serves the page that holds the card form, or signs people in to a `cde` system, or administers one). `out`: neither, and kept apart so that taking it over would not put card data at risk.

### 3.2 The reference (the solution; the prompt never shows it)

Six zones (internet, office, provider, edge, shop-net, warehouse). Eight flows cross (`f8` and `f9` don't). Scope: `web` impacting; `orders-api`, `backoffice`, `orders-db` cde (the back office handles card numbers, and the other two share its unfiltered subnet); `app-logs` cde (it holds card numbers and codes today); `stock-db` out. The weaknesses, each from a different topic:

| Flow, letter | The design's fact | L x I | Controls that answer it | From topic |
| --- | --- | --- | --- | --- |
| `f6` S | a password alone, on a public address, and a signed-in member can refund | 3 x 3 = 9 | `mfa`, `access-proxy`, `mutual-tls` (not `authn`: a password already is one) | strong-auth, zero-trust |
| `f5` S | the hook takes any caller | 3 x 2 = 6 | `signing`, `mutual-tls` (not `tls`) | crypto |
| `f1` T | a third party's script, unpinned, on the page around the card form | 2 x 3 = 6 | `integrity` | vulnerabilities, compliance (PCI DSS 6.4.3) |
| `f4` S or I | the refund-capable key in a repository contractors read | 2 x 3 = 6 | `secret-store` (not `encryption`: an encrypted key in the repository still has a key somewhere) | secrets |
| `f9` I | card numbers and codes in the request logs | 2 x 3 = 6 | `minimise-data` only (PCI DSS 3.3.1: not stored after authorization "even if encrypted", fact P4) | audit, compliance |
| `f6` R | refunds recorded without who made them | 2 x 2 = 4 | `audit-log`, or `accept` | audit |

ATT&CK (v20.1, facts A1 and A2): `f6` S takes T1110 or T1078 and their sub-techniques; `f4` takes T1552 and its sub-techniques. The reference model is 64 lines (`prototypes/checkpoint/tm/out/reference.tm`).

### 3.3 Checks (each runs one `tm-check` part with the reference from `checks.yaml`; under a second each)

| id | End state (the description) | `test_skills` |
| --- | --- | --- |
| `model-reads` | The model reads: every line is one of the format's | `csa.sec.threat-modeling/draw-the-system` |
| `design-untouched` | `~/design.md` is as it was | `csa.linux.shell/navigate` |
| `diagram-matches-design` | Every part and flow the design names is there, of the right kind, drawn from the side that starts it | `csa.sec.threat-modeling/draw-the-system` |
| `zones-where-trust-changes` | Two parts share a zone exactly when one organisation runs both on one unfiltered network | `csa.sec.threat-modeling/draw-the-system` |
| `in-pci-scope` | Every process and store the shop runs is marked `cde`, `impacting` or `out` as PCI DSS's rule gives it | `csa.sec.compliance/pci-scope` *(proposed, section 8)* |
| `every-crossing-reviewed` | Every flow that crosses a boundary has all six letters reviewed, and no two threats read the same | `csa.sec.threat-modeling/stride` |
| `design-weaknesses-found` | Everything the design describes as weak has a threat on its flow, rated by the design's scales, and none is marked `none` | `csa.sec.threat-modeling/stride`, `csa.sec.threat-modeling/rank-risks` |
| `ranked-by-risk` | Each risk is likelihood times impact; `top` lists every risk of 6 or more, highest first | `csa.sec.threat-modeling/rank-risks` |
| `answered-a` to `answered-e` | "A risk of 6 or more that the design describes has a control of a kind that answers it" (five checks with the same description, one per high weakness, in an order the page doesn't explain) | `csa.sec.threat-modeling/respond-to-risk` and, in turn: `csa.sec.strong-auth/phishing-resistance`; `csa.sec.crypto/hash-mac-signature`; `csa.sec.vulnerabilities/scan-and-read`; `csa.sec.secrets/keep-secrets-out`; `csa.sec.audit/what-to-log` |
| `nothing-left-open` | Every other threat has a control or an `accept`, and no risk of 6 or more is accepted | `csa.sec.threat-modeling/respond-to-risk` |
| `attack-techniques` | The two threats the task names carry an ATT&CK technique that fits | `csa.sec.threat-modeling/attack-and-abuse` |
| `attack-tree` | A tree for the highest risk: three leaves or more, an AND node, and the cheapest path's cost | `csa.sec.threat-modeling/attack-trees` |

Why five `answered` checks: ADR-0012 wants a failed check to bring back the skill behind it. One check for all five controls would name six skills and bring all of them back for one wrong choice. Five checks with one shared description give nothing away (the page never says which weakness is which) and a learner who answers the key in the repository with `encryption` gets `csa.sec.secrets/keep-secrets-out` back on Today, not the whole module. The prototype's `controls` part is one function; the writer splits it by the reference's weakness (`tm-check controls --only N`).

A failure never names the flow, the letter or the right value ("a control is of a kind that doesn't answer its threat"), as in the topic.

### 3.4 Wrong models (each a `wrong/*.sh` that writes the model; all 25 tried)

`psp-inside`, `one-big-zone` (zones); `logs-as-process`, `hook-backwards` (diagram); `missing-letter`, `boilerplate` (review); `none-where-weak`, `logs-rated-low` (likelihood 1 for the logs), `script-rated-anyone` (likelihood 3 for the script) (findings); `risk-sum`, `top-unordered` (ranking); `tls-for-the-hook`, `encrypt-the-logs`, `password-rules-for-sign-in`, `key-stays-in-repo-encrypted`, `accept-a-high` (controls); `web-out-of-scope` ("it never sees a card number"), `only-backoffice-in-scope` (the shared subnet ignored), `logs-out-of-scope`, `everything-in-scope` (the lazy safe answer), `web-called-cde`, `customer-scoped` (scope); `attack-wrong`, `tree-sum`, `tree-flat`. Plus two not prototyped: `design-edited.sh` (a checksum) and `copied-other-story.sh` (the clinic's model: its element names differ, so `diagram-matches-design` and everything after it fail). At about 3 s a container run: about 90 s of CI.

### 3.5 How a copied answer is defeated, honestly

A threat model is the learner's reading of a design; the checker can't make up a new shop at check time and re-run their thinking. What the design does instead:

1. **The reference is in `checks.yaml`, not in the image**, so nothing in the lab holds the answer. (The page shows a lab's solution only after a pass.)
2. **Three stories whose answers differ in every part**, not in names only. The shop embeds the provider's form (its page is `impacting`), handles card numbers in its back office, and leaks them into logs. The clinic redirects to the provider's hosted page, has a card terminal on the reception's flat office network (so the reception PCs are `cde` by connection), and emails invoices with a guessable link. The bakery posts cards from its own form to its own API (its web tier is `cde`) and keeps card numbers for repeat orders (PCI DSS 3.5.1). The weaknesses, ratings, scope and fitting controls of one fail the others' `diagram`, `scope`, `findings` and `answered` checks.
3. **Once the steps are opened, only a fresh version proves the build** (ADR-0012), and the steps show the shop's model, which fails both versions.
4. **Boilerplate fails:** no two threats may read the same with names masked, `none` is refused where the design says weak, and a control must be of a kind that answers its threat's letter and, for the five high weaknesses, the narrower list the reference gives.

What stays ungraded by machine, and goes to the explain: whether a threat sentence is insightful, and whether a `none` reason is true beyond its length. Open question 3 offers the alternative (a small mechanical piece with inputs made up at check time) and why I don't recommend it.

### 3.6 Support for part 1 (ADR-0012)

- **Solved sibling `example-model-the-print-shop`** (worked example, plain lab, 25 minutes). A print shop that takes payment by a link the provider emails: four elements the shop runs, six flows, three weaknesses. Labelled steps: 1 read the design and list what the shop runs; 2 zones, by owner and network; 3 the scope line for each part, with the rule said aloud for one `cde` by connection and one `impacting`; 4 STRIDE on each crossing flow; 5 rate by the scales; 6 a control that answers the letter, shown failing first with `tls` for a spoofing threat; 7 ATT&CK and the tree. Its checks are part 1's against its own reference.
- **Steps** (fill-in, each the whole shop model but one part): `step-draw-and-scope` (threats, controls and tree given; the learner writes the zones, each element's zone and the six scope lines); `step-find-the-threats` (diagram and scope given; the learner writes the threats and `none` lines with their ratings; the controls already name `t1` to `t6`, and the prompt says so); `step-rank-and-answer` (threats given with likelihood and impact; the learner writes each risk, `top`, the controls, the two techniques and the tree's `cheapest`); `step-the-whole-model` (an empty model with the order of work as comments). Hints on every step.
- **Fresh versions** `build-model-the-checkout-clinic` and `-bakery`, as in 3.5. Each `exercise.yaml` says in a comment what differs from the shop in every part, and `wrong/steps-pasted.sh` (the shop's model with the names changed) proves it. The clinic here is its payment desk, a different system from topic 39's booking service.

## 4. Part 2: `debug-the-staff-sign-in` (identity lab, 60 minutes)

### 4.1 The system (every part is in the prompt, the working ones too)

```
office 10.0.5.2    idp 10.0.5.10         orders 10.0.5.20          api 10.0.5.30              time 10.0.5.40
staff laptop       Keycloak, realm shop  the orders site            the orders API             the shop's time server
(signin)           idp.shop.test:8443    orders.shop.test           orders-api.shop.test       time.shop.test
                                         Apache, mod_auth_openidc   Apache, mod_oauth2         chronyd, serving only
```

One switch, five machines on the identity-lab base. Staff open `https://orders.shop.test/orders/mine`; the site sends them to the identity provider (client `orders-web`: confidential, code flow with PKCE S256), and after sign-in calls the orders API with the access token it was given; the page shows who signed in and their orders. The API answers only a token the provider signed, from the realm's issuer, for `https://orders-api.shop.test` (the API's own name is its audience). Every machine keeps its clock from the shop's time server (`systemctl status timesync@MACHINE` shows which server it asks and what it did; the servers are the `server` lines of the machine's `/etc/chrony/chrony.conf`). The realm is the file `/etc/keycloak/realms/shop.json` on `idp`, applied at start and at `sudo systemctl reload keycloak@idp`. Scenery clients, sealed in spirit and used by the checks: `kiosk` (the shop-floor kiosk, tokens for `https://kiosk-api.shop.test`), `old-admin-reports` (a report job of the old admin site, tokens for `https://admin.shop.test/api`), `stock-sync` (the stock job, tokens for the orders API that last four seconds).

The story the prompt tells: last week the orders pages moved from the old admin site (`https://admin.shop.test/orders`) to a site of their own, and the orders API got its own name.

### 4.2 The three faults (never in the prompt), all tried

| # | Fault | Where it lives, and why it lasts | Evidence (captured) | Skill |
| --- | --- | --- | --- | --- |
| 1 | The provider still sends sign-ins for `orders-web` back to the old address: `redirectUris` is `https://admin.shop.test/orders/oidc/callback` | the realm file, applied at every start | the provider's page: `We are sorry... Invalid parameter: redirect_uri` (HTTP 400, before any sign-in form); its journal: `type="LOGIN_ERROR" ... clientId="orders-web" ... error="invalid_redirect_uri", redirect_uri="https://orders.shop.test/oidc/callback"` | `csa.sec.federation/trace-oidc`, `/choose-flow` |
| 2 | `orders`' clock is 12 minutes slow: its time sync asks `ntp1.dc.shop.test`, a server that no longer exists | `orders`' `/etc/chrony/chrony.conf`; the machine's hardware clock error is scenery, so every boot starts 720 s out until time sync steps it | the browser gets `400 Bad Request` at `/oidc/callback` after a sign-in that worked; `journalctl -u apache2@orders`: `oidc_proto_validate_iat: "iat" validation failure (1795386473): JWT was issued more than 600 seconds in the future`; that line's own timestamp is 12 minutes behind the journal's (`Nov 22 22:27:53 ... [Sun Nov 22 22:15:53 ...]`); `journalctl -u timesync@orders`: `time server ntp1.dc.shop.test: the name doesn't resolve; the clock is not synchronized`; `on orders date -u` against `on idp date -u` | `csa.sec.federation/validate-token` |
| 3 | The site's access tokens are still issued for the old API name: the audience mapper says `https://admin.shop.test/api` | the realm file | the page: `signed in as ana` then `the orders API refused the request: HTTP 401`; `journalctl -u apache2@api`: `AH01631: user ...: authorization failure for "/v1/orders"`; `jwt show` on the token: `"aud": "https://admin.shop.test/api"` beside the API's `Require oauth2_claim aud:https://orders-api.shop.test` | `csa.sec.federation/validate-token` |

**They form a chain**, which is what makes this one broken sign-in and not three: fault 1 stops the sign-in before a token exists; with it fixed, fault 2 refuses the ID token; with that fixed, the person is signed in and fault 3 shows. Each fix changes the error and the machine it comes from (the provider, then the site, then the API), which is the trace the federation topic taught.

**No overlap with topic 44's debug** (a stale client secret, a pinned signing key, a disabled grant: its open question 6 says the same from its side).

### 4.3 The prompt (substance; house rule 5)

The system as in 4.1. **Symptom:** "Since the move, no member of staff can sign in to the orders site: the sign-in ends on an error page. Ana's test account is in `/etc/idlab/accounts`; `on office signin https://orders.shop.test/orders/mine --user ana` is her browser." **Three faults.** "Fixing one changes what you see: sign in again after each fix." **The rules of the fix:**

- The provider sends a sign-in for the orders site back to the site's own callback and nowhere else.
- The orders site stays a confidential client with PKCE, and gets no other grant.
- The orders API keeps checking every token's signature, issuer, audience and expiry, and answers only tokens issued for it. The site's tokens name the API and nothing else.
- Tokens keep their lifetimes, and nothing accepts a token further from its own clock than it does now.
- Every machine's clock is kept right by the shop's time server.
- The time server, the network and the other clients are not yours to change.
- Every fix lasts a restart: a change at the provider is in its realm file.
- Time yourself: 60 minutes.

### 4.4 Checks (end states; the page lists them after a first try). All tried (`sso/checks.sh`)

| id | End state | How | `test_skills` |
| --- | --- | --- | --- |
| `staff-sign-in` | Ana ends up signed in to the orders site and sees her orders | the base's `signin` from `office`, a real sign-in end to end | `csa.sec.federation/trace-oidc` |
| `redirect-only-to-the-site` | The provider sends a sign-in for the orders site back to its callback, and refuses every other address | authorization requests with the right address (200, the form) and seven wrong ones, each 400: three made from a number chosen at check time (a sibling path, a longer path, another host), a look-alike host, plain `http`, the old address, another host under `shop.test` | `csa.sec.federation/choose-flow` |
| `client-kept-strict` | The orders site is registered as strictly as it was | admin API: confidential, PKCE S256, no implicit or password grant | `csa.sec.federation/choose-flow` |
| `api-serves-staff` | The orders API answers the token Ana's sign-in gives the site, and that token names the API alone | the check runs the code flow itself (`oidc_login`), calls the API, reads `aud` | `csa.sec.federation/validate-token` |
| `api-refuses-other-audiences` | The API refuses a token issued for something else | real tokens from `kiosk` and `old-admin-reports`, each 401 | `csa.sec.federation/validate-token` |
| `api-refuses-bad-tokens` | The API refuses a token the provider didn't sign, and one that has expired | `stock-sync`'s fresh token: 200; the same re-signed by a key made now (`forge-token`): 401; a second `stock-sync` token shown only after its four seconds: 401 | `csa.sec.federation/validate-token` |
| `clocks-right` | Every machine's clock is within two seconds of the right time, kept there by the shop's time server | `clock_offset` on three machines; `timesync@orders` and `@idp` enabled, active, and their last journal line names `time.shop.test` | `csa.sec.federation/validate-token` |
| `no-extra-leeway` | Nothing accepts tokens further from its clock, or for longer, than before | no `OIDCIDTokenIatSlack` above 600 in `orders`' Apache files; the realm's access-token lifespan is 300 | `csa.sec.federation/validate-token` |
| `realm-saved` | The provider's running realm is what its file says | the base's `kc_saved idp` | `csa.sec.federation/choose-flow` |
| `at-boot` | Everything the sign-in needs starts at boot | six units enabled | `csa.linux.services/systemctl` |
| `scenery-untouched` | The time server, the network and `orders`' hardware clock are as they were | `netlab intact` | `csa.net.troubleshooting/prove-and-record` |

Eleven checks, about 10 s a run in all (7 s of it the wait for a token to expire), so the limits add to 330 s. Before any work, 7 of 11 pass and 4 fail (`staff-sign-in`, `redirect-only-to-the-site`, `api-serves-staff`, `clocks-right`).

The writer's change from the prototype: `api-serves-staff` and `staff-sign-in` should say "the check couldn't finish a sign-in" and stop when the sign-in itself fails, so a redirect fault doesn't also bring back `validate-token`.

### 4.5 Wrong fixes (13, all tried; each failed the check aimed at it)

| Wrong fix | The shortcut | Fails |
| --- | --- | --- |
| `redirect-wildcard` | `https://orders.shop.test/*` | `redirect-only-to-the-site` |
| `redirect-star` | `*` | `redirect-only-to-the-site` |
| `redirect-old-kept` | the new address added, the old one left | `redirect-only-to-the-site` |
| `api-any-audience` | the API's audience rule deleted | `api-refuses-other-audiences`, `api-serves-staff` |
| `api-old-audience` | the API told to accept the old name | `api-refuses-other-audiences`, `api-refuses-bad-tokens`, `api-serves-staff` |
| `api-no-expiry` | `verify.exp=skip` on the API | `api-refuses-bad-tokens` |
| `slack-raised` | `OIDCIDTokenIatSlack 3600` on the site, the clock left wrong | `no-extra-leeway`, `clocks-right` |
| `clock-by-hand` | the machine's clock offset written by hand, time sync left asking a dead server | `clocks-right` (and after a reboot the clock is 12 minutes out again) |
| `live-only` | both provider fixes made through the admin API, not the file | `realm-saved` |
| `long-tokens` | access tokens made to last an hour | `no-extra-leeway` |
| `no-redirect-fix`, `no-audience-fix`, `no-clock-fix` | two of three | the fault's own checks |

To add when written, not tried: `public-client.sh` (`client-kept-strict`) and `time-server-edited.sh` (`scenery-untouched`). For CI, `redirect-star` can go (the wildcard script covers the rule).

### 4.6 What was measured (section 11 has the findings)

The lab image: the base prototype's 1.34 GB as Docker Desktop reports it, plus kilobytes. Boot to "running" with the provider answering and the realm applied: 10 to 15 s over 16 boots. Memory: 720 to 800 MiB per lab. A realm reload after an edit: 1.7 s. The contract: pristine, solution, restart trial and 13 wrong fixes, 584 s.

## 5. Part 3: `build-answer-the-leak` (systemd lab on `lab-base-sec`, 60 minutes, in `prove.more`)

*Designed on parts the topic designers tried; not prototyped by me* (open question 2): gitleaks 8.16 over a repository's history and as a server-side hook (secrets brief, fact S1 and its write lab); `openssl ca` revocation, a CRL and clients that check it (PKI brief); a hash-chained trail and its verifier (audit brief).

### 5.1 The story and the machine

One server, the shop's payments server (`pay1` in the prompts, the story of `lab-base-sec`). Yesterday a contractor pushed the payment service's repository to a public mirror; it was public from 09:10 to 15:25 UTC. `/srv/incident/sheet.txt` gives those times, the shop's own address range, and the rules below. On the machine:

- `/srv/git/paygate.git`, the service's repository (about 40 commits, made by the seed), and a clone in `~/paygate`. Its history holds three secrets: the provider API key in `config/prod.env` (still there), the TLS private key of `pay.shop.test` (added and "removed" two commits later), and a database password in an old commit of a script.
- `paygate.service` (scenery, user `paygate`): serves `https://pay.shop.test:8443` with a certificate from the shop's issuing CA, and calls the provider with the key it reads from `/etc/paygate/prod.env` (mode 0644).
- `psp.service` (scenery): the provider's stand-in. `psp-console keys list|create|revoke` stands for its dashboard: two keys may be active at once.
- `/srv/ca`: the shop's issuing CA as topic 43 laid it out (`openssl ca`, its database, serial and CRL number), and where its CRL is published. `till-check` (scenery) is what the tills run before each sale: fetch the CRL, then connect, refusing a revoked certificate.
- `/var/log/paygate/audit.log`: the provider calls the service made, one hash-chained line each (time, key id, source address, action, amount, outcome), in topic 46's format, with its verifier.

### 5.2 What the learner does (the sheet's required end state)

1. **Find what leaked.** `~/incident/leaked.tsv`: one line for each secret anywhere in the repository's history (`commit path kind`), found with the scanner over the history, not the working tree.
2. **Rotate the key, service up throughout.** A new key at the provider, the service using it from a file only its own user can read (or a systemd credential), the leaked key revoked at the provider, nothing secret in a unit's `Environment=` or in the repository's current files.
3. **Stop the next one at the push.** A pre-receive hook on the repository that refuses a push holding a secret and takes a clean one.
4. **Revoke and replace the certificate.** The leaked certificate revoked for key compromise, a fresh CRL published, a new key pair (never the old key re-signed), a new certificate from the CA served with its chain, the key file private.
5. **Say what the leaked key did.** `~/incident/exposure.txt`: how many calls were made with the leaked key from outside the shop's addresses while the mirror was public, their refunds' total, and the first one's time, from a trail whose chain verifies.

### 5.3 Checks

| id | End state | How | `test_skills` |
| --- | --- | --- | --- |
| `leaks-listed` | The list holds every secret in the history and nothing else | compared with what the seed planted; a secret only in an old commit must be there | `csa.sec.secrets/scan-for-leaks` |
| `service-pays` | The payment service takes a test payment | the check posts one through `paygate` | `csa.sec.secrets/rotate-and-revoke` |
| `leaked-key-dead` | The provider refuses the leaked key | the check calls the stand-in with it: 401 | `csa.sec.secrets/rotate-and-revoke` |
| `key-kept-private` | The live key is in no file others can read, no unit's environment, and no current file of the repository | modes, `systemctl show`, a scan of `HEAD` | `csa.sec.secrets/keep-secrets-out` |
| `push-guard` | The repository refuses a push with a secret and accepts a clean one | the check pushes two commits to a scratch branch, one holding a provider-format key **made up at check time**, and removes the branch | `csa.sec.secrets/scan-for-leaks` |
| `old-cert-revoked` | The CA's published CRL verifies, is fresh, and lists the leaked certificate, for key compromise | `openssl crl`, the serial, the reason | `csa.sec.pki/revocation` |
| `tills-refuse-the-old` | A till refuses a server that presents the leaked certificate and key | the check starts a throwaway server on 127.0.0.1 with the leaked pair (from the history) and runs `till-check` against it | `csa.sec.pki/revocation` |
| `new-cert-served` | The service presents a certificate from the CA for `pay.shop.test`, with its chain, on a key that isn't the leaked one, and `till-check` passes | `openssl s_client`, public keys compared | `csa.sec.pki/run-a-ca`, `csa.sec.pki/fix-chains` |
| `key-file-private` | The new private key is readable only by the service's user | mode and owner | `csa.linux.permissions/chmod-chown` |
| `trail-intact` | The audit trail's chain verifies and its earlier lines are as they were | the verifier; a checksum of the seeded part | `csa.sec.audit/hash-chains` |
| `exposure-right` | The three figures are what the trail gives for the leaked key, outside addresses and the window | computed by the check from the trail | `csa.sec.audit/what-to-log` |
| `lasting` | The service and the hook are in place after a restart | units enabled; the restart trial does the rest | `csa.linux.services/systemctl` |

### 5.4 Wrong fixes

`worktree-scan-only.sh` (the history-only secrets missed), `old-key-left-active.sh`, `revoked-before-switch.sh` (the service left on the dead key: `service-pays`), `key-world-readable.sh`, `key-in-unit-environment.sh`, `history-rewritten-only.sh` (the commit removed with a forced push and nothing rotated: `leaked-key-dead`), `hook-scans-head-only.sh` (a secret in an earlier commit of the same push gets through), `not-revoked.sh`, `crl-not-republished.sh`, `same-key-resigned.sh`, `leaf-only.sh` (no chain), `counts-inside-too.sh`, `counts-outside-window.sh`. Thirteen, one for each rule the sheet states.

### 5.5 Fresh version `build-answer-the-leak-clinic`

The clinic's lab-results service: what leaked is an API token and the private key of a **client** certificate (its mutual-TLS identity to the laboratory), so the party that must refuse the old certificate is a server checking a CRL, not a till; other secrets, another window, other figures. The same checks with the story's particulars; its `exercise.yaml` says what differs.

## 6. Why a third part, and the spec text

**Coverage without part 3.** Part 1 retrieves threat modeling in full and, as judgement, one idea each from strong authentication, cryptography, secrets, audit, vulnerabilities and compliance. Part 2 retrieves federation by hand. Nothing in either makes the learner rotate a secret, revoke a certificate, or read an audit trail for who did what, though those are what an architect is asked for on the worst day of the year, and they are skills of three topics (45, 43, 46) that otherwise end the module unretrieved. **Under the owner's rule:** best learning (one incident worked end to end, where the order of steps matters: rotate before revoking, revoke before reissuing means nothing if clients don't check); best retention (a build weeks after the topics, the retrieval a checkpoint exists for); free (local). Cost: an hour for the learner and about 8 minutes of CI. What stays out of every part and is covered by the explain: authorization policy (topic 40's Cedar), conditional access and break glass (41), envelope encryption (42), zero trust's proxy and segmentation (47), the patch loop (48). A fourth part would make a five-hour checkpoint.

**Replacement text for the spec** (`docs/specs/cloud-solutions-architect.md`, the Checkpoint 4 block), then `python -m uv run python tools/outline_cloud_track.py`:

```markdown
**Checkpoint 4: the threat model, the broken sign-in and the leak** (`csa.m4.checkpoint`).

1. Threat-model a web app that takes payments: its trust boundaries, its PCI DSS scope, its top risks and a control for each.
2. Fix a single sign-on, run locally with an open-source identity provider, that fails in three ways.
3. Answer a leak: find the secrets in a repository's history, rotate the key, revoke and replace the certificate, and read the audit trail for what the leaked key did.
```

## 7. The explain (20 minutes, opens once part 1 passes)

**Prompt** (it names no fault of part 2 and no step of part 3): "A colleague's plan for the shop's new back office: one shared admin account with a long password; 'encrypt everything' with one key kept in the app's settings; ten-year certificates so nothing ever expires; API keys in the repository, 'because it's private'; logs kept on the server for a month; patch whatever scores 9 or more, and the rest when there's time; a VPN, so that everything inside can be trusted; and 'we passed the audit, so we're secure'. In your own words, say what goes wrong with each and what you would do instead. Then give two ways the three clouds differ that would change how you build it."

**Rubric:**

| id | Required | Description |
| --- | --- | --- |
| `identity` | yes | One shared account means nobody can be held to an action and one phish gives everything. People sign in as themselves, with the least permission the job needs and duties split (who requests is not who approves); administrators use phishing-resistant MFA (a security key or passkey), with a break-glass account kept apart, alerted on and tested. |
| `keys` | yes | One key beside the data protects nothing: whoever reads the settings reads everything. Envelope encryption: a data key for each item or set, wrapped by a key that stays in a key-management service, which decides and records who may unwrap; keys rotate. |
| `certificates` | yes | A ten-year certificate is a ten-year exposure if its key leaks, and revocation only works where clients check it. Short lifetimes issued and renewed automatically, a CA whose root stays offline, and revocation published and checked. |
| `secrets` | yes | A private repository is read by many people and machines, and history keeps what was removed. Secrets stay out of code, images and logs, in a store that hands them to the workload by its identity; they are rotated, and scanners stop them at the push. Short-lived, issued-on-demand credentials are better still. |
| `logs` | yes | Logs on the server are lost with it and can be edited by whoever breaks in. Decide what to record (who, what, when, from where, the outcome; never secrets or card data), send it off the machine, make it tamper-evident (a hash chain, sealing, write-once storage), and keep it as long as the rules say (PCI DSS: 12 months, three of them at hand). |
| `patching` | yes | A severity score says how bad, not how likely. Rank by what is being exploited (CISA's KEV list), how likely exploitation is (EPSS) and what the system holds and faces; give each rank a deadline, and track what's overdue. |
| `zero-trust` | yes | A VPN trusts a place: one stolen laptop is inside. Decide each request by who is asking, from which device, for which app, as close to the app as possible, and keep services apart from each other. |
| `compliance` | yes | An audit samples evidence against a framework's controls for a scope, at a point in time. It is a floor and a way to prove what you do; the threats that matter to this system come from modelling it. |
| `clouds` | yes | Two real differences, from the topics' own tables. For example: how permissions combine (AWS identity and resource policies with explicit deny and organisation-wide guardrails; Azure role assignments at a scope; Google Cloud allow policies inherited down the hierarchy); what each cloud's audit trail records with no setup; each cloud's key-management or secrets service. |
| `sign-in` | no | Single sign-on: tokens issued for one audience, sent back only to registered addresses, short-lived, on machines whose clocks agree. (Not required, and worded generally, because part 2 is open while the explain is.) |

**Model answer:** the writer drafts about 450 words in the module's own words. Every figure in it comes from a topic's verified facts (the PCI DSS retention figure is fact P6).

## 8. What this checkpoint assumes, and where the designs don't yet fit

### 8.1 Skills assumed of each topic (ids as in the briefs of 2026-11-12)

| Topic | Skill ids used here | What the checkpoint needs from it |
| --- | --- | --- |
| `csa.sec.threat-modeling` | all six | the line format and `tm-check`; zones by owner; STRIDE on crossing flows; the 1-to-3 scales; controls by letter; ATT&CK by ID; trees |
| `csa.sec.compliance` | `pci-scope` **(does not exist yet)** | PCI DSS scope: what card data is, the CDE, connection and impact, segmentation, what handing the card form to a provider changes |
| `csa.sec.strong-auth` | `phishing-resistance` | that a password alone, and a longer password, don't answer a spoofed sign-in; a security key does |
| `csa.sec.crypto` | `hash-mac-signature` | that a signature or MAC, not TLS, proves who sent a webhook |
| `csa.sec.vulnerabilities` | `scan-and-read` | third-party code as part of what you run. **Weak fit:** no skill in its table covers a script loaded from someone else's server |
| `csa.sec.secrets` | `keep-secrets-out`, `scan-for-leaks`, `rotate-and-revoke` | where secrets belong; gitleaks over history and as a pre-receive hook; rotation with two active keys |
| `csa.sec.audit` | `what-to-log`, `hash-chains` | what never to log; reading a trail for who did what in a window; a chain that verifies |
| `csa.sec.pki` | `run-a-ca`, `revocation`, `fix-chains` | `openssl ca`: issue from a new CSR, revoke with a reason, publish a CRL, a client that checks it, a complete chain |
| `csa.sec.federation` | `trace-oidc`, `choose-flow`, `validate-token` | the code flow hop by hop and where each error arrives; exact redirect URIs; `aud`, `exp`, `iat` and leeway; `jwt show`; the realm file and `kcadm.sh` for looking |
| `csa.sec.authn-authz`, `csa.sec.zero-trust` | none in a check | the explain's `identity` and `zero-trust` items |
| Modules 1 and 3 | `csa.linux.services/systemctl`, `csa.linux.permissions/chmod-chown`, `csa.linux.shell/navigate`, `csa.net.troubleshooting/prove-and-record` | exist on main |

### 8.2 Places I could not make fit (for the critic)

1. **PCI DSS scope is one sentence in topic 49's brief** ("the cardholder data environment in one sentence"), and part 1 checks it. The spec's part 1 is a payments app, so scope is fair to ask, but only if taught. **Needed in topic 49:** a sixth skill, `pci-scope` (the house rule allows six), or the same under `framework-landscape`: a lesson section of about 300 words from PCI DSS section 4 (facts P1 to P3), a worked scoping of a small shop, and at least three come-back questions (which of these five systems is in scope; what moving the card form to the provider's frame changes; what one flat network does). Without it, part 1's prompt would be teaching, which a proof must not.
2. **No topic teaches time sync.** Module 2 teaches Kerberos's five-minute rule and "fix the time source" (`csa.hw.windows-ad/kerberos-tickets`), and topic 44 teaches leeway as arithmetic, but nothing shows a machine's clock, its time sync's status or a `server` line. **Needed in topic 44:** two paragraphs (a token's times are read against the reader's clock; where a machine's time comes from, and how to see that it's wrong), one step in its worked example (`on app date -u`, `systemctl status timesync@app`), and two come-back questions under `validate-token`. The base's first lab should also say that a machine's clock here is a stand-in (below).
3. **`tm-check` needs three more control kinds** (`secret-store`, `separation-of-duties`, `patch`), the `scope` line and part, a reference that can narrow a weakness's allowed controls, and `controls --only N`. All are additions; topic 39's labs are unaffected. Topic 39's brief already recommends the `scope` extension (its open question 1).
4. **The provider's address.** The base prototype's Keycloak answers at `https://idp.shop.test:8443`; the federation brief writes `https://idp.shop.test`. Part 2 follows the base. Whoever settles the base settles this for every identity lab.
5. **mod_oauth2 isn't in the base prototype's image** (it has mod_auth_openidc and mod_auth_mellon). Part 2 installed `libapache2-mod-oauth2` 3.3.1 in a `RUN` of its own. The federation brief asks the base for it (its F1); so does this.
6. **Machine names.** The federation brief's machines are `office`, `idp`, `app`, `api`; part 2's are `office`, `idp`, `orders`, `api`, `time`. Deliberate: a checkpoint's debug is unfamiliar work.
7. **`lab-base-sec` and part 3.** Part 3 assumes that base has git, gitleaks 8.16 and openssl (the secrets brief says its labs find git and gitleaks there). Its scenery servers are Python, so nginx isn't needed.
8. **Strong authentication, conditional access, Cedar and zero trust are in no part's hands-on work.** Named in section 6; the explain carries them.

### 8.3 What part 2 assumes the identity-lab base provides

Everything below was used from the base designer's prototype image and worked, except where a finding in section 11 says otherwise:

- Keycloak 26.8.2 as `keycloak@M`, with realms from `/etc/keycloak/realms/*.json` (secrets as `${NAME}` from `secrets.env`), applied at start and at reload; the unit "starting" until the realm answers; `kc_saved`.
- Apache as `apache2@M` with mod_auth_openidc, its secrets from the machine's `secrets.env`, logging to the journal.
- `lab-ca issue`, `lab-secret` (and `--account`), test accounts in `/etc/idlab/accounts`.
- **Machines' own clocks:** `lab-clock set M SECONDS` at build (a hardware clock error, scenery), libfaketime loaded into everything a machine runs, `timesync@M` reading the machine's `chrony.conf` and stepping its clock, `chrony@M` as a time server that never sets a clock, `clock_offset`, and a `date` that refuses `-s` on the lab machine. Part 2's clock fault is built wholly from these.
- `signin` (the terminal browser), `oidc_login`, `jwt show`, `forge-token`, `kc`, `secret`.

## 9. Time

Part 1: 75 (the design is about 600 words, read twice; a 64-line model; topic 39's build is 70 for six flows and no scope). Part 2: 60 (three faults in a chain across three machines; topic 44's debug is 45). Part 3: 60. Explain: 20. Work: 215 minutes; with starting three labs (part 2's is up in 10 to 15 s) and running checks more than once (part 2's take about 10 s): **`estimated_minutes: 240`**, the same as Checkpoint 3.

## 10. CI cost

| Lab | Kind | Container runs | Estimate |
| --- | --- | --- | --- |
| `build-model-the-checkout`, 2 versions, example, 4 steps | plain | 8 labs; up to 29 runs for the build | 10 min (topic 39 measured 72 s for a build with 16 wrong models) |
| `debug-the-staff-sign-in` | identity | 15 (or 14 without `redirect-star`) | **measured 584 s** alone on the owner's PC; allow 12 min with four labs at once |
| `build-answer-the-leak` and `-clinic` | systemd, one machine | 2 x 15 | 8 min (estimated at 15 s a run) |
| **Checkpoint** | | | **about 30 minutes** |

Over the 20-minute aim, under Checkpoint 3's 35. The identity lab is the heavy one: an image Docker Desktop reports as 1.34 GB and 720 to 800 MiB of memory per running lab, so four at once on a runner is about 3 GB.

## 11. Prototype findings (2026-11-22, Docker Desktop 29.8.2)

1. **Part 2 runs on the base prototype as designed.** A lab of five machines built `FROM lab-base-idproto` in about 9 s, booted in 10 to 15 s, and the realm file was applied in 1.8 s at first start and 1.7 s at a reload.
2. **`kc_saved` reports a difference after the first sign-in** when the realm file has a group-membership mapper without `"multivalued": "true"`: Keycloak adds that setting itself the first time the mapper is used (`clients.orders-web.protocolMappers.groups.config.multivalued: now "true"; from its file null`). The solution failed `realm-saved` until the file said it. **For the base:** either its comparison ignores settings Keycloak fills in, or its README tells every lab to write this one. Every identity lab with a `groups` claim meets it.
3. **mod_oauth2 remembers a token it has accepted.** A four-second token shown to the API, then shown again after seven seconds, was answered 200; a second token never shown before its expiry was refused (`_oauth2_jose_jwt_validate_exp: "exp" validation failure (...): JWT expired 3 seconds ago`). So the expiry check uses a token the API hasn't seen. Topic 44's `api-refuses-bad-tokens` ("expired: 401") needs the same care, and its lesson may want the fact: a resource server that caches validation results can honour a token a little past its expiry.
4. **The clock fault shows three ways at once**, which is what makes it findable: the site's log says the ID token was issued "more than 600 seconds in the future" (mod_auth_openidc 2.4.15.1's default slack), the site's own log timestamps trail the journal's by 12 minutes, and `timesync@orders` says in plain words that its server's name doesn't resolve. Fixing `chrony.conf` and restarting `timesync@orders` stepped the clock (`clock stepped by +720.0 s`); Apache needed no restart (libfaketime rereads the offset within about ten seconds, which the solution waits out).
5. **A clock set by hand is caught without a reboot.** Writing the offset file directly makes sign-in work; `clocks-right` fails it because the time sync's last journal line still says it isn't synchronized.
6. **A slow clock, not a fast one, is the right fault for the site.** A site 12 minutes slow sees every ID token as issued in the future, past the 600-second slack. (Only the slow clock was tried.) Certificates aren't a second symptom: the base's CA dates them a day back.
7. **`verify.exp=skip` is a real mod_oauth2 option** and the wrong fix that uses it loads cleanly and is caught only by behaviour (`api-refuses-bad-tokens`), which is why that check holds a real expired token and doesn't read the configuration.
8. **The restart trial passed:** after `docker restart`, boot in 14 s and all eleven checks again (the realm from its file, the clock stepped again by the time sync from its 720-second hardware error).
9. **Part 1's checker:** the reference passes all ten parts; a blank model fails six; each of 25 wrong models fails exactly one part, the one aimed at it (`python tm/wrongs.py`).
10. **An earlier prototype of part 2** (image `cp4-sso:proto`, built 2026-11-12 from the plain network base with its own copies of the clock tools) was on this machine with the same story and faults; it booted in under 20 s at 739 MiB. The image was removed, with its base copy `cp4-base-net`.

**Part 2's contract** (`contract-sso-1.log`): pristine fails 4 of 11; the solution passes 11 and passes 11 after a restart; 13 wrong fixes each fail 1 to 3 checks, always including the one for their own shortcut; 15 container runs, 584 s.

## 12. Platform work needed first

| # | What | Smallest version | Blocks |
| --- | --- | --- | --- |
| K1 | The identity-lab base, with machines' clocks, `timesync@`, `chrony@`, `signin`, `kc_saved`, `forge-token`, and mod_oauth2 | the base designer's prototype plus one package | part 2 |
| K2 | `tm-check` in a shared place, with `scope`, three control kinds, narrowed controls and `--only` | topic 39's proposed `content/lab-bases/tm/`, and a test in `tools/tests/` that runs the reference and the wrong models (`wrongs.py` is that test) | part 1 and its seven sibling labs |
| K3 | `lab-base-sec` with git, gitleaks and openssl | as the audit designer proposed | part 3 |
| K4 | The map's note on a checkpoint in progress lists further parts | ADR-0012's amendment says it should before a checkpoint with parts is `ready`; check whether Checkpoint 2's or 3's work did it | the checkpoint going `ready` |
| K5 | Five checks with one description | nothing in the validator forbids it today as far as I read; the writer confirms with `validate_content.py`, and if it does, the descriptions get "(1 of 5)" to "(5 of 5)" | part 1's `answered-*` |

No new item types, no migration, no app work.

**Docker Desktop against GitHub's runners** (house rule 4):

| Need | Part | Docker Desktop | GitHub's runners |
| --- | --- | --- | --- |
| Namespaces, veth, a bridge | 2 | works | works for Module 3 |
| Java 21 and Keycloak inside a network namespace | 2 | works | **not tried**; no kernel feature beyond the network base's |
| libfaketime through a machine's own `/etc/ld.so.preload` (C programs, Python, the JVM) | 2 | works for Apache and Python; Keycloak's machine had no offset | **not tried**; plain user-space, so no difference is expected, but one identity lab should run there before any is written |
| Real time of day agreeing between the lab and the runner's clock | 2 | works | expected; the checks compare machines with the lab machine's own clock, never with an outside one |
| Plain Python 3 | 1 | works (CPython 3.12 on Windows for the prototype; no third-party module) | works |

## 13. Cost

**Money: none.** Every part is local. No real-cloud version is proposed: Module 10 builds single sign-on on the three clouds, and a tenant-level mistake in a real identity provider is not a checkpoint's risk to take.

**Licences** (all free for this use): Keycloak 26.8.2, Apache-2.0, pinned by the base with a checksum; mod_auth_openidc 2.4.15.1, Apache-2.0; mod_oauth2 3.3.1, AGPL-3.0+ (Ubuntu's copyright file; run unmodified); libfaketime 0.9.10, GPL-2; chrony 4.5, GPL-2; Apache 2.4.58, Apache-2.0; OpenJDK 21, GPL-2 with the Classpath exception; gitleaks 8.16, MIT (the secrets brief's fact). All but Keycloak are Ubuntu 24.04's packages.

**Secrets:** none in the repository. Part 2's client secrets, Ana's password and every key are made at build by the base's tools. Part 3's "leaked" secrets are made by its seed and are valid nowhere.

## 14. Open questions, each with a recommendation under the owner's rule

1. **The spec and the outline name part 2's three faults** ("the wrong audience, the wrong redirect, and clock skew"), and the generated objectives repeat them, which house rule 5 forbids for a debug. *Recommendation:* the objectives and the page never name them (section 2), and the spec's line becomes "fails in three ways" (section 6). The plan keeps the detail. Best learning: finding them is the exercise.
2. **Part 3 isn't prototyped.** *Recommendation:* prototype before writing, in this order of risk: the till's refusal of a revoked certificate served by a throwaway server; the pre-receive hook refusing a made-up key (gitleaks' rules must match the provider-format key the seed and the check use, so define that format with a custom rule in the server's own configuration, as the secrets brief found necessary); the rotation with two active keys. If any proves too long for 60 minutes, drop step 5 (the exposure figures) before anything else.
3. **Should part 1 have a piece whose inputs are made up at check time?** The alternative: the learner also writes a small script (as topic 39's write lab does) that the check runs on invented models. *Recommendation:* no. It would prove awk, not the model, and add 20 minutes; section 3.5's four defences are what a judgement task can honestly have. If the critic wants a check-time element, the cheapest honest one is for `labcheck start` to pick one of the three stories for a learner's first attempt, which is platform work and not proposed here.
4. **Six weaknesses or fewer in part 1?** Five highs and a medium make a 64-line model. *Recommendation:* keep six, one per topic, and if the writer's own timed run passes 75 minutes, drop the `f6` R medium first (the audit topic is also in `f9`).
5. **Part 2's clock fault depends on a stand-in** (a machine's clock is libfaketime's offset; time sync is a small program reading `chrony.conf`). *Recommendation:* accept it, and say so once in the base's first lesson and in this lab's prompt in a sentence: every container shares one real clock, and a lab must never set it. What the learner sees and does is what they would on real machines.
6. **`estimated_minutes: 240` with three parts.** *Recommendation:* keep it; parts count whenever they pass, so the checkpoint spreads over sittings.
7. **Should `api-serves-staff` insist the token names the API alone?** A learner who adds the new audience and leaves the old one has a working sign-in whose tokens also work at the old admin API. *Recommendation:* insist (it is in the prompt's rules, and it is the least-privilege point of an audience).

## 15. Unverified

- **Part 3 as a whole** (section 5): designed, not run. Whether `lab-base-sec` as finally built has what it needs.
- **Parts 1's sibling labs:** the solved example, the four steps and the two fresh versions are designed, not prototyped; their designs and references are the writer's to make from 3.5 and 3.6. `copied-other-story.sh` and `steps-pasted.sh` were not run.
- **Nothing ran on a GitHub runner**, and nothing ran four identity labs at once (the federation brief measured that: 32 to 33 s boots).
- **`tm-check` here is my re-implementation** from topic 39's brief; that designer's own prototype was not on disk. The two may differ in details (for example, which control kinds answer T).
- **SAQ types** (A, A-EP, D) are not used in any check. The 2025 change to SAQ A was read (facts P7, P8); SAQ A-EP's and D's eligibility text was not, so the lesson material topic 49 adds should read them from PCI SSC before stating them.
- **PCI DSS v4.0.1's text was read from a copy** of the standard hosted by a college (fact P1's source), because PCI SSC's own library refused an automated fetch (HTTP 403). The copy's title page, date, page footers and metadata are PCI SSC's. The writer opens the official library in a browser before quoting.
- **ATT&CK:** T1110.004 and T1552.001 were opened (v20.1). T1078 and T1195 were not.
- **Whether the validator accepts five checks with one description** (K5).
- The explain's `clouds` examples are from memory of the topics' briefs, not re-read at the clouds' own pages; the writer takes them from the topics' verified facts.

## Appendix: facts read for this checkpoint (2026-11-22)

| # | Claim | Source |
| --- | --- | --- |
| P1 | PCI DSS v4.0.1, June 2024. Section 4: requirements apply to "The cardholder data environment (CDE), which is comprised of: System components, people, and processes that store, process, or transmit cardholder data and/or sensitive authentication data, and, System components that may not store, process, or transmit CHD/SAD but have unrestricted connectivity to system components that store, process, or transmit CHD/SAD", and to "System components, people, and processes that could impact the security of cardholder data and/or sensitive authentication data"; its examples of the last include "name resolution, or e-commerce (web) redirection servers" | https://www.middlebury.edu/sites/default/files/2025-01/PCI-DSS-v4_0_1.pdf (a copy; official: https://www.pcisecuritystandards.org/document_library/ ); the CDE definition also at https://www.pcisecuritystandards.org/glossary/ |
| P2 | "To be considered out of scope for PCI DSS, a system component must be properly segmented (isolated) from the CDE, such that the out-of-scope system component could not impact the security of cardholder data and/or sensitive authentication data, even if that component was compromised." | as P1 |
| P3 | Account data: cardholder data (PAN, cardholder name, expiration date, service code) and sensitive authentication data (full track data, card verification code, PINs/PIN blocks). "Use of a PCI DSS compliant TPSP does not make a customer PCI DSS compliant, nor does it remove the customer's responsibility for its own PCI DSS compliance." | as P1 |
| P4 | 3.3.1 "SAD is not stored after authorization, even if encrypted"; 3.3.1.2 the card verification code is not stored after authorization; 3.4.1 PAN masked when displayed, "the BIN and last four digits are the maximum"; 3.5.1 PAN "rendered unreadable anywhere it is stored" | as P1 |
| P5 | 6.4.3 payment page scripts: each authorized, its integrity assured, an inventory with justification; 11.6.1 a change- and tamper-detection mechanism for payment pages' headers and scripts, at least weekly or by a targeted risk analysis; 8.4.2 "MFA is implemented for all non-console access into the CDE"; 8.6.2 passwords for application and system accounts "not hard coded in scripts, configuration/property files, or bespoke and custom source code"; 12.5.2 scope documented and confirmed at least every 12 months | as P1 |
| P6 | 10.5.1 "Retain audit log history for at least 12 months, with at least the most recent three months immediately available for analysis"; 10.2.1.2 logs capture "all actions taken by any individual with administrative access" | as P1 |
| P7 | SAQ A, January 2025: requirements 6.4.3 and 11.6.1 (and 12.3.1 for it) removed from SAQ A; a new eligibility criterion, that the merchant has confirmed its site "is not susceptible to attacks from scripts that could affect the merchant's e-commerce system(s)"; effective 31 March 2025 | https://blog.pcisecuritystandards.org/important-updates-announced-for-merchants-validating-to-self-assessment-questionnaire-a |
| P8 | FAQ 1588 (February 2025): that criterion applies to merchants whose page embeds a provider's payment form (an iframe), not to those that redirect; it is met by techniques such as 6.4.3 and 11.6.1's, or by the provider's confirmation that its embedded solution protects against script attacks | https://www.pcisecuritystandards.org/faqs/1588/ |
| P9 | PCI SSC glossary: a payment page may be "A document or component displayed in an inline frame within a non-payment page"; payment page scripts are commands "processed and/or interpreted by a consumer's browser" | https://www.pcisecuritystandards.org/glossary/ |
| O1 | RFC 9700 (BCP 240, January 2025): authorization servers "MUST utilize exact string matching except for port numbers in localhost redirection URIs of native apps"; "access tokens SHOULD be audience-restricted to a specific resource server" | https://www.rfc-editor.org/rfc/rfc9700.html |
| O2 | RFC 7519: "Each principal intended to process the JWT MUST identify itself with a value in the audience claim", else the JWT must be rejected; for `exp` and `nbf`, "Implementers MAY provide for some small leeway, usually no more than a few minutes, to account for clock skew"; `iat` "can be used to determine the age of the JWT" | https://www.rfc-editor.org/rfc/rfc7519.html |
| O3 | OpenID Connect Core 3.1.3.7: "The ID Token MUST be rejected if the ID Token does not list the Client as a valid audience"; "The current time MUST be before the time represented by the exp Claim"; "The iat Claim can be used to reject tokens that were issued too far away from the current time" | https://openid.net/specs/openid-connect-core-1_0.html |
| K1 | Keycloak 26.8.2, Server Administration Guide, Valid Redirect URIs: "Exact (case sensitive) string matching is used to compare valid redirect URIs. You can use wildcards at the end of the URL pattern"; the full wildcard `*` "can also be configured ... Please do not use it in production environments"; "Make your registered redirect URIs as specific as feasible" | https://www.keycloak.org/docs/latest/server_admin/index.html |
| K2 | Keycloak's refusal of an unregistered redirect URI: the page "Invalid parameter: redirect_uri" (HTTP 400) and the event `LOGIN_ERROR ... error="invalid_redirect_uri"`; a client's `access.token.lifespan` attribute overrides the realm's | captured (prototype); the override is in the guide's client advanced settings ("The value overrides the realm option with same name") |
| K3 | mod_auth_openidc 2.4.15.1 refuses an ID token issued more than 600 seconds from its clock by default (`OIDCIDTokenIatSlack`): `"iat" validation failure (...): JWT was issued more than 600 seconds in the future` | captured (prototype) |
| K4 | mod_oauth2 3.3.1: `Require oauth2_claim aud:...` failing gives 401 and `AH01631 ... authorization failure`; `verify.exp=skip` switches the expiry check off; a token already accepted is answered from its cache after expiry | captured (prototype) |
| A1 | ATT&CK v20.1: T1110.004 Brute Force: Credential Stuffing, tactic Credential Access, platforms include Identity Provider, IaaS and SaaS | https://attack.mitre.org/techniques/T1110/004/ |
| A2 | ATT&CK v20.1: T1552.001 Unsecured Credentials: Credentials In Files, tactic Credential Access, platforms include IaaS and Containers | https://attack.mitre.org/techniques/T1552/001/ |
