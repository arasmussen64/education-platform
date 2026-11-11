# Writing brief: Windows Server and Active Directory (`csa.hw.windows-ad`, topic 19)

Written 2026-11-11 for whoever writes the topic. Every "read on" date below is 2026-11-11 unless it says otherwise. The prototype this brief leans on is in `proto-windows-ad/` beside this file; section 16 says what is in it and what happened when it ran.

## 1. The short version

- **Two layers.** A free one (a Samba Active Directory domain controller and a Linux member in one lab container, checked by `tools/labcheck.py`) and a paid one (two Windows Server VMs and one Linux VM in the learner's Azure subscription, about $0.60 for a three-hour sitting).
- **The topic can be `ready` on the free layer alone.** Its worked example, fill-in, write, build and debug are all local labs. Two of them (the build and the debug) were built in full and passed the repository's real checker on this machine: pristine fails, the solution passes, every wrong fix fails the check it was written for.
- **The Azure lab is an extra until the owner has run it once.** Nothing in it has been executed. Every command's arguments were checked against the CLI's own help, every price came from Azure's public price API, and the list of what is still unproven is in section 12.6.
- **It needs no platform work for the free layer.** The Azure extra needs a small cloud mode for the checker (section 14).
- **Honest size: about six hours**, not the outline's 240 minutes. Section 15 recommends splitting it in two; the brief works either way.

## 2. What the learner will be able to do

1. Say what an Active Directory domain is made of (a directory of accounts, DNS names that point at its controllers, Kerberos for proving who you are, Group Policy for settings), and read a directory entry's name.
2. Find a domain's controllers the way a member does, through DNS SRV records, and fix a member that is asking a resolver which has never heard of the domain.
3. Read Kerberos evidence: tell the first ticket from a service ticket in `klist`, name what each `kinit` failure means, and say why five minutes of clock drift stops logins.
4. Join a Linux server to a domain, say what the join created, limit who may log in to it, and repair a member whose own account has gone stale. Say what the same steps are on Windows.
5. Predict which Group Policy objects reach a given user or computer, from where they are linked and what is blocked or enforced.
6. Explain how Entra ID differs from AD DS, how the two are connected, and which of them (or which managed domain service) a given workload needs on each cloud.

**The six-month core.** What should still be there half a year later, and what the review pool is built to keep:

- **A diagnosis order for "domain logins are broken":** names first (does the SRV record answer from this machine?), then time, then the machine's own account, then who is permitted. Four questions, each with one command.
- **Reading `klist`** and the four `kinit` errors on sight.
- **The trust rule:** the domain that holds the resource trusts the domain that holds the accounts; access flows the opposite way to the trust.
- **Last writer wins** for Group Policy (local, site, domain, OU; the closest OU last), with "enforced beats block".
- **One paragraph on Entra ID against AD DS:** web sign-in tokens over HTTPS and a flat tenant, against Kerberos and LDAP inside a network with OUs and Group Policy; and the judgement that an application which speaks Kerberos or LDAP still needs domain services somewhere.

## 3. Prerequisites and assumed knowledge

### 3.1 Real prerequisites

Replace the outline's `csa.m1.checkpoint` with:

| Topic | Why this topic needs it |
| --- | --- |
| `csa.linux.shell` | Every recall item reads command output with `grep`, `awk`, `cut` and `wc`. |
| `csa.linux.permissions` | Local users and groups, `sudo`, and logging in over SSH: a domain account is taught as "the same thing, kept somewhere else". |
| `csa.linux.services` | `systemctl` and `journalctl`: the labs restart `dnsmasq` and `sssd` and read SSSD's and `sshd`'s journal. |
| `csa.linux.net-tools` | `dig`, `nc`, `ss`, and a second machine made from a network namespace (the "office"); dc1 in these labs is the same idea. |
| `csa.linux.hardening` | `AllowGroups` in `sshd`, and the rule that a fix must not weaken the server. The debug uses both. |

`csa.hw.hypervisors` is needed only by the Azure extra (what a VM is). List it if the extra is linked from the lesson.

### 3.2 Terms this topic must define itself

None of these has been taught by the time a learner reaches topic 19. Module 3 (DNS in depth) and Module 4 (authentication, cryptography) come later on the module map, so nothing may be borrowed from them.

| Term | Where it's needed | One-line definition the lesson must give |
| --- | --- | --- |
| directory, LDAP | whole topic | A directory is a database of accounts, groups and machines that many systems read; LDAP is the protocol for asking it questions. |
| domain, domain controller (DC) | whole topic | A domain is one such directory with a DNS name; a DC is a server that holds a copy and answers logins. |
| forest, tree, global catalog | structure, trusts | One or more domains that share a schema and trust each other; the catalog is a searchable index of all of them. |
| organisational unit (OU), distinguished name (DN) | structure, policy | A folder inside the domain; the DN is an entry's full path, read right to left. |
| authentication against authorisation | join, debug | Proving who you are, against being allowed to do the thing. Module 4 teaches it properly; this topic needs the two words. |
| SRV record, forwarder, reverse lookup (PTR) | discovery | Module 1 taught `dig` and address records only. SRV: "which host and port offers this service for this domain". |
| FQDN | join | A machine's full name, `lab.ad.shop.test`. |
| Kerberos, KDC, realm, principal, ticket, TGT, service ticket, SPN, keytab | Kerberos, join | See the picture in section 5.2. Realm is the domain's name in capitals. |
| "a key derived from your password" | Kerberos | Enough to say: both you and the DC can compute it, nobody else can, and the password itself never crosses the network. |
| clock skew, time synchronisation | Kerberos | Module 1 didn't teach `chrony` or NTP. One sentence: machines keep their clocks agreed by asking a time server. |
| computer account, machine password | join | A domain account for the machine itself, with a long random password the machine keeps in a file. |
| SID, UPN, NetBIOS name | reading output | Only as labels on real output: `S-1-5-21-…`, `alice@ad.shop.test`, `SHOP\alice`. |
| Group Policy object (GPO), link, SYSVOL | policy | A named bundle of settings; it does nothing until linked to a site, domain or OU; its files live on a share every DC carries. |
| trust, direction, transitive | trusts | One domain accepting another's logins. |
| Entra ID, tenant, token, OAuth / OpenID Connect / SAML | comparison | "Web sign-in protocols over HTTPS that hand an application a signed token." Module 10 teaches them. |
| MDM (Intune) | comparison | Settings pushed to devices over the internet by a management service, where Group Policy needs the domain's network. |
| RDP, PowerShell | Azure extra only | Module 6 teaches PowerShell. The extra gives each command whole and says what it does. |

**Never assume the owner's work history** covers any of this (memory: no assumed strengths). The lesson explains a domain as if it were new.

## 4. Skills

| Skill | What it covers |
| --- | --- |
| `directory-structure` | What a domain holds and how it's arranged: domain, forest, domain controller, OUs, users, groups and computers; reading a DN and an LDAP query's result; trusts between domains, their direction and whether they pass along. |
| `dc-discovery` | How a member finds a domain controller: the domain's SRV records, the domain's own DNS, a forwarder for its zone, and what breaks when a member asks a resolver that doesn't know the domain. |
| `kerberos-tickets` | The first ticket and service tickets, principals and service names, `kinit` and `klist`, the five-minute clock rule, and reading the common failures. |
| `domain-join` | What joining creates (a computer account, a machine password in a keytab, service names), joining Linux with `realm` and SSSD and Windows with `Add-Computer`, who may log in to a member, and repairing a member whose machine account no longer matches. |
| `group-policy` | What a GPO is and where it lives, linking, the order they apply in, block and enforce, refresh times, and predicting which GPOs reach a user or computer. |
| `entra-vs-adds` | How Entra ID differs from AD DS in protocols, structure and device management; how they are connected; managed domain services on the three clouds; choosing for a workload. |

Every skill has at least four questions that can come back (section 11) and is practised before a proof asks for it (section 9.4).

## 5. Lesson plan

### 5.1 Order of ideas

Each idea is tied to the resource section that teaches it (numbers are rows of the table in section 7). "Lesson" means the lesson's own words have to do the work.

| # | Idea | Taught by |
| --- | --- | --- |
| 1 | Why this exists: one account per person that every server accepts, instead of an `/etc/passwd` on each (the learner's Module 1 picture). | Lesson |
| 2 | What a domain holds: users, groups, computers, OUs; the DC; the forest. | R1 units 2 to 5 (main resource), R2 |
| 3 | Names: reading `CN=Alice Ng,OU=Engineering,OU=Staff,DC=ad,DC=shop,DC=test` right to left. | Lesson (picture B below), R1 unit 6 |
| 4 | How a member finds a DC: SRV records in the domain's own DNS. Why the member must ask a resolver that knows the domain. | R3 first half, lesson (picture A) |
| 5 | Kerberos: prove who you are once, get a ticket, trade it for tickets to services. Five minutes of clock tolerance; ten-hour tickets. | R4, lesson (picture C); R5 as the optional deep read |
| 6 | Joining: the machine gets an account and a secret of its own. Logging in to a member is two questions: is the password right (the DC answers), and is this person allowed here (the member answers). | R6, lesson (picture D) |
| 7 | When the machine's secret stops matching: the member is cut off although users' passwords still work; the fix is to join again. | Lesson (no resource explains this for a beginner) |
| 8 | Group Policy: an object, a link, an order (local, site, domain, OU), block and enforce, a refresh every 90 minutes plus up to 30. | R7 |
| 9 | Trusts: direction and whether they pass along. | R8 first third, lesson (one picture: "the house with the files gives the other house's ID office a key") |
| 10 | Entra ID is not AD DS in the cloud: different protocols, no OUs, no Group Policy; how the two are synchronised; Entra-joined, hybrid-joined and domain-joined devices. | R9, R10 |
| 11 | When a cloud workload still needs a domain: DCs on VMs, or a managed domain. The three clouds' offerings and what each costs to think about. | R10, R11, R12, R13, R14 |
| 12 | What this lab's DC is and isn't: Samba speaks the same protocols, and AWS sells a directory built on it, but it isn't Windows. | Lesson, R13, R15 |

### 5.2 Pictures in words the lesson must supply

No resource found does these well for someone who has never seen a domain.

- **A. The domain's phone listing.** A member that knows only the name `ad.shop.test` asks DNS one question, "who offers LDAP for this domain?", and gets back a line like `0 100 389 dc1.ad.shop.test.`: priority, weight, port, host. Show the real line from the lab (section 16.5), then show the same question sent to a resolver that has never heard of the domain: `status: NXDOMAIN`. Everything a member does starts with this lookup, which is why "check DNS first" is the first rule.
- **B. An address read backwards.** A DN is a postal address with the country first: `DC=test`, `DC=shop`, `DC=ad` is the domain; `OU=Staff`, `OU=Engineering` are folders inside it; `CN=Alice Ng` is the entry. Policy follows the folders; permissions follow groups. That one sentence heads off the commonest confusion (an OU is not a group).
- **C. The ticket booth.** At the start of the day you show your password once at the booth (the KDC, which runs on every DC) and get a day pass, the ticket-granting ticket. For each ride (a file server, LDAP, SSH to a member) you show the day pass at the booth and get a ticket for that ride only, stamped with the ride's name. The ride never sees your password and never phones the booth; it can read the ticket because the booth sealed it with the ride's own secret. Every ticket carries a time, and a ride refuses one whose time is more than five minutes from its own clock, which stops a copied ticket being replayed later. Then show real `klist` output with both lines (section 16.5) and map each line to the story.
- **D. The machine has an account too.** Joining gives the server a row in the directory (`CN=LAB,CN=Computers,…`), a 120-character password nobody ever types, and a file (`/etc/krb5.keytab`) holding it. With that the server can ask the directory who `alice` is and what groups she is in. If the directory's copy of that password changes and the file doesn't, the server is locked out of the directory while every user's password still works: `kinit alice` succeeds and logging in fails. The real evidence for that state is in section 16.5.
- **E. Layers of paint.** Group Policy settings are painted on in order: local, site, domain, then each OU from the outermost in. The last coat shows. "Block inheritance" on an OU skips the coats from above; "enforced" on a link is a coat that can't be painted over or skipped.

### 5.3 Where the three clouds differ

Mark these in the lesson as differences, and leave the depth to Modules 10 to 12.

| Idea | Azure | AWS | Google Cloud |
| --- | --- | --- | --- |
| The provider's own identity service (not a domain) | Microsoft Entra ID | IAM Identity Center | Cloud Identity |
| A managed domain (Kerberos, LDAP, Group Policy, domain join) | Microsoft Entra Domain Services | AWS Managed Microsoft AD (real Windows DCs); Simple AD (built on Samba 4, no trusts) | Managed Service for Microsoft AD (real Windows DCs) |
| Making a cloud network's machines ask the DCs for names | Custom DNS servers on the virtual network | A DHCP option set, or a Route 53 Resolver rule | A Cloud DNS forwarding zone |
| Your own DCs on VMs | Supported on all three; you patch, back up and place them yourself. | | |

The managed-domain row and the Azure DNS cell are sourced in section 6. The AWS and Google Cloud DNS cells are from memory and **must be checked** before they are printed (I did not open those pages); if unchecked, say only "each cloud has its own setting for this".

## 6. Verified facts

Each claim the topic may make, where it was confirmed, and when. Anything not in this list is not confirmed.

| # | Claim | Source | Read |
| --- | --- | --- | --- |
| F1 | Kerberos tolerates 5 minutes of clock difference by default in a Windows domain (Default Domain Policy). | learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/maximum-tolerance-for-computer-clock-synchronization | 2026-11-11 |
| F2 | The default lifetime of a user's first ticket is 10 hours. | …/security-policy-settings/maximum-lifetime-for-user-ticket (same site) | 2026-11-11 |
| F3 | MIT Kerberos's `clockskew` default is 300 seconds; with `kdc_timesync` on (the default) the client corrects for its own wrong clock using the KDC's time. | web.mit.edu/kerberos/krb5-latest/doc/admin/conf_files/krb5_conf.html; behaviour confirmed in the prototype (16.4) | 2026-11-11 |
| F4 | Members find DCs by asking DNS for SRV records named `_ldap._tcp.<domain>`; the DC then tells the client which site it is in from its IP subnet. | learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/dc-locator (dated 2025-07-10) | 2026-11-11 |
| F5 | The KDC runs on every domain controller and uses the directory as its account database; a client gets a ticket-granting ticket at sign-in and presents it to get a service ticket per service. | learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-authentication-overview (dated 2026-09-14) | 2026-11-11 |
| F6 | Group Policy refreshes every 90 minutes by default, with a random extra of up to 30 minutes; local policy is processed before domain-based policy; enforced links and block inheritance change what is inherited. | learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/group-policy/group-policy-processing (dated 2025-06-16) | 2026-11-11 |
| F7 | Trusts are one-way or two-way and transitive or not; direction decides which way authentication requests flow. | learn.microsoft.com/en-us/entra/identity/domain-services/concepts-forest-trust (dated 2025-06-30) | 2026-11-11 |
| F8 | On an Entra-joined or registered device, sign-in uses OAuth and OpenID Connect; on a domain-joined one, Kerberos and NTLM. Entra-joined devices are managed by MDM such as Intune; domain-joined ones by Group Policy and must reach the domain's network. | learn.microsoft.com/en-us/entra/identity/domain-services/compare-identity-solutions (dated 2025-06-30) | 2026-11-11 |
| F9 | Entra Domain Services offers domain join, Group Policy, LDAP and Kerberos/NTLM as a managed service; no domain-admin rights; no schema extensions; trusts need the Enterprise SKU. | same page, and …/domain-services/overview (dated 2026-02-16) | 2026-11-11 |
| F10 | Entra Domain Services, Standard, is $0.15 an hour in East US 2 (about $110 a month). | Azure Retail Prices API, `contains(serviceName,'Domain Services')` | 2026-11-11 |
| F11 | Active Directory needs a federation service for SaaS apps; Entra ID supports OAuth2, SAML and WS-* directly. Linux machines can use Active Directory as a Kerberos realm. | learn.microsoft.com/en-us/entra/fundamentals/compare (table; page dated 2022-08-17, updated 2026-06-23) | 2026-11-11 |
| F12 | Every Azure, Microsoft 365 or Dynamics subscriber already has an Entra tenant; licences are Free, P1, P2 and others. | learn.microsoft.com/en-us/entra/fundamentals/what-is-entra (dated 2026-06-18) | 2026-11-11 |
| F13 | Only paid customers can create an additional workforce tenant; a free tenant or a trial subscription can't. | learn.microsoft.com/en-us/entra/fundamentals/create-new-tenant (dated 2026-07-29) | 2026-11-11 |
| F14 | AWS Simple AD "is powered by a Samba 4 Active Directory Compatible Server" and doesn't support trusts, MFA or PowerShell. | docs.aws.amazon.com/directoryservice/latest/admin-guide/directory_simple_ad.html | 2026-11-11 |
| F15 | AWS Managed Microsoft AD runs Microsoft Active Directory as a managed service, a pair of DCs across Availability Zones, and supports trusts. | docs.aws.amazon.com/directoryservice/latest/admin-guide/directory_microsoft_ad.html | 2026-11-11 |
| F16 | Google's Managed Microsoft AD "runs actual Microsoft Active Directory domain controllers on Windows virtual machines", supports a forest trust to on-premises, and GPOs on OUs under its Cloud OU. | docs.cloud.google.com/managed-microsoft-ad/docs/overview | 2026-11-11 |
| F17 | Ubuntu's own guide joins with `sudo realm join`, and `realm` doesn't set up home directories: `sudo pam-auth-update --enable mkhomedir`. It lists correct system time as a prerequisite. | documentation.ubuntu.com/server/how-to/sssd/with-active-directory/ (modified 2026-07-02) | 2026-11-11 |
| F18 | Samba's guide: don't use `.local` for the domain (Avahi uses it); use a subdomain of a name you control; the realm can't be renamed after provisioning; Kerberos needs synchronised time on every member. | wiki.samba.org/index.php/Setting_up_Samba_as_an_Active_Directory_Domain_Controller | 2026-11-11 |
| F19 | `.test` is reserved for testing and never resolves on the internet. | rfc-editor.org/rfc/rfc6761.html | 2026-11-11 |
| F20 | Entra publishes its sign-in endpoints as an OpenID Connect discovery document over HTTPS (authorize, token and key URLs; tokens signed RS256), and has no Kerberos or LDAP SRV records for its sign-in host. | login.microsoftonline.com/common/v2.0/.well-known/openid-configuration; `nslookup -type=SRV _kerberos._tcp.login.microsoftonline.com` returned "Non-existent domain" | 2026-11-11 |
| F21 | Windows Server needs 2 GB of memory with Desktop Experience (4 GB recommended on the newest release) and 32 GB of disk as an absolute minimum to install. | learn.microsoft.com/en-us/windows-server/get-started/hardware-requirements (dated 2025-07-02) | 2026-11-11 |
| F22 | Windows 11 in Azure needs per-user licences the learner is unlikely to hold (Windows 11 Enterprise E3/E5 or Azure Virtual Desktop access). | learn.microsoft.com/en-us/azure/virtual-machines/windows/windows-desktop-multitenant-hosting-deployment (dated 2025-05-22) | 2026-11-11 |

Azure facts used only by the extra lab are in section 12.

**Sources that disagree or that I could not confirm** are listed in section 17.

## 7. Resources

All free to read, all opened on 2026-11-11, all linked and never copied. Minutes are from the page's own length at 200 words a minute, or the provider's stated duration.

| # | Title | URL | Type | Licence | Minutes | Skills | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1 | Introduction to AD DS (Microsoft Learn training module, 8 units) | learn.microsoft.com/en-us/training/modules/introduction-to-ad-ds/ | interactive | Microsoft Learn terms of use; linked, not copied | 60 (the page's own figure) | directory-structure | **Main resource** (`index 0`). I confirmed it exists, its units and its length; I did not read every unit. The writer should go through it once and name the units to read. |
| R2 | Active Directory Domain Services overview | learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/virtual-dc/active-directory-domain-services-overview | reading | CC BY 4.0 (the source repository, MicrosoftDocs/windowsserverdocs, carries that licence); linked | 3 | directory-structure | Short; good as the two-minute map before R1. |
| R3 | Locating Active Directory domain controllers | learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/dc-locator | reading | CC BY 4.0 (same repository); linked | 11 (read the first half: 6) | dc-discovery | Dense after the SRV section; tell the learner where to stop. |
| R4 | Kerberos authentication overview in Windows Server | learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-authentication-overview | reading | CC BY 4.0 (same repository); linked | 5 | kerberos-tickets | Dated 2026-09-14. |
| R5 | Designing an Authentication System: a Dialogue in Four Scenes (MIT, 1988) | web.mit.edu/kerberos/dialogue.html | reading | © MIT 1988, 1997, with a notice permitting use and copying without fee; linked | 38 | kerberos-tickets | Optional. The best explanation of *why* tickets look the way they do; too long to require. |
| R6 | How to set up SSSD with Active Directory (Ubuntu Server documentation) | documentation.ubuntu.com/server/how-to/sssd/with-active-directory/ | reading | Canonical; licence not found on the page or in the repository; linked only | 7 | domain-join | The lab follows this guide step for step. |
| R7 | Group Policy processing for Windows | learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/group-policy/group-policy-processing | reading | CC BY 4.0 (same repository); linked | 11 | group-policy | |
| R8 | How trust relationships work for forests in Active Directory | learn.microsoft.com/en-us/entra/identity/domain-services/concepts-forest-trust | reading | Microsoft Learn (the Entra docs repository's licence file is MIT, which reads as covering code; treat as linked only) | 20 (read to the end of "One-way and two-way trusts": 7) | directory-structure | |
| R9 | Compare Active Directory to Microsoft Entra ID | learn.microsoft.com/en-us/entra/fundamentals/compare | reading | Microsoft Learn; linked only | 5 | entra-vs-adds | One table; the page body dates from 2022 but was updated 2026-06-23. |
| R10 | Compare Microsoft directory-based services (AD DS, Entra ID, Entra Domain Services) | learn.microsoft.com/en-us/entra/identity/domain-services/compare-identity-solutions | reading | Microsoft Learn; linked only | 8 | entra-vs-adds, domain-join | The device-join table is the clearest statement of F8. |
| R11 | Overview of Microsoft Entra Domain Services | learn.microsoft.com/en-us/entra/identity/domain-services/overview | reading | Microsoft Learn; linked only | 7 | entra-vs-adds | |
| R12 | AWS Managed Microsoft AD | docs.aws.amazon.com/directoryservice/latest/admin-guide/directory_microsoft_ad.html | reading | © AWS; no open licence found; linked only | 3 | entra-vs-adds | |
| R13 | Simple AD (AWS Directory Service) | docs.aws.amazon.com/directoryservice/latest/admin-guide/directory_simple_ad.html | reading | © AWS; linked only | 3 | entra-vs-adds | The link between the lab's Samba and a real cloud product. |
| R14 | Managed Microsoft AD overview (Google Cloud) | docs.cloud.google.com/managed-microsoft-ad/docs/overview | reading | CC BY 4.0 (stated on the page) | 4 | entra-vs-adds | |
| R15 | Setting up Samba as an Active Directory Domain Controller (Samba wiki) | wiki.samba.org/index.php/Setting_up_Samba_as_an_Active_Directory_Domain_Controller | reading | CC BY (the wiki's footer: "Content is available under CC-BY unless otherwise noted") | 12 | directory-structure, dc-discovery | Reference for Checkpoint 2 part 3. The wiki rate-limits automated fetches (HTTP 429); a browser is fine. |
| R16 | krb5.conf (MIT Kerberos documentation) | web.mit.edu/kerberos/krb5-latest/doc/admin/conf_files/krb5_conf.html | reading | © MIT; linked only | 37 (reference; look up three settings) | kerberos-tickets | Only for `clockskew`, `kdc_timesync`, `rdns`. |

Required reading: R1, R2, R3 (half), R4, R6, R7, R8 (a third), R9, R10: about **110 minutes**. Optional: R5, R11 to R16.

**Not used, and why.** Third-party Kerberos videos and blog explainers were not opened and are not listed. An official Microsoft video would be worth an embed if the writer finds one and confirms it; the lesson's own ticket-booth picture carries the idea meanwhile.

## 8. The two layers and what each proves

| | Layer (a): local, free, checked in CI | Layer (b): Azure, about $0.60 a sitting, checked on the learner's machine |
| --- | --- | --- |
| What it is | One lab container: `lab`, an Ubuntu 24.04 server, and `dc1`, Samba 4.19 running as an Active Directory domain controller in namespaces of its own on the far side of a virtual cable (the Module 1 "office" pattern). | A resource group with a Windows Server domain controller, a Windows Server member and an Ubuntu member, no public addresses on any of them. |
| Proves | Finding a domain through DNS; getting and reading Kerberos tickets; LDAP queries; what a join creates; logging in as a domain user; who is permitted; repairing a stale machine account; which GPOs reach whom (Samba computes the same order, block and enforce). | Promoting a Windows server to a DC with the Windows tools; joining a Windows machine; a GPO really being applied by a Windows client (`gpupdate`, `gpresult`, a registry value appearing); the cloud network's DNS setting; cost control and teardown; the same Linux join against real Windows. |
| Doesn't prove | Anything about Windows: Server Manager, PowerShell's directory commands, Group Policy *processing* on a Windows client, the Windows time service, RDP. Clock skew can only be shown, not planted as a fault (16.4). Trusts are explained and quizzed, not built. | Anything in CI. Nobody has run it yet. |
| How checked | `labcheck.py test` in the Labs workflow: pristine fails, the solution passes, each wrong fix fails. | A local script asks Azure and the VMs questions through `az` (12.5); CI replays recorded answers. |
| Status | Two labs built and passing (16.3). Three more designed on the same image. | Designed and priced. Unproven until the owner runs it once. |

**What Samba does not teach about Windows, said plainly in the lesson's recap:** the lab's DC speaks Active Directory's protocols well enough that SSSD, `adcli` and `kinit` can't tell the difference, and AWS sells a directory built on the same software (F14). But a Windows administrator's day is spent in tools this lab doesn't have, and Group Policy's real work, a Windows client fetching and applying settings, never happens here. The Azure extra is where that is seen.

## 9. Practice ladder

All labs share one image layer (section 16.1), boot systemd (`lab: { init: systemd }`) and use the same story: the shop's domain is `ad.shop.test` (short name `SHOP`), `dc1` is 10.0.9.10, `lab` is 10.0.9.1, the site's ordinary resolver (dnsmasq) runs on `lab` and has never heard of the domain. People: `alice` and `carol` in the group `linux-admins`, `bob` not. `on-dc COMMAND` runs a command on dc1.

### 9.1 Worked example (lab): `example-meet-the-domain`

Skills: `dc-discovery`, `kerberos-tickets`, `directory-structure`, `domain-join`. About 40 minutes. The image is the build lab's (pristine: DC up and seeded, `lab` not joined, names not forwarded). Every command below was run in the prototype as the `learner` user; real output is in 16.5.

| Step label | Lines | What the note says |
| --- | --- | --- |
| Ask for the domain's controllers, and get nothing | `dig _ldap._tcp.ad.shop.test SRV` | `status: NXDOMAIN`: the resolver this machine uses has never heard of the domain. |
| Ask dc1 itself | `dig +short @10.0.9.10 _ldap._tcp.ad.shop.test SRV` | `0 100 389 dc1.ad.shop.test.`: priority, weight, port, host. The domain's own DNS lives on its controllers. |
| Forward the domain's zone | write `/etc/dnsmasq.d/ad.conf` with two `server=/zone/10.0.9.10` lines, restart `dnsmasq`, `dig` again | A conditional forwarder: only this zone goes to dc1. The second line is the reverse zone, so 10.0.9.10 has a name. |
| Get a ticket | `kinit alice@AD.SHOP.TEST`, `klist` | One line: `krbtgt/AD.SHOP.TEST@AD.SHOP.TEST`, valid ten hours. The realm is the domain in capitals; lower case fails with "KDC reply did not match expectations". |
| Use it | `ldapsearch -Q -LLL -Y GSSAPI -H ldap://dc1.ad.shop.test -b 'DC=ad,DC=shop,DC=test' '(sAMAccountName=alice)' dn memberOf`, `klist` | No password asked. `klist` has a second line now, `ldap/dc1.ad.shop.test`: a ticket for that one service. |
| Send a password in the clear, and be refused | the same search with `-x -D alice@ad.shop.test -w …` | `Strong(er) authentication required … Transport encryption required`. The DC won't take a password over an unencrypted connection, and the labs never turn that off. |
| See what five minutes means | a three-line `krb5.conf` with `kdc_timesync = 0`, then `faketime -f '+4m' kinit alice` and `faketime -f '+6m' kinit alice` | Four minutes works; six gives `Clock skew too great`. `faketime` lies to one command about the time; the machine's clock is never touched. Linux's Kerberos normally corrects for a wrong clock by asking the KDC the time; Windows doesn't, which is why this error is a Windows classic. |
| Join | `realm discover ad.shop.test`, `sudo realm join -v -U Administrator ad.shop.test` | Read the output: a computer account `CN=LAB,CN=Computers,…`, a generated 120-character password, entries added to `/etc/krb5.keytab`. |
| Look at what the join made | `sudo klist -k /etc/krb5.keytab`, `id alice@ad.shop.test`, `on-dc samba-tool computer list` | The machine's own principals; a domain user now has a UID here; the directory lists `LAB$`. |
| Log in as a domain user | `sudo pam-auth-update --enable mkhomedir`, `ssh alice@ad.shop.test@localhost`, `klist` inside | The login asked the DC about the password and handed alice a ticket. |

Checks (read-only): `~/example/srv.txt` holds the SRV line for dc1 fetched through the machine's own resolver; `~/example/tickets.txt` (saved `klist`) has both a `krbtgt/` and an `ldap/dc1` line; the machine's keytab can authenticate (`kinit -k 'LAB$'`); `getent passwd alice@ad.shop.test` answers. Wrong fixes: `asked-dc-directly.sh` (never adds the forwarder, saves the `@10.0.9.10` answer: the own-resolver check fails); `no-service-ticket.sh` (saves `klist` before using LDAP).

### 9.2 Recall items

Twenty-six, each answerable in about a minute, built on output captured from the prototype (16.5) wherever it says "real". House rules for every multiple-choice item: four choices of similar length, the right one never the longest by more than a few words, its position varied, the teaching detail in the explanation and not in the choice.

| Id | Type | Skill | Scenario and right answer |
| --- | --- | --- | --- |
| `dir-dn-parts` | predict_shell | directory-structure | `users.ldif`: real `dn:` lines for five accounts across `CN=Users`, `OU=Staff` and `OU=Engineering,OU=Staff`. `grep -c 'OU=Staff,DC=ad' users.ldif` prints how many sit anywhere under Staff. Explanation reads one DN right to left. |
| `dir-ldap-result` | predict_shell | directory-structure | `result.ldif`: the real answer to `(&(objectClass=user)(memberOf=CN=linux-admins,…))`. `grep '^sAMAccountName' result.ldif \| cut -d' ' -f2 \| sort` prints `alice`, `carol`. |
| `mcq-ou-or-group` | mcq | directory-structure | "Sales laptops need one set of settings; Sales people need a shared folder." Right: an OU for the laptops' settings, a group for the folder. Wrong: a group for both; an OU for both; a separate domain. |
| `mcq-domain-or-forest` | mcq | directory-structure | "A subsidiary must not be administrable by the parent's domain admins." Right: a separate forest; a domain inside the same forest isn't a security boundary. Wrong: a child domain; a separate OU; a separate site. |
| `mcq-trust-direction` | mcq | directory-structure | "People in CORP must open files on servers in PARTNER; nothing the other way." Right: PARTNER trusts CORP, one way. Wrong: CORP trusts PARTNER; two-way; no trust, duplicate accounts. |
| `mcq-trust-passes-along` | mcq | directory-structure | "A trusts B with an external, non-transitive trust; B trusts C the same way. Can C's users reach A?" Right: no. Wrong: yes through B; only its admins; only by IP. |
| `dns-srv-fields` | predict_shell | dc-discovery | `srv.txt`: the real answer line plus a second controller with a worse priority. `sort -k5,5n srv.txt \| head -n 1 \| awk '{print $NF, $7}'` prints the preferred host and its port. |
| `dns-ports-services` | predict_shell | dc-discovery | `records.txt`: the real `dig +short` answers for `_ldap`, `_kerberos`, `_gc` and `_kpasswd` (ports 389, 88, 3268, 464), labelled. `grep -c ' 88 ' records.txt`. Explanation: which service is on which port. |
| `mcq-wrong-resolver` | mcq | dc-discovery | Real: `dig` through the machine's resolver says NXDOMAIN, `dig @10.0.9.10` answers, `realm discover` says "No such realm found". Right: forward the domain's zone from the site's resolver to the DCs. Wrong: add dc1 to `/etc/hosts`; open port 389 in the firewall; set the realm in `krb5.conf`. Explanation: a hosts file can't hold an SRV record. |
| `mcq-cloud-network-dns` | mcq | dc-discovery | "A new VM in a cloud network can't find the domain; it asks the provider's default resolver." Right: make the network hand out the DCs as its DNS servers, or forward the domain's zone to them, then renew the VM's lease. Wrong: give the VM a public address; open Kerberos's port to the internet; rename the VM. |
| `krb-klist-lines` | predict_shell | kerberos-tickets | `klist.txt`: real output with a `krbtgt/`, an `ldap/dc1` and a `host/lab` line. `grep -c '@AD.SHOP.TEST$' …` or `awk` printing the service names. Explanation: which is the day pass. |
| `krb-ticket-hours` | predict_shell | kerberos-tickets | Real line `07:51:28 … 17:51:28`. Bash arithmetic prints the lifetime in hours: `10`. |
| `mcq-krb-skew` | mcq | kerberos-tickets | Real: `Clock skew too great`; the member's clock is seven minutes behind. Right: fix the member's time source; five minutes is the tolerance. Wrong: reset the password; raise the tolerance to an hour; join again. |
| `mcq-krb-no-kdc` | mcq | kerberos-tickets | Real: `Cannot find KDC for realm "AD.SHOP.TEST"`. Right: the machine's resolver can't answer the domain's SRV records. Wrong: wrong password; account disabled; clock. |
| `mcq-krb-revoked` | mcq | kerberos-tickets | Real: `Client's credentials have been revoked`. Right: the account is disabled, locked or expired; the password may be fine. Wrong: wrong password; the ticket expired; DNS. |
| `mcq-krb-by-address` | mcq | kerberos-tickets | Real: `Server not found in Kerberos database`, from an LDAP search aimed at `ldap://10.0.9.10`. Right: tickets are issued for service *names*; use the DC's name (and give its address a reverse record). Wrong: the DC is down; the user lacks rights; the clock. |
| `mcq-krb-next-ticket` | mcq | kerberos-tickets | "alice holds a TGT and now connects to `lab` over SSH with Kerberos. Which line appears in `klist`?" Right: `host/lab.ad.shop.test@AD.SHOP.TEST`. Wrong: a second `krbtgt`; `alice/lab…`; `ldap/dc1…`. |
| `join-read-the-output` | predict_shell | domain-join | `join.txt`: real `realm join -v` output. `grep -c 'Added the entries to the keytab' join.txt` and `grep -o 'CN=LAB,CN=Computers[^ ]*' join.txt \| head -n 1`. |
| `mcq-right-password-refused` | mcq | domain-join | Real journal: `pam_sss(sshd:auth): authentication success` then `pam_sss(sshd:account): Access denied for user bob`. Right: the password is right; this server's access rule doesn't include him. Wrong: reset his password; the DC is unreachable; his account is disabled. |
| `mcq-machine-key-stale` | mcq | domain-join | Real: `kinit alice` works; SSSD logs `Failed to initialize credentials using keytab … Preauthentication failed`. Right: the machine's own account no longer matches its keytab; leave and join again, then restore the access rule. Wrong: reset alice's password; restart SSSD until it connects; copy a keytab from another server. |
| `mcq-permit-the-group` | mcq | domain-join | "The operations team must log in to forty servers; people join and leave it monthly." Right: permit the domain group on each server. Wrong: permit each person by name; permit every domain account; create local accounts. |
| `gpo-who-gets-what` | predict_shell | group-policy | `alice.txt`, `bob.txt`, `carol.txt`: real `samba-tool gpo list` output. `grep -l 'Lock screen' *.txt` prints `alice.txt` and `bob.txt`. Explanation: carol is in `CN=Users`, outside the OU the GPO is linked to. |
| `mcq-gpo-closest-wins` | mcq | group-policy | "A domain-level GPO locks the screen after 15 minutes; one linked to the Servers OU says 5. Nothing is enforced." Right: 5, the OU's is applied last. Wrong: 15; the stricter always; whichever was created last. |
| `mcq-gpo-block-enforce` | mcq | group-policy | Real: Engineering blocks inheritance; the Staff link is enforced. "Which reach alice?" Right: Engineering's own and the enforced Staff one, not the domain default. Wrong: all three; only Engineering's; none. |
| `gpo-refresh-arithmetic` | predict_shell | group-policy | Bash arithmetic: a change at 10:00, a 90-minute refresh plus up to 30. Prints the latest time every running member has it without `gpupdate`: `12:00`. |
| `entra-discovery-doc` | predict_shell | entra-vs-adds | `openid-configuration.json`: the real document, trimmed to six keys. `grep -c 'https://login.microsoftonline.com' …`. Explanation: an app finds Entra with one HTTPS request; a member finds a DC with an SRV lookup inside the network. |
| `mcq-app-speaks-kerberos` | mcq | entra-vs-adds | "A file-sharing application that authenticates with Kerberos moves to cloud VMs. The company already has Entra ID." Right: it still needs domain services: DCs on VMs or a managed domain. Wrong: Entra ID alone; a VPN to Entra; nothing, Kerberos works over the internet. |
| `mcq-which-join` | mcq | entra-vs-adds | Three devices: a company laptop used with web apps, a server VM running the Kerberos application, a personal phone. Right: Entra joined, domain joined, Entra registered. |
| `mcq-no-gpo-in-entra` | mcq | entra-vs-adds | "Settings for 300 Entra-joined laptops that are rarely on the office network." Right: an MDM policy (Intune) assigned to a group. Wrong: a GPO linked to an OU; a logon script on SYSVOL; a trust. |
| `managed-domain-cost` | predict_shell | entra-vs-adds | Bash arithmetic with the real prices: a managed domain at 15 cents an hour against two B2s Windows VMs at 4.96 cents, over 730 hours. Prints both to the dollar. Explanation: the VMs look cheaper until someone has to patch and back them up; say the prices' date. |

(Twenty-nine rows; drop to about twenty-four in `practice` and keep the rest for the review pool only. The four arithmetic and cost items need their expected output pinned by running them, as the validator does.)

### 9.3 Fill-in (lab): `fill-domain-report`

Skills: `dc-discovery`, `kerberos-tickets`, `directory-structure`. About 25 minutes. Image: the build lab's with the names already forwarded and `lab` already joined at first boot (the debug lab's `lab-member.service` without its faults). A starter script `~/bin/domain-report` has four gaps (`___`). When finished it prints:

```text
controller: dc1.ad.shop.test
machine account: ok
linux-admins: alice carol
tgt hours: 10
```

Gaps: the SRV name to ask for; the keytab check (`kinit -k` for the machine's principal); the LDAP filter for members of a group; the arithmetic on `klist`'s two times. Checks run the script and compare each line with the truth computed in the check (the group's members from `samba-tool group listmembers`, sorted), then run it again after the check's own throwaway change cannot be made (checks only read), so use the second-input trick the shell labs use: the script takes the group as `$1`, and a check calls it with `'domain users'` as well, where the answer is longer. Wrong fixes: `hard-coded-members.sh` (prints `alice carol` whatever the argument); `asks-for-a-records.sh` (looks up `dc1` by name, not the SRV record: passes today, so the check must compare against a second SRV name, `_kerberos._tcp`, given as `$2`); `user-ticket-not-machine.sh` (checks alice's ticket where the machine's is asked).

### 9.4 Write (lab): `write-policy-scope`

Skills: `group-policy`, `directory-structure`. About 30 minutes. Image: the build lab's, plus a seed that adds users `dev`, `erin` and `frank`. From a blank shell, on dc1:

- an OU `Staff` with a child `Engineering` and a child `Contractors`;
- alice in Engineering, bob in Staff, frank in Contractors, carol left where she is;
- a GPO `Lock screen` linked to Staff; `Engineering tools` linked to Engineering; `Contractor limits` linked to Contractors, which must not inherit anything from above **except** a GPO `Security baseline`, linked at the domain, that nobody may escape.

Checks ask Samba which GPOs reach each of four people (`samba-tool gpo list USER`), by display name, never by GUID (GUIDs are new every run). Expected: alice gets Engineering tools, Lock screen, Security baseline (and the domain default); bob gets Lock screen and Security baseline; frank gets Contractor limits and Security baseline and **not** Lock screen or the domain default; carol gets Security baseline and the default only. Wrong fixes: `baseline-not-enforced.sh` (frank loses the baseline); `no-block.sh` (frank also gets Lock screen); `linked-to-the-wrong-ou.sh` (Engineering tools on Staff: bob gets it); `created-not-linked.sh`. All four behaviours (link, inherit, block, enforce) were confirmed in the prototype (16.5).

**Each skill is practised before a proof asks for it:**

| Skill | Practised in | First asked for in |
| --- | --- | --- |
| directory-structure | example, fill-in, write, six recall items | explain; Checkpoint 2 |
| dc-discovery | example, fill-in, four recall items | build |
| kerberos-tickets | example, fill-in, seven recall items | debug |
| domain-join | example (the whole join, guided), four recall items | build |
| group-policy | write, four recall items | explain; Checkpoint 2 |
| entra-vs-adds | five recall items | explain |

## 10. Proofs

### 10.1 Build (lab): `build-join-the-domain`

**Built and passing.** The whole lab folder is at `proto-windows-ad/content/csa.hw.windows-ad/exercises/build-join-the-domain/`: the prompt, seven checks, the solution and five wrong fixes. Use it as written; change only the wording.

The brief the learner gets: make `lab` find the domain through the resolver it already uses, with the site's own names still resolving and nothing about dc1 typed into a hosts file or a Kerberos config; join it; let members of `linux-admins` log in over SSH into a home directory made on first login, and nobody else; leave dc1 as strict as it was. No commands are named.

| Check | What it tests | The shortcut it rejects |
| --- | --- | --- |
| `finds-the-dc` | `dig` for the domain's SRV record through the machine's own resolver names dc1. | Hard-coding: `wrong/hard-coded.sh` joins successfully with dc1 in `/etc/hosts`, `kdc =` in `krb5.conf` and `ad_server` in SSSD, passes every other check, and fails this one. |
| `site-names-resolve` | `intranet.shop.internal` still answers. | Replacing the site resolver's configuration wholesale. |
| `joined` | The directory holds a computer account, and the machine can authenticate with its own keytab (`kinit -k 'LAB$'`). | Fixing names and stopping. |
| `alice-logs-in`, `carol-logs-in` | A real SSH password login for each member of the group, landing in `/home/NAME@ad.shop.test` and holding a ticket (`klist -s`). | Permitting one person by name (carol fails); skipping home directories. |
| `bob-kept-out` | bob *can* get a ticket with his password, and the login is still refused. | Leaving every domain account permitted. Checking that bob's password works first means the refusal is authorisation, not a typo. |
| `dc-still-strict` | A password sent over unencrypted LDAP is still refused. | Turning off `ldap server require strong auth` on dc1 to make a simple bind work. |

Still to add when writing: a wrong fix `dc-weakened.sh` that sets that option and restarts dc1 (the check exists; the wrong fix proving it doesn't yet).

### 10.2 Debug (lab): `debug-nobody-can-log-in`

**Built and passing.** Folder: `proto-windows-ad/content/csa.hw.windows-ad/exercises/debug-nobody-can-log-in/`.

The prompt gives the system's purpose (members of `linux-admins` log in to `lab` with domain passwords; nobody else in the domain may; local accounts as before), the symptom (since Monday no domain account can log in) and the number of faults (three). It names none of them and no file. Check descriptions state the end state only.

The three faults (for the writer; never shown): the site resolver's forwarder for the domain's zone points at an address where nothing answers; the computer account's password was reset on dc1, so the keytab no longer matches; an SSH hardening file allows only a local group. They surface one after another, each with its own evidence (16.5): `Cannot find KDC`; then `kinit alice` works while SSSD logs `Failed to initialize credentials using keytab … Preauthentication failed`; then `sshd` refusing a user whose groups aren't listed.

| Check | What it tests | The shortcut it rejects |
| --- | --- | --- |
| `finds-the-dc` | As in the build. | `wrong/resolver-bypassed.sh`: leaves the broken forwarder, works around it with a hosts entry and `kdc =`; everything else passes. |
| `machine-trusted` | `kinit -k 'LAB$'` succeeds. | `wrong/not-rejoined.sh`. |
| `alice-logs-in`, `carol-logs-in` | Real logins. | |
| `bob-kept-out` | bob gets a ticket; SSSD's own access rule refuses him for a service other than SSH (`sssctl user-checks bob@… -a acct -s login`), and SSH refuses him too. | `wrong/forgot-the-rule.sh`: joining again writes a fresh SSSD configuration that permits every domain account. SSH's group list still stops bob, so only the direct question to SSSD catches it. This is the lab's best trap: the repair itself undoes a protection. |
| `ssh-still-restricted` | `ben`, a local account in no allowed group, is refused by a real login attempt, and `ssh-users` is still listed. | `wrong/ssh-rule-deleted.sh`: deleting the hardening file instead of adding the domain group. Tested by behaviour, not by reading the file (the audit's finding about `sshd -T`). |
| `dc-still-strict` | As in the build. | |

Why clock skew isn't a fault here: section 16.4.

### 10.3 Explain

Prompt:

> A company runs Active Directory on two servers in its office. It is moving forty application servers (Windows and Linux) and three hundred staff laptops to the cloud, and a colleague proposes: "We already have Entra ID with our email, and that's Active Directory in the cloud, so we can switch the domain controllers off." Explain, in your own words: what the domain does today for a server that is joined to it and for a person who logs in; how a joined server finds a domain controller and proves a person's identity, and the two things outside the directory that this depends on; how Entra ID differs, and which of the forty servers and three hundred laptops could use it alone; what you'd run in the cloud for the rest, on whichever provider, and how the two directories are kept in step; and one thing a lab built on Samba could not have shown you about Windows.

Rubric:

| Id | Required | Description |
| --- | --- | --- |
| `what-the-domain-does` | yes | One directory of accounts and groups that every joined machine accepts; Kerberos logins; a machine account per member; settings pushed by Group Policy through OUs. |
| `finding-and-proving` | yes | A member finds a DC through the domain's DNS SRV records, so it must ask a resolver that knows the domain; identity is proved with Kerberos tickets from the DC (a first ticket, then one per service), which fail if clocks differ by more than five minutes. DNS and time are the two dependencies. |
| `entra-differs` | yes | Entra ID signs people in to web and SaaS applications with tokens over HTTPS (OpenID Connect, OAuth, SAML); it has no Kerberos or LDAP for servers to use, no OUs and no Group Policy; devices are joined or registered to it and managed by MDM. Laptops used with web apps can be Entra joined; servers running applications that expect Kerberos, LDAP or Group Policy can't rely on it alone. |
| `what-to-run` | yes | For those servers, domain services in the cloud: domain controllers on VMs, or a managed domain (Entra Domain Services, AWS Managed Microsoft AD, Google's Managed Microsoft AD), reachable on the servers' network with the network's DNS pointed at it; accounts kept in step by synchronising the directory to Entra ID. |
| `samba-limit` | no | The lab's controller was Samba: the protocols are the same, but Windows's own tools and a Windows client actually applying Group Policy weren't seen. |
| `trust` | no | Where two directories must stay separate, a trust lets one accept the other's logins; the domain holding the resource trusts the domain holding the accounts. |

The model answer is the writer's to draft from the rubric; keep it under 350 words, in the first person, like Module 1's.

## 11. Review pool

Short, mixed, mostly judgement and arithmetic. At least two per skill; the build and debug never come back.

| Skill | In the pool | Also able to come back (not in the pool) |
| --- | --- | --- |
| directory-structure | `dir-dn-parts`, `mcq-trust-direction`, `mcq-ou-or-group` | `dir-ldap-result`, `mcq-domain-or-forest`, `mcq-trust-passes-along`, `write-policy-scope` |
| dc-discovery | `dns-srv-fields`, `mcq-wrong-resolver` | `dns-ports-services`, `mcq-cloud-network-dns`, `fill-domain-report` |
| kerberos-tickets | `krb-klist-lines`, `krb-ticket-hours`, `mcq-krb-by-address` | the other four `mcq-krb-*`, `fill-domain-report` |
| domain-join | `mcq-right-password-refused`, `mcq-machine-key-stale` | `join-read-the-output`, `mcq-permit-the-group` |
| group-policy | `gpo-who-gets-what`, `gpo-refresh-arithmetic` | `mcq-gpo-closest-wins`, `mcq-gpo-block-enforce`, `write-policy-scope` |
| entra-vs-adds | `mcq-app-speaks-kerberos`, `mcq-which-join` | `entra-discovery-doc`, `mcq-no-gpo-in-entra`, `managed-domain-cost` |

Fourteen in the pool, eight of them predict-the-output on real output or arithmetic. A timed rebuild of `build-join-the-domain` (target: 15 minutes) is a good later addition, once labs can record a time.

## 12. Layer (b): the real thing in Azure

**Status: designed, priced, not run.** I used `az` only to read: help pages, `az vm list-skus`, `az vm image list-skus` and `az vm image show`. No resource was created, changed or deleted, and no subscription identifier is written anywhere in this folder.

### 12.1 What gets built

One resource group in East US 2 holding: a virtual network with one subnet and a network security group with no inbound rules of its own; a NAT gateway for outbound traffic; `dc1` (Windows Server, the domain controller and DNS server); `app1` (Windows Server, a member); `web1` (Ubuntu 24.04, a member). No VM has a public address. The learner reaches the Windows desktops through Azure Bastion's free Developer tier in the portal.

### 12.2 Sizes and prices

Prices are pay-as-you-go, US dollars, East US 2, from the Azure Retail Prices API (`prices.azure.com/api/retail/prices`), read 2026-11-11. The script that fetched them is `proto-windows-ad/azure_prices.py`. The same prices apply in East US, North Central US, West US 2 and West US 3; other regions cost more (Central US is about 15% higher).

| Thing | Choice | Why | Per hour |
| --- | --- | --- | --- |
| `dc1` | `Standard_B2s` (2 vCPU, 4 GiB), Windows | 4 GiB is what the newest Windows Server recommends with a desktop (F21). Smaller is unproven. | $0.0496 |
| `app1` | `Standard_B2s`, Windows | Same reason. `Standard_B1ms` (1 vCPU, 2 GiB, $0.0246) meets the stated minimum and might do; untested. | $0.0496 |
| `web1` | `Standard_B1s` (1 vCPU, 1 GiB), Linux | SSSD is small. | $0.0104 |
| NAT gateway | Standard | New virtual networks have no outbound access by default (12.3). | $0.0450, plus $0.045 per GB |
| NAT gateway's address | Standard static public IPv4 | Required by the gateway. | $0.0050 |
| Disks | Standard SSD: three 32 GiB OS disks (E4, $2.40 a month each) and one small data disk for the directory database | The "smalldisk" Windows images. A default Windows image has a 127 GiB disk (E10, $9.60 a month). | about $0.013 |
| Bastion | Developer | Free, shared, one connection at a time, portal only; available in East US 2. | $0 |
| **Total** | | | **about $0.17 an hour** |

- **A three-hour sitting: about $0.52, plus a few cents of NAT data: call it $0.60.**
- **Forgotten for 24 hours, VMs running: about $4.15.**
- **Forgotten after auto-shutdown has stopped the VMs:** the NAT gateway, its address and the disks keep charging, about $1.50 a day, **about $46 if left a month**. Auto-shutdown is a seat belt, not teardown; deleting the resource group is the only thing that ends the bill.
- Against the $150 monthly credit: a sitting is 0.4% of it; ten forgotten days are 10%.

**This subscription can't use the newer, cheaper burstable sizes.** `az vm list-skus -l eastus2 --size Standard_B` lists only the first-generation B sizes for it (B1ls, B1s, B1ms, B2s, B2ms and larger); `Standard_B2als_v2` and its family are absent, though the price API quotes them ($0.0468 for Windows). `Standard_B2s` is restricted for this subscription in availability zone 3 only, so the VMs are created without a zone.

**Windows 11 is not an option** for the member: it needs per-user licences (F22). Windows Server's licence is part of the VM's hourly Windows price. This is a ready-made example for topic 20.

### 12.3 Azure facts the lab depends on

| # | Claim | Source | Read |
| --- | --- | --- | --- |
| A1 | Bastion has four tiers; Developer is free, uses shared infrastructure, supports one VM connection at a time, portal only, no virtual-network peering; it needs no dedicated subnet or public address. Basic and above bill by the hour from deployment whether used or not. | learn.microsoft.com/en-us/azure/bastion/bastion-overview (dated 2026-02-04); …/bastion/bastion-sku-comparison (dated 2025-11-24) | 2026-11-11 |
| A2 | Bastion Developer's regions include East US 2, Central US, North Central US, West US and West Central US, and not East US or West US 2. | …/bastion/bastion-sku-comparison, "Regional availability" | 2026-11-11 |
| A3 | Bastion Basic is $0.19 an hour, Standard $0.29, Premium $0.45. | Retail Prices API, `serviceName eq 'Azure Bastion'` | 2026-11-11 |
| A4 | A VM reached through Bastion needs RDP (3389) or SSH (22) open inbound, and no public address. | learn.microsoft.com/en-us/azure/bastion/quickstart-host-portal (dated 2026-01-20) | 2026-11-11 |
| A5 | Just-in-time VM access needs Microsoft Defender for Servers Plan 2 enabled on the subscription. | learn.microsoft.com/en-us/azure/defender-for-cloud/just-in-time-access-usage (dated 2026-07-03) | 2026-11-11 |
| A6 | Run Command runs a script on a VM through the VM agent as System, with no inbound port; output is the last 4,096 bytes; a run takes at least about 20 seconds; one at a time; 90 minutes at most; it needs outbound connectivity to return results; running one needs `Microsoft.Compute/virtualMachines/runCommand/action` (Virtual Machine Contributor or higher). | learn.microsoft.com/en-us/azure/virtual-machines/windows/run-command (dated 2025-08-18) | 2026-11-11 |
| A7 | New virtual networks default to private subnets (API versions after 31 March 2026; the portal already does): VMs have no outbound access unless given one explicitly, such as a NAT gateway. | learn.microsoft.com/en-us/azure/virtual-network/ip-services/default-outbound-access (dated 2026-07-24) | 2026-11-11 |
| A8 | After changing a virtual network's DNS servers, each VM must renew its lease (`ipconfig /renew` on Windows) or restart to pick them up. Azure's own resolver is 168.63.129.16. | learn.microsoft.com/en-us/azure/virtual-network/virtual-networks-name-resolution-for-vms-and-role-instances (dated 2025-07-24) | 2026-11-11 |
| A9 | Microsoft's guide to a DC on an Azure VM puts the directory database on a data disk with caching disabled, uses a static private address, and sets the DCs as the network's DNS servers. | learn.microsoft.com/en-us/windows-server/identity/ad-ds/deploy/virtual-dc/adds-on-azure-vm (dated 2025-05-12); learn.microsoft.com/en-us/azure/architecture/example-scenario/identity/adds-extend-domain (dated 2026-06-16) | 2026-11-11 |
| A10 | A budget is an alert, not a cap: "Resources aren't affected, and your consumption isn't stopped." Cost data arrives in 8 to 24 hours and budgets are evaluated once a day. | learn.microsoft.com/en-us/azure/cost-management-billing/costs/tutorial-acm-create-budgets (dated 2025-06-26) | 2026-11-11 |
| A11 | `az vm auto-shutdown -g GROUP -n VM --time hhmm` sets a daily shutdown in UTC, with an optional `--email`. | `az vm auto-shutdown --help`, Azure CLI 2.89.1 on this machine | 2026-11-11 |
| A12 | `az consumption budget create-with-rg` creates a budget scoped to a resource group and takes `--notifications`; the command group is marked preview. | `az consumption budget create-with-rg --help`, same CLI | 2026-11-11 |
| A13 | Current image names: `MicrosoftWindowsServer:WindowsServer:2022-datacenter-smalldisk-g2` and `…:2025-datacenter-smalldisk-g2` (and `-core-` variants); `Canonical:ubuntu-24_04-lts:server`. | `az vm image list-skus -l eastus2 …` | 2026-11-11 |
| A14 | `Install-ADDSForest -DomainName … -InstallDns -DatabasePath … -LogPath … -SysvolPath …` creates a new forest and restarts the server; `Add-Computer -DomainName … -OUPath … -Credential … -Restart` joins a machine. | learn.microsoft.com/en-us/powershell/module/addsdeployment/install-addsforest; …/microsoft.powershell.management/add-computer | 2026-11-11 |
| A15 | `Set-GPRegistryValue` puts a registry-based setting in a GPO; `gpresult /r` shows the resulting set of policy on a machine. | learn.microsoft.com/en-us/powershell/module/grouppolicy/set-gpregistryvalue; learn.microsoft.com/en-us/windows-server/administration/windows-commands/gpresult | 2026-11-11 |
| A16 | Domain-joined Windows machines take their time from the domain's own hierarchy; Azure hosts pass accurate time to VMs. | learn.microsoft.com/en-us/azure/virtual-machines/windows/time-sync | 2026-11-11 |

### 12.4 Guardrails first, then the build

The spec puts budgets and alerts in Module 8, six modules after this lab (the audit's finding). So this lab carries its own, and they come before anything that bills. Because Module 8's vocabulary hasn't been taught, the runbook defines each word as it appears: subscription, resource group, tag, region, virtual network, subnet, network security group.

**Reaching the VMs safely, and why this way.** Three options were weighed:

| Option | Cost | Verdict |
| --- | --- | --- |
| Bastion Developer | Free | **Chosen.** No public address on any VM, nothing to open to the internet. One connection at a time and portal only, which is enough here. |
| Bastion Basic | $0.19 an hour, more than all three VMs together | The fallback if Developer misbehaves: $0.57 for a sitting. It bills until deleted. |
| A public address on each VM with RDP limited to the learner's own address | About half a cent an hour each | Rejected: it puts a domain controller on the internet behind one rule, and a home address changes. |
| Just-in-time access | Needs Defender for Servers Plan 2, a paid plan (A5) | Rejected. |

**Steps.** Shown as they would be given; arguments are from the CLI's help, and none of this has been run.

```bash
# 0. Which subscription am I in? Stop here if it isn't the practice one.
az account show --query name -o tsv

RG=csa-hw-windows-ad
LOC=eastus2
TAG=topic=csa.hw.windows-ad

# 1. One resource group: everything goes in it, so one delete removes everything.
az group create -n $RG -l $LOC --tags $TAG

# 2. A budget on the group with an email at 80% of $5. An alert, not a cap (A10).
#    The exact shape of --time-period and --notifications is to be confirmed
#    on the first run (the command is in preview); the portal is the fallback.
az consumption budget create-with-rg -g $RG --budget-name $RG --amount 5 \
  --category Cost --time-grain Monthly \
  --time-period start-date=2026-11-01 end-date=2027-11-01 \
  --notifications "{actual80:{enabled:true,operator:GreaterThanOrEqualTo,threshold:80,contact-emails:[YOU@example.com]}}"

# 3. The network. The security group gets no rules of its own: Azure's
#    defaults allow traffic inside the virtual network and deny the internet.
az network nsg create -g $RG -n nsg-servers --tags $TAG
az network public-ip create -g $RG -n pip-nat --sku Standard --tags $TAG
az network nat gateway create -g $RG -n nat-lab --public-ip-addresses pip-nat --idle-timeout 4 --tags $TAG
az network vnet create -g $RG -n vnet-lab --address-prefixes 10.20.0.0/24 --tags $TAG
az network vnet subnet create -g $RG --vnet-name vnet-lab -n servers \
  --address-prefixes 10.20.0.0/26 --nsg nsg-servers --nat-gateway nat-lab

# 4. The domain controller: no public address, a fixed private one, a small
#    data disk with caching off for the directory database (A9).
read -s -p "Admin password: " PW
az vm create -g $RG -n dc1 --size Standard_B2s \
  --image MicrosoftWindowsServer:WindowsServer:2022-datacenter-smalldisk-g2:latest \
  --admin-username labadmin --admin-password "$PW" \
  --vnet-name vnet-lab --subnet servers --private-ip-address 10.20.0.4 \
  --public-ip-address "" --nsg "" --storage-sku StandardSSD_LRS \
  --data-disk-sizes-gb 4 --data-disk-caching None --tags $TAG
az vm auto-shutdown -g $RG -n dc1 --time 0300      # UTC; pick an hour you're asleep
```

Then, in dc1's desktop through Bastion (portal: the VM, Connect, Bastion), in PowerShell as administrator. Each line gets a sentence in the runbook:

```powershell
# 5. Prepare the data disk as F:, add the role, and create the forest.
Get-Disk | Where-Object PartitionStyle -eq 'RAW' | Initialize-Disk -PartitionStyle GPT -PassThru |
  New-Partition -DriveLetter F -UseMaximumSize | Format-Volume -FileSystem NTFS
Install-WindowsFeature AD-Domain-Services -IncludeManagementTools
Install-ADDSForest -DomainName ad.shop.test -DomainNetbiosName SHOP -InstallDns `
  -DatabasePath F:\NTDS -LogPath F:\NTDS -SysvolPath F:\SYSVOL
# It asks for a recovery password, then restarts the server.
```

```bash
# 6. Make the network hand out dc1 as its DNS server, then create the members,
#    which pick that up at first boot (A8).
az network vnet update -g $RG -n vnet-lab --dns-servers 10.20.0.4
az vm create -g $RG -n app1 --size Standard_B2s \
  --image MicrosoftWindowsServer:WindowsServer:2022-datacenter-smalldisk-g2:latest \
  --admin-username labadmin --admin-password "$PW" \
  --vnet-name vnet-lab --subnet servers --private-ip-address 10.20.0.5 \
  --public-ip-address "" --nsg "" --storage-sku StandardSSD_LRS --tags $TAG
az vm create -g $RG -n web1 --size Standard_B1s --image Canonical:ubuntu-24_04-lts:server:latest \
  --admin-username labadmin --generate-ssh-keys \
  --vnet-name vnet-lab --subnet servers --private-ip-address 10.20.0.6 \
  --public-ip-address "" --nsg "" --storage-sku StandardSSD_LRS --tags $TAG
az vm auto-shutdown -g $RG -n app1 --time 0300
az vm auto-shutdown -g $RG -n web1 --time 0300
```

On dc1 again: the people and a policy with something to see.

```powershell
# 7. Two folders, two people, a group, and a GPO that sets one harmless
#    registry value on every server in the Servers folder.
New-ADOrganizationalUnit -Name Servers
New-ADOrganizationalUnit -Name Staff
$pw = Read-Host -AsSecureString
New-ADUser alice -Path 'OU=Staff,DC=ad,DC=shop,DC=test' -AccountPassword $pw -Enabled $true
New-ADUser bob   -Path 'OU=Staff,DC=ad,DC=shop,DC=test' -AccountPassword $pw -Enabled $true
New-ADGroup linux-admins -GroupScope Global -Path 'OU=Staff,DC=ad,DC=shop,DC=test'
Add-ADGroupMember linux-admins alice
New-GPO -Name 'Server baseline' | New-GPLink -Target 'OU=Servers,DC=ad,DC=shop,DC=test'
Set-GPRegistryValue -Name 'Server baseline' -Key 'HKLM\Software\Policies\ShopLab' `
  -ValueName Baseline -Type String -Value applied
```

On app1 (through Bastion): `Add-Computer -DomainName ad.shop.test -OUPath 'OU=Servers,DC=ad,DC=shop,DC=test' -Credential SHOP\labadmin -Restart`, then after the restart `gpupdate /force` and `gpresult /r /scope computer`, and look for the registry value.

On web1 (through Bastion's SSH): exactly the local lab's join (`sudo apt install realmd sssd-ad sssd-tools libnss-sss libpam-sss adcli krb5-user`, `sudo realm join -U labadmin ad.shop.test`, `sudo pam-auth-update --enable mkhomedir`, `sudo realm permit -g linux-admins@ad.shop.test`). The point of doing it twice is that it is the same.

Last: run the checker (12.5), then `az group delete -n $RG --yes`, then run the checker's teardown check.

**Time:** about three hours the first time (VM creation about 5 minutes each, the forest about 15 with its restart, the rest typing and reading). Unproven.

### 12.5 How it would be checked

A script on the learner's machine, using the `az` session they already have. It only asks questions. Nothing leaves the machine except which checks passed (ADR-0014): no subscription, tenant, resource or user names.

| Check | How | Rejects |
| --- | --- | --- |
| `guardrails` | `az group show` has the tag; `az consumption budget list -g $RG` shows a budget with an enabled notification; every VM has an auto-shutdown schedule (`az resource list -g $RG --resource-type Microsoft.DevTestLab/schedules`). | Building first and adding guardrails never. |
| `nothing-public` | No network interface in the group has a public address; no inbound rule in any security group allows 3389, 22, 5985 or `*` from `Internet`, `*` or `0.0.0.0/0`. | Opening RDP to the world to get in. |
| `sizes` | Every VM's size is one of the three in 12.2. | A size picked from a tutorial at ten times the price. |
| `domain-up` | Run Command on dc1, one PowerShell script printing compact JSON: `(Get-ADDomain).DNSRoot`, the SRV lookup `Resolve-DnsName -Type SRV _ldap._tcp.ad.shop.test`, the paths of the database and SYSVOL. | A forest with the wrong name; the database left on the OS disk. |
| `network-asks-dc` | `az network vnet show --query dhcpOptions.dnsServers` is dc1's address. | Typing dc1 into each member's hosts file or adapter. |
| `windows-member` | Run Command on app1: `(Get-CimInstance Win32_ComputerSystem).PartOfDomain`, `Test-ComputerSecureChannel`, and its computer object's DN from dc1 is under `OU=Servers`. | Joined into the default container. |
| `policy-applied` | Run Command on app1: the registry value `HKLM\Software\Policies\ShopLab\Baseline` is `applied`, and `gpresult /r /scope computer` names `Server baseline`. | Setting the registry value by hand (then `gpresult` doesn't name the GPO). This is the check Samba can't offer. |
| `linux-member` | Run Command (shell) on web1: `realm list` shows the domain; `kinit -k` with the machine's principal works; `sssctl user-checks alice@… -a acct` succeeds and for bob says permission denied. | Everyone permitted. |
| `torn-down` | Run separately after the delete: `az group exists -n $RG` is `false` and `az resource list --tag topic=csa.hw.windows-ad` is empty. | Stopping the VMs and calling it done. |

Each Run Command takes at least 20 seconds and returns at most 4,096 bytes (A6), so each script prints one short JSON line and the whole check takes two or three minutes.

**One departure from ADR-0014 to accept knowingly:** the ADR says the checker has read-only access. Run Command is not read-only in what it *could* do (it runs a script as System); the checker's scripts only read. A custom role of Reader plus the one run-command action would hold it to that; for a single learner in their own subscription, their own sign-in is simpler.

**In CI** (ADR-0014, section 3): each check is a small Python function over the JSON that `az` returned, tested against saved answers: one set from a correct build, one from each wrong build. Until the owner has run the lab, those files can only be written by hand from the documented output shapes, and must be labelled as such. They prove the functions' logic, not that Azure answers that way.

### 12.6 What stays unproven until the owner runs it once

- Every command in 12.4. The arguments exist (checked in `--help`); whether the lines work together was not tested.
- That `Standard_B2s` promotes a forest comfortably, and how long it takes.
- That a 30 GiB "smalldisk" image has room (`az vm image show` didn't report the disk size, so even the 30 is from the image's name).
- That Bastion Developer connects to VMs in a private subnet behind a security group with only Azure's default rules.
- That Run Command returns output from VMs whose only way out is the NAT gateway.
- The budget command's exact syntax, and whether deleting the group deletes its budget.
- That Ubuntu 24.04's `realm join` behaves against a Windows Server 2022 or 2025 controller as it does against Samba. Ubuntu's guide (F17) says it does; SSSD's Group Policy-based access check, which passed against Samba's default policies, is the part most likely to differ.
- That each check's output fits in 4,096 bytes.
- The real cost. The estimate is arithmetic on list prices.

### 12.7 The Entra ID comparison: what is free, and safe

The learner's Azure subscription already sits in an Entra tenant (F12). Three things can be done at no cost; only the first two are recommended.

1. **Read-only, in the browser, no account at all:** the `entra-discovery-doc` recall item, built on Entra's public sign-in document (F20). Checked like any recall item.
2. **Read-only, in the learner's own tenant, during the Azure lab:** look, change nothing. `az ad signed-in-user show --query userPrincipalName`; `az rest --method get --url https://graph.microsoft.com/v1.0/organization --query "value[0].verifiedDomains[].name"`; decode the middle part of `az account get-access-token --query accessToken -o tsv` and read `iss`, `aud`, `exp` beside a `klist` from web1: a signed token from an HTTPS endpoint against a ticket from a KDC. And on app1, `dsregcmd /status`: `DomainJoined : YES`, `AzureAdJoined : NO`. None of this can be sent to the platform (it contains the tenant's identity), so it is a guided look inside the lab's runbook, not a check.
3. **Writes to the tenant: not recommended.** Creating a test user, or Entra-joining a VM with the `AADLoginForWindows` extension, costs nothing but leaves objects in the tenant the owner really uses; a joined VM's device object outlives the VM. A separate practice tenant would be the clean answer, but only paid customers can create one (F13), and whether this subscription counts was not tested. Leave both to Module 10, which is about Entra, and where the spec's open question on the sign-in labs' identity provider gets decided.

## 13. How the topic and the checkpoint use the two layers

- **Everything the topic needs to be `ready` is in layer (a):** the worked example, 24 or so recall items, the fill-in, the write, the build, the debug and the explain. The validator's ladder rules are met with local labs alone, exactly as Module 1's topics meet them.
- **The Azure lab sits outside `practice`, `prove` and the review pool until it has been run once.** The lesson links to its runbook under a heading that says what it is: optional, about $0.60 and three hours, real Windows, not yet run by anyone. Nothing in the topic's progress depends on it, and no proof claims it.
- **The explain prompt asks for the Samba limit** (rubric point `samba-limit`), so a learner who stops at layer (a) has still said in their own words what they haven't seen.
- **After the owner's first run** (with their go-ahead, since it spends credit): save the answers the checker got, replace the hand-written test files with them, fix the runbook where it was wrong, and only then give the lab a place in the ladder: as a second, optional build in this topic, and as a fresh version of Checkpoint 2 part 3 (see `csa.m2.checkpoint.part3.md`).

## 14. Platform work

**None is needed for layer (a).** The labs run in the checker as it is: `runtime: lab`, `lab: { init: systemd }`, checks as commands, a solution and wrong fixes. Things to know, none blocking:

- **CI time.** A contract run took 440 to 504 seconds a lab here (6 or 7 container starts at about 60 seconds each, on a machine other work was sharing). Five labs are 35 to 40 minutes on one shard. Keep wrong fixes to four or five a lab, or give this topic's labs a shard to themselves.
- **A third shared image layer.** The topic's packages add 160 MB and about 75 seconds to the first build (486 MB against Module 1's 325 MB). Every lab in the topic and in Checkpoint 2 part 3 must keep the second `RUN` line identical so it is built once.
- **The audit's open items matter more here:** the `docker exec` line `labcheck start` prints is mangled by Git Bash (every lab), and `start` silently wipes a lab in progress (these labs take an hour).

**For layer (b), the smallest thing that would do:**

1. `tools/cloudcheck.py` beside `labcheck.py`: a list of checks, each one `az` command with `-o json` and a small Python function over the result; `check` prints the same result JSON the lab page already accepts; `--record DIR` saves the answers with names and identifiers scrubbed; `test` replays saved answers (CI).
2. A content marker so the lab can live in `content/` without the Docker contract: `runtime: cloud` on the exercise, with the validator checking structure only and CI running the replay. Until that exists, the runbook and the script live outside the ladder and record nothing.

**Useful to both, already suggested by the audit:** a validator warning when a multiple-choice answer is the longest choice by half again or more. This brief's rule for distractors is easy to break without it.

**For Checkpoint 2:** the content model's `prove` holds one build and one debug, and the checkpoint has three parts. See the checkpoint brief.

## 15. Cost, time and open questions

**Cost.** Layer (a): nothing. Layer (b): about $0.60 a sitting from the Azure credit; nothing from the AWS or Google Cloud free tiers is used. AI: one explain grading, as every topic.

**Time.**

| Part | Minutes |
| --- | --- |
| Required reading (section 7) | 110 |
| The lesson's own intro and recap | 15 |
| Recall, 24 items | 35 |
| Worked example | 40 |
| Fill-in | 25 |
| Write | 30 |
| Build | 40 |
| Debug | 45 |
| Explain | 15 |
| **Total, layer (a)** | **355: set `estimated_minutes: 360`** |
| Azure extra | 180 more |

**Open questions, each with a recommendation under the owner's rule (best learning and retention; free or inside the Azure credit).**

1. **Split the topic?** Six hours is three to four times a Module 1 topic. *Recommend: yes, into two topics of about three hours,* because shorter topics get their first reviews sooner and a learner isn't holding six skills at once. A: "Active Directory: domains, names and tickets" (`directory-structure`, `dc-discovery`, `kerberos-tickets`; the worked example to the end of the clock step; the fill-in; a new build and debug about tickets, for which the Kerberos-over-SSH step in 16.5 and the reverse-record fault are ready material). B: "Joining machines, Group Policy and Entra ID" (the other three skills; the join build and the debug as built here; the write). It means a spec change (a 21st topic in the module) and two more proofs to write. If the spec must stay as it is, keep one topic and tell the learner in the intro that it is three sittings, with the seam after the fill-in.
2. **The domain's name.** The prototype uses `ad.shop.test` (reserved for testing, F19). `ad.shop.internal` would show the real rule, "a subdomain of a name you control" (F18), since the site's names are already `shop.internal`. *Recommend: keep `.test`* as tested; the rename is cheap but means running every contract again.
3. **Who runs the Azure lab first, and when.** It spends the owner's credit, so it needs the owner's go-ahead (CLAUDE.md, and the spec's "the owner approves each run"). *Recommend: put it in `docs/owner-queue.md` as one priced item: about $0.60, three hours, guardrails first.* An agent must not run it alone.
4. **NAT gateway or public addresses for outbound.** The gateway is the bulk of the forgotten-lab cost. A public address on `web1` alone (half a cent an hour) would do for its package installs if Run Command turns out to work without outbound access on the Windows VMs. *Recommend: the NAT gateway for the first run,* because it is what an architect should reach for now that default outbound access is gone (A7); revisit with the first run's evidence.
5. **Windows Server 2022 or 2025, desktop or Core.** *Recommend 2022 with a desktop on B2s for the first run:* it is the release the documentation's examples assume and a beginner can see what they are doing. 2025 asks for more memory (F21).
6. **Kerberos single sign-on over SSH** works in the prototype with two settings (16.5). *Recommend: use it in topic A if the topic is split; leave it out of the single topic,* which is long enough.
7. **A local Windows Server evaluation in Hyper-V** on the owner's Windows 11 Pro machine would be free and real Windows, as the audit noted. *Recommend: not now.* It can't be checked in CI, needs a multi-gigabyte download and a second learner may not have Hyper-V; the Azure extra costs cents and teaches cloud habits on the way.

## 16. The prototype: what was tried, and what happened

Everything here ran on this machine on 2026-11-10 and 11: Docker Desktop, engine 29.8.2, Linux containers on WSL 2, 8 CPUs, 16 GB, shared with other agents' containers. Folder: `proto-windows-ad/`.

### 16.1 The image

- **Base:** `ubuntu:24.04`, with Module 1's shared first `RUN` line unchanged, so that layer is reused.
- **The topic's layer** (one more `RUN`, identical in every lab of the topic): `samba-ad-dc samba-ad-provision samba-dsdb-modules samba-vfs-modules winbind krb5-user smbclient ldb-tools ldap-utils libsasl2-modules-gssapi-mit realmd polkitd sssd-ad sssd-tools libnss-sss libpam-sss adcli faketime sshpass`, then `systemctl disable smbd nmbd winbind samba-ad-dc sssd`.
- **Versions installed:** Samba 4.19.5 (`2:4.19.5+dfsg-4ubuntu9.8`), SSSD 2.9.4, realmd 0.17.1, adcli 0.9.2, MIT Kerberos 1.20.1, faketime 0.9.10.
- **Size:** 486 MB. The topic's layer took 75 seconds to install.
- **Files** (`proto-windows-ad/common/`): `network.sh` and `lab-network.service` (the namespace `dc`, a veth pair, the site resolver, and `lab`'s own `/etc/hosts` and `/etc/resolv.conf`); `dc-enter` and `on-dc` (enter dc1's network, hostname and mount namespaces with its own `/etc/samba` and `/var/lib/samba`); `dc-provision.sh`, `dc-seed.sh` and `lab-dc.service` (create the domain at first boot, start Samba, add people and a reverse zone); `site.conf` (dnsmasq); `realmd.conf`.

### 16.2 How dc1 is made

One container, two machines. `lab` is the container itself. `dc1` is a network namespace joined by a veth pair (10.0.9.1 to 10.0.9.10), entered with `ip netns exec dc unshare --uts --mount …`, which gives it its own hostname and, by bind mounts, its own Samba state under `/srv/dc`. `ip netns exec` also puts `/etc/netns/dc/resolv.conf`, `hosts` and `samba/` over the files in `/etc`. Samba runs there as a systemd unit of the lab machine (`Type=notify`). From `lab`, dc1 is another host: it answers on 53, 88, 389, 445, 464, 636 and 3268 at its own address and nowhere else.

### 16.3 Results under the real checker

`run_contract.py` imports the repository's `tools/labcheck.py` and calls its `test_lab()` on a lab folder outside the repository. Nothing in the repository was written.

| Lab | Result | Time |
| --- | --- | --- |
| `csa.hw.windows-ad/build-join-the-domain` | Contract kept, first run. Pristine: 2 of 7 checks pass. Solution: 7 of 7. Five wrong fixes, each failing the checks intended: `dns-only` (joined and both logins), `everyone-can-log-in` (`bob-kept-out`), `hard-coded` (`finds-the-dc` only), `no-home-directory` (both logins), `only-alice` (`carol-logs-in`). | 504 s including the image build |
| `csa.hw.windows-ad/debug-nobody-can-log-in` | Contract kept. Pristine: 2 of 7. Solution: 7 of 7. Four wrong fixes: `forgot-the-rule` (`bob-kept-out`), `not-rejoined` (four checks), `resolver-bypassed` (`finds-the-dc` only), `ssh-rule-deleted` (`ssh-still-restricted`). | 440 s |
| `csa.m2.checkpoint/build-stand-up-the-domain` | See `csa.m2.checkpoint.part3.md`. | |

**Reliability.** Eight containers started four at a time (what CI does), each booted, joined with the reference solution, logged alice in and refused bob: 8 of 8, booting in 68 to 72 seconds each under that load and 14 to 34 seconds alone. With the two contract runs and the manual sessions, about thirty container starts and no failure. The checker's boot limit is 480 seconds.

**Timings to plan around:** provisioning a domain, 23 to 24 seconds; Samba's start, 1 second, and its DNS about a second after it reports ready (scripts must wait for it); `realm join`, 1 to 4 seconds; a domain user's first SSH login, up to 8 seconds; later ones, 1 to 4. All far inside the checker's 30 seconds a check.

### 16.4 What did not work, and what was done about it

| Tried | What happened | Resolution |
| --- | --- | --- |
| Creating the domain while the image is built | `samba-tool domain provision` fails without privileges: `set_nt_acl_conn: fset_nt_acl returned NT_STATUS_ACCESS_DENIED` (it stores Windows permissions on SYSVOL in a way a build isn't allowed to). | Provision at first boot, in the privileged container: 24 seconds added to every start. |
| `realm` as installed | `realm: Couldn't discover realms: Not authorized to perform this action`. | Install `polkitd`. |
| `realm join` as installed | `Necessary packages are not installed`: on Ubuntu, realmd asks PackageKit whether SSSD is present, and a server image has no PackageKit. `automatic-install = no` alone doesn't help. | `/etc/realmd.conf` gives a file path for each package, so realmd can see for itself. The path contains the machine's architecture; the Dockerfile fills it in. Tested on x86-64 only. |
| `ldapsearch -Y GSSAPI` straight after the first provision | `Server not found in Kerberos database`: the LDAP client turned the DC's name into its address and back, found no reverse record, and asked for a ticket for `ldap/10.0.9.10`. | The seed adds a reverse zone and a PTR record. (`ldapsearch -N` also works.) Kept as a recall item, and it is ready material for a fault. |
| Clock skew with `faketime` | `faketime -f '+10m' kinit alice` **succeeded**. MIT's client corrects for its own wrong clock from the KDC's reply (`kdc_timesync`, F3). | With `kdc_timesync = 0` in a three-line config: 299 seconds off works, 301 fails with `Clock skew too great`. The worked example uses that and says why. |
| Clock skew as a planted fault | Not possible honestly. Every namespace in a container shares the kernel's clock, so dc1 and `lab` can't disagree; and `date -s` in a privileged container would move the clock of Docker's whole VM. | Skew is shown in the worked example and asked about in recall. It isn't in the debug. **The lesson must say never to set the date in a lab.** |
| A domain user's UID in a check | It differs on every boot: SSSD derives UIDs from the domain's SID, which is new with every provision. | Checks never mention a UID, SID or GUID; they use names. |
| A member's short hostname | With `lab` as the whole name, `adcli` registers only `host/LAB`, and Kerberos over SSH has no full name to ask for. | `network.sh` writes `10.0.9.1 lab.ad.shop.test lab` to `/etc/hosts` (Docker's mount is replaced, as the networking labs replace `resolv.conf`). |
| Fetching the Samba wiki from a script | HTTP 429. | Read through the fetch tool instead. |

Not tried: an ARM machine; GitHub's runners (Module 1's systemd and namespace labs already run there privileged, which is the same footing); a second DC; a trust between two domains (`samba-tool domain trust` exists, with create, validate and namespaces subcommands, and was not exercised).

### 16.5 Captured output, for fixtures

Real output from the prototype, to copy into recall items' `files:`. Times and the domain's SID will differ in any new run; the shapes won't.

```text
$ dig +short @10.0.9.10 _ldap._tcp.ad.shop.test SRV        0 100 389 dc1.ad.shop.test.
$ dig +short @10.0.9.10 _kerberos._tcp.ad.shop.test SRV    0 100 88 dc1.ad.shop.test.
$ dig +short @10.0.9.10 _gc._tcp.ad.shop.test SRV          0 100 3268 dc1.ad.shop.test.
$ dig +short @10.0.9.10 _kpasswd._tcp.ad.shop.test SRV     0 100 464 dc1.ad.shop.test.
$ dig @10.0.9.10 _ldap._tcp.ad.shop.test SRV   (answer section)
_ldap._tcp.ad.shop.test. 900	IN	SRV	0 100 389 dc1.ad.shop.test.
$ dig _ldap._tcp.ad.shop.test SRV   (through the site resolver)
;; ->>HEADER<<- opcode: QUERY, status: NXDOMAIN, id: 38951
$ realm discover ad.shop.test       (through the site resolver)
realm: No such realm found: ad.shop.test
```

```text
kinit: Cannot find KDC for realm "AD.SHOP.TEST" while getting initial credentials
kinit: Password incorrect while getting initial credentials
kinit: Client 'carol@AD.SHOP.TEST' not found in Kerberos database while getting initial credentials
kinit: Client's credentials have been revoked while getting initial credentials      (account disabled, or expired)
kinit: KDC reply did not match expectations while getting initial credentials        (realm typed in lower case)
kinit: Clock skew too great while getting initial credentials                        (kdc_timesync = 0, six minutes off)
kinit: Preauthentication failed while getting initial credentials                    (kinit -k with a stale keytab)
```

```text
$ klist
Ticket cache: FILE:/tmp/krb5cc_1001
Default principal: alice@AD.SHOP.TEST

Valid starting     Expires            Service principal
11/11/26 07:51:28  11/11/26 17:51:28  krbtgt/AD.SHOP.TEST@AD.SHOP.TEST
	renew until 11/12/26 07:51:28
11/11/26 07:51:28  11/11/26 17:51:28  ldap/dc1.ad.shop.test@
	renew until 11/12/26 07:51:28
	Ticket server: ldap/dc1.ad.shop.test@AD.SHOP.TEST
```

```text
$ ldapsearch -x -H ldap://dc1.ad.shop.test -D alice@ad.shop.test -w … 
ldap_bind: Strong(er) authentication required (8)
	additional info: BindSimple: Transport encryption required.
$ ldapsearch -Q -LLL -Y GSSAPI -H ldap://dc1.ad.shop.test -b DC=ad,DC=shop,DC=test '(sAMAccountName=alice)' dn sAMAccountName userPrincipalName memberOf
dn: CN=Alice Ng,CN=Users,DC=ad,DC=shop,DC=test
sAMAccountName: alice
userPrincipalName: alice@ad.shop.test
memberOf: CN=linux-admins,CN=Users,DC=ad,DC=shop,DC=test
$ ldapwhoami -Q -Y GSSAPI -H ldap://dc1.ad.shop.test
u:SHOP\alice
```

```text
$ sudo realm join -v -U Administrator ad.shop.test      (selected lines)
 * Resolving: _ldap._tcp.ad.shop.test
 * Performing LDAP DSE lookup on: 10.0.9.10
 * Successfully discovered: ad.shop.test
 * Calculated computer account name from fqdn: LAB
 * Authenticated as user: Administrator@AD.SHOP.TEST
 * Looked up short domain name: SHOP
 * Generated 120 character computer password
 * Using keytab: FILE:/etc/krb5.keytab
 * A computer account for LAB$ does not exist
 * Found well known computer container at: CN=Computers,DC=ad,DC=shop,DC=test
 * Created computer account: CN=LAB,CN=Computers,DC=ad,DC=shop,DC=test
 * Set computer password
 * Added the entries to the keytab: LAB$@AD.SHOP.TEST: FILE:/etc/krb5.keytab
 * Added the entries to the keytab: host/LAB@AD.SHOP.TEST: FILE:/etc/krb5.keytab
 * Added the entries to the keytab: RestrictedKrbHost/LAB@AD.SHOP.TEST: FILE:/etc/krb5.keytab
 * Successfully enrolled machine in realm
```

```text
sshd: pam_sss(sshd:auth): authentication success; logname= uid=0 euid=0 tty=ssh ruser= rhost=127.0.0.1 user=bob@ad.shop.test
sshd: pam_sss(sshd:account): Access denied for user bob@ad.shop.test: 6 (Permission denied)
sshd: Failed password for bob@ad.shop.test from 127.0.0.1 port 44404 ssh2
sshd: fatal: Access denied for user bob@ad.shop.test by PAM account configuration [preauth]

sssd: ldap_child: Failed to initialize credentials using keytab [MEMORY:/etc/krb5.keytab]: Preauthentication failed. Unable to create GSSAPI-encrypted LDAP connection.
adcli update:  ! Couldn't authenticate as machine account: LAB: Preauthentication failed
realm join (while still joined): realm: Already joined to this domain

sshd: Accepted gssapi-with-mic for alice@ad.shop.test from 10.0.9.1 port 59592 ssh2: alice@AD.SHOP.TEST
```

The last line is Kerberos single sign-on over SSH. It needs `GSSAPIAuthentication yes` in `sshd`'s configuration and `includedir /var/lib/sss/pubconf/krb5.include.d/` at the top of `/etc/krb5.conf`; then `klist` gains `host/lab.ad.shop.test@AD.SHOP.TEST`.

```text
$ on-dc samba-tool gpo list alice        (alice in OU=Engineering,OU=Staff)
GPOs for user alice
    Engineering tools {39929F04-46BD-460F-A116-87E9E08BB7DF}
    Lock screen 10 min {6A2EECF7-B9FC-45E0-A395-3359C850E3E3}
    Default Domain Policy {31B2F340-016D-11D2-945F-00C04FB984F9}
$ on-dc samba-tool gpo list bob          (bob in OU=Staff)
    Lock screen 10 min {…}
    Default Domain Policy {…}
$ on-dc samba-tool gpo list carol        (carol in CN=Users)
    Default Domain Policy {…}
after "gpo setinheritance OU=Engineering,… block":      alice gets only Engineering tools
after relinking Lock screen to OU=Staff with --enforce: alice gets Engineering tools and Lock screen 10 min
```

```text
$ on-dc samba-tool domain passwordsettings show
Password complexity: on
Password history length: 24
Minimum password length: 7
Minimum password age (days): 1
Maximum password age (days): 42
Account lockout duration (mins): 30
Account lockout threshold (attempts): 0
after "passwordsettings set --min-pwd-length=14", creating a user with a 7-character password:
ERROR(ldb): Failed to add user 'erin':  - 0000052D: Constraint violation - check_password_restrictions: the password is too short. It should be equal or longer than 14 characters!
```

Entra's public sign-in document (F20), the six keys to keep: `issuer` `https://login.microsoftonline.com/{tenantid}/v2.0`; `authorization_endpoint` `https://login.microsoftonline.com/common/oauth2/v2.0/authorize`; `token_endpoint` `…/common/oauth2/v2.0/token`; `jwks_uri` `…/common/discovery/v2.0/keys`; `id_token_signing_alg_values_supported` `["RS256"]`; `scopes_supported` `["openid","profile","email","offline_access"]`.

## 17. Not confirmed

Things this brief states or implies that I could not verify, so the writer knows where to look again.

- **R1's content.** I confirmed the training module exists, has eight units and is listed at 60 minutes. I did not read the units, so "the best main resource for a beginner" is a judgement from its outline.
- **The Windows wording** of the stale-machine-account error ("the trust relationship between this workstation and the primary domain failed") is from memory. Don't print it without finding it on a Microsoft page.
- **The AWS and Google Cloud cells for DNS** in 5.3 (DHCP option sets, Route 53 Resolver rules, Cloud DNS forwarding zones) are from memory.
- **Which Windows Server release AWS Managed Microsoft AD runs on:** the page states one; my fetch cut the sentence off. Say "Windows Server" without a year.
- **Licences:** Ubuntu's server documentation (none found); the Entra documentation repository (its licence file is MIT, which normally covers code); AWS's documentation (no open licence found). All three are linked only, which is safe whatever the answer.
- **The price of the 4 GiB data disk** wasn't looked up; the total uses a 32 GiB disk's price as an upper bound.
- **Everything in 12.6.**
- **CI.** The labs ran on this machine only. GitHub's runners should behave the same (privileged systemd containers with network namespaces already run there for Module 1), but Samba's use of extended attributes on the runner's filesystem is untested.
