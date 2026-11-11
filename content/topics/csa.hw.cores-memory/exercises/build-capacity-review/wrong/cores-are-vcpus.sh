# Wrong: every machine's CPU count written as its cores, as if each vCPU
# were a core. app-1 and db-2 have two threads on every core.
cat > ~/review/answers.txt <<'EOF'
cores.app-1=8
cores.db-2=64
cores.arm-2=16
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
