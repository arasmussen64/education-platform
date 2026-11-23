# Writing brief: `csa.sec.pki` (topic 43), Certificates and PKI

Design only. Nothing here is in the repository. Sources were read on 2026-11-12 and each fact below carries its URL. Mechanisms marked **tried** were run on 2026-11-12 in Docker Desktop 29.8.2 on the owner's PC, in a throwaway container from the existing `lab-base-net` image (OpenSSL 3.0.13, nginx 1.24.0, curl 8.5.0; Ubuntu 24.04), and once more in an `ubuntu:24.04` prototype image for the extended-key-usage and CRL-size measurements. The CA configuration used is `prototypes/cps/pki/ca.cnf`. Every container I started was removed; `lab-base-net` was only read, never rebuilt or retagged.

## 1. What the learner will be able to do

1. Run a private certificate authority the way it's run in production, in miniature: an offline root that signs only issuing CAs and its own CRL, and an online issuing CA with a configuration, a database of what it issued and revoked, serial numbers and a policy. Issue from a CSR made where the key lives, and read the CA's database.
2. Limit what an issuing CA can do: `pathlen:0`, name constraints and extended key usage on the CA's own certificate, and say who enforces each (the clients, never the CA software).
3. Revoke a certificate and make the revocation reach the clients that matter: publish a CRL at the address in the certificate, keep it fresh with a timer, run an OCSP responder, and make a server that accepts client certificates actually check (nginx's `ssl_crl` and `ssl_ocsp`). Say what each fails like when it goes stale or down, and why browsers check differently.
4. Rotate below the leaf: bring in a new issuing CA while the old one's certificates are still in use, stop issuing from the old one in time, keep both in relying parties' bundles for the overlap, and plan a root's replacement years ahead.
5. Fix chain errors at depth from `openssl verify` and nginx's error log: a wrong or old intermediate, an expired intermediate, a path that's too long, a CA certificate that isn't one, a name outside the constraints, a revoked certificate, a CRL that's missing or expired; and match a certificate to its issuer by key identifiers.

**The six-month core.**

- A CA is a key, a certificate, a database and a policy. The root stays offline and signs issuing CAs; issuing CAs sign leaves. Limits on a CA (`pathlen`, name constraints, EKU) are checked by the clients, not by the CA that issues.
- A revocation is only as good as the freshest list a client holds: a CRL lasts until its `nextUpdate`, and one past it fails everybody. Publish on a timer well inside the CRL's life; relying parties fetch on a timer and reload.
- OCSP answers live but makes the responder part of your availability; short-lived certificates avoid revocation altogether.
- Rotate a CA by overlap: new CA first, both trusted, old one retired when its last leaf expires.
- Read `error N at D depth`: D says which certificate, N says what. 20 at 0 with the right name is a key mismatch; 10 at 1 is an expired intermediate; 25, 26, 47 and 79 are the CA's limits; 3, 12 and 23 are revocation.

## 2. Prerequisites and terms

**Recommended `prerequisites:`** `[csa.sec.crypto]` (topic 42), which reaches `csa.net.certificates` through `csa.m3.checkpoint`. Crypto gives signatures, hashes, key strength and the KMS idea of keys that never leave their store, which this topic applies to a CA's own key.

**The split with Module 3, stated plainly.** `csa.net.certificates` (topic 32) **owns** what a certificate holds and how a client walks a chain: X.509, subject, issuer, subjectAltName, validity, serial, basic constraints and `pathlen` (its fill-in already sets `CA:TRUE,pathlen:0`), key usage and EKU, root, intermediate, leaf, full chain, trust store, CSR, the verify codes 0, 10, 18, 19, 20 and 21, and 62, a CA made once with `openssl req -x509` and `openssl x509 -req`, ACME, renewal, mutual TLS and nginx's `ssl_verify_client`, `ssl_client_certificate` and `ssl_trusted_certificate`. `csa.net.http-tls` (topic 31) **owns** OCSP, a responder's signed `good`/`revoked`/`unknown` answer, stapling, and names a CRL in a sentence. **This topic adds** running the CA itself (`openssl ca`, its database and CRLs), the offline root and issuing CAs, name constraints and EKU on CAs, revocation end to end (CRL distribution points, OCSP responders, relying parties that check, freshness, soft and hard failure, browsers' approaches), rotating CAs, and chain errors at depth (codes 3, 12, 23, 25, 26, 47 and 79, and 20 caused by a key mismatch rather than a missing certificate). It never re-teaches the Module 3 words; where it uses one, it names the topic.

**Builds on (for the writer):** `csa.net.certificates` and `csa.net.http-tls` as above; the network base and its `on`, `nginx@M`, `journalctl -u`, machine-level units (B9) and `ocsp-responder@` (already a unit in topic 31's labs); `csa.linux.services` (units; `systemctl enable --now`); `csa.sec.crypto` (signature, hash, key strength, HSM in a sentence).

**Terms this topic must define itself:**

- **Certificate authority software** against **a CA** (the key and certificate); `openssl ca`; its **configuration** sections (`[ ca ]`, the CA's own section, `policy`, extension sections), **database** (`index.txt`: status `V`/`R`/`E`, expiry, revocation date and reason, serial, file, subject), `serial`, `crlnumber`, `new_certs_dir`, `unique_subject`, `copy_extensions`.
- **Offline root**, **issuing CA** (also subordinate CA), **two-tier hierarchy**, **CA compromise**.
- **Name constraints** (permitted and excluded subtrees), **relying party** (anyone who checks a certificate).
- **Authority key identifier (AKI)** and **subject key identifier (SKI)**, and **path building** (how a client finds the issuer: by name, then by key identifier).
- **CRL**: thisUpdate, nextUpdate, CRL number, entries, reason codes, **CRL distribution point (CDP)**, **delta CRL** (one sentence), **authority information access (AIA)** with its OCSP and caIssuers addresses, **OCSP signing certificate** (EKU `OCSPSigning`).
- **Soft fail** and **hard fail**; **CRLSets** (Chrome) and **CRLite** (Firefox), one sentence each; **short-lived certificate** as an alternative to revocation.
- **Cross-signing** and **root rollover** (one paragraph).
- **systemd timer**: a `.timer` unit that starts its `.service` on a schedule (`OnBootSec=`, `OnUnitActiveSec=`, `Persistent=`), `systemctl list-timers`. Module 1 never taught timers (searched: no `csa.linux.*` lesson mentions `OnCalendar` or a `.timer` unit); topic 32 used `certbot@web.timer` as scenery only.

## 3. Skills

| Skill | What it covers |
| --- | --- |
| `run-a-ca` | `openssl ca` and its configuration, database, serials and policy; issuing from a CSR made on the machine that keeps the key; offline root, online issuing CA; why `openssl ca` is a teaching tool ("does not have production quality") and what runs real CAs (step-ca, AD CS, OpenBao's PKI engine, the clouds' private CAs). |
| `ca-hierarchy` | Two tiers and why; `pathlen`, name constraints, EKU on a CA certificate, a separate issuing CA per purpose; that relying parties enforce all of it (tried: `openssl ca` issues outside its constraints, clients refuse with 47). |
| `revocation` | Revoking; CRLs (lifetime, CDP, size, publishing timers), OCSP responders (signing certificate, the stale first answer), relying parties that check (nginx `ssl_crl` and `ssl_ocsp`, `openssl verify -crl_check_all`, `curl --crlfile`), soft and hard failure, browsers' CRLSets and CRLite, the CA/Browser Forum's rules, short-lived certificates. **A calculation skill: four estimate items.** |
| `ca-rotation` | Rotating an issuing CA by overlap, when to stop issuing from the old one, both in relying parties' bundles, a root's replacement and cross-signing. **A calculation skill: three estimate items.** |
| `fix-chains` | Reading `error N at D depth` and nginx's `client SSL certificate verify error: (N:…)` for 3, 10 at depth 1, 12, 20 with a key mismatch, 23, 25, 26, 47 and 79; `openssl verify -show_chain`; matching AKI to SKI; nginx's `key values mismatch` for a chain file in the wrong order. |

## 4. Lesson plan

About 3,000 words (24 minutes) with its tables.

1. **What topic 32 left (lesson only).** In topic 32 the learner made a root and an intermediate once and signed a server certificate. Nothing remembered what was issued, nothing could take a certificate back, and nothing stopped the intermediate signing anything at all. This topic runs a CA as a service with a memory and limits. One paragraph, then the labs' machines (idea 10).
2. **A CA is a key, a certificate, a database and a policy (OpenSSL PKI Tutorial, "Simple PKI", the main resource; the lesson supplies the picture).** The picture in words: a notary's office. The stamp is the private key, kept in the safe; the notary's registration on the wall is the CA certificate; the register book records every document stamped, by number (`index.txt` and `serial`); the office's rules say what may be stamped and with which wording (the policy and extension sections). `openssl ca -config ca.cnf -extensions server -in api.csr -out api.pem` stamps a CSR and writes a line `V 261212200339Z  20C4…CD07 unknown /CN=api` (tried); `-revoke` turns `V` into `R` with a date and a reason (`R … 261112200350Z,keyCompromise …`, tried). The CSR is made on the machine that will hold the key; only the CSR and the certificate travel. One paragraph of honesty from the tool's own manual: `openssl ca` "was originally meant as an example of how to do things in a CA. Its code does not have production quality" (fact 1). Companies run step-ca (topic 32's ACME CA), Active Directory Certificate Services, EJBCA, OpenBao's PKI engine, or a cloud's private CA; `openssl ca` is used here because every part of a CA is a file you can read.
3. **Two tiers (Smallstep's "Intermediates, Chains, and Bundling").** Why the root is offline: a root's certificate is in every trust store and can't be taken back quickly; if an issuing CA is compromised, the root revokes it and signs a new one; if the root is compromised, every trust store must change. So the root key lives on a machine with no network (in the labs, `root`, a machine with no cable: files reach it through a shared folder, as a USB stick would), is used a few times a year, and signs only issuing CAs and its own CRL. The issuing CA is online and signs leaves. **Limits on a CA** go in its own certificate, and the lesson shows each one failing in the lab:
   - `pathlen:0` (topic 32's): no CA under it. A sub-CA it signed gives `error 25 at 2 depth lookup: path length constraint exceeded` (tried).
   - **Name constraints**: `nameConstraints = critical, permitted;DNS:.shop.test` lets the CA's certificates be good only for names under `shop.test` (RFC 5280 §4.2.1.10: only in CA certificates, applying to subject names and subjectAltNames, fact 2). The lesson's key point, tried: `openssl ca` issued a certificate for `www.example.test` from that CA without complaint, and `openssl verify` refused it, `error 47 at 0 depth lookup: permitted subtree violation`. **Clients enforce limits, not CAs.**
   - **EKU on the CA**: an issuing CA whose own certificate says `extendedKeyUsage = clientAuth` can't vouch for a server: `openssl verify -purpose sslserver` gives `error 26 at 1 depth lookup: unsuitable certificate purpose`; without `-purpose` it passes (tried). So a client-certificate CA is limited to client certificates, which is topic 32's "a CA kept for clients alone", now enforced.
4. **Revocation: CRLs (Smallstep's "Revocation"; Jamie Nguyen's chapter optional; the lesson supplies the timing).** A CRL is a signed list of revoked serial numbers with two dates: `thisUpdate` and `nextUpdate`, by which the next one will be out (RFC 5280 §5.1.2.5 makes `nextUpdate` mandatory, fact 2). Every certificate names where its CRL lives, the **CRL distribution point** (`crlDistributionPoints = URI:http://crl.shop.test/issuing.crl`). The picture: a bank's list of stolen cards, printed each morning and valid until tomorrow's comes. A shop that never fetches the new list keeps accepting stolen cards; a shop whose list has expired accepts no cards at all. Both happen with CRLs (tried): an old CRL says a revoked certificate is fine (`OK`); a CRL past `nextUpdate` fails every certificate, `error 12 at 0 depth lookup: CRL has expired`, and nginx then refuses every partner with `400` and logs `(12:CRL has expired)`. Size, measured: an empty CRL was 169 bytes and each revoked entry about 36 bytes (16-byte serials, no reason codes; 1,000 entries, 36,178 bytes; fact 14), which is why big CAs split CRLs and why short lifetimes keep them small. One sentence on delta CRLs. **A CRL-publishing timer**: the CA regenerates its CRL on a schedule well inside the CRL's life (the labs: every hour for a 2-hour CRL; Microsoft Cloud PKI publishes every 3.5 days a CRL valid 7, fact 11), and every relying party that caches it refreshes on a schedule too. The lesson teaches the timer unit here (terms).
5. **Revocation: OCSP, and who checks (topic 31's OCSP, Smallstep's "Revocation", nginx's directives, Mozilla's CRLite post).** An OCSP responder answers for one serial at a time, signed by a certificate whose EKU is `OCSPSigning` (or by the CA); the certificate names it in its **AIA** extension. In the lab the responder is `openssl ocsp -index index.txt`, which re-reads the database when it changes, but the first answer after a change was still the old one (tried: `good`, then `revoked`, `revoked`), so checks ask twice. **Who checks, and what failure does**, which the lesson must put in one table because the resources don't:

   | Relying party | Checks | When the list or responder fails |
   | --- | --- | --- |
   | nginx with `ssl_crl` (client certificates) | the CRL file, read when nginx loads its settings; it must hold the CRL of every CA in the chain ("their CRLs should be specified in the same file", fact 6) | missing CA's CRL: `(3:unable to get certificate CRL)` and 400 for everyone; expired: `(12:…)`, 400; a new file isn't seen until a reload (tried, all three) |
   | nginx with `ssl_ocsp leaf` (from 1.19.0) | asks the responder about the client's own certificate on each handshake (with `ssl_ocsp_cache`, caches) | responder down: 400, `certificate status request failed`: hard fail (tried); `ssl_ocsp on` asks about the intermediate too and gets `unknown` from a responder that only knows leaves (tried) |
   | `openssl verify -crl_check` / `-crl_check_all` | the leaf's CRL / every CA's | `error 3`, `error 12` (tried) |
   | Chrome | CRLSets: about 600 kB, about 1% of revocations (as Mozilla reports) | doesn't ask CAs online |
   | Firefox | CRLite since Firefox 137: all revocations, about 300 kB a day; OCSP for domain-validated certificates off from 142 | doesn't ask CAs online |

   The public web's rules (CA/Browser Forum ballot SC-063, 2023): CRLs required, OCSP optional; a new CRL within 24 hours of a revocation; short-lived certificates (at most 7 days from 15 March 2026) need no revocation information at all (fact 7). Let's Encrypt ended OCSP in 2025 (topic 31's). **The judgement:** browsers soft-fail or don't ask, because a stalled responder would break the web; a partner API should hard-fail but must then keep its CRL fresh or its responder up, because the API's availability now includes theirs. Shorter certificates shrink the problem, which is why topic 32's lifetimes are falling.
6. **Rotating CAs (lesson only; Smallstep's chains section for the words).** A leaf is rotated by ACME (topic 32). An issuing CA is rotated by overlap, drawn as a timeline: a new issuing CA (new key) starts issuing on day 0; the old one stops issuing on day 0 and stays trusted until the last certificate it issued expires; relying parties' bundles hold both for that time; servers send the intermediate that issued their own leaf. Two rules with numbers: stop issuing from a CA while its remaining life is still longer than a leaf's lifetime; keep it in bundles for one leaf lifetime after its last issue. The trap, tried: a new issuing CA with the **same name** and a new key, with the old one sent as the chain, gives `error 20 at 0` even though the names match, because the leaf's AKI is the new key's SKI; `openssl x509 -noout -ext authorityKeyIdentifier` on the leaf and `-ext subjectKeyIdentifier` on the candidate show it. A root is rotated years ahead: the new root goes into trust stores first, so devices that update slowly have it before anything chains to it; a **cross-signed** certificate (the new root's key, certified by the old root) lets new chains work on old devices during the overlap.
7. **Chain errors at depth (lesson only, all tried; topic 32 owned 0, 10, 18 to 21 and 62).** The lesson's reference table:

   | `openssl verify` says | Means | Usually |
   | --- | --- | --- |
   | `error 20 at 0`, issuer name matches what was sent | the sent intermediate isn't the one whose key signed the leaf (AKI ≠ SKI) | an old intermediate after a re-key |
   | `error 10 at 1` | the intermediate itself expired | a CA nobody rotated |
   | `error 25 at 2` | a CA below one with `pathlen:0` | someone made a sub-CA |
   | `error 79 at 1` | a certificate without `CA:TRUE` signed the one below | a leaf used as a CA |
   | `error 26 at 1` (with a purpose) | the CA's own EKU doesn't allow this use | a client CA's certificate on a server |
   | `error 47 at 0` | a name outside the CA's name constraints | a certificate issued for the wrong domain |
   | `error 23 at 0` | revoked | |
   | `error 3 at N` | no CRL for the CA at depth N | `-crl_check_all` or nginx without the root's CRL |
   | `error 12 at N` | that CRL is past `nextUpdate` | a publishing or fetching timer stopped |
   | nginx: `key values mismatch` | the first certificate in `ssl_certificate` isn't the key's | the chain file starts with the intermediate |

   And the habit: `openssl verify -show_chain -CAfile root.pem -untrusted chain.pem leaf.pem` prints the path it built, depth by depth.
8. **Where the three clouds differ (their pages, facts 9 to 12).**

   | | AWS | Azure | Google Cloud |
   | --- | --- | --- | --- |
   | Managed private CA | AWS Private CA: $400 a CA a month (general-purpose) or $50 (short-lived certificate mode); $0.75 a certificate for the first 1,000 a month, then $0.35, then $0.001; short-lived $0.058 each; OCSP $0.06 a certificate a month plus $0.20 per 100,000 queries; 30-day free trial of the first CA in a Region | no general-purpose managed private CA on the pages read: Key Vault certificates are self-signed or from its partner public CAs (DigiCert, GlobalSign), and other CAs' certificates are merged in by hand without auto-renewal; Microsoft Cloud PKI is a two-tier root and issuing CA for Intune-managed devices only, up to three CAs, CRLs valid 7 days and published every 3.5 days | Certificate Authority Service, in two tiers: DevOps (no listing, describing or revoking of certificates: meant for short-lived ones) and Enterprise (lifecycle and revocation); prices not confirmed (the page renders in the browser) |
   | Lesson | a private CA is a real monthly cost; short-lived mode is cheaper because it gives up revocation | Azure leaves private PKI to you, or to Intune for devices | the cheap tier is the one that can't revoke |

9. **The labs (lesson only).** Machines on the network base: `root` (the offline root; no cable), `ca` (the issuing CA, its CRLs served by `nginx@ca` at `crl.shop.test`, `ocsp-responder@ca` at `ocsp.shop.test:8888`), `web` (`api.shop.test`, the partner API, `nginx@web` requiring client certificates), `warehouse` and `courier` (partners, each with its own key), `office`, `resolver`. The CA's files are in each machine's own `/etc/shop-ca`. Files travel to `root` and back through `/home/learner/transfer`. Lab clock: CRLs last 2 hours and are republished hourly (the real figures, days, are in every prompt).

**Read now:** the OpenSSL PKI Tutorial's "Simple PKI", the main resource (about 1,500 words and its configuration files, 15 minutes; type along in the worked example instead of on your own machine). Then Smallstep's "Everything you should know about certificates and PKI…", the sections "Intermediates, Chains, and Bundling" and "Revocation" (about 2,000 words, 15 minutes), and nginx's `ssl_crl`, `ssl_ocsp`, `ssl_ocsp_responder` and `ssl_verify_depth`. Optional: Mozilla's CRLite post, Jamie Nguyen's CRL chapter (2015, still right for the commands), RFC 5280 §4.2.1.9 and §4.2.1.10, the clouds' pages behind the table.

## 5. Verified facts

All read or tried on 2026-11-12.

| # | Claim | Source |
| --- | --- | --- |
| 1 | `openssl ca`: `-gencrl` "generates a CRL based on information in the index file"; `-crldays`, `-crlhours` and `-crlsec` set `nextUpdate`; `-revoke`, `-crl_reason` (any reason makes the CRL v2); the database "must be present though initially it will be empty" and is hard to fix if corrupted; `unique_subject`; WARNINGS: "originally meant as an example of how to do things in a CA. Its code does not have production quality." The manual doesn't say the command checks name constraints. | https://docs.openssl.org/3.0/man1/openssl-ca/ |
| 2 | RFC 5280: pathLenConstraint is "the maximum number of non-self-issued intermediate certificates that may follow" (§4.2.1.9); name constraints "MUST be used only in a CA certificate", apply to the subject DN and subjectAltNames, and only to name forms present (§4.2.1.10); CRL issuers "MUST include the nextUpdate field", the date "by which the next CRL will be issued" (§5.1.2.5). | https://www.rfc-editor.org/rfc/rfc5280.txt |
| 3 | **Tried** (OpenSSL 3.0.13): `openssl ca` issued `www.example.test` from a CA constrained to `.shop.test`; `openssl verify` gave `error 47 at 0 depth lookup: permitted subtree violation`. A sub-CA under `pathlen:0`: `error 25 at 2`. A `CA:FALSE` certificate used as a CA: `error 79 at 1 depth lookup: invalid CA certificate`. An intermediate made with `-startdate 20250101000000Z -enddate 20260101000000Z`: `error 10 at 1`. A re-keyed intermediate with the same name, old one sent: `error 20 at 0`; both sent: `OK`. A revoked leaf with a fresh CRL: `error 23 at 0`; with the CRL from before the revocation: `OK`; `-crl_check_all` without the root's CRL: `error 3 at 1`; no CRL at all: `error 3 at 0`; a CRL made with `-crlsec 2`, five seconds later: `error 12 at 0 depth lookup: CRL has expired`. A server certificate under a CA whose EKU is `clientAuth`: `error 26 at 1 depth lookup: unsuitable certificate purpose` with `-purpose sslserver`, `OK` without a purpose. | prototype |
| 4 | **Tried:** `openssl ocsp -index …` re-reads `index.txt` after a revocation, but the first answer after the change was still `good`; the next two were `revoked`. | prototype |
| 5 | **Tried** (nginx 1.24.0): `ssl_crl` with only the issuing CA's CRL refused every client, `client SSL certificate verify error: (3:unable to get certificate CRL)`; with both CRLs, a good client got 200 and a revoked one 400 `The SSL certificate error`; an expired CRL gave 400 and `(12:CRL has expired)`; a regenerated CRL file wasn't used until `nginx -s reload`. `ssl_ocsp leaf` with `ssl_ocsp_responder`: good client 200, revoked 400 (`certificate revoked`); `ssl_ocsp on` refused the good client (`certificate status unknown`, the intermediate asked about); responder stopped: 400 (`certificate status request failed`). `curl --crlfile` with only the issuing CA's CRL: verify result 3. | prototype |
| 6 | nginx: `ssl_crl` "Specifies a file with revoked certificates (CRL) in the PEM format used to verify client certificates. When using intermediate certificates, their CRLs should be specified in the same file" (since 0.8.7); `ssl_ocsp on \| off \| leaf` (1.19.0), `leaf` validates "the client certificate only", needs `ssl_verify_client` and a `resolver` for names; `ssl_ocsp_responder` (only `http://`); `ssl_ocsp_cache`; `ssl_verify_depth` default 1. | https://nginx.org/en/docs/http/ngx_http_ssl_module.html |
| 7 | CA/Browser Forum ballot SC-063v4 (July 2023), "Make OCSP Optional, Require CRLs, and Incentivize Automation": a new CRL within 24 hours of recording a revocation, otherwise at least every 7 days (if every certificate has an OCSP pointer) or 4 days; short-lived subscriber certificates (10 days, then at most 7 days for those issued from 15 March 2026) need no CRLDP or OCSP pointer and needn't be revoked. The ballot page gives no single effective date for "OCSP optional"; secondary sources say 15 March 2024 (not confirmed). | https://cabforum.org/2023/07/14/ballot-sc063v4-make-ocsp-optional-require-crls-and-incentivize-automation/ |
| 8 | Mozilla: CRLite enabled for all desktop Firefox users in Firefox 137; about 300 kB of revocation data a day (a 4 MB snapshot every 45 days plus deltas), updated every 12 hours; Firefox to disable OCSP for domain-validated certificates in Firefox 142; Chrome's CRLSets about 600 kB, covering about 1% of revocations (35,000 of 4 million), by Mozilla's account. | https://hacks.mozilla.org/2025/08/crlite-fast-private-and-comprehensive-certificate-revocation-checking-in-firefox/ |
| 9 | AWS Private CA: "$400 per private CA per month for general-purpose mode", "$50 … for short-lived certificate mode"; general-purpose certificates $0.75 (1–1,000), $0.35 (1,001–10,000), $0.001 (10,001+) a month per Region; short-lived $0.058; OCSP "$0.06 per certificate per month" plus "$0.20 per 100,000 OCSP queries"; no CA operation charge for the first 30 days, for the first CA in each Region. | https://aws.amazon.com/private-ca/pricing/ |
| 10 | Google Certificate Authority Service tiers: DevOps has no "listing, describing, and revoking certificates" and no customer-managed CA key; Enterprise has both. Prices not confirmed: the pricing page's figures render in the browser. | https://docs.cloud.google.com/certificate-authority-service/docs/tiers |
| 11 | Microsoft Cloud PKI: issues certificates "for Intune-managed devices"; a two-tier root and issuing CA hosted by Microsoft, keys in Azure Managed HSM; SCEP; "The CRL validity period is seven days. Publishing and refresh happen every 3.5 days. The CRL is updated with every certificate revocation"; up to three CAs per tenant. ms.date 2026-09-08. | https://learn.microsoft.com/en-us/intune/intune-service/protect/microsoft-cloud-pki-overview |
| 12 | Azure Key Vault certificates: created in the vault (self-signed or from partner CAs DigiCert and GlobalSign, which auto-renew) or imported; "Non-partnered providers and authorities are also allowed but don't support automatic renewal." ms.date 2026-07-10. | https://learn.microsoft.com/en-us/azure/key-vault/certificates/about-certificates |
| 13 | OpenBao has a PKI secrets engine that "generates dynamic X.509 certificates", with ACME. | https://openbao.org/docs/secrets/pki/ |
| 14 | **Measured** (OpenSSL 3.0.13, ECDSA P-256 root, 16-byte random serials, no reason codes): a DER CRL with 0 entries 169 bytes, 100 entries 3,777, 1,000 entries 36,178: about 36 bytes an entry. | prototype |
| 15 | The OpenSSL PKI Tutorial v2.0 (Stefan H. Holek), last updated 2024-05-16, recommends OpenSSL 3.0.5 or later; "Simple PKI" builds a root CA and a signing CA with `openssl ca`, issues, revokes (`-revoke`, `-crl_reason`) and makes a CRL (`-gencrl`). | https://pki-tutorial.readthedocs.io/en/latest/simple/index.html |

## 6. Resources

All opened on 2026-11-12. Linked, never copied.

| Title | URL | Type | Licence | Minutes | Skills |
| --- | --- | --- | --- | --- | --- |
| OpenSSL PKI Tutorial: "Simple PKI" (Stefan H. Holek), the main resource | https://pki-tutorial.readthedocs.io/en/latest/simple/index.html | reading, type-along | © Stefan H. Holek 2012–2022 (no licence stated; linked only) | 15 | `run-a-ca`, `revocation` |
| Everything you should know about certificates and PKI but are too afraid to ask (Mike Malone, Smallstep, updated 2026-02-04): "Intermediates, Chains, and Bundling" and "Revocation" | https://smallstep.com/blog/everything-pki/ | reading | © 2026 Smallstep Labs, all rights reserved; linked only | 15 | `ca-hierarchy`, `revocation`, `ca-rotation` |
| nginx's ngx_http_ssl_module: `ssl_crl`, `ssl_ocsp`, `ssl_ocsp_responder`, `ssl_ocsp_cache`, `ssl_verify_depth` | https://nginx.org/en/docs/http/ngx_http_ssl_module.html | reading | © F5, Inc. (its footer, as recorded in topic 31) | 4 | `revocation` |
| CRLite: fast, private, and comprehensive certificate revocation checking in Firefox (Mozilla Hacks, August 2025): optional | https://hacks.mozilla.org/2025/08/crlite-fast-private-and-comprehensive-certificate-revocation-checking-in-firefox/ | reading | © Mozilla; the licence wasn't read: the writer confirms the footer | optional (about 10) | `revocation` |
| OpenSSL Certificate Authority, "Certificate revocation lists" (Jamie Nguyen, 2015): optional | https://jamielinux.com/docs/openssl-certificate-authority/certificate-revocation-lists.html | reading | © Jamie Nguyen 2013–2015 (no licence stated) | optional (7) | `revocation`, `run-a-ca` |
| RFC 5280, §4.2.1.9 Basic Constraints and §4.2.1.10 Name Constraints: optional | https://www.rfc-editor.org/rfc/rfc5280 | reading | IETF Trust; linked | optional | `ca-hierarchy` |
| AWS Private CA pricing; Google CAS tiers; Microsoft Cloud PKI overview: optional, behind the clouds table | the URLs of facts 9 to 11 | reading | © AWS; CC BY 4.0 except as noted (Google); Microsoft Learn (the writer confirms the licence of the memdocs content) | optional | `run-a-ca`, `revocation` |

**Reading time:** 34 minutes assigned, plus the lesson's 24.

## 7. Practice ladder

The worked example, fill-in, build and debug are network labs on `lab-base-net` (`lab: { init: systemd, restart_trial: true }`), with no topic layer: openssl, nginx, curl and Unbound are in the base. A machine with no cable (`root`) is a first for the base: **try `machine root` with no `link` or `lan` line before writing** (expected to work: a namespace with only `lo`). Each lab ships an empty `/etc/shop-ca` on the lab machine, as the base's README asks for a program it doesn't know. The write lab is a plain lab on Module 3's plain `RUN` line (openssl is in it). Recall items quote captured output with its date.

### 7.1 `example-run-the-ca` (worked example, lab), skills `run-a-ca`, `revocation`, `ca-hierarchy`

Labelled steps:

1. **Read the CA.** `on ca cat /etc/shop-ca/issuing/ca.cnf` (the sections), `index.txt`, `serial`, `crlnumber`; `openssl x509 -noout -ext basicConstraints,nameConstraints,keyUsage` on the issuing CA (tried output in fact 3's prototype).
2. **Issue from a CSR.** `on web openssl req -new -key … -out /home/learner/transfer/api.csr`; `on ca openssl ca -config … -extensions server -in … -out …`; the new `V` line; `-ext crlDistributionPoints,authorityInfoAccess` on the certificate.
3. **Watch a limit hold.** Issue `www.example.test` (it's issued); `openssl verify` refuses it with 47. "The CA wrote it; the clients refuse it."
4. **Publish a CRL.** `openssl ca -gencrl -crlhours 2 -out /etc/shop-ca/public/issuing.crl`; `curl http://crl.shop.test/issuing.crl` from `office`; `openssl crl -noout -lastupdate -nextupdate -crlnumber`.
5. **Revoke.** The courier lost its laptop: `-revoke … -crl_reason keyCompromise`; the `R` line; `verify -crl_check` with the old CRL says OK, with a new one `error 23`.
6. **OCSP.** Ask `ocsp.shop.test:8888` twice about the courier's certificate (`good`, then `revoked`, as fact 4), and say why.
7. **The API checks.** `web`'s nginx has `ssl_crl` with both CRLs; the courier gets 400; the error log says `(23:certificate revoked)`.
8. **Keep it fresh.** `systemctl list-timers` shows `crl-publish@ca.timer` and `crl-fetch@web.timer`; the worked example reads the two units.

Checks: each step's end state. Wrong fixes: `stale-crl-on-web.sh` (revoked, published, never reloaded on web), `only-issuing-crl.sh` (web's file lacks the root's CRL). 35 minutes.

### 7.2 Recall on running a CA

- **`index-revoked`** (`predict_shell`). A captured `index.txt` with five lines (tab-separated). Command: `awk -F'\t' '$1 == "R" {split($3, r, ","); print $4, r[2]}' index.txt`. Expected: the revoked serials and reasons. Explanation reads each field.
- **`mcq-where-the-csr-is-made`** (mcq). Right: "On the server that will use the key; only the CSR travels." Wrong: "On the CA, which then copies the key to the server." / "On the offline root, so the key is never online." / "Anywhere, as long as the key is sent encrypted."
- **`mcq-openssl-ca-production`** (mcq). Right: "Its own manual says it's an example, not production code." Wrong: "It can't revoke, so it only suits short-lived certificates." / "It can't sign intermediates, only leaves." / "It needs an HSM, which most companies lack."

### 7.3 `fill-issuing-ca` (fill-in, lab), skills `ca-hierarchy`, `run-a-ca`

The issuing CA's `ca.cnf` with gaps in `[ v3_issuing ]` (the root signs the issuing CA's CSR with it, on `root`) and `[ server ]`: `pathlen`, the name-constraint line, the CA's key usage, the CDP URI and the OCSP URI. The prompt gives the names (`.shop.test`, `crl.shop.test`, `ocsp.shop.test:8888`) and says the root's files are on `root` and reach it through `/home/learner/transfer`. Then sign `api.shop.test`'s CSR.

Checks (the check signs its own test certificates with the issuing key using `openssl x509 -req`, which writes nothing to the CA's database): `issuing-ca-limits` (pathlen 0, critical name constraint permitting `.shop.test` only, `keyCertSign, cRLSign`), `limits-hold` (a check-made certificate for a random name outside `.shop.test` gives 47; a check-made sub-CA gives 25), `api-cert` (`api.shop.test` verifies under the root, its CDP and AIA name the given URLs, and both URLs answer from `office`), `root-key-stays` (no file outside `root`'s own folder holds a key whose public half is the root's). Wrong fixes: `no-name-constraints.sh`, `constraint-not-critical.sh`, `no-pathlen.sh`, `wrong-crl-url.sh`, `root-key-copied.sh` (signs on `ca` with a copy of the root key). 30 minutes.

### 7.4 Recall on hierarchy

- **`mcq-who-enforces-constraints`** (mcq, captured). The `openssl ca` run that issued `www.example.test` and the verify line with 47. Right: "Clients enforce name constraints; the CA software didn't check." Wrong: "The CA is broken: it must refuse names outside its constraints." / "The constraint only applies to certificates issued after a restart." / "Name constraints only cover the subject, not subjectAltNames."
- **`mcq-pathlen-zero`** (mcq). Right: "Its certificates work, but a CA it signs fails at clients." Wrong: "It can't sign anything at all." / "It may sign one more CA, but no more below that." / "Path length only matters to the root."
- **`mcq-why-offline-root`** (mcq). Right: "A stolen issuing CA can be revoked and replaced by the root." Wrong: "An offline root makes certificates verify faster." / "Clients can't check a root that is online." / "Root keys are too large for an online server."
- **`mcq-client-ca-eku`** (mcq, captured error 26). Right: "The issuing CA's own EKU allows only client certificates." Wrong: "The leaf lacks `serverAuth` in its EKU." / "The CA is missing from the trust store." / "The leaf's subjectAltName doesn't match."

### 7.5 Recall on revocation (calculation skill: four estimates)

- **`mcq-stale-crl-ok`** (mcq, captured `OK` with the old CRL). Right: "The CRL was made before the revocation and is still in date." Wrong: "OpenSSL ignores reason code keyCompromise." / "The certificate's serial was reused for a new certificate." / "`-crl_check` only checks the root's CRL."
- **`mcq-everyone-refused`** (mcq, captured `(12:CRL has expired)` log line). Right: "The CRL on web passed its nextUpdate; every client fails." Wrong: "One partner's certificate expired; the rest are refused in turn." / "The OCSP responder is down, so nginx refuses everyone." / "The root certificate expired at midnight."
- **`mcq-reload-after-crl`** (mcq). The CRL file on web was replaced an hour ago, but the revoked partner still gets in. Right: "nginx read the old CRL when it loaded; it needs a reload." Wrong: "CRLs take an hour to apply, as nextUpdate says." / "nginx only checks CRLs for certificates issued after it." / "The partner's TLS session ticket skips the CRL."
- **`mcq-hard-or-soft`** (mcq). The partner API, OCSP responder unreachable. Right: "Refuse the client: an unchecked certificate might be revoked." Wrong: "Accept it: like a browser, assume good if no answer." / "Accept it, but only for read-only requests." / "Restart nginx so it stops asking the responder."
- **`est-crl-worst-case`** (estimate; numbers unlike the lesson's Microsoft example, so it's worked, not recalled). A CA publishes a CRL every 12 hours, each valid for 48 hours, and a client fetches a new one only when its copy expires. A certificate is revoked a minute after a CRL was published. At most how many hours can that client go on trusting it? Exactly. given `{publish: 12, valid: 48}`; working `valid` (48); mistakes `publish-interval` (12), `sum` (60).
- **`est-crl-size`** (estimate, the measured figures). A CRL of 169 bytes plus 36 bytes per revoked certificate; 250,000 revoked. Size in megabytes (1,000,000 bytes), within 10%. working `(169 + 36 * revoked) / 1000000` (9.0); mistakes `empty-size-per-entry` (42.25), `kilobytes` (9,000).
- **`est-crl-traffic`** (estimate). 5,000 servers each download a 2 MB CRL every 12 hours. Gigabytes a day (1,000 MB), exactly. working `servers * 2 * 2 / 1000` (20); mistake `once-a-day` (10).
- **`est-fetch-timer`** (estimate). The CRL on the API lasts 48 hours. The fetch timer must still leave time for two failed fetches in a row before the CRL expires. Longest timer interval in hours, exactly. working `48 / 3` (16); mistakes `one-failure` (24), `no-failures` (48).

### 7.6 `write-chain-doctor` (write, plain lab), skill `fix-chains`

Write `~/bin/chain-doctor LEAF CHAIN ROOT [CRL]` that prints, for a leaf, its sent chain, the trusted root and optionally a CRL file (all PEM), exactly one line: `ok`, or one of `wrong-intermediate`, `missing-intermediate`, `expired DEPTH`, `not-a-ca DEPTH`, `path-too-long DEPTH`, `name-not-permitted`, `revoked`, `crl-expired DEPTH`, `untrusted-root`. The prompt gives the meanings and the codes (section 4, idea 7) and says the script runs `openssl verify -show_chain -CAfile ROOT -untrusted CHAIN [-crl_check_all -CRLfile CRL] LEAF` and maps its first `error N at D` line, and that 20 needs one more look: `wrong-intermediate` when the chain holds a certificate whose subject is the leaf's issuer but whose SKI isn't the leaf's AKI (`openssl x509 -noout -ext subjectKeyIdentifier`, `-ext authorityKeyIdentifier`), `missing-intermediate` otherwise.

Checks build fresh PKIs at check time in a temporary folder (EC P-256, random names, so a hard-coded answer fails), one fault each, about a second each: a good chain, a re-keyed intermediate with the same name, no intermediate, an expired intermediate (backdated with `openssl ca -startdate -enddate`, tried), a `CA:FALSE` "intermediate", a sub-CA under `pathlen:0`, a name outside the constraints, a revoked leaf with a fresh CRL, an expired CRL (made with `-crlsec 1` and a two-second wait), and an unrelated root. Each check compares one line. Wrong fixes: `every-20-missing.sh` (no AKI/SKI look), `depth-from-chain-order.sh` (prints the position in CHAIN, not the error's depth), `ignores-crl.sh` (no `-crl_check_all`), `crl-check-leaf-only.sh` (`-crl_check`, which reports `error 3` for the intermediate's missing CRL in a case built for that, so `crl-expired` is never seen at depth 1), `hard-coded-ok.sh`, `first-line-of-verify.sh` (prints openssl's own first line). 35 minutes. Plain lab: no network, about 1.5 minutes of CI.

### 7.7 Recall on rotation (calculation skill: three estimates)

- **`mcq-replace-or-add`** (mcq). A new issuing CA is in service; partners' certificates from the old one last up to 200 more days. What goes in the API's client-CA bundle? Right: "Both issuing CAs until the old one's last certificate expires." Wrong: "Only the new CA, so old certificates are pushed to renew." / "Only the root, since both issuing CAs chain to it." / "The old CA only, until every partner has a new certificate."
- **`aki-ski-match`** (`predict_shell`). Files with the `openssl x509 -noout -ext …` output of a leaf (AKI) and two intermediates named alike (SKIs). Command: `grep -A1 'Authority Key' leaf.txt | tail -1` against each intermediate's SKI line, printing which one matches. Expected: `issuing-2026.txt`.
- **`est-stop-issuing`** (estimate). An issuing CA's certificate lasts 1,826 days; leaves last 90. For how many days from its start may it issue full-length leaves? Exactly. working `ca_days - leaf_days` (1,736); mistakes `whole-life` (1,826), `half` (913).
- **`est-bundle-overlap`** (estimate). The old issuing CA issued its last 200-day certificate on its final day of issuing. For how many days after that must relying parties keep trusting it? Exactly. working `leaf_days` (200); mistake `zero` (0).
- **`est-root-lead`** (estimate). Devices update their trust stores at least every 2 years; issuing CAs under a root last 5 years and must not outlive it. How many years before the old root expires must the new root start shipping? Exactly. working `store_years + ca_years` (7); mistakes `store-only` (2), `ca-only` (5).

### 7.8 Recall on chain errors at depth

- **`depth-which-cert`** (mcq, captured `error 10 at 1 depth lookup: certificate has expired`). Right: "The intermediate expired; the leaf may be fine." Wrong: "The leaf expired, one day ago." / "The root expired, at depth 1 of the store." / "The CRL expired, one hour ago."
- **`mcq-same-name-20`** (mcq, captured `error 20 at 0` with matching names). Right: "The intermediate sent has the right name but not the key that signed the leaf." Wrong: "The leaf's subjectAltName doesn't match the request." / "The root isn't in the client's trust store." / "The intermediate's certificate has expired."
- **`mcq-key-values-mismatch`** (mcq). nginx won't start: `key values mismatch`. Right: "The chain file starts with the intermediate, not the server's certificate." Wrong: "The private key is for a different CA." / "The key file's permissions are too open." / "The certificate has expired since the last start."

### 7.9 Ladder order

`example-run-the-ca`, `index-revoked`, `mcq-where-the-csr-is-made`, `fill-issuing-ca`, `mcq-who-enforces-constraints`, `mcq-pathlen-zero`, `mcq-why-offline-root`, `mcq-stale-crl-ok`, `mcq-everyone-refused`, `mcq-reload-after-crl`, `est-crl-worst-case`, `est-crl-size`, `write-chain-doctor`, `depth-which-cert`, `mcq-same-name-20`, `mcq-replace-or-add`, `est-stop-issuing`, `est-root-lead`. Review-only: `mcq-openssl-ca-production`, `mcq-client-ca-eku`, `mcq-hard-or-soft`, `est-crl-traffic`, `est-fetch-timer`, `aki-ski-match`, `est-bundle-overlap`, `mcq-key-values-mismatch`.

Every skill is practised before the proofs: `run-a-ca` (7.1, 7.2, 7.3), `ca-hierarchy` (7.1, 7.3, 7.4), `revocation` (7.1, 7.5), `ca-rotation` (7.7), `fix-chains` (7.6, 7.8). Sixteen multiple-choice items: measure first.

## 8. Proofs

### 8.1 Build: `build-partner-pki` (network lab, 55 minutes), skills `run-a-ca`, `ca-hierarchy`, `revocation`

**Brief.** The shop's partner API (`api.shop.test` on `web`) must accept only partners' certificates from a PKI of the shop's own. From blank files (directories and empty databases given; the prompt names every path):

1. on `root` (no network): a root CA, its key never leaving `root`, and the root's CRL; the root also signs the issuing CA for the shop's own staff, `staff`, whose CSR is waiting in the transfer folder (the API must not trust it);
2. on `ca`: an issuing CA for partners, signed by the root, that can't sign CAs, is good only for names under `partners.shop.test`, and only for client certificates; its certificates name `http://crl.shop.test/partners.crl` and `http://ocsp.shop.test:8888`;
3. certificates for `warehouse` and `courier` from CSRs made on their machines;
4. `nginx@ca` serving both CRLs at `crl.shop.test`, `ocsp-responder@ca` answering, and a CRL republished every hour (lab clock: each lasts 2 hours), enabled so it survives a restart;
5. on `web`: client certificates required, from that issuing CA only, checked against both CRLs, which `web` fetches every 30 minutes and reloads nginx after;
6. the courier's laptop has gone: revoke its certificate so the API refuses it within the hour.

**Checks:**

- `partners-in` (`timeout: 60`, waits for nginx, the responder and the resolver once): the warehouse's certificate gets 200 from `api.shop.test`.
- `revoked-out`: the courier gets 400; `openssl ocsp` asked twice about its serial says `revoked` the second time.
- `only-this-ca`: a check-made client certificate from a check-made CA with the same subject names gets 400.
- `limits`: check-made certificates signed with the issuing key (without touching its database) for a name outside `partners.shop.test`, with EKU `serverAuth`, and a sub-CA's leaf, each get 400 from the API and the matching `openssl verify` error (47, 26 with `-purpose sslclient`, 25).
- `ca-limits-in-cert`: the issuing CA certificate has `pathlen:0`, a critical name constraint and EKU `clientAuth`.
- `root-offline`: no file outside `root`'s own folder holds the root's private key, and `root` has no interface but `lo`.
- `crls-fresh`: both CRLs served at the CDP verify under their CAs, `nextUpdate` at least 60 minutes ahead; `crl-publish@ca.timer` is enabled and fires at most every 60 minutes; `crl-fetch@web.timer` enabled, at most every 30 minutes.
- `web-loaded-fresh`: the CRL nginx loaded (the file on `web`, and nginx's start or reload after it was written) is the one being served.
- `lasting` (with the restart trial): nginx's site is enabled and its settings test clean.

**Wrong fixes:** `root-key-on-ca.sh`, `no-name-constraints.sh`, `no-pathlen.sh`, `no-ca-eku.sh`, `verify-optional.sh` (`ssl_verify_client optional`), `trusts-root-only.sh` (`ssl_client_certificate` holds just the root, so every CA the root signs is trusted; the prompt's step 1 also has the learner sign a second issuing CA, `staff`, for the shop's own people, with a staff member's certificate given; the check `only-this-ca` also sends that staff certificate, which must get 400), `issuing-crl-only.sh` (fails `partners-in`: error 3), `not-revoked.sh`, `published-once.sh` (no publish timer), `no-fetch-timer.sh`, `crl-too-short.sh` (CRL valid 30 minutes with an hourly timer: `crls-fresh`). Eleven.

Shortcuts rejected: verification made optional, a broad trust list, revocation not checked, limits left off the CA, the root key online, a fix that lasts only until the next CRL expires.

### 8.2 Debug: `debug-partners-locked-out` (network lab, 40 minutes), skills `revocation`, `fix-chains`, `ca-rotation`, `ca-hierarchy`

**Scenario.** The build's PKI, a week on. Yesterday the issuing CA was re-keyed (`partners-2`, same name, new key) and a new partner, `courier`, was onboarded from it. The machines: `root`, `ca`, `web`, `warehouse` (certificate from the old issuing CA), `courier` (from the new one), `office`, `resolver`, and a monitor on `office` that calls the API every minute as `warehouse` and logs the status.

**Prompt:** "Partners call the shop's API with their own certificates. Since this morning every partner's call gets `400`, including the courier's, who joined yesterday. The office's browser still shows the API's own certificate as fine. There are three faults; fixing one can change what you see. Rules: keep client certificates required and checked against the CRLs; don't change what the issuing CA's certificate allows; a partner may get a new certificate only from the partners' issuing CA, for a name it's allowed." Checks listed only after a first try.

**Faults:** (1) `crl-fetch@web.timer` was disabled during the re-key, so web's CRL passed `nextUpdate` (everyone 400, `(12:CRL has expired)`); (2) web's client-CA bundle was replaced with the new issuing CA's certificate only, so the warehouse (old CA) fails with 20 at depth 0; the fix is both (the overlap rule), not the old one alone; (3) the courier's certificate was issued for `courier.partner.test`, outside the constraint, so it fails with 47; the fix is a new certificate from the courier's CSR for `courier.partners.shop.test` (the CSR is made again on `courier`).

**Checks:** `warehouse-in`, `courier-in` (with its new certificate), `revocation-still-checked` (the ex-partner's certificate shipped in the scenario, revoked last week and listed in the CRL, still gets 400), `fetch-timer-on`, `both-cas-trusted` (bundle holds both issuing CAs and nothing else), `ca-unchanged` (the issuing CA certificates' sha256s are the scenario's), `names-in-constraint` (every client certificate the CA issued since yesterday, in `index.txt`, is under `partners.shop.test` or revoked).

**Wrong fixes:** `crl-check-removed.sh`, `verify-optional.sh`, `crl-fetched-once.sh` (fresh CRL by hand, timer still off: fails `fetch-timer-on`), `bundle-old-only.sh` (courier fails), `bundle-root-only.sh`, `constraints-dropped.sh` (a new issuing CA without name constraints), `courier-name-left.sh` (a fresh certificate with the same wrong name), and three `two-of-three-*.sh`. Ten.

### 8.3 Explain

**Prompt:** "A colleague proposes for the company's internal services: one root CA that signs every server's certificate directly, certificates valid five years, and no revocation, 'because we can just replace a certificate if we need to'. Explain, in your own words, what you'd build instead and why: the hierarchy and the limits you'd put on each CA, and who enforces them; how a revocation reaches the services that rely on a certificate, what goes wrong when the list or the responder fails, and why browsers behave differently; how you'd rotate an issuing CA and, one day, the root; and what the three clouds offer for a private CA."

**Rubric:**

- `hierarchy` (required): offline root signing only issuing CAs and its CRL; issuing CAs online; a compromised issuing CA is revoked and replaced, a compromised root means changing every trust store.
- `limits` (required): `pathlen:0`, name constraints, EKU per purpose on the issuing CA; enforced by relying parties, not the CA software.
- `revocation` (required): CRLs at the CDP with a nextUpdate, published on a timer well inside it, fetched and reloaded by relying parties; an expired CRL locks everyone out; OCSP is live but a dependency; hard fail for a partner API, soft fail or none in browsers (CRLSets, CRLite); short lifetimes shrink the problem.
- `rotation` (required): new issuing CA, old stops issuing while its remaining life exceeds a leaf's, both trusted until the old one's last leaf expires; a new root distributed years ahead, cross-signing for the overlap.
- `clouds` (optional): AWS Private CA's two modes and their monthly prices, Google CAS's tiers (DevOps can't revoke), no general managed private CA on Azure (Key Vault's partner CAs; Cloud PKI for Intune devices).

## 9. Review pool

| Skill | Come-back questions |
| --- | --- |
| `run-a-ca` | `index-revoked`, `mcq-where-the-csr-is-made`, `mcq-openssl-ca-production`, `fill-issuing-ca` |
| `ca-hierarchy` | `mcq-who-enforces-constraints`, `mcq-pathlen-zero`, `mcq-why-offline-root`, `mcq-client-ca-eku`, `fill-issuing-ca` |
| `revocation` | `mcq-stale-crl-ok`, `mcq-everyone-refused`, `mcq-reload-after-crl`, `mcq-hard-or-soft`, `est-crl-worst-case`, `est-crl-size`, `est-crl-traffic`, `est-fetch-timer` |
| `ca-rotation` | `mcq-replace-or-add`, `aki-ski-match`, `est-stop-issuing`, `est-bundle-overlap`, `est-root-lead` |
| `fix-chains` | `depth-which-cert`, `mcq-same-name-20`, `mcq-key-values-mismatch`, `aki-ski-match`, `write-chain-doctor` |

`review_pool:` the eight review-only items of 7.9, with `est-crl-worst-case`, `depth-which-cert` and `index-revoked`.

## 10. Platform work needed first

None that blocks. Two small things:

1. **A machine with no cable** on the network base: confirm `netlab` accepts `machine root` with no `link`/`lan` line and that `netlab verify` handles it. If it doesn't, the smallest change is to skip machines without links in `netlab up`'s address and route steps (a few lines), with a fallback of a `root` machine on a lan of its own with no other member.
2. **`/etc/shop-ca` on the lab machine** in each lab's Dockerfile (`RUN mkdir -p /etc/shop-ca`), as the base README requires for a machine-own folder of a program the base doesn't know.

The `ocsp-responder@.service` unit from topic 31 is reused with its paths changed; `crl-publish@` and `crl-fetch@` are machine-level units and timers (B9's pattern), shipped per lab.

## 11. Cost and time

**Money: none.** No cloud account. AWS Private CA would cost $400 a month for one CA (fact 9), far outside any free tier: priced in an estimate in review, never built.

**Learner minutes:** lesson 24, readings 34, 18 practice recall items at 1.5 each 27, worked example 35, fill-in 30, write 35, build 55, debug 40, explain 20: **about 300**.

**CI time:** network labs on the base boot in 2 to 3 s for seven machines (Module 3's figure); checks are openssl and curl calls of under a second each, with one 60-s wait per run. Example 4 containers (1.5 min), fill-in 7 (2.5), write (plain, 7 containers, 1.5), build 13 (5), debug 12 (4.5): **about 15 minutes**. No topic layer, so nothing extra to build.

## 12. Open questions, each with a recommendation

1. **Which CA software: `openssl ca`, step-ca or OpenBao's PKI engine?** `openssl ca` shows every part of a CA as a file (the database, serials, CRLs), is already in the base and costs no download, and its own manual's warning becomes a lesson point. step-ca (topic 32) and OpenBao's PKI engine hide the database behind an API. **Recommendation: `openssl ca`**, with step-ca, OpenBao PKI and the clouds' private CAs named as what production uses.
2. **CRL or OCSP in the build?** Both are taught; the build requires CRLs at nginx (what CA/B Forum now requires publicly) and an OCSP responder at the CA, checked by `openssl ocsp`. **Recommendation: as designed**; `ssl_ocsp leaf` is practised in the worked example's reading and the hard-fail item, not required in the build, so one build doesn't depend on a responder's stale first answer.
3. **Lab clock.** CRLs of 2 hours with hourly publishing, against 7 days and 3.5 days in Microsoft's service and 4 to 7 days for public CAs. **Recommendation: as designed**, every prompt giving the real figures beside the lab's, as Module 3 did (its brief §3.3).
4. **A topic-43 explain about the clouds' private CAs being expensive.** AWS's $400 a month is a real design input ("who runs our internal CA?"). **Recommendation: keep it optional in the rubric**, and let Module 20's key-management topic own the build-or-buy decision.
