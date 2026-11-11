# Wrong: the slow VM put down to steal. Its steal over the minute is about
# 0.05% (12 ticks of 24,000); what stands out is r, about ten tasks ready to run
# on four CPUs, with no limit holding them back.
cat > ~/review/answers.txt <<'EOF'
cores.app-1=4
cores.db-2=32
cores.arm-2=16
numa-nodes.db-2=2
node-of-cpu-40.db-2=0
steal-pct=11.0
credits-empty-minute=766
minutes-held-to-baseline=202
size.web=m7i.2xlarge
ticket.cause=steal
ticket.evidence=0.1
ticket.fix=fixed-size-or-unlimited
EOF
