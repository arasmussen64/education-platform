# Senior Cloud Architect Knowledge Map & Learning Roadmap

Nov 8, 2026 · @Alex Rasmussen

## How to use this roadmap

A senior cloud architect is not someone who knows every service; it is someone who can take a vague business problem and turn it into a system that is secure, resilient, observable, and affordable, then defend every trade-off to a CFO and a kernel engineer in the same meeting. This map lists what that person knows, grouped into 12 domains, so you can audit yourself and sequence your study.

**Depth levels.** Every item below is implicitly tagged at one of three levels. Decide which level each item needs for you before you study it.

| Level | Meaning | Test |
| --- | --- | --- |
| L1 Aware | You know it exists, what problem it solves, and when to bring in a specialist | Can explain it in two sentences to a non-expert |
| L2 Working | You have built or operated it hands-on at least once | Can set it up from a blank account without a tutorial |
| L3 Deep | You can design, debug, and teach it; you know the failure modes | Can predict how it breaks under load, misconfiguration, or region loss |

**Where you already stand.** With nine years across Dell, Tintri, and Microsoft, Azure networking at Senior Support Engineer depth, and Oracle Database@Azure SME work, Domains 1, 2, and the Azure half of Domain 3 are likely already at L2–L3. Your gaps are most likely in the second-cloud (AWS) fluency that most architect roles screen for, Kubernetes and platform engineering, data and streaming architecture, FinOps, and the business layer in Domain 12. The 24-month sequence near the end is built on that assumption; adjust it after the self-assessment at the bottom.

**Rules for using the list.**

1. Do not try to reach L3 on everything. A senior architect is L3 on roughly a third of this map, L2 on another third, and L1 on the rest. Which third depends on your target role (enterprise infra, app modernization, data platform, security).
2. Learn one cloud deeply and a second cloud comparatively. Pattern knowledge transfers; console knowledge does not.
3. Every concept gets a build. If you cannot deploy it, break it, and fix it in a sandbox, you are at L1 regardless of what you have read.
4. Write as you go. Architecture Decision Records and one-page design docs are both the job and the best study method.

## Domain 1: Computing and OS fundamentals

Everything in the cloud is a Linux box, a hypervisor, or an abstraction hiding one. Architects who skip this layer design systems they cannot debug.

**Linux internals**

- Process model: fork/exec, PIDs, signals, zombies, init systems (systemd units, targets, journald)
- Memory: virtual memory, paging, the OOM killer, swap, huge pages, why a container is OOM-killed before the node is
- CPU scheduling: CFS, nice values, cgroups v2 CPU shares and quotas, CPU throttling in containers
- Filesystems: ext4, XFS, inodes, mount options, LVM, overlayfs (how container layers work)
- Storage stack: block vs file vs object, IOPS vs throughput vs latency, queue depth, fsync and durability
- Networking stack: sockets, TCP state machine, ephemeral ports, conntrack, netfilter/iptables/nftables, network namespaces
- Namespaces and cgroups as the primitives containers are built from
- Shell fluency: bash, awk, sed, grep, jq, strace, tcpdump, ss, lsof, perf, iostat, vmstat
- Package management, patching strategy, immutable vs mutable images, golden image pipelines
- Boot process, cloud-init, user data, instance metadata services (IMDSv2 and why it matters)

**Windows Server (L1–L2 for enterprise work)**

- Active Directory, Group Policy, Kerberos, domain trusts; how Entra ID differs from AD DS
- Windows licensing in cloud (BYOL, hybrid benefit, dedicated hosts)

**Virtualization and hardware**

- Type 1 vs type 2 hypervisors, KVM/QEMU, Hyper-V, Nitro, paravirtualization, SR-IOV
- CPU architectures: x86 vs ARM (Graviton, Ampere, Cobalt), instruction sets, when ARM saves 20–40%
- GPU basics: CUDA cores vs tensor cores, VRAM as the constraint, NVLink, MIG partitioning
- NUMA, vCPU vs physical core, hyperthreading, noisy neighbors, burstable credits
- Memory tiers, NVMe, local ephemeral disk vs network-attached disk

**Compute theory**

- Amdahl's law, Little's law, queueing theory basics (utilization vs latency curve)
- Latency numbers every engineer should know (L1 cache to cross-region round trip)
- Concurrency vs parallelism, async I/O, thread pools, connection pools

## Domain 2: Networking

Networking is the domain where most cloud outages and most security breaches actually live. For you this is a strength to formalize rather than build; the items marked (cross-cloud) are where to spend time.

**Core protocols**

- OSI and TCP/IP models as debugging tools, not trivia
- IPv4 subnetting, CIDR math on sight, VLSM, RFC 1918, IPv6 addressing and dual-stack design
- ARP, ICMP, TCP handshake and teardown, window scaling, congestion control (CUBIC, BBR), UDP, QUIC/HTTP3
- DNS deeply: recursion vs authority, record types, TTLs, split-horizon, DNSSEC, negative caching, private zones
- TLS 1.2/1.3 handshake, certificates, chains, SNI, mTLS, OCSP stapling, certificate lifecycle automation (ACME)
- HTTP/1.1 vs 2 vs 3, headers, caching semantics, CORS, WebSockets, gRPC over HTTP/2
- BGP: path selection, communities, route reflection; how it drives Direct Connect/ExpressRoute/Interconnect
- Routing fundamentals: longest prefix match, static vs dynamic, route tables, asymmetric routing pitfalls
- NAT: SNAT, DNAT, port exhaustion, NAT gateway costs, when to avoid NAT entirely

**Cloud networking (cross-cloud)**

| Concept | AWS | Azure | GCP |
| --- | --- | --- | --- |
| Virtual network | VPC (regional) | VNet (regional) | VPC (global) |
| Subnet scope | AZ | Region | Region |
| Peering | VPC peering, Transit Gateway | VNet peering, Virtual WAN | VPC peering, NCC |
| Private service access | PrivateLink, VPC endpoints | Private Link, Private Endpoints, Service Endpoints | Private Service Connect, Private Google Access |
| Dedicated circuit | Direct Connect | ExpressRoute | Cloud Interconnect |
| L7 load balancer | ALB | Application Gateway, Front Door | External HTTP(S) LB |
| L4 load balancer | NLB | Azure Load Balancer | Network LB / passthrough |
| Firewall | Network Firewall, SGs, NACLs | Azure Firewall, NSGs, ASGs | Cloud Firewall, hierarchical policies |
| Global DNS/traffic | Route 53 | Traffic Manager, Azure DNS | Cloud DNS, Cloud Load Balancing |
| CDN/edge | CloudFront | Front Door, Azure CDN | Cloud CDN, Media CDN |

- Hub-and-spoke vs mesh vs Transit Gateway/Virtual WAN; when each breaks down (route table limits, cost)
- IP address management across hundreds of VNets/VPCs, overlapping CIDR remediation, IPAM tooling
- Hybrid connectivity design: redundant circuits, BGP failover, VPN as backup, bandwidth planning, MACsec
- Multi-region and multi-cloud interconnect, egress cost modeling, data gravity
- Stateful vs stateless firewalling, security group design patterns, micro-segmentation
- Network virtual appliances (Palo Alto, Fortinet) vs native firewalls, inspection architectures, Gateway Load Balancer
- Service mesh networking: sidecars (Istio, Linkerd), eBPF-based (Cilium), ambient mesh
- Kubernetes networking: CNI plugins, pod CIDR planning, kube-proxy vs eBPF, ingress controllers, Gateway API, network policies
- DDoS protection tiers, WAF rule design, bot management, rate limiting
- Global anycast, GeoDNS, latency-based routing, health-check design and the failover flap problem
- Zero trust network access (ZTNA) replacing VPN: identity-aware proxies, device posture
- Packet capture and flow log analysis (VPC Flow Logs, NSG flow logs, mirroring)
- SD-WAN integration and branch connectivity
- Network performance: MTU and jumbo frames, bandwidth per instance size, placement groups/proximity groups, accelerated networking/ENA/SR-IOV

## Domain 3: Cloud platform mastery

The goal is to know the *category* at L3 and the *service names* at L2 on your primary cloud and L1–L2 on your secondary. The table maps categories across the big three; the bullets under it are what you must understand about each category regardless of vendor.

| Category | AWS | Azure | GCP |
| --- | --- | --- | --- |
| VMs | EC2 | Virtual Machines, VMSS | Compute Engine, MIGs |
| Containers (managed K8s) | EKS | AKS | GKE (Standard/Autopilot) |
| Containers (serverless) | ECS Fargate, App Runner | Container Apps, ACI | Cloud Run |
| Functions | Lambda | Azure Functions | Cloud Functions / Cloud Run functions |
| PaaS web | Elastic Beanstalk | App Service | App Engine |
| Object storage | S3 | Blob Storage | Cloud Storage |
| Block storage | EBS | Managed Disks | Persistent Disk, Hyperdisk |
| File storage | EFS, FSx | Azure Files, NetApp Files | Filestore |
| Relational (managed) | RDS, Aurora | Azure SQL, Database for PostgreSQL/MySQL | Cloud SQL, AlloyDB, Spanner |
| NoSQL document/KV | DynamoDB | Cosmos DB | Firestore, Bigtable |
| Cache | ElastiCache | Azure Cache for Redis | Memorystore |
| Data warehouse | Redshift | Synapse, Fabric | BigQuery |
| Message queue | SQS | Service Bus, Storage Queues | Pub/Sub |
| Pub/sub events | SNS, EventBridge | Event Grid | Pub/Sub, Eventarc |
| Streaming | Kinesis, MSK | Event Hubs | Pub/Sub, Managed Kafka |
| Workflow orchestration | Step Functions | Logic Apps, Durable Functions | Workflows |
| Secrets | Secrets Manager, Parameter Store | Key Vault | Secret Manager |
| Keys/HSM | KMS, CloudHSM | Key Vault, Managed HSM | Cloud KMS, Cloud HSM |
| Identity | IAM, IAM Identity Center | Entra ID, RBAC | Cloud IAM |
| Monitoring | CloudWatch, X-Ray | Azure Monitor, App Insights | Cloud Monitoring, Cloud Trace |
| IaC (native) | CloudFormation, CDK | ARM, Bicep | Deployment Manager (deprecated), Infra Manager |
| Governance | Organizations, Control Tower, SCPs | Management Groups, Policy, Blueprints/Landing Zones | Resource Manager, Org Policy |
| Migration | MGN, DMS, Snowball | Azure Migrate, Data Box | Migrate to VMs, Transfer Appliance |
| GenAI platform | Bedrock | Azure OpenAI / AI Foundry | Vertex AI |

**Compute: what to know about the category**

- Instance family taxonomy (general, compute, memory, storage, accelerated) and how to right-size from metrics
- Pricing models: on-demand, reserved/savings plans, spot/preemptible, dedicated hosts; spot interruption handling
- Autoscaling: metric-based, scheduled, predictive; scale-in protection; warm pools; cooldowns
- Placement: AZ spread, placement/proximity groups, capacity reservations, zonal vs regional services
- Serverless trade-offs: cold starts, concurrency limits, execution duration caps, state handling, cost cliffs at scale
- Container orchestration choice: managed K8s vs serverless containers vs PaaS, and when each is wrong
- Image pipelines: Packer, golden AMIs/images, image galleries, vulnerability scanning in the pipeline

**Storage**

- Object storage: consistency model, storage classes and lifecycle tiering, versioning, object lock/immutability, multipart upload, presigned URLs, event notifications, cross-region replication, request pricing
- Block storage: IOPS/throughput provisioning, snapshot mechanics (incremental, crash-consistent vs app-consistent), encryption, multi-attach
- File storage: NFS vs SMB, performance tiers, when to use NetApp/FSx ONTAP for enterprise workloads
- Data transfer: egress costs, Snowball/Data Box, storage gateways, transfer acceleration
- Backup: RPO/RTO per tier, backup vaults, immutable backups against ransomware, cross-account/cross-subscription isolation

**Databases (as a category; depth in Domain 6)**

- Managed relational: HA topologies (multi-AZ, zone-redundant, read replicas), failover time, connection pooling (PgBouncer, RDS Proxy), parameter tuning, major version upgrades
- Distributed SQL: Aurora, Spanner, Cosmos DB for PostgreSQL, Yugabyte, CockroachDB; what you pay in latency for global consistency
- Oracle in cloud: RDS for Oracle, Oracle Database@Azure, Exadata Cloud, licensing (you have L3 here; leverage it)
- NoSQL: partition key design, hot partitions, single-table design, consistency tiers, RU/WCU capacity models
- Caching: Redis data structures, eviction policies, cache-aside vs write-through, cluster mode

**Messaging and integration**

- Queue vs topic vs stream; at-least-once vs exactly-once; idempotency; dead-letter queues; ordering guarantees; visibility timeouts
- Event-driven service integration patterns (EventBridge/Event Grid as the enterprise event bus)
- API management: gateways, throttling, versioning, developer portals, API monetization

**Platform-level knowledge**

- Account/subscription/project structure as the primary security and billing boundary
- Regions, availability zones, local zones, edge locations; data residency and sovereign clouds
- Service quotas and limits as a design constraint
- Shared responsibility model and where it shifts per service tier (IaaS → PaaS → SaaS)
- Release lifecycles: preview vs GA, deprecation handling, API versioning
- Reading the SLA fine print: what is actually credited, composite SLA math across dependent services

## Domain 4: Identity, security, and compliance

Security is not a domain; it is a property of every other domain. But architects are expected to own the identity model, the encryption posture, and the compliance story end to end.

**Identity and access**

- Authentication vs authorization; OAuth 2.0 flows (auth code + PKCE, client credentials, device code), OIDC, SAML 2.0, SCIM provisioning
- Entra ID / IAM Identity Center / Cloud Identity as the enterprise IdP; federation; B2B and B2C patterns
- Workload identity: managed identities, IAM roles, workload identity federation, OIDC for CI/CD (no long-lived keys)
- RBAC vs ABAC vs policy-as-code; least privilege as an iterative process (access analyzers, permission boundaries, custom roles)
- Privileged access: PIM/JIT elevation, break-glass accounts, separation of duties
- Conditional access, MFA (phishing-resistant: FIDO2, passkeys), device compliance, risk-based policies
- Cross-account/cross-tenant access patterns, resource-based policies, trust policies, confused deputy problem
- Secrets management and rotation, secret-zero problem, dynamic secrets (Vault)

**Data protection**

- Encryption at rest: envelope encryption, CMK vs platform keys, key hierarchies, key rotation, BYOK/HYOK, HSM tiers
- Encryption in transit: TLS everywhere, mTLS between services, certificate management at scale
- Confidential computing: TEEs, SGX, SEV-SNP, confidential VMs and containers
- Data classification, DLP, tokenization, masking, field-level encryption
- Data residency, sovereignty, and cross-border transfer rules

**Network and infrastructure security**

- Zero trust architecture (NIST 800-207): identity as the perimeter, micro-segmentation, continuous verification
- Defense in depth across edge (WAF/DDoS), network (firewalls, private endpoints), host (hardening, EDR), app, data
- Threat modeling: STRIDE, attack trees, MITRE ATT&CK for cloud, abuse cases in design reviews
- Container and Kubernetes security: image scanning, admission control (OPA/Gatekeeper, Kyverno), pod security standards, runtime security (Falco), RBAC, secrets handling
- Supply chain security: SBOMs, Sigstore/cosign signing, SLSA levels, dependency scanning, provenance attestation
- Vulnerability management, patch SLAs, CVSS vs exploitability (EPSS, KEV)

**Detection and response**

- Cloud-native detection: GuardDuty, Defender for Cloud, Security Command Center; CSPM, CWPP, CNAPP as categories
- SIEM/SOAR (Sentinel, Splunk, Chronicle); log sources that matter; audit log retention and immutability
- Incident response in cloud: forensics on ephemeral infra, snapshotting, isolation playbooks, credential revocation
- Security chaos engineering and purple teaming

**Compliance and governance**

- Frameworks: SOC 2, ISO 27001, PCI DSS 4.0, HIPAA, FedRAMP, CMMC, GDPR, CIS Benchmarks, NIST CSF 2.0 and 800-53
- Mapping controls to cloud services; inheriting controls from the provider; evidence automation
- Policy as code: Azure Policy, SCPs, Org Policy, OPA; preventive vs detective controls
- Shared responsibility documentation for auditors; compliance in regulated industries (financial services, healthcare, public sector)
- Security review process for architectures: what a design review must cover before approval

## Domain 5: Architecture patterns and distributed systems

This is the domain that separates a senior engineer from an architect. Services change every year; these ideas have not changed in twenty.

**Distributed systems theory**

- CAP and PACELC; what "eventual consistency" actually promises; consistency models (linearizable, sequential, causal, read-your-writes)
- The fallacies of distributed computing (all eight, with a real outage story for each)
- Consensus: Paxos and Raft at L1–L2; leader election; quorums; split brain; how etcd, ZooKeeper, and DynamoDB use them
- Time in distributed systems: clock skew, NTP, logical clocks, Lamport and vector clocks, TrueTime
- Partitioning/sharding strategies: hash, range, directory; rebalancing; hot keys; consistent hashing
- Replication: sync vs async, leader-follower vs multi-leader vs leaderless, replication lag, conflict resolution (LWW, CRDTs)
- Idempotency, exactly-once delivery myths, the outbox pattern, deduplication windows
- Two-phase commit vs sagas (choreography vs orchestration), compensating transactions
- Backpressure, load shedding, admission control, bounded queues

**Resilience patterns**

- Timeouts, retries with exponential backoff and jitter, retry budgets, retry storms
- Circuit breaker, bulkhead, fallback, fail-fast vs fail-safe
- Health checks: liveness vs readiness vs startup; shallow vs deep; the deep-health-check cascading failure
- Graceful degradation and feature flags as a resilience tool
- Cell-based architecture and shuffle sharding (blast radius reduction)
- Static stability: designing so the control plane can fail and the data plane keeps serving
- Multi-AZ, multi-region active/passive, active/active; the data layer is always the hard part
- Chaos engineering: hypothesis-driven, steady state, blast radius, GameDays

**Application architecture styles**

- Monolith vs modular monolith vs microservices vs serverless; when microservices are the wrong answer (most of the time for small teams)
- Domain-Driven Design: bounded contexts, aggregates, ubiquitous language, context mapping as the basis for service boundaries
- Event-driven architecture: events vs commands, event sourcing, CQRS, event schemas and registries, schema evolution
- API design: REST maturity, resource modeling, pagination, versioning, gRPC, GraphQL trade-offs, AsyncAPI, OpenAPI-first
- Strangler fig, anti-corruption layer, branch by abstraction for modernization
- Twelve-factor app and its cloud-native successors
- Multi-tenancy: silo vs pool vs bridge models, tenant isolation, noisy neighbor controls, per-tenant cost attribution
- Hexagonal/clean architecture at L1 so you can talk to application teams credibly

**Caching and performance**

- Cache hierarchy: browser, CDN, API gateway, application, database buffer pool
- Cache invalidation strategies, TTL design, cache stampede (thundering herd) and request coalescing
- Read-heavy vs write-heavy patterns, write-behind, materialized views
- Performance testing: load, stress, soak, spike; percentiles (p50/p99/p99.9) over averages; capacity planning

**Enterprise integration**

- Enterprise integration patterns (Hohpe): message router, translator, splitter/aggregator, content-based routing
- Integration styles: file transfer, shared database, RPC, messaging; legacy mainframe/ERP integration realities
- iPaaS, ESB history, and why API-led connectivity replaced it

**Reference frameworks to know cold**

- AWS Well-Architected (6 pillars), Azure Well-Architected, Google Cloud Architecture Framework
- Cloud Adoption Frameworks (AWS CAF, Azure CAF) and landing zone reference architectures
- TOGAF and Zachman at L1 (enterprise architecture vocabulary); C4 model for diagrams; arc42 for documentation

## Domain 6: Data architecture

Data is where cloud bills, compliance exposure, and lock-in concentrate. Most infrastructure architects are weakest here; closing this gap is a differentiator.

**Storage paradigms and when each wins**

- Relational: normalization, indexing (B-tree, hash, GIN, covering), query plans, isolation levels, locking, MVCC, connection limits
- Document, key-value, wide-column, graph, time-series, search (Elasticsearch/OpenSearch), vector; a one-line "use when" for each
- Polyglot persistence and its operational tax
- OLTP vs OLAP vs HTAP; row vs columnar storage; compression and encoding

**Modern data platform**

- Data lake vs warehouse vs lakehouse; open table formats (Apache Iceberg, Delta Lake, Hudi) and why Iceberg won
- File formats: Parquet, ORC, Avro, JSON; partitioning and compaction; small-file problem
- Medallion architecture (bronze/silver/gold); ELT vs ETL; dbt as the transformation standard
- Orchestration: Airflow, Dagster, Prefect; managed equivalents (MWAA, Data Factory, Cloud Composer)
- Ingestion: CDC (Debezium), batch loaders, streaming ingestion, API connectors (Fivetran, Airbyte)
- Warehouses: BigQuery, Snowflake, Redshift, Synapse/Fabric, Databricks SQL; separation of storage and compute; pricing models (on-demand vs slots vs credits)
- Query engines: Spark, Trino/Presto, DuckDB; when a laptop beats a cluster
- Data catalogs, lineage, data contracts, data mesh (domain ownership) vs centralized platform
- Semantic layers and BI tools (Power BI, Looker, Tableau) at L1

**Streaming**

- Kafka fundamentals: topics, partitions, consumer groups, offsets, retention, compaction, exactly-once semantics, Kafka Connect, Schema Registry
- Managed streaming: MSK, Event Hubs (Kafka-compatible), Confluent Cloud, Pub/Sub, Kinesis
- Stream processing: Flink, Spark Structured Streaming, Kafka Streams; windows, watermarks, late data, state stores
- Lambda vs Kappa architecture; when batch is still correct

**Data governance and lifecycle**

- Data classification and ownership; PII discovery; retention and deletion (right to be forgotten in an immutable lake)
- Master data management, data quality frameworks (Great Expectations, Soda), observability for data pipelines
- Backup, point-in-time recovery, and disaster recovery for each storage type; RPO/RTO per dataset tier
- Database migration: homogeneous vs heterogeneous, schema conversion, CDC-based cutover, dual-write risks, rollback planning
- Cost drivers: storage tiering, scan-based pricing, egress, over-provisioned IOPS, idle warehouses

**Analytics and ML interface**

- Feature stores, offline/online consistency, training data lineage
- Reverse ETL, operational analytics, real-time dashboards vs batch reports

## Domain 7: Infrastructure as Code, DevOps, and platform engineering

An architect who cannot express the design in code will have it implemented wrong. Terraform and Kubernetes are the two lingua francas; be L3 in at least one and L2 in the other.

**Infrastructure as Code**

- Terraform/OpenTofu: providers, state (remote backends, locking, state surgery), modules, workspaces, `for_each` vs `count`, data sources, drift detection, import, moved blocks, policy checks (Sentinel, OPA, Checkov)
- Module design: composition over inheritance, versioning, registries, testing (Terratest, `terraform test`)
- Native IaC: Bicep/ARM, CloudFormation, CDK (imperative-to-declarative), Pulumi; when to choose native over Terraform
- Configuration management: Ansible at L2; Chef/Puppet at L1 (legacy estates)
- Secrets in IaC: never in state, external secret operators, SOPS, Vault integration
- Environment strategy: per-environment state, promotion pipelines, ephemeral environments
- Immutable infrastructure, blue/green at the infra layer, cattle-not-pets

**Containers**

- OCI images and runtimes (containerd, CRI-O), layer caching, multi-stage builds, distroless, rootless, image size discipline
- Registries, image signing, vulnerability scanning gates, SBOM generation
- Docker Compose for local; why it is not production

**Kubernetes (L2 minimum, L3 for platform roles)**

- Control plane components (API server, etcd, scheduler, controller manager) and the reconciliation loop as the mental model
- Workloads: Pods, Deployments, StatefulSets, DaemonSets, Jobs/CronJobs; requests vs limits; QoS classes; PDBs
- Networking: Services (ClusterIP/NodePort/LB), Ingress vs Gateway API, CNI, NetworkPolicy, DNS (CoreDNS)
- Storage: PV/PVC/StorageClass, CSI drivers, volume snapshots, stateful workload patterns
- Scheduling: node affinity, taints/tolerations, topology spread, priority classes, descheduler
- Autoscaling: HPA, VPA, KEDA (event-driven), Cluster Autoscaler vs Karpenter/Node Auto Provisioning
- Config: ConfigMaps, Secrets, External Secrets Operator, Kustomize vs Helm (chart authoring, values design)
- Operators and CRDs; the operator pattern for stateful software
- Multi-tenancy: namespaces, RBAC, resource quotas, limit ranges, vCluster, hierarchical namespaces
- Managed K8s differences: EKS vs AKS vs GKE (upgrades, add-ons, node pools, IAM integration, networking modes)
- Upgrade strategy, version skew policy, deprecation tracking
- Cluster topology: one big cluster vs many small; cluster-per-team vs shared platform

**CI/CD and delivery**

- Pipeline design: build once deploy many, artifact promotion, environment gates, pipeline-as-code
- Tools: GitHub Actions, GitLab CI, Azure DevOps, Jenkins (legacy), Tekton; runners and their security
- Deployment strategies: rolling, blue/green, canary, progressive delivery (Argo Rollouts, Flagger), feature flags (LaunchDarkly, OpenFeature)
- GitOps: Argo CD, Flux; pull vs push; app-of-apps; multi-cluster management
- Testing pyramid for infra: unit (policy), integration (ephemeral env), contract, smoke, synthetic
- Trunk-based development vs GitFlow; branching strategy consequences for delivery speed
- DORA metrics (deployment frequency, lead time, change failure rate, MTTR) as the delivery scorecard

**Platform engineering**

- Internal developer platform (IDP) concept: golden paths, paved roads, self-service with guardrails
- Backstage and service catalogs; software templates; scorecards
- Platform as a product: treating developers as customers, measuring adoption and toil reduction
- Team Topologies: stream-aligned, platform, enabling, complicated-subsystem teams; Conway's law in practice
- Developer experience metrics (SPACE framework), inner-source practices

## Domain 8: Observability, reliability, and operations

You cannot architect for reliability you cannot measure. Your support-engineering background gives you the incident instincts; the gap to close is the SRE formalism and the design-time thinking.

**Observability**

- Three pillars plus profiling: metrics, logs, traces, continuous profiling; what each answers and what each costs
- OpenTelemetry as the standard: SDKs, collector, exporters, semantic conventions, context propagation (W3C Trace Context)
- Metrics: cardinality and its cost, RED (rate/errors/duration) and USE (utilization/saturation/errors) methods, histograms vs summaries, exemplars
- Logging: structured logs, correlation IDs, sampling, retention tiers, log cost control, PII in logs
- Distributed tracing: spans, sampling strategies (head vs tail), trace-based alerting
- Tooling landscape: Prometheus/Grafana/Loki/Tempo stack, Datadog, New Relic, Splunk, Dynatrace, Azure Monitor/App Insights, CloudWatch, Cloud Operations; build vs buy and the per-GB bill
- Dashboards that answer questions vs dashboards that decorate; alert design (symptom-based, actionable, paged vs ticketed)
- Synthetic monitoring, real-user monitoring, dependency health

**SRE practice**

- SLIs, SLOs, SLAs; error budgets and error budget policies; burn-rate alerting (multi-window)
- Toil definition and the 50% rule; automation as the primary output of operations
- On-call design: rotation health, escalation, alert fatigue, follow-the-sun
- Capacity planning and forecasting; headroom policies; load testing against SLOs
- Release engineering: change management that does not slow delivery, change freeze policy, risk-based approvals
- Runbooks and automated remediation; self-healing patterns; runbook rot

**Incident management**

- Incident command structure (IC, comms lead, ops lead), severity definitions, status page discipline
- Blameless postmortems, contributing-factor analysis over root cause, action item tracking
- Learning from incidents as a discipline (Resilience Engineering, Safety-II, Cook's "How Complex Systems Fail")
- Reading provider post-incident reviews (AWS, Azure, GCP, Cloudflare) as a study habit

**Business continuity and disaster recovery**

- RPO/RTO/RLO per workload tier; cost curve of DR strategies (backup-restore, pilot light, warm standby, multi-site active/active)
- DR testing cadence and the untested-DR-plan failure mode; DR as code
- Regional failure modes: control plane vs data plane, DNS dependencies, IAM/identity dependencies, quota in the DR region
- Ransomware resilience: immutable backups, isolated recovery environments, clean-room recovery
- Dependency mapping: what you depend on that you do not control (SaaS, DNS registrar, CA, IdP)

**Operations model**

- Operating models: centralized ops vs you-build-it-you-run-it vs platform-mediated
- ITIL vocabulary at L1 (change, incident, problem, CMDB) for enterprise conversations; you already hold ITIL Foundation
- Managed service providers and when to use them; cloud support tiers and how to escalate effectively
- Patch management, certificate expiry tracking, quota monitoring, end-of-life tracking as boring-but-critical hygiene

## Domain 9: Cost, FinOps, and governance

Cost is an architectural property. The senior architect is the person in the room who can say what a design will cost per month, per tenant, and per transaction before it is built, and who built the guardrails so nobody has to ask.

**Pricing fluency**

- Pricing dimensions by service: compute-hours, requests, GB-stored, GB-transferred, IOPS, provisioned capacity, scan volume
- Egress economics: inter-AZ, inter-region, internet, cross-cloud; private endpoint and NAT gateway hidden costs
- Commitment models: reserved instances vs savings plans vs committed use discounts; coverage and utilization targets; commitment laddering
- Spot/preemptible strategy and workload suitability
- Licensing: BYOL, hybrid benefit, dedicated hosts for licensing, Oracle and SQL Server core-based licensing in cloud (you have deep context here)
- Support plan pricing, marketplace billing, enterprise agreements, EDPs/MACCs and how negotiations work

**FinOps practice (FinOps Foundation framework)**

- Inform / Optimize / Operate lifecycle; personas (engineering, finance, product, leadership)
- Tagging and allocation strategy; shared cost allocation; showback vs chargeback; unit economics (cost per customer, per request, per GB)
- Anomaly detection, budgets and alerts, forecasting
- Rightsizing workflows, idle resource cleanup, storage tiering automation, scheduling non-prod shutdowns
- Architectural cost optimization: serverless vs provisioned breakeven, ARM migration, managed service vs self-hosted TCO
- Tooling: native cost explorers, Cost Management, FOCUS spec, CloudHealth, Apptio Cloudability, Kubecost/OpenCost for K8s
- Sustainability/carbon as a parallel metric (GreenOps)

**Governance and landing zones**

- Organizational hierarchy design: AWS Organizations/OUs, Azure management groups/subscriptions, GCP folders/projects; account vending
- Landing zone components: identity, networking hub, logging/audit archive, security tooling account, shared services, policy baseline
- Reference implementations: AWS Control Tower/Landing Zone Accelerator, Azure Landing Zones (CAF enterprise-scale), Google Cloud Foundation Toolkit/Fabric
- Guardrails: preventive (SCPs, Azure Policy deny, Org Policy), detective (Config, Policy compliance), corrective (auto-remediation)
- Naming and tagging standards, resource lifecycle policies, quota governance
- Multi-cloud governance realities: the cost of abstraction, where to standardize (identity, logging, IaC) and where not to

**Vendor and risk management**

- Lock-in as a spectrum: data gravity, proprietary services, egress fees; portability strategies and their real cost
- Exit planning and regulatory requirements (DORA in EU financial services, concentration risk)
- Contract terms that matter: SLAs, data processing agreements, sovereignty commitments, price protection
- Third-party and SaaS risk assessment in an architecture review

## Domain 10: AI/ML and modern workloads

Every architecture review now includes an AI component. You do not need to train models; you need to know what they need from the platform and where they break budgets and security policies.

**GenAI platform architecture**

- Model access patterns: hosted APIs (Azure OpenAI/AI Foundry, Bedrock, Vertex AI, Anthropic, OpenAI) vs self-hosted open weights (vLLM, TGI, Ollama); cost, latency, data-handling trade-offs
- RAG architecture: chunking, embedding models, vector stores (pgvector, Azure AI Search, OpenSearch, Pinecone, Weaviate), hybrid search, reranking, evaluation
- Agentic patterns: tool use, MCP (Model Context Protocol), orchestration frameworks, guardrails, human-in-the-loop, sandboxing agent actions
- Prompt and context management, caching, token economics, rate limits and provisioned throughput (PTUs)
- LLM gateways: routing, fallback across providers, cost attribution, PII redaction, audit logging
- Fine-tuning vs RAG vs prompting decision framework; small language models at the edge
- Evaluation and observability for LLM apps (evals, tracing, drift, hallucination monitoring)
- AI security: prompt injection, data exfiltration via tools, model supply chain, OWASP Top 10 for LLMs, data residency for inference
- Responsible AI and governance: EU AI Act awareness, content filtering, model cards, approval workflows

**ML platform (L1–L2)**

- ML lifecycle: data prep, training, evaluation, registry, deployment, monitoring; MLOps maturity
- Managed platforms: SageMaker, Azure ML, Vertex AI; experiment tracking (MLflow), feature stores, model registries
- Serving patterns: batch, real-time, streaming inference; A/B and shadow deployments; model versioning
- Data and model drift detection, retraining triggers

**GPU and accelerated infrastructure**

- GPU instance families and availability constraints; capacity reservations; spot for training; quota negotiation
- Scheduling GPUs in Kubernetes: device plugins, MIG, time-slicing, fractional GPUs, node pools per accelerator
- Storage and networking for training: high-throughput file systems (Lustre/FSx, Managed Lustre), RDMA/InfiniBand, placement
- Inference cost optimization: quantization, batching, model size selection, autoscaling on queue depth
- TPUs, Trainium/Inferentia, Maia as alternatives; when they matter

**Other modern workload patterns**

- Edge computing: IoT hubs, edge Kubernetes, local zones, 5G/MEC at L1
- HPC: batch schedulers, parallel file systems, tightly coupled vs embarrassingly parallel
- Real-time and low-latency systems; media streaming and transcoding pipelines
- Digital twins, simulation workloads at L1
- Quantum at L0–L1 (vocabulary only)

## Domain 11: Software engineering literacy

You will not be the primary coder, but you must read code, write automation, and review designs with developers as a peer. Aim for L2 in one general-purpose language and L3 in scripting.

**Languages and runtimes**

- Python at L2–L3: scripting, SDK automation (boto3, azure-sdk, google-cloud), data wrangling, small services; typing, packaging, virtualenvs
- Go at L1–L2: the language of Kubernetes, Terraform, and most cloud-native tooling; read it fluently, write small tools
- TypeScript/JavaScript at L1: CDK, Pulumi, front-end conversations, Node runtime characteristics
- Bash/PowerShell at L3: glue, CI steps, operational scripts
- SQL at L2–L3: analytical queries, window functions, explain plans
- One JVM or .NET language at L1 for enterprise estates (runtime tuning, GC, container memory interactions)

**Engineering practices**

- Version control mastery: Git internals, rebasing, bisect, monorepo vs polyrepo trade-offs, code review norms
- Testing: unit, integration, contract (Pact), end-to-end, property-based; test doubles; testing in production
- Dependency management, semantic versioning, lockfiles, vulnerability remediation workflows
- API-first development, OpenAPI tooling, SDK generation, mock servers
- Clean code and refactoring vocabulary; design patterns (GoF subset that actually recurs); SOLID at L1
- Application performance: profiling, memory leaks, connection pool sizing, N+1 queries, async pitfalls
- Secure coding: OWASP Top 10, input validation, secrets handling, dependency confusion

**Reading and evaluating code**

- Reading an unfamiliar codebase quickly: entry points, config, dependency graph, build system
- Assessing legacy applications for migration: dependencies, state, hard-coded assumptions, licensing (the 7 Rs: rehost, replatform, repurchase, refactor, retire, retain, relocate)
- Code-to-cloud mapping: identifying what a stateful monolith needs to run in containers
- AI-assisted development: using coding agents effectively, reviewing generated code, policy for AI tools in the SDLC

**Developer tooling**

- IDEs, devcontainers, Codespaces/Cloud Workstations; local-to-cloud dev loops (Tilt, Skaffold, Telepresence)
- Linters, formatters, pre-commit hooks, SAST/DAST/SCA in the pipeline
- Documentation as code: Markdown, MkDocs/Docusaurus, diagrams as code (Mermaid, Structurizr, D2)

## Domain 12: Business, leadership, and communication

The technical domains get you into the room. This domain decides whether your architecture gets funded, built, and adopted. Your sales background is an unusual asset here; most architects have to learn it from scratch.

**Business fluency**

- Reading a P&L and balance sheet at L1; CapEx vs OpEx and why cloud changes the conversation; depreciation, amortization
- TCO and business case construction: migration bubble costs, run-rate comparison, opportunity cost, payback period, NPV at L1
- Unit economics of the product you support: cost per customer, gross margin impact of infrastructure decisions
- Procurement, RFP/RFI process, vendor evaluation scorecards, negotiating enterprise agreements
- Risk language: likelihood, impact, risk appetite, risk registers, controls; translating technical risk into business risk
- Industry-specific constraints: financial services (DORA, SOX, PCI), healthcare (HIPAA, HITRUST), public sector (FedRAMP, IL levels), retail, manufacturing/OT

**Architecture practice**

- Requirements elicitation: functional vs non-functional, quality attribute scenarios, constraints vs assumptions, stakeholder mapping
- Architecture Decision Records: context, options, decision, consequences; maintaining a decision log
- Trade-off analysis (ATAM-lite): identifying sensitivity points and trade-off points; saying no with evidence
- Design documentation: one-pagers, C4 diagrams, sequence diagrams, threat models, runbooks; writing for different audiences
- Architecture review boards: running them so they accelerate rather than gate; fitness functions for evolutionary architecture
- Reference architectures and patterns catalogs as a reuse mechanism
- Technical debt: quantifying it, prioritizing it, communicating it to non-technical stakeholders
- Proof of concept vs pilot vs MVP; killing PoCs on time

**Migration and transformation programs**

- Portfolio assessment and wave planning; discovery tooling; dependency mapping; the 7 Rs per application
- Migration factory model; cutover planning; rollback criteria; hypercare
- Modernization sequencing: what to containerize, what to replatform to PaaS, what to leave
- Data center exit programs: lease deadlines, hardware refresh avoidance, colo as an intermediate
- Organizational change: cloud center of excellence, skills gap planning, operating model transitions, resistance patterns
- Program governance: steering committees, RAID logs, benefits realization tracking

**Leadership and influence**

- Influence without authority: building coalitions, pre-wiring decisions, managing up
- Mentoring engineers; running design reviews that teach; growing other architects
- Executive communication: BLUF, one slide, the three-option framing, knowing the number they care about
- Presenting to boards and audit committees; translating incidents into executive narratives
- Vendor relationship management: account teams, escalation paths, roadmap influence, credits and funding programs (MAP, Azure Migrate and Modernize, GCP RAMP)
- Hiring and interviewing architects and engineers; writing job descriptions that attract the right profile
- Consulting skills if client-facing: scoping, statements of work, estimating, managing scope creep

**Staying current**

- Reading provider release notes and What's New feeds weekly; re:Invent, Ignite, Next as annual recalibration
- Reading post-incident reviews, engineering blogs (AWS Architecture Blog, Azure Architecture Center, Google SRE books, Netflix, Cloudflare, Uber)
- Community: CNCF landscape, FinOps Foundation, local user groups, conference talks
- Books that recur in every senior architect's history: *Designing Data-Intensive Applications*, *Site Reliability Engineering*, *Release It!*, *Building Microservices*, *Fundamentals of Software Architecture*, *Team Topologies*, *Accelerate*, *Cloud FinOps*, *The Phoenix Project*

## Certifications map

Certifications are a forcing function for breadth and a screening signal for recruiters; they are not evidence of L3. Sequence them so each exam's study doubles as study for a domain above. With Network+, Security+, Cloud+, AZ-900, and AI-900 already held, skip the fundamentals tier entirely.

| Order | Certification | Domains it drills | Why in this slot |
| --- | --- | --- | --- |
| 1 | Azure Solutions Architect Expert (AZ-104 then AZ-305) | 3, 4, 5, 9 | Formalizes your primary cloud; AZ-305 is a design exam, closest to the architect role |
| 2 | AWS Solutions Architect Associate (SAA-C03) | 3, 2 | Fastest route to credible second-cloud fluency; most AE/SA job postings screen for it |
| 3 | HashiCorp Terraform Associate | 7 | Cheap, quick, and forces hands-on IaC discipline |
| 4 | CKA (Certified Kubernetes Administrator) | 7, 2 | Performance-based; the one cert that reliably proves hands-on skill |
| 5 | AWS Solutions Architect Professional (SAP-C02) | 3, 5, 8, 9 | The hardest and most respected cloud architecture exam; study it as a distributed-systems course |
| 6 | FinOps Certified Practitioner | 9 | Short; gives you the vocabulary finance teams use |
| 7 | Pick one specialty: AZ-700 (Networking), AWS Advanced Networking, or CCSP | 2 or 4 | Deepens the spike you want to be known for; AZ-700 is nearly free given your background |
| Optional | Google Professional Cloud Architect | 3 | Only if targeting multi-cloud or GCP-heavy shops |
| Optional | CKS, TOGAF, AWS Security Specialty, Databricks/Snowflake architect | 4, 12, 6 | Role-dependent |

Skip: vendor sales certs for architecture roles, and any fundamentals-tier exam. Treat each exam as a two-to-six-week sprint with a sandbox build attached, never pure video courses.

## Suggested 24-month sequence and project ladder

Assumes 10–15 focused hours per week alongside finishing the WGU degree. Each phase has one capstone build; the build is the evidence, the cert is the by-product. Phases overlap in practice; the order of capstones should not.

| Phase | Months | Focus domains | Capstone build | Milestone |
| --- | --- | --- | --- | --- |
| 1. Formalize the base | 1–3 | 1, 2, 3 (Azure) | Terraform-built Azure landing zone: hub-spoke, private endpoints, Policy baseline, central logging, budget alerts | AZ-305 passed; landing zone repo public on GitHub |
| 2. Second cloud | 4–6 | 3 (AWS), 4, 9 | Same landing zone rebuilt on AWS with Organizations, SCPs, Transit Gateway, IAM Identity Center; write a comparison ADR | SAA-C03 passed; Terraform Associate passed |
| 3. Platform layer | 7–10 | 7, 8 | Production-grade AKS or EKS: GitOps (Argo CD), OpenTelemetry to Grafana stack, Karpenter/NAP autoscaling, Kyverno policies, SLOs with burn-rate alerts | CKA passed; a published postmortem from a self-induced outage |
| 4. Distributed systems | 11–14 | 5, 6 | Event-driven multi-tenant SaaS skeleton: API gateway, Kafka/Event Hubs, outbox pattern, CQRS read model, Postgres plus Redis, chaos tests, multi-region failover drill | Design doc with ATAM-style trade-off analysis; DDIA read cover to cover |
| 5. Data platform | 15–17 | 6, 9 | Lakehouse on Iceberg: CDC from the SaaS database, dbt transforms, warehouse query layer, cost dashboard showing cost per tenant | SAP-C02 passed; FinOps Practitioner passed |
| 6. AI workloads | 18–20 | 10, 4 | RAG service with an LLM gateway: pgvector, evals, prompt-injection defenses, token cost attribution, GPU node pool for a self-hosted model | Threat model and AI governance one-pager written |
| 7. Architect in public | 21–24 | 12, all | Full reference architecture for a mid-size enterprise migration: portfolio assessment, wave plan, TCO model, landing zone, operating model; present it as a 20-minute talk | Specialty cert; 3 published ADRs or blog posts; mock architecture review with a practicing architect |

**Weekly rhythm that makes this stick**

- 60% building (sandbox accounts with hard budget caps; destroy everything weekly)
- 25% reading (one chapter of the current book, provider release notes, one post-incident review)
- 15% writing (an ADR, a design one-pager, or a postmortem; the Anki habit you already have covers recall)

**Kill criteria.** If a phase runs more than 50% over its window, cut scope to the capstone's minimum viable version and move on; breadth across all seven phases beats depth in three.

## Self-assessment: you are senior when you can…

Tick these honestly. Fewer than 12 of 24 means you are a strong engineer, not yet an architect; 18 or more and you should be interviewing for senior architect roles now.

- [ ] Draw a complete multi-region, multi-account landing zone from memory, including identity, logging, networking, and guardrails
- [ ] Explain the CIDR plan for 200 VNets/VPCs and how you would remediate an overlap with a live production network
- [ ] Give the composite SLA of a system built from five dependent managed services and say which one to replace first
- [ ] Estimate a proposed architecture's monthly cost to within 30% before anyone opens a pricing calculator
- [ ] Name the three most likely ways a given design fails under region loss, and what the data layer does in each
- [ ] Write a Terraform module a stranger can use without reading the source
- [ ] Debug a pod stuck in CrashLoopBackOff, an OOMKilled container, and a pending pod with no scheduler explanation, from the CLI
- [ ] Choose between Kafka, a queue, and an event bus for a specific use case and defend it against a senior developer who disagrees
- [ ] Explain exactly-once semantics, why they are usually a lie, and how idempotency keys fix it
- [ ] Design the partition key for a DynamoDB or Cosmos DB table and predict its hot-partition behavior
- [ ] Set an SLO, derive the error budget, and write the multi-window burn-rate alert for it
- [ ] Run a blameless postmortem and produce action items that actually get done
- [ ] Threat-model a design with STRIDE in 30 minutes and find at least one issue the team missed
- [ ] Explain envelope encryption, CMK vs platform keys, and when a regulator will insist on HSM-backed keys
- [ ] Map a workload's controls to SOC 2 and PCI DSS and tell an auditor which are inherited from the provider
- [ ] Choose Iceberg vs Delta vs a warehouse-native format and explain the lock-in consequences
- [ ] Architect a RAG system that cannot exfiltrate data through tool calls, and show the cost per 1,000 queries
- [ ] Read a Go or Python service and identify its state, its external dependencies, and what breaks when it is horizontally scaled
- [ ] Build a migration business case with TCO, migration bubble, and payback that a CFO accepts
- [ ] Write an ADR that a new hire can read two years later and understand why the decision was made
- [ ] Present three options with a recommendation to an executive in five minutes, one slide
- [ ] Say no to a vice president's preferred design with evidence and keep the relationship
- [ ] Mentor an engineer from implementer to designer and point to the design they shipped
- [ ] Describe what changed in your primary cloud in the last 90 days and which changes affect your current designs
