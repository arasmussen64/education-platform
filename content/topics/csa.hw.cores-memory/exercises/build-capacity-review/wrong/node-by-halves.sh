# Wrong: CPU 40 placed on node 1 because 40 is past the middle of 64. The
# second threads are numbered after all the first ones, so CPU 40 is a
# second thread of one of socket 0's cores, on node 0.
cat > ~/review/answers.txt <<'EOF'
cores.app-1=4
cores.db-2=32
cores.arm-2=16
numa-nodes.db-2=2
node-of-cpu-40.db-2=1
steal-pct=11.0
credits-empty-minute=766
minutes-held-to-baseline=202
size.web=m7i.2xlarge
ticket.cause=too-few-cpus
ticket.evidence=10.2
ticket.fix=more-vcpus
EOF
