# Writing brief: `csa.sec.authn-authz` (topic 40), Authentication and authorization

Design only. Nothing here is in the repository. Sources were read on 2026-11-12 and each fact below carries its URL. Lab mechanics marked **tried** were run on 2026-11-12 in Docker Desktop 29.8.2 on the owner's PC (kernel 6.18.33.2-microsoft-standard-WSL2), in a plain `ubuntu:24.04` container with Python 3.12 from Ubuntu's archive, the Cedar CLI 4.14.0 and OPA 1.21.4, both downloaded from their GitHub releases and checked by sha256. Everything started was removed afterwards. The prototype files are in `prototypes/authn-strong/policy/` (`Dockerfile`, `lab/shop.cedarschema`, `lab/reference.cedar`, `lab/policycheck`, `lab/make-wrong.py` and the wrong policies it made in `lab/wrong/`, `lab/reference.rego` and `lab/batch.rego` for the comparison with OPA).

The companion brief is [csa.sec.strong-auth.md](csa.sec.strong-auth.md) (topic 41). The two share one new lab base, the **policy-lab base** (section 10), and topic 41 builds on this topic's vocabulary.

## 1. What the learner will be able to do

1. Tell authentication from authorization in any system put in front of them: which step proves who someone is (and with which factors), which step decides what they may do, where each happens, what each failure looks like (`401` against `403`), and why a token from the first step is only an input to the second.
2. Write access rules as code in Cedar: role-based rules (roles as groups), attribute-based rules (`when` and `unless` on the principal's, the resource's and the request's attributes), a `forbid` that no `permit` can override, validated against a schema, and tested against requests.
3. Apply least privilege as a loop rather than a one-off: start narrow or from a managed role, observe real use over a window long enough to see rare legitimate jobs, cut what is unused into a custom role at the narrowest scope, watch for denials, repeat. Read an analyzer's report and do the sums (what share is unused, how long a window must be, what the analysis costs).
4. Enforce separation of duties: name the duties that must not meet in one person, and express them as conflicting roles (static) or as a per-request rule (dynamic: the approver is not the requester).
5. Compare the three clouds' policy models side by side: how AWS combines identity, resource, boundary and organization policies with explicit deny; how an Azure role assignment joins a principal, a role and a scope, adds up, and is cut by deny assignments; how Google's allow policies inherit down the hierarchy and its deny policies are checked first. Name each cloud's least-privilege tools and what they cost.

**The six-month core.** What should still be there half a year on, and what the review pool is built around:

- **Authentication** proves who (a password is something you know; a phone or key something you have; a fingerprint something you are; MFA is two different kinds). **Authorization** decides, on every request, whether that proven principal may do this action to this resource now. `401` means "who are you?", `403` means "I know who you are, and no".
- **Default deny, and an explicit deny wins.** Nothing is allowed until a rule allows it, and a rule that forbids beats every rule that allows: Cedar's `forbid`, AWS's explicit `Deny`, Azure's deny assignments, Google's deny policies.
- **RBAC** gives permissions to roles and people to roles: easy to read and audit, but it multiplies with every dimension (department × store × level). **ABAC** writes the rule over attributes and stays one rule. **Policy as code** keeps rules in files that are versioned, reviewed and tested.
- **Least privilege is a loop.** Observe, cut, watch, repeat. An analyzer only sees what happened in its window, so a job rarer than the window looks unused.
- **Separation of duties:** no one person can complete a sensitive task alone.
- **The three clouds:** AWS: union of identity and resource policies, inside the intersection of SCPs, RCPs and boundaries, explicit deny wins. Azure: principal + role + scope, additive, deny assignments first. Google: role bindings inherited down organization, folder, project, resource and added up; deny policies checked before allow policies.

## 2. Prerequisites and terms

**Recommended `prerequisites:`** `[csa.m3.checkpoint]`, as the outline has it. The spec's map runs Module 3 to Module 4, and within Module 4 this topic can be taken before or after Threat modeling (topic 39): it uses no word topic 39 defines. Module 2 is not a prerequisite, so Active Directory's groups and Kerberos tickets are mentioned only as "if you took Module 2" asides.

**Builds on (for the writer, not for `prerequisites:`):**

| Topic | What this topic uses from it |
| --- | --- |
| `csa.linux.permissions` | Users, groups, `chmod` modes, `sudo` and `sudoers`, SSH key pairs. The lesson opens with them: an SSH key check is authentication, a file mode or a `sudoers` line is authorization, and Linux's model (owner, group, others) is the learner's first access-control model. Its line "least privilege; `sudo -l -U name` shows what someone may run" is retrieved, not retaught. |
| `csa.linux.hardening` | Least privilege for services (service users, `600` secrets, no blanket `NOPASSWD`) and its one line "multi-factor authentication belongs on the cloud console". |
| `csa.linux.shell`, `csa.linux.scripting` | `awk`, `sort`, `uniq -c`, `comm`, `grep -c`, for reading access logs in the recall items and the write lab. |
| `csa.net.http-semantics` | An HTTP request, its headers, status codes (it taught 200, 204, 301, 304, 404, 405, 412, 429, 502 to 504, **not 401 or 403**, which this topic defines), and the cookie. |
| `csa.net.http-tls`, `csa.net.certificates` | Public-key signatures (a token is signed; one sentence), and mutual TLS: a client certificate is how a machine authenticates (retrieval in one recall item). |

**Terms this topic must define itself** (no earlier topic defines them; the owner column is for the module critic):

| Term | Notes |
| --- | --- |
| identity, principal (a person, or a workload: a service, a job, a VM), credential | "Workload identity" in one sentence; Module 10's `csa.iam.workload-identity` goes further. |
| authentication factor and its three kinds; MFA | One paragraph. Topic 41 owns which MFA methods resist phishing. |
| session, token, claim | One sentence each: the proof a sign-in leaves behind, which the app reads on later requests. `csa.sec.federation` (topic 44) opens tokens up; this topic never shows a token's format. |
| authorization, permission, policy, request (principal, action, resource, context), decision | The request model the labs use. |
| default deny, explicit deny | |
| least privilege, privilege creep, scope, wildcard | |
| separation of duties, static and dynamic | |
| RBAC, role, role explosion; ABAC, attribute; ReBAC | ReBAC in one paragraph (relationships such as "owner of", "member of the team that owns"); no lab uses it. |
| policy as code; policy decision point (PDP) and policy enforcement point (PEP) | One paragraph: the app asks (and enforces), the policy engine decides. Topic 47 (zero trust) builds on PDP and PEP; if its designer defines them, the critic picks one owner. |
| Cedar's words: entity, entity type, `permit`, `forbid`, scope, `when`, `unless`, `in`, schema, validation | Only as the labs need them. |
| access analyzer, last-accessed information, policy generation, role recommendation, custom role, just-in-time access, eligible against active assignment | Concepts from the clouds' documentation; Module 10 uses the real tools. |
| `401 Unauthorized`, `403 Forbidden` | With RFC 9110's own wording. |

## 3. Skills

| Skill | What it covers |
| --- | --- |
| `authn-or-authz` | Which step proves who and which decides what may be done; factors and what counts as MFA (two of the same kind doesn't); where each happens (identity provider against app or policy engine); `401` against `403`; a token as the output of authentication and an input to authorization; an authentication fact (`mfa`) used in an authorization rule. |
| `access-models` | RBAC, ABAC, ReBAC and policy as code: what each is good and bad at, role explosion, writing and reading Cedar (`permit`, `forbid`, `when`, `unless`, roles as groups with `in`), default deny and forbid-wins, schema validation catching a typo. **Calculation items:** role-explosion counts and "how many of these requests are allowed" counts, four estimates. |
| `least-privilege` | Minimum permissions at the narrowest scope; wildcards; managed against custom roles; the loop (observe, cut, watch, repeat); the analyzers (AWS IAM Access Analyzer, last-accessed information, Google's role recommender, Azure's PIM and access reviews) and their windows and prices; reading a usage log against a grant. **A calculation skill: four estimate items.** |
| `separation-of-duties` | Duties that must not meet (request and approve, write and audit, deploy and approve the change); static (conflicting roles) against dynamic (a per-request rule); expressing it as a `forbid`; why a "temporary" exception is a hole. One estimate (pairs of roles to review). |
| `cloud-policy-models` | AWS's evaluation (identity and resource-based policies as a union, boundaries, SCPs and RCPs as an intersection that grants nothing by itself, explicit deny), Azure's role assignments (principal, role, scope; additive; deny assignments; conditions), Google's allow and deny policies (bindings, inheritance as a union, deny checked first, conditions, principal access boundaries), and each cloud's just-in-time access (PIM, Google's Privileged Access Manager). |

Five skills. Every one is practised before either proof asks for it (section 7.9), and every one has at least two come-back questions (section 9).

## 4. Lesson plan

The lesson is about 2,100 words (16 minutes). Each idea names the resource it pairs with, and the explanation the lesson must supply itself.

1. **Two questions every system asks (lesson only, then Microsoft's page).** Start from Module 1: when you `ssh` to a server, the server first checks your key (who are you?), then the file modes and `sudoers` decide what you may touch (what may you do?). The same two steps happen on every website and every cloud API. Picture in words, which no resource draws well for a beginner: a hotel. The front desk checks your passport once (**authentication**) and gives you a key card (**the token**). Every door then checks the card (**authorization**): your room opens, the gym opens until 22:00, the manager's office never does. The front desk doesn't decide which doors open; the door locks don't look at passports. Read Microsoft's "Authentication vs. authorization" (6 minutes) for the definitions, then the lesson adds what the page doesn't:
   - **Factors.** Something you know, have, are. Two of the same kind (a password and a security question) is still one factor. MFA is two different kinds. Topic 41 is about which second factors a phishing site can steal; here it's enough that MFA is a fact about how someone signed in, which an authorization rule can ask for ("refunds only in a session that used MFA").
   - **`401` and `403`.** RFC 9110: `401 Unauthorized` means the request "lacks valid authentication credentials" and the server must say how to authenticate (`WWW-Authenticate`); `403 Forbidden` means the server "understood the request but refuses to fulfill it", and credentials, if sent, are "insufficient". The name `Unauthorized` is a historical misnomer: it means unauthenticated. One line on why some apps answer `404` instead of `403` (not admitting the resource exists).
2. **Rules: who, what, which thing, under what conditions (OWASP, then Cedar's syntax page).** Every authorization decision has four inputs: a **principal**, an **action**, a **resource**, and the **context** (time, network, whether this session used MFA). The engine that decides is the **policy decision point**; the app that asks and then obeys is the **policy enforcement point**. OWASP's cheat sheet, sections "Enforce Least Privileges", "Deny by Default" and "Validate the Permissions on Every Request" (about 10 minutes), gives the principles. The lesson adds the hotel picture again for **default deny**: a new door opens for nobody until someone programs it.
3. **Three ways to write the rules (OWASP's "Prefer Attribute and Relationship Based Access Control over RBAC", then the lesson).**
   - **RBAC:** permissions go to roles, people go into roles. Linux groups are RBAC. Its weakness is **role explosion**, which the lesson shows with numbers: four departments × six stores × two levels needs 48 roles to say "staff see their own store's orders", one rule with attributes.
   - **ABAC:** the rule compares attributes: `principal.store == resource.store`. NIST SP 800-162's definition in one sentence.
   - **ReBAC:** access follows relationships ("editors of a folder edit the documents in it"); one paragraph, no lab.
   - **Policy as code:** whichever model, the rules live in files that are versioned, reviewed, tested in CI and deployed like code, rather than clicked into a console. Module 18 does it for infrastructure with OPA; this module uses **Cedar**, the language AWS built for application authorization (section 12, open question 1, says why Cedar here and OPA later).
4. **Cedar in fifteen lines (Cedar's "Basic policy construction" and "Authorization", 12 minutes).** Walk the worked example's policy: `permit` with a scope (`principal in Role::"support"`, `action == Action::"view"`) and a `when`; a `forbid ... unless { context.mfa }`. Cedar's decision rule, quoted from its documentation: no request is allowed unless some `permit` grants it, and "any satisfied `forbid` policy _overrides_" a permit. A policy that errors is skipped. Then **the schema**: the list of entity types, attributes and actions. `cedar validate` against it turns a typo into an error with a suggestion (tried: `principal.stor` gives "attribute `stor` on entity type `Staff` not found ... did you mean `store`?"). The lesson shows the same one rule in OPA's Rego beside it, and what happened in the prototype: Rego accepted a policy that reads `input.principal.rol` (a typo) without complaint, even with `opa check --strict`, and the rule silently never matched (tried). Fail-safe, but invisible; a schema makes it visible.
5. **Least privilege, as a loop (AWS's best-practice sections, Google's role recommendations page, then the lesson).** NIST's definition in one line ("the minimum system resources and authorizations that the entity needs"). Then the picture the docs don't draw for a beginner: least privilege is **a thermostat, not a switch**. Start from what the job needs (or from a managed role, which AWS says may not be least privilege "because they are available for use by all AWS customers"), observe what is really used, cut the rest into a **custom role** at the narrowest **scope**, watch for denials, repeat. The observation step is what the analyzers automate:
   - AWS: IAM Access Analyzer's **unused access** findings ($0.20 per IAM role or user analyzed per month), **policy generation** from up to 90 days of CloudTrail (free; it can't see data events or `iam:PassRole`), and **last accessed information** (at least 400 days of service information).
   - Google: **role recommendations** from up to 90 days of permission use (30 or 60 for projects); they never suggest more access; basic-role recommendations are free, the rest need Security Command Center Premium or Enterprise.
   - Azure: no free usage-based recommender for Azure RBAC today. Microsoft Entra Permissions Management, which did this across clouds, stopped being sold on 2025-04-01 and its support ended on 2025-11-01; its CIEM features continue inside Defender for Cloud's paid Defender CSPM plan. What Azure gives everyone is the model itself (narrow scopes, custom roles without wildcards, at most three subscription owners), and with Entra ID Governance or P2, PIM's **just-in-time** activation and access reviews.
   - **The window trap**, which the write lab makes real: an analyzer only sees its window. A job that runs every 100 days is invisible to a 90-day look-back and gets "recommended" away. Read the job's purpose, not only its log.
6. **Separation of duties (NIST's glossary, then the lesson).** "No user should be given enough privileges to misuse the system on their own." Static: the roles "requester" and "approver" never go to the same person. Dynamic: anyone may approve, but not their own request, decided per request. In Cedar the dynamic form is one `forbid ... when { resource.requested_by == principal }`. The lesson says why the forbid matters more than the permits: a later, broader `permit` (someone adds "managers may approve anything") can't undo a `forbid`.
7. **Three clouds, side by side (AWS evaluation logic, Azure RBAC overview, Google IAM overview, about 25 minutes in all; the lesson's table).** The lesson's table, worded from each page as read on 2026-11-12:

   | | AWS | Azure | Google Cloud |
   | --- | --- | --- | --- |
   | Who gets access | identity-based policies on users and roles, resource-based policies on resources | a **role assignment**: security principal + role definition + scope | an **allow policy** on a resource: role bindings of principals to roles |
   | Where it applies | the account; Organizations SCPs and RCPs limit whole accounts | management group, subscription, resource group or resource, inherited downwards | organization, folder, project or resource, inherited downwards |
   | How grants combine | identity and resource-based policies in one account: a **union**; with a permissions boundary or SCP/RCP: an **intersection** ("SCPs and RCPs alone are insufficient to grant permissions") | **additive**: "your effective permissions are the sum of your role assignments" | the **union** of all allow policies from the resource up to the organization |
   | What beats a grant | an explicit `Deny` in any of them | a **deny assignment** ("if a deny assignment applies, access is blocked"), checked first | a **deny policy**: "IAM always checks relevant deny policies before checking relevant allow policies" |
   | Attributes | `Condition` blocks, tags | role assignment **conditions** (Azure ABAC) | **IAM Conditions** on bindings |
   | Least-privilege tools | IAM Access Analyzer (unused access, policy generation, validation, custom checks), last accessed information | PIM (just in time), access reviews; usage-based recommendations only in paid Defender CSPM | role recommender and policy insights, Privileged Access Manager |

8. **Recap** as in the content README: the six-month core in eight bullets.

**Where the three clouds differ** is idea 7's table, plus idea 5's analyzer list. A Module 10 learner meets each cloud's real tools; this topic gives the model and the vocabulary.

## 5. Verified facts

Each read on 2026-11-12 unless marked.

| # | Claim | Source |
| --- | --- | --- |
| F1 | Authentication "is the process of proving that you are who you say you are"; authorization "is the act of granting an authenticated party permission to do something" (ms.date 2025-03-21, 701 words) | https://learn.microsoft.com/en-us/entra/identity-platform/authentication-vs-authorization |
| F2 | `401 (Unauthorized)`: the request "has not been applied" because it lacks valid credentials, and the server "MUST send a WWW-Authenticate header field"; `403 (Forbidden)`: "the server understood the request but refuses to fulfill it", and if credentials were provided, "the server considers them insufficient" (RFC 9110 §15.5.2 and §15.5.4) | https://www.rfc-editor.org/rfc/rfc9110.html |
| F3 | Least privilege: each entity is granted "the minimum system resources and authorizations that the entity needs to perform its function" (NIST SP 800-53 Rev. 5, citing CNSSI 4009-2022) | https://csrc.nist.gov/glossary/term/least_privilege |
| F4 | Separation of duty: "no user should be given enough privileges to misuse the system on their own" (NIST SP 800-192); enforced statically through conflicting roles or dynamically at access time | https://csrc.nist.gov/glossary/term/separation_of_duty |
| F5 | ABAC: access decided by evaluating attributes of the subject, object, requested operation and sometimes environment conditions against policy (NIST SP 800-162, January 2014, updated 2019-08-02, final) | https://csrc.nist.gov/pubs/sp/800/162/upd2/final |
| F6 | OWASP's recommendations: enforce least privileges, deny by default, validate the permissions on every request, prefer attribute- and relationship-based access control over RBAC, and seven more; licence CC BY-SA 4.0 (the cheat-sheet repository's licence, read through GitHub's API) | https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html |
| F7 | Cedar: "no request is authorized ... unless there is a specific `permit` policy that grants it"; "any satisfied `forbid` policy _overrides_ it"; "if a policy's evaluation returns `error` ... it is skipped" | https://docs.cedarpolicy.com/auth/authorization.html |
| F8 | Cedar policy syntax: effect (`permit`, `forbid`), scope (`principal`, `action`, `resource` with `==`, `in`, `is`), conditions (`when`, `unless`), annotations (about 1,300 words) | https://docs.cedarpolicy.com/policies/syntax-policy.html |
| F9 | Cedar's documentation repository is Apache-2.0 (GitHub's licence API for `cedar-policy/cedar-docs`) | https://github.com/cedar-policy/cedar-docs |
| F10 | Cedar CLI 4.14.0 released 2026-10-17 with a Linux x86_64 binary; tarball sha256 `2db9a0dbf6555c256c11c688b67f043ddbf9af06bdd1bf8d7c9fff3fa2e81886` (matched its published `.sha256`, tried); binary 18,461,520 bytes; Apache-2.0 (its `LICENSE`, "Copyright Cedar Contributors" in `NOTICE`). 4.14.1 followed on 2026-11-02 (too new to pin today) | https://github.com/cedar-policy/cedar/releases/tag/cedar-policy-cli-v4.14.0 |
| F11 | **Tried:** `cedar run-tests` takes a JSON array of tests and refuses one without `reason` and `num_errors` (`missing field \`reason\``); with `"reason": []` and `"num_errors": 0` it checks the decision, printing `fail: expected Deny, got Allow` for a disagreement and `results: N passed, M failed` | prototype `policy/lab/policycheck` |
| F12 | **Tried:** `cedar validate --schema ... --policies ...` rejects `principal.stor` with "attribute `stor` on entity type `Staff` not found" and "did you mean `store`?", exit status 3 | prototype |
| F13 | OPA 1.21.4, released 2026-10-23, static Linux binary sha256 `2ab571f367f293bb19523b76f92f1945bbf245003392c7f392903f95c2b9b630` (matched, tried), 64 MB, Rego v1, Apache-2.0. **Tried:** `opa check --strict` accepted a rule reading the misspelt `input.principal.rol`, and `opa eval` returned `false`; a comprehension can't use `with` directly (`rego_parse_error: unexpected with keyword`), so batch evaluation needs a helper function | https://github.com/open-policy-agent/opa/releases/tag/v1.21.4 |
| F14 | AWS, one account: identity-based and resource-based permissions are "the union of the permissions of the two types", and "an explicit deny in either of these policies overrides the allow"; with a permissions boundary, "the intersection"; with SCPs or RCPs, "an action must be allowed by all three policy types" | https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html |
| F15 | AWS best practices include "Apply least-privilege permissions", "Get started with AWS managed policies and move toward least-privilege permissions" (managed policies "might not grant least-privilege permissions for your specific use cases because they are available for use by all AWS customers"), "Use IAM Access Analyzer to generate least-privilege policies based on access activity", "Regularly review and remove unused ..."; "SCPs and RCPs alone are insufficient to grant permissions"; phishing-resistant MFA "such as passkeys and security keys wherever possible" | https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html |
| F16 | IAM Access Analyzer: external, internal and unused access analyzers, policy validation, custom policy checks, policy generation from CloudTrail; unused access findings cover unused roles, access keys, passwords, services and actions; service-linked roles aren't analyzed for unused access | https://docs.aws.amazon.com/IAM/latest/UserGuide/what-is-access-analyzer.html |
| F17 | Prices: unused access analyzer $0.20 per IAM role or user analyzed per month; internal access $9.00 per resource monitored per Region per month; custom policy checks $0.0020 per API call; external access analysis, policy validation and policy generation free | https://aws.amazon.com/iam/access-analyzer/pricing/ |
| F18 | Policy generation analyzes "a time period of up to 90 days" of CloudTrail; doesn't identify action-level activity for data events; `iam:PassRole` isn't tracked | https://docs.aws.amazon.com/IAM/latest/UserGuide/access-analyzer-policy-generation.html |
| F19 | Last accessed information: service tracking period "at least 400 days"; it includes all attempts, not just successful ones | https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_last-accessed.html |
| F20 | Azure: "A role assignment consists of three elements: security principal, role definition, and scope"; four scope levels; "an additive model ... the sum of your role assignments"; deny assignments are checked first ("If a deny assignment applies, access is blocked"); conditions evaluated last; free with the subscription (ms.date 2024-03-12, updated 2025-10-15) | https://learn.microsoft.com/en-us/azure/role-based-access-control/overview |
| F21 | Azure best practices: grant least privilege; "a maximum of 3 subscription owners"; limit privileged administrator roles; use PIM; assign roles to groups; use role IDs; avoid wildcards in custom roles (ms.date 2025-03-30) | https://learn.microsoft.com/en-us/azure/role-based-access-control/best-practices |
| F22 | PIM: just-in-time, time-bound, approval, MFA on activation, justification, notifications, access reviews; eligible against active assignments; licensed through Microsoft Entra ID Governance (ms.date 2026-04-23). The pricing page lists "select PIM capabilities" in P2 and full PIM in Entra ID Governance or Entra Suite | https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-configure ; https://www.microsoft.com/en-us/security/business/microsoft-entra-pricing |
| F23 | Microsoft Entra Permissions Management: no longer sold to new EA and direct customers from 2025-04-01; support ended 2025-11-01; CIEM features continue in Defender for Cloud's Defender CSPM plan. **Read from search-result summaries of Microsoft's two Tech Community posts, not from the posts themselves**: the writer opens both before quoting | https://techcommunity.microsoft.com/blog/microsoft-entra-blog/important-change-announcement-microsoft-entra-permissions-management-end-of-sale/4399382 ; https://techcommunity.microsoft.com/blog/microsoft-entra-blog/11-days-remaining-support-for-microsoft-entra-permissions-management-ends-novemb/4462424 |
| F24 | Google: an allow policy holds role bindings; basic, predefined and custom roles (basic roles "shouldn't be used in production"); child resources inherit their parents' policies; "The union of all of these policies is called the effective allow policy"; deny policies, IAM Conditions, principal access boundary policies | https://docs.cloud.google.com/iam/docs/overview |
| F25 | Google: "IAM always checks relevant deny policies before checking relevant allow policies"; deny policies are inherited, and a higher-level deny applies even where lower levels are more permissive | https://docs.cloud.google.com/iam/docs/deny-overview |
| F26 | Google role recommendations: observation period up to 90 days (30 or 60 for project-level); "a role recommendation never suggests a change that increases a principal's level of access"; basic-role recommendations "available at no charge", others need Security Command Center Premium or Enterprise; insights for newly granted roles can take up to 15 days | https://docs.cloud.google.com/policy-intelligence/docs/role-recommendations-overview |
| F27 | Google Privileged Access Manager: just-in-time temporary elevation through entitlements and grants with a maximum duration, optional approval and justification, logged to Cloud Audit Logs; some features need Security Command Center Enterprise or Premium; core pricing not stated on the page | https://docs.cloud.google.com/iam/docs/pam-overview |

Where sources disagree or couldn't be confirmed: F23 as marked; Google's pages showed no "last updated" date or licence footer in the text fetched (Module 3 recorded Google's pages as CC BY 4.0 "except as otherwise noted" from Google's site policies; the writer confirms in a browser); Microsoft Learn's Entra pages are in `MicrosoftDocs/entra-docs`, whose `LICENSE` file says MIT (read through GitHub's API), while Module 3 recorded Azure's pages as CC BY 4.0 (`azure-docs`): the writer records each page's licence from its own repository.

## 6. Resources

Fetched on 2026-11-12. Minutes are the assigned parts at about 130 words a minute.

| # | Title | URL | Type | Licence | Minutes | Skills | Checked |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1 (main) | Authorization Cheat Sheet (OWASP): read "Introduction" and the first five recommendations, "Enforce Least Privileges" to "Prefer Attribute and Relationship Based Access Control over RBAC" | https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html | reading | CC BY-SA 4.0 | 13 (about 1,700 of its 3,500 to 4,000 words) | `access-models`, `least-privilege`, `authn-or-authz` | 2026-11-12 |
| R2 | Authentication vs. authorization (Microsoft identity platform) | https://learn.microsoft.com/en-us/entra/identity-platform/authentication-vs-authorization | reading | MIT per `MicrosoftDocs/entra-docs`'s LICENSE (confirm) | 6 | `authn-or-authz` | 2026-11-12 |
| R3 | Basic policy construction in Cedar, then Cedar's "Authorization" page | https://docs.cedarpolicy.com/policies/syntax-policy.html ; https://docs.cedarpolicy.com/auth/authorization.html | reading | Apache-2.0 (`cedar-docs`) | 12 | `access-models`, `separation-of-duties` | 2026-11-12 |
| R4 | Policy evaluation logic (AWS IAM): the three "Evaluating ..." sections | https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html | reading | © Amazon Web Services | 5 | `cloud-policy-models` | 2026-11-12 |
| R5 | Security best practices in IAM (AWS): "Apply least-privilege permissions" to "Regularly review and remove unused ..." | https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html | reading | © Amazon Web Services | 5 | `least-privilege` | 2026-11-12 |
| R6 | What is Azure role-based access control (Azure RBAC)?: "How Azure RBAC works" to "How Azure RBAC determines if a user has access to a resource" | https://learn.microsoft.com/en-us/azure/role-based-access-control/overview | reading | CC BY 4.0 (`azure-docs`) | 9 | `cloud-policy-models` | 2026-11-12 |
| R7 | IAM overview (Google Cloud): allow policies, roles, the resource hierarchy, deny policies, conditions | https://docs.cloud.google.com/iam/docs/overview | reading | CC BY 4.0 (confirm footer in a browser) | 8 | `cloud-policy-models` | 2026-11-12 |
| R8 | Role recommendations overview (Google Cloud Policy Intelligence): optional | https://docs.cloud.google.com/policy-intelligence/docs/role-recommendations-overview | reading | CC BY 4.0 (confirm) | 6 | `least-privilege` | 2026-11-12 |
| R9 | Best practices for Azure RBAC: optional | https://learn.microsoft.com/en-us/azure/role-based-access-control/best-practices | reading | CC BY 4.0 | 5 | `least-privilege` | 2026-11-12 |
| R10 | Using AWS IAM Access Analyzer: optional, the capability list and pricing section | https://docs.aws.amazon.com/IAM/latest/UserGuide/what-is-access-analyzer.html | reading | © Amazon Web Services | 4 | `least-privilege` | 2026-11-12 |
| R11 | Guide to ABAC Definition and Considerations (NIST SP 800-162): reference only | https://csrc.nist.gov/pubs/sp/800/162/upd2/final | reading | US government work | reference | `access-models` | 2026-11-12 |

Assigned reading (R1 to R7): about 58 minutes; R8 to R11 are "More resources". No video is assigned: none was found that could be watched and checked in this pass, and the house rule is that a resource nobody opened isn't one.

## 7. Practice ladder

Every lab here is a **plain lab on the policy-lab base** (section 10): `runtime: lab`, `lab: { restart_trial: true }`, no systemd, no network. The learner edits files in nano under `~/` and runs `cedar` and the base's helpers. Checks run the base's `policycheck` library, which **makes up its requests at check time**: every combination of the rules' cases (role, action, same or different store, each side of every number in a rule, who handled the resource, MFA or not), with **new random names for every principal, resource and store in every run**, so a policy that names this run's people, or a store like `"north"`, can't be written in advance (tried: a policy with `resource.store == "north"` passed 1 run in 4 while store names came from a list of eight; with random names it fails every run). Each check covers one rule's cases, so a failure points at one skill, and prints the first three disagreements in words ("support staff, own store, refunding an order of exactly 100 that someone else handled, with MFA: the rules say allow, your policy says deny").

**Every amount boundary is its own case** (tried: with one case drawn at random from 100 and 101, a policy with `< 100` instead of `<= 100` passed every run in which 101 was drawn; with 100 and 101 both always present it fails every time).

### 7.1 `example-who-may-refund` (worked example, plain lab), skills `authn-or-authz`, `access-models`, `separation-of-duties`

The shop's order system. `~/shop/` holds `shop.cedarschema` (staff with a `store`, orders with `store`, `amount`, `handled_by`; actions `view`, `refund`, `export`; context `mfa`), `entities.json` (roles `support`, `supervisor`, `finance`, `warehouse`; eight staff; twelve orders), `session-alice.json` (what the identity provider said about Alice after she signed in: who she is, that she used a password and an authenticator app; no token format shown), and an empty `policies.cedar`. The base's helper **`ask PRINCIPAL ACTION RESOURCE [mfa=yes|no]`** builds the request from `entities.json`, runs `cedar authorize -v`, and prints `ALLOW` or `DENY` and the deciding policy ids.

Labelled steps:

1. **Authentication already happened.** `cat ~/shop/session-alice.json`. The app trusts the identity provider's word on *who*; the policy decides *what*. `ask alice view o-1001` prints `DENY` with no policy listed: default deny.
2. **A role.** Add `permit (principal in Role::"support", action == Action::"view", resource);`. Alice (support) may view; Wen (warehouse) may not. That's RBAC: the rule names a role, not a person.
3. **An attribute.** Narrow it with `when { principal.store == resource.store }`; `ask alice view o-1009` (another store's order) now denies. That's ABAC.
4. **Validate.** Misspell `store` as `stor`, run `cedar validate --schema shop.cedarschema --policies policies.cedar`, read the suggestion, fix it.
5. **A refund rule and a forbid.** Add the support refund `permit` (own store, amount up to 100), then `forbid (principal, action == Action::"refund", resource) when { resource.handled_by == principal };`. `ask alice refund o-1004` (an order Alice handled) denies, and `-v` names the forbid even though the permit matched too: forbid wins. That's separation of duties, decided per request.
6. **MFA as an input.** Add `forbid (principal, action == Action::"refund", resource) unless { context.mfa };` and compare `ask alice refund o-1003 mfa=yes` with `mfa=no`: an authentication fact used in an authorization rule.
7. **Run the check.** The page's `check` runs the same made-up requests the proofs use, for the four rules the example built.

Checks: `validates`, `view-rules`, `refund-rules`, `forbid-rules` (each over generated requests). Wrong fix: `no-forbid.sh` (steps 1 to 4 only). Minutes: 30.

### 7.2 Recall on authentication and authorization

| Id | Type | Scenario and right answer | Distractors to write in full |
| --- | --- | --- | --- |
| `mcq-401-or-403` | mcq | A signed-in contractor opens the payroll API and gets an error; an anonymous script calling the same URL gets a different one. Which code should each get? Right: the contractor `403`, the script `401` | both `401`; both `403`; contractor `401`, script `403` |
| `mcq-which-step` | mcq | Four events on a server: the SSH server checks Ben's key; `sudo` reads `/etc/sudoers` for Ben; nginx checks a client certificate (Module 3's mutual TLS); an app reads a role from Ben's session. Which two are authentication? Right: the SSH key check and the client certificate check | the key check and `sudoers`; `sudoers` and the role; the certificate and the role |
| `mcq-two-factors` | mcq | Which sign-in is multi-factor? Right: a password and a code from an authenticator app | a password and a security question; a password and a PIN; two passwords from different systems |
| `mcq-token-is-input` | mcq | The app has a valid session for Dina, who signed in with MFA an hour ago. Should every request still go through the policy? Right: yes, every request is decided on its own; the session only proves who she is | no, the sign-in already checked her access; only requests that change data; only once per hour |
| `est-decide-eight` | estimate | A short Cedar policy (three permits, one forbid, given in the prompt) and eight requests in a table. How many are allowed? Exactly. Answer 3; mistakes: 4 (the forbid ignored for one request), 5 (default deny forgotten: a request no permit covers counted as allowed). `skills: [access-models]` | |

### 7.3 `fill-warehouse-rules` (fill-in, plain lab), skills `access-models`, `separation-of-duties`

A different story from the build: the warehouse stock system (pickers, supervisors, auditors; bins with a `zone`; actions `pick`, `adjust`, `approve-adjustment`, `audit`). `~/warehouse/policies.cedar` has every rule written except four gaps, each a `...` in place of one word or expression, and the prompt says which rule each gap belongs to (Cedar refuses to parse a file with a gap, which the prompt says too):

1. pickers pick in their own zone: the gap is the attribute comparison in `when { ... }`;
2. supervisors adjust stock in any zone: the gap is the role in `principal in Role::"..."`;
3. no one approves an adjustment they made: the gap is the effect keyword (`forbid`);
4. auditors audit but change nothing: the gap is `unless` or `when` on a forbid that ties `adjust` and `approve-adjustment` to "not an auditor".

Checks: `validates`; `pick-rules`, `adjust-rules`, `approval-rules`, `auditor-rules`, `default-deny` (generated requests). A check description never holds the word a gap asks for. Wrong fixes: `permit-not-forbid.sh` (gap 3 filled with `permit`: self-approvals allowed), `zone-hard-coded.sh` (`principal.zone == "A"`), `auditor-may-adjust.sh` (gap 4 inverted), `everyone-adjusts.sh` (gap 2 widened to `principal`, which leaves the scope unconstrained). Minutes: 25.

### 7.4 Recall on access models

| Id | Type | Scenario and right answer | Distractors |
| --- | --- | --- | --- |
| `mcq-forbid-wins` | mcq | A new `permit` lets managers approve any expense; an older `forbid` stops anyone approving their own. A manager submits and approves her own expense. Right: denied, because a satisfied `forbid` overrides any `permit` | allowed, because the newer policy wins; allowed, because `permit` and `forbid` cancel out to the default; denied only if the forbid is listed first |
| `mcq-no-rule-matches` | mcq | A request for an action no policy mentions. Right: denied (default deny) | allowed, because nothing forbids it; an error that blocks the app; allowed for principals in any role |
| `mcq-rbac-or-abac` | mcq | "Each regional manager sees the sales of their own region; there are 14 regions." Which model needs one rule? Right: ABAC (compare the manager's region with the sale's) | RBAC with one role per region; RBAC with a single "regional manager" role and nothing else; ReBAC, because regions are relationships |
| `mcq-typo-silent` | mcq | In a policy language without a schema, a rule reads a misspelt attribute. Right: the rule never matches and nothing warns; a schema check catches it | the engine refuses to start; every request is allowed; the misspelt attribute is treated as empty, so the rule always matches |
| `est-role-explosion` | estimate | A company wants "staff see their own department's data in their own country", with 5 departments, 9 countries and 2 seniority levels that see different fields. How many roles does pure RBAC need? Exactly. Answer 90; mistakes 16 (5 + 9 + 2), 45 (levels forgotten) | |
| `est-decide-six` | estimate | Second "how many allowed" item: a policy with `unless` and a schema-valid but always-false condition (`principal.store == resource.store` on actions whose resources have the same store only half the time); six requests. Answer 2; mistakes 3, 4 | |
| `est-decide-seven` | estimate | Third, with role hierarchy through `in` (a `supervisor` group inside `support`): seven requests. Answer 4; mistakes 2 (hierarchy ignored), 5 | |

### 7.5 Recall on least privilege (calculation skill)

| Id | Type | Scenario and right answer |
| --- | --- | --- |
| `unused-from-log` | predict_shell | Files `granted.txt` (one action a line, 12 lines) and `log.txt` (90 days of `date principal action resource` lines for the `reports` service). Command: `awk '$2=="reports" {print $3}' log.txt \| sort -u > used.txt; comm -23 <(sort granted.txt) used.txt`. Output: the seven granted actions never used. Pinned in Git Bash and in CI's bash; `comm` and process substitution work in both (the writer runs it in both). `skills: [least-privilege]` |
| `used-counts` | predict_shell | The same log, `awk '$2=="reports" {print $3}' log.txt \| sort \| uniq -c \| sort -rn \| head -3`: the three most-used actions with counts. `skills: [least-privilege]` |
| `est-unused-share` | estimate | A role grants 48 actions; the analyzer saw 9 of them used in its window. What percentage is unused? Within 1 (absolute). Answer 81.25; mistakes 18.75 (the used share), 39 (a count, not a percentage) |
| `est-window-to-see` | estimate | A data-retention job runs once every 100 days. AWS's policy generation looks back at most 90 days; Google's project-level role recommendations can look back 30, 60 or 90. What is the shortest look-back, in days, that is sure to include at least one run? Exactly. Answer 100; mistake 90 ("the longest window offered"), 50 |
| `est-analyzer-cost` | estimate | An AWS account has 340 IAM roles, of which 40 are service-linked, and 25 IAM users. One unused access analyzer at $0.20 per role or user analyzed per month (prices_as_of 2026-11-12, prices_source the pricing page). Monthly cost in dollars? Exactly. Answer 65 (service-linked roles aren't analyzed); mistakes 73 (service-linked counted), 60 (users forgotten) |
| `est-unused-count` | estimate | A service account holds Google's basic Editor role. The recommender's insight says it used 14 of the role's permissions; the prompt gives the role's permission count as stated on the day of writing (the writer reads it from Google's role reference and pins the number). How many permissions would a custom role drop? Exactly. (The writer may replace this with a constructed number if the reference doesn't state a count) |
| `mcq-managed-role` | mcq | Why isn't an AWS managed policy least privilege for your job? Right: it's written for every AWS customer's version of the job, so it grants more than yours needs. Distractors: AWS changes managed policies without notice so they can't be trusted; managed policies can't be scoped to resources at all; managed policies don't support deny statements |
| `mcq-loop-order` | mcq | Which order is the least-privilege loop? Right: observe usage over a window, cut to a custom role, watch for denials, repeat. Distractors: cut first then observe; grant admin until complaints stop; copy a colleague's role then observe |

### 7.6 `write-tighten-service-roles` (write, plain lab), skills `least-privilege`, `separation-of-duties`

The least-privilege loop, with a local stand-in for the clouds' analyzers.

- `~/ops/policies.cedar` today gives three services broad access: `Service::"reports"` may do every action on every resource (`permit (principal == Service::"reports", action, resource);`), as may `Service::"deployer"` and `Service::"backup"`.
- `~/ops/jobs.txt` says in plain words what each service is for: reports reads orders and writes report files, and **once a quarter** exports a summary to finance; the deployer creates and updates releases but must never approve its own change; backup reads every store's data and writes to the backup vault, never deletes.
- `/var/log/ops/access.log`: 120 days of requests (constructed, written by `seed.sh` from a loop counter so the checks can compute the truth), including exactly one quarterly export, 104 days ago.
- The base's **`access-review [--days N] PRINCIPAL`** (scenery, an analyzer stand-in labelled "modelled on IAM Access Analyzer's unused access findings and Google's role recommendations") evaluates the current policy over the catalogue of actions and resource types (`~/ops/catalogue.txt`) with `cedar`, compares it with the log over the last N days (default 90), and prints `granted and used`, `granted, never used in N days`.

The task: replace the three broad policies with one role per service (`Role::"report-writer"` and so on, each service `in` its role in `~/ops/entities.json`), each with only what its job needs, and keep the deployer's separation of duties with a `forbid`. The prompt says: run `access-review` with `--days 90`, then read `jobs.txt`, and reconcile the two; anything the job needs stays, whether the log's window saw it or not.

Checks (generated requests, new resource names every run):

- `jobs-still-work`: every kind of request in the log (action and resource type, with new resource ids) is allowed for its service, **including the quarterly export** (which `--days 90` doesn't show).
- `nothing-else`: for each service, every other action and resource type in the catalogue is denied (made up from the catalogue, so a policy that lists only the log's resource ids fails `jobs-still-work`, and one that keeps `action` unconstrained fails here).
- `no-self-approval`: the deployer may not approve a change it made; another principal with the approver role may.
- `own-principal-only`: a made-up new service with no role is denied everything (no `permit (principal, ...)` left behind).
- `validates`.

Wrong fixes: `window-90.sh` (built from the 90-day review only: quarterly export missing), `ids-from-log.sh` (resource ids copied from the log), `kept-wildcard.sh` (`action` left open for reports), `backup-deletes.sh`, `no-sod-forbid.sh`, `shared-role.sh` (all three services in one role with the union of their needs), `forgot-backup.sh`. Minutes: 40.

### 7.7 Recall on separation of duties

| Id | Type | Scenario and right answer |
| --- | --- | --- |
| `mcq-sod-static-dynamic` | mcq | "Nobody approves a payment they requested" when everyone may both request and approve. Static or dynamic? Right: dynamic, checked per request (a rule comparing approver and requester). Distractors: static, by never giving one person both roles; neither, it's least privilege; static, because it's written in a policy file |
| `mcq-sod-which-pair` | mcq | Which pair most needs separating? Right: changing the payroll system and auditing the payroll system's logs. Distractors: reading orders and reading invoices; deploying the website and reading its logs; creating a ticket and commenting on it |
| `mcq-temporary-exception` | mcq | During a busy week a manager is given both "request" and "approve" for payments "temporarily". What's the risk worth naming? Right: one person can now move money alone, and temporary grants tend to stay. Distractors: the approval workflow will run slower; the manager's MFA stops applying; the audit log can't record who approved |
| `est-sod-pairs` | estimate | A finance system has 12 roles; to find conflicts, every pair of roles is reviewed once. How many pairs? Exactly. Answer 66; mistakes 132 (each pair counted twice), 144 |

### 7.8 Recall on the clouds' policy models

| Id | Type | Scenario and right answer |
| --- | --- | --- |
| `mcq-aws-explicit-deny` | mcq | An IAM role's policy allows `s3:GetObject` on a bucket; the bucket policy denies that role. Right: denied, an explicit deny in either overrides the allow. Distractors: allowed, identity policies win inside the account; allowed, the more specific statement wins; denied only if the role is in another account |
| `mcq-aws-scp-grants-nothing` | mcq | An SCP allows `ec2:*` for an account; a new IAM user there has no policies. Can they start an instance? Right: no, SCPs limit but grant nothing. Distractors: yes, the SCP grants it to everyone in the account; yes, until a permissions boundary is set; only from the console |
| `mcq-azure-additive` | mcq | Contributor at the subscription, Reader on one resource group. What can she do in that group? Right: everything Contributor allows, because Azure RBAC adds assignments up. Distractors: only read, the narrower scope wins; only read, Reader is more specific; nothing, conflicting assignments cancel |
| `mcq-azure-deny-assignment` | mcq | What overrides an Azure role assignment? Right: a deny assignment that applies to the principal and scope. Distractors: a Reader assignment at a lower scope; removing the principal from one of its groups only; a resource lock |
| `mcq-gcp-inherit` | mcq | Viewer at the folder, Editor on one project in it. On that project she is: Right: an editor (the effective policy is the union). Distractors: a viewer, the folder wins; an editor only if the folder allows inheritance; a viewer, the narrower grant is ignored |
| `mcq-gcp-deny-first` | mcq | A deny policy at the organization denies deleting buckets; the project grants Storage Admin. Right: deletion is denied; deny policies are checked before allow policies. Distractors: allowed, the project is more specific; allowed for Owners only; denied only for service accounts |
| `mcq-analyzer-by-cloud` | mcq | Which cloud's usage-based recommendations for its basic roles come at no charge? Right: Google Cloud (role recommendations for basic roles). Distractors: AWS (unused access analysis is free); Azure (Entra Permissions Management is included in P1); all three, for any role |
| `mcq-jit` | mcq | What does "eligible" mean in PIM, and what's its point? Right: the person may activate the role for a limited time when needed, so the access isn't standing. Distractors: the person has the role permanently but can't use it without approval each request; the role is assigned to a group the person may join; the role is visible but grants nothing until a review |

### 7.9 Ladder order for `topic.yaml`, and which proof needs what

`example-who-may-refund`, `mcq-401-or-403`, `mcq-which-step`, `mcq-two-factors`, `est-decide-eight`, `mcq-forbid-wins`, `mcq-no-rule-matches`, `fill-warehouse-rules`, `mcq-rbac-or-abac`, `est-role-explosion`, `unused-from-log`, `est-unused-share`, `est-window-to-see`, `est-analyzer-cost`, `mcq-loop-order`, `write-tighten-service-roles`, `mcq-sod-static-dynamic`, `est-sod-pairs`, `mcq-aws-explicit-deny`, `mcq-azure-additive`, `mcq-gcp-deny-first`, `mcq-analyzer-by-cloud`: 22 entries, of which 17 recall. The rest are review-only (section 9).

| Skill | Practised in | Needed by |
| --- | --- | --- |
| `authn-or-authz` | example steps 1 and 6, four recall items | build (the MFA rule), explain |
| `access-models` | example, fill-in, four recall items | build, debug |
| `least-privilege` | write lab, five recall items | build (default deny, nothing more), explain |
| `separation-of-duties` | example step 5, fill-in gap 3, write lab, two recall items | build, debug |
| `cloud-policy-models` | four recall items in the ladder, four more in review | explain |

**Multiple choice measurement.** 16 mcq items in the topic (12 in the ladder, 4 review-only). The writer writes every choice in full, measures right-answer length against the longest wrong one (aim 1.3, never over 1.5), and keeps the right answer the longest in no more than a third of them (the validator's line is half). `mcq-which-step` and `mcq-analyzer-by-cloud` have list-like answers: write all four choices as pairs of the same shape.

## 8. Proofs

### 8.1 Build: `build-clinic-records` (plain lab, 50 minutes), skills: `access-models`, `separation-of-duties`, `least-privilege`, `authn-or-authz`

A clinic's records system, from a blank `~/clinic/policies.cedar`. Given: `clinic.cedarschema` (staff with a `ward` and roles; patients with a `ward`; records of three kinds, `Chart`, `Note`, `Invoice`; prescriptions with `written_by`; actions `view`, `add-note`, `edit`, `prescribe`, `dispense`, `bill`; context `mfa` and `on_shift`), `entities.json` for a small clinic, and `ask`. The prompt's rules:

1. Doctors and nurses view the charts and notes of patients on their own ward.
2. Doctors edit charts; nurses only add notes.
3. Billing staff see invoices of any ward and nothing clinical.
4. Doctors prescribe; pharmacists dispense; **nobody dispenses a prescription they wrote** (a doctor who is also registered as a pharmacist exists in the data).
5. **Nobody opens their own record** through the system (a nurse who is also a patient exists).
6. Every `edit`, `prescribe` and `dispense` needs a session that used MFA, and staff act only while `on_shift`.
7. Everything else is denied.

Checks (each over its rule's generated cases, with new names every run; a clinic member with two roles, and one who is also a patient, are made up in every run):

| Check | Tests | Skill |
| --- | --- | --- |
| `validates` | `cedar validate` against the schema passes | `access-models` |
| `ward-viewing` | rule 1, both wards, both roles | `access-models` |
| `edit-or-note` | rule 2 | `access-models` |
| `billing-only-invoices` | rule 3 | `least-privilege` |
| `prescribe-dispense` | rule 4, including the two-role person | `separation-of-duties` |
| `not-your-own-record` | rule 5, including the nurse-patient | `separation-of-duties` |
| `mfa-and-shift` | rule 6, every combination of `mfa` and `on_shift` | `authn-or-authz` |
| `default-deny` | made-up actions on made-up record kinds from the schema, and a principal with no role | `least-privilege` |

Shortcuts the checks must reject (each a `wrong/*.sh`): `allow-all.sh`; `ward-hard-coded.sh` (`resource.ward == "B"`); `nurse-edits.sh`; `billing-sees-charts.sh`; `self-dispense.sh` (rule 4 as a role check only: fails for the two-role person); `own-record-open.sh`; `mfa-only-on-edit.sh` (rule 6 for `edit` alone); `shift-ignored.sh`; `forbid-everything-clinical.sh` (a blanket forbid that makes ward viewing fail: availability is checked as well as denial). Nine wrong fixes; the reference solution is about 40 lines of Cedar.

**Not prototyped as this lab.** Its mechanism is the prototype's (`policycheck` over `cedar run-tests`), which kept its promise on 10 policies: the reference passed 384 cases and each of 8 wrong policies failed in every one of 3 runs, in 0.8 s a run (tried). The writer builds this lab's case generator from the base's library and runs the contract before writing the lesson.

### 8.2 Debug: `debug-hr-portal` (plain lab, 40 minutes), skills: `access-models`, `separation-of-duties`, `least-privilege`

The HR portal's policy set (`~/hr/policies.cedar`, about 50 lines, with a schema and entities). The prompt describes what the portal is for and its rules in full: employees see their own salary; managers see the salaries of their direct reports; HR partners see every salary in the departments they support; raises are requested by managers and approved by HR partners, **never by the person who requested them**; auditors read the payroll log and change nothing. **Symptom:** "An internal audit found three ways the policies don't match these rules. Some people can see or do more than the rules allow, and one group says it can't do part of its job." Three faults. Rules of the fix: change only `policies.cedar`; don't delete a `forbid` or add one that blocks a whole role; everything the rules allow must still be allowed.

The three faults (the prompt names none of them):

1. **An unconstrained scope.** A permit meant for managers reads `permit (principal, action == Action::"viewSalary", resource) when { resource.department == principal.department };`: everyone sees their department colleagues' salaries.
2. **An inverted forbid.** The separation-of-duties rule reads `forbid (principal, action == Action::"approveRaise", resource) unless { resource.requested_by == principal };`: it blocks every approval except self-approval. HR partners report that they can't approve anyone's raise; a manager who is also an HR partner can approve his own.
3. **A widened action list.** The auditors' permit reads `action in [Action::"readPayrollLog", Action::"editPayrollLog"]`: auditors can change what they audit.

Checks (generated requests): `own-salary`, `manager-reports`, `hr-partner-departments`, `raise-approval` (another's request allowed, own refused), `auditors-read-only`, `nothing-more` (made-up principals in each role against every action), `validates`. Descriptions state end states ("HR partners can approve raises requested by others, and nobody can approve their own"). Checks are listed on the page only after a first try.

Wrong fixes: `delete-forbid.sh` (fault 2 "fixed" by deleting the forbid), `forbid-all-approvals.sh`, `managers-see-nothing.sh` (fault 1 fixed by deleting the permit: managers lose their reports), `auditors-removed.sh` (fault 3 fixed by deleting the auditor permit), `two-of-three.sh`, `hard-coded-names.sh` (faults "fixed" for the names in `entities.json`: fails on made-up principals). Six wrong fixes.

### 8.3 Explain

**Prompt (draft):** "A colleague says: 'We've got single sign-on with MFA now, so the app doesn't need its own access rules, and anyway giving the support team admin is simpler for now.' Explain, in your own words: the difference between authenticating someone and authorizing what they do, and where each happens; why every request still needs a decision; how you'd set up the support team's access with least privilege, as a process and not a one-off, and what the clouds' tools add (and miss); what separation of duties would forbid here and how you'd enforce it; and how AWS, Azure and Google Cloud each decide when two rules disagree."

**Rubric:**

- `authn-vs-authz` (required): authentication proves who (factors; MFA is two different kinds) and happens at the identity provider; authorization decides each request's action on a resource, in the app or a policy engine; a session or token is the result of the first and only an input to the second; `401` against `403` named or implied.
- `every-request` (required): access is checked on every request, default deny; MFA at sign-in doesn't stop a signed-in person doing what they shouldn't.
- `least-privilege-loop` (required): start from what the job needs, observe actual use over a window long enough for rare tasks, cut to a custom role at the narrowest scope, watch denials, repeat; analyzers observe (AWS Access Analyzer, Google's role recommender) but only within their window and can't know the job's purpose.
- `separation-of-duties` (required): a concrete pair of duties that mustn't meet, enforced statically (roles) or dynamically (a per-request rule), and why a deny/forbid holds against later broad grants.
- `clouds-differ` (required): explicit deny wins on AWS (union within the intersection of SCPs and boundaries), Azure adds assignments up and checks deny assignments first, Google adds up inherited bindings and checks deny policies first.
- `models` (optional): RBAC against ABAC (role explosion), policy as code (reviewed, tested, versioned).

**Model answer:** about 300 words covering each required row (the writer drafts it, as Module 3 did).

## 9. Review pool

At least two come-back questions per skill; the estimates in it use new numbers.

| Skill | Review items |
| --- | --- |
| `authn-or-authz` | `mcq-401-or-403`, `mcq-which-step`, `mcq-token-is-input` (review-only), `mcq-two-factors` |
| `access-models` | `mcq-forbid-wins`, `mcq-typo-silent` (review-only), `est-decide-six` (review-only), `est-decide-seven` (review-only), `mcq-rbac-or-abac` |
| `least-privilege` | `est-unused-share`, `est-window-to-see`, `est-analyzer-cost`, `est-unused-count` (review-only), `used-counts` (review-only), `mcq-managed-role` (review-only), `unused-from-log` |
| `separation-of-duties` | `mcq-sod-static-dynamic`, `mcq-sod-which-pair` (review-only), `mcq-temporary-exception` (review-only), `est-sod-pairs` |
| `cloud-policy-models` | `mcq-aws-explicit-deny`, `mcq-aws-scp-grants-nothing` (review-only), `mcq-azure-additive`, `mcq-azure-deny-assignment` (review-only), `mcq-gcp-inherit` (review-only), `mcq-gcp-deny-first`, `mcq-jit` (review-only) |

Calculation skills and their estimates: `least-privilege` 4 (`est-unused-share`, `est-window-to-see`, `est-analyzer-cost`, `est-unused-count`), `access-models` 4 (`est-role-explosion`, `est-decide-eight`, `est-decide-six`, `est-decide-seven`). No proof reuses an item's numbers. The six-month core is mostly judgement on real policies and real numbers: which rule decides, which cloud adds up and which denies first, how long a window must be.

## 10. Platform work needed first

| # | What | Smallest version | Blocks |
| --- | --- | --- | --- |
| A1 | **The policy-lab base**, `content/lab-bases/policy/` | A plain base (no systemd), `FROM ubuntu:24.04`: Module 3's plain `RUN` line byte for byte (`sudo nano less python3 ipcalc sipcalc openssl curl`, the learner user), then one `RUN` that installs `ca-certificates xz-utils` and the Cedar CLI 4.14.0 from its GitHub release, checked by sha256 in the same `RUN` (the recipe is the prototype's `policy/Dockerfile`, with the binary installed as `/usr/local/bin/cedar`). Helpers: `ask` (a request from an entities file, `cedar authorize -v`, `ALLOW`/`DENY` and the deciding ids), `access-review` (section 7.6), `ca-whatif` (topic 41's), and `checklib.py`, the check library: a case generator over named rule dimensions with random names, the `cedar run-tests` driver (with `"reason": []` and `"num_errors": 0`), and plain-words reporting of the first three disagreements. A README in the shape of the network-lab base's. `labcheck` already builds a base a lab names (`FROM lab-base-policy`), the validator already checks the base exists, and `labs.yml` already watches `content/lab-bases/**` | every topic-40 lab; topic 41's write lab |
| A2 | `checklib.py`'s own tests in `tools/tests/` | The generator always includes both sides of every numeric boundary and never repeats a name in a run; the driver reports a decision mismatch and ignores reasons; a wrong-policy table like the prototype's 8 policies | A1 |

No app work. No new item types: everything is `mcq`, `estimate`, `predict_shell` and labs. Nothing to change in `labcheck`.

## 11. Cost and time

**Money: none.** Every lab is local. No real-cloud lab: the clouds' analyzers are taught from their documentation, priced in estimate items, and used for real in Module 10 (`csa.iam.least-privilege`, `csa.iam.troubleshooting`), where IAM Access Analyzer's free policy generation fits AWS's free use. The unused access analyzer is not free ($0.20 per role or user a month), so a later lab that uses it is priced then.

**Learner time.** Lesson 16, assigned reading 58, 17 ladder recall items at 1.5 = 26, worked example 30, fill-in 25, write 40, build 50, debug 40, explain 20: **about 305 minutes**. To bring it to 290, move R7 (Google's overview, 8) behind the lesson's own table and make it optional, and move `mcq-analyzer-by-cloud` and `mcq-gcp-deny-first` to review-only. Recommended `estimated_minutes: 290`.

**CI time.** Plain labs on the policy base: a container starts in about a second and a check run takes about a second (tried: 384 generated cases through `cedar run-tests` in 0.8 s). Contracts: example 4 runs (pristine, solution, restart trial, one wrong fix), fill-in 7, write 10, build 12, debug 9: 42 runs at about 5 s each with the restart's few seconds, **about 4 minutes** of container time for the topic, plus one build of the base per CI shard (about 20 s for the Cedar layer, measured as part of a 13 s download and unpack on the owner's PC). The base image was 316 MB as Docker Desktop reported it (Ubuntu with Python, curl, the two binaries; without OPA's 64 MB, about 250 MB).

**Docker Desktop against CI.** Nothing here touches the kernel, systemd or the network: a plain container with a binary and Python. The one difference to expect is speed, which no check depends on.

## 12. Open questions, each with a recommendation

1. **Cedar or OPA's Rego for the policy-as-code labs?** Both are Apache-2.0, run offline as one binary and evaluate in under a second (tried). **Recommendation: Cedar.** It is the better teacher for a learner without Python: its words are the lesson's (`permit`, `forbid`, `principal`, `action`, `resource`, `when`, `unless`), its decision rule (default deny, forbid wins) is the one every cloud uses, and its schema turns typos into errors with a suggestion, where Rego accepted a misspelt attribute silently (tried). Rego is a general query language whose rule bodies, `some`, `with` and undefined-versus-false take a lesson of their own; Module 18's `csa.iac.policy` (OPA and Conftest) and Module 19's Gatekeeper teach it where it dominates. This topic shows one rule in Rego beside Cedar so the learner sees that policy as code is a family. Cedar is a download from GitHub, not Ubuntu's archive: pinned by version and sha256, as step-ca was in Module 3.
2. **One policy-lab base, or helpers copied into each lab?** **Recommendation: a base** (A1): five topic-40 labs and topic 41's write lab share `ask`, `checklib.py`, `access-review` and `ca-whatif`, and later Module 10 drills can use it. It costs one small folder and nothing in `labcheck`.
3. **A real-cloud lab here?** **Recommendation: no.** The model and the sums are what this topic owns; Module 10 builds on each cloud's real IAM, where AWS's free policy generation and IAM itself fit the free tier and Azure's RBAC is free in the owner's subscription.
4. **Should topic 40 teach MFA methods?** **Recommendation: only the factor kinds and that MFA is an input to authorization.** Which methods resist phishing is topic 41's whole first skill; teaching it twice would split one idea across two topics.
5. **Azure's analyzer gap.** Microsoft's cross-cloud analyzer is retired (F23) and its features moved into a paid Defender plan. **Recommendation:** say so plainly in the lesson's table rather than leave the Azure cell empty, and re-read Microsoft's two posts before quoting dates (the facts list marks them as read from search summaries).

**Look up again on the day of writing:** the Cedar CLI's newest release older than two weeks and its sha256; IAM Access Analyzer's prices; Google's role-recommendation tiers and the basic Editor role's permission count (for `est-unused-count`); the Permissions Management dates (F23); each Microsoft and Google page's licence in its own repository or footer.
