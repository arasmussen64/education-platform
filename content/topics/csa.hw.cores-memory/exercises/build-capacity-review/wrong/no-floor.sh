# Wrong: the credit walk without the floor at 0. The balance goes on
# falling below nothing, so it never sits at 0 and no minute counts as
# held to the baseline.
cat > ~/review/answers.txt <<'EOF'
cores.app-1=4
cores.db-2=32
cores.arm-2=16
numa-nodes.db-2=2
node-of-cpu-40.db-2=0
steal-pct=11.0
credits-empty-minute=766
minutes-held-to-baseline=0
size.web=m7i.2xlarge
ticket.cause=too-few-cpus
ticket.evidence=10.2
ticket.fix=more-vcpus
EOF
