# ADR-0014: Proving cloud skills with labs in the learner's own clouds

- **Status:** Accepted (2026-11-09)
- **Date:** 2026-11-08

## Context

The owner asked for a Cloud Solutions Architect track ([spec](../specs/cloud-solutions-architect.md)). It has to prove competency, not just knowledge, across AWS, Azure and Google Cloud, up to the top of the senior pay band. The learner has accounts on all three clouds for practice.

The platform's rules weren't written with cloud work in mind:
- Every topic needs four proofs, including building from a blank editor and debugging unfamiliar work ([ADR-0002](0002-mastery-and-gating.md)).
- Every exercise is machine-verified in CI: its reference solution passes, and known-wrong solutions fail ([ADR-0004](0004-content-model.md)).
- Exercises run as Python in the browser, through the harness. The harness can't build a network on AWS, or check one.
- Hosting stays on free tiers ([ADR-0005](0005-free-hosting-first.md)), so the platform can't run cloud sandboxes for learners.

Certification-style knowledge tests are what this track exists to go beyond. A senior architect is judged on whether the network actually routes, whether the failover actually finishes within its RTO, and whether the design survives questioning.

## Decision

### 1. Seven kinds of proof

| Kind | Where it runs | How it's checked |
|---|---|---|
| Drills (subnetting, policy evaluation, availability, cost, capacity) | The browser, as Python exercises in the existing harness | Hidden tests, as today |
| Code katas (infrastructure as code from a blank file) | The learner's machine | Offline: OpenTofu's test framework with mocked providers, and policy checks on the plan |
| Lab builds | The learner's sandbox accounts | The lab checker, live |
| Break-fix | The learner's sandbox, broken by a fault module the learner applies | The lab checker: the symptoms are gone, and the fix is right |
| Explanations, designs and postmortems | The browser | AI grades them against a rubric, through the AI proxy ([ADR-0013](0013-explain-grading.md)). Code checks the numbers in a design. |
| Game days | The learner's sandbox, with a failure the learner sets off | The lab checker measures time to detect and recover, and data lost |
| Defend it | The browser | AI plays stakeholders, then grades the answers against a rubric |

### 2. The lab checker

The lab checker is a Python command-line tool in this repository (`labs/`), run on the learner's machine.

- **Least privilege.** It uses its own identity in each sandbox, with read-only roles (for example AWS `ReadOnlyAccess`, Azure Reader and Google Cloud Viewer). It also gets permission to run each lab's probes, which are small functions the lab deploys inside the network, and the clouds' policy simulators and path-analysis tools. It can't change the learner's resources.
- **Credentials stay local.** It signs in the clouds' usual local ways: SSO profiles, `az login`, `gcloud auth`. The platform never sees credentials, account IDs or resource names. It receives only:
  - which lab was checked;
  - the checker's version;
  - which checks passed, with timings.
- **Checks are small Python functions.** They read what the cloud APIs return and run probes: an HTTP request, a DNS lookup, a policy-simulator question about an action that must be denied. Each check names the skill it tests (`topic/skill`), so a failed check brings that skill back ([ADR-0011](0011-mistakes-come-back.md)).
- **Teardown is a check.** Every lab tags what it creates with its topic ID, and the last check confirms that nothing tagged is left.

How results reach the platform is decided when the checker is built. The learner could paste a code, or the checker could send them while the learner is signed in. While the owner is the only learner, results are trusted as they are. Results get signed before any public launch, as in-browser hidden tests will be.

### 3. Verified in CI without touching a cloud

ADR-0004 still holds. CI tests the checks, not the cloud:
- **Each check is tested against recorded API responses.** A recording from a correct build must pass, and one from each known-wrong build must fail. Account IDs and names are scrubbed from recordings.
- **Code katas and fault modules** go through OpenTofu's offline tests and policy checks.
- **Every lab is run once for real.** Before a lab is marked `ready`, its author runs it end to end in a sandbox and records the responses. That costs money, so the owner approves each run.

### 4. Cost and safety

- Labs run only in sandbox accounts, subscriptions and projects, never in production or an employer's.
- The track's first cloud lab sets budgets, alerts and region restrictions, before anything else is built.
- Every lab states its expected cost and how long it runs.
- Expensive or physical things, such as dedicated circuits and large GPU clusters, are designed and reviewed, then practised with a stand-in.
- The learner applies fault modules and game-day failures themselves, with their own credentials, from code they can read. The checker never breaks anything.
- To keep the test fair, each fault module picks its faults at random from a published list. The learner can audit everything a module could do without knowing which faults it chose. Looking spoils the exercise, just as reading hidden tests would.

### 5. Tools

- **Clouds:** AWS, Microsoft Azure and Google Cloud.
- **Infrastructure as code:** Terraform's language (HCL). CI checks it with OpenTofu, which is open source (MPL 2.0). Learners can use either tool, and each cloud's own tool is taught once.
- **Automation and checks:** Python, the platform's first language.
- **Portable layers, used throughout:** Kubernetes, OpenTelemetry and open data formats.

### 6. AI

- **The tutor rules don't change** ([ADR-0003](0003-ai-roles-and-guardrails.md)): hints only, and off during proofs.
- **AI grades explanations, designs and postmortems** through the AI proxy. Each rubric gets its own test set before it's used, as ADR-0013 did.
- **A new role: the examiner.** In "Defend it", AI plays stakeholders who question a design. It asks and never helps. It's part of the proof, so unlike the tutor it's on during the check.

## Alternatives considered

- **Knowledge tests only.** These are cheap and easy to verify, but they measure recognition, which is the gap this track exists to close.
- **Sandboxes hosted by the platform.** These would give the strongest checks, but the platform can't carry the cloud bills or the abuse risk on free tiers (ADR-0005).
- **Third-party lab platforms.** Their labs are good, but they're paid and closed, and their results can't feed the platform's proofs and reviews.
- **Offline code checks only.** These are free and fast, but they can't show that a network routes, that a failover happens or that a fix works. They're kept for drills and reviews.
- **Screenshots graded by AI.** These are easy to fake, and they show the console, not how the system behaves.
- **Self-reported completion.** ADR-0002 rules this out.

## Consequences

- The track can prove real skill, including speed, on real clouds, at no hosting cost to the platform.
- There are new things to build:
  - support for more than one track in the app;
  - the lab checker;
  - tests against recorded responses;
  - fault modules and game-day modules.

  All of this comes after v1, which is Python only.
- New kinds of learner events are needed: lab checks, design submissions and game-day results. They stay append-only ([ADR-0008](0008-event-log.md)), and they're defined when they're built.
- Learners need local tools: Python, OpenTofu or Terraform, the three cloud CLIs and Docker. They also pay for their own labs, within the guardrails.
- The checks need upkeep as cloud APIs change. Recordings get refreshed, and the checker pins its SDK versions.
- There will be more AI grading. Designs are longer than explanations and may need a bigger model, so the $10 monthly cap may need revisiting with the owner.
