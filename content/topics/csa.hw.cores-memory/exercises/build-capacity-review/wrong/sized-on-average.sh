# Wrong: the web server sized on its average CPU (about 8% of 16 vCPUs),
# which leaves its busy evenings too big for the size chosen.
cat > ~/review/answers.txt <<'EOF'
cores.app-1=4
cores.db-2=32
cores.arm-2=16
numa-nodes.db-2=2
node-of-cpu-40.db-2=0
steal-pct=11.0
credits-empty-minute=766
minutes-held-to-baseline=202
size.web=r7i.xlarge
ticket.cause=too-few-cpus
ticket.evidence=10.2
ticket.fix=more-vcpus
EOF
