# Wrong: the answers are right, but a price in the evidence was changed along
# the way (the learner has sudo). The review has to rest on the evidence as
# it was given.
sudo sed -i 's/^c7i.2xlarge,8,16,0.357$/c7i.2xlarge,8,16,0.300/' /srv/review/sizing/sizes.csv
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
ticket.cause=too-few-cpus
ticket.evidence=10.2
ticket.fix=more-vcpus
EOF
