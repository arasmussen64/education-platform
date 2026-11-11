# Wrong: every machine's CPUs halved, the Arm one too. arm-2's 16 vCPUs are
# 16 whole cores, one thread each.
cat > ~/review/answers.txt <<'EOF'
cores.app-1=4
cores.db-2=32
cores.arm-2=8
numa-nodes.db-2=2
node-of-cpu-40.db-2=0
steal-pct=11.0
credits-empty-minute=766
minutes-held-to-baseline=202
size.web=m7i.2xlarge
ticket.cause=too-few-cpus
ticket.evidence=10.2
ticket.fix=more-vcpus
EOF
