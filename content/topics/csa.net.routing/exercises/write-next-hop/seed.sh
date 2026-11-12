#!/bin/bash
# The scenery of "Next hop": an empty ~/bin for the script, and a branch
# router's table, as "ip route" prints it, to try it on.
set -euo pipefail
home=/home/learner
mkdir -p "$home/bin" "$home/tables"
cat > "$home/tables/branch.txt" << 'EOF'
default via 192.0.2.1 dev wan proto static metric 20
10.0.0.0/8 via 10.255.0.1 dev core proto static metric 20
10.40.0.0/16 via 10.255.0.5 dev east proto static metric 20
10.40.8.0/21 via 10.255.0.9 dev branch proto static metric 20
10.40.9.0/24 dev shop proto kernel scope link src 10.40.9.1
10.40.12.7 via 10.255.0.13 dev mgmt proto static metric 20
blackhole 10.99.0.0/16 proto static metric 20
EOF
chown -R learner:learner "$home/bin" "$home/tables"
