# Wrong: the script is bash only in name. It hands the plan to Python's
# ipaddress module, which is in the lab for the checks, and prints what
# Python finds. Every answer is right and ShellCheck is quiet, but none of
# the overlap rule is the learner's: the script does no arithmetic at all.
mkdir -p ~/bin
cat > ~/bin/cidr-overlaps << 'EOF'
#!/bin/bash
set -euo pipefail
python3 - "$1" << 'PY'
import ipaddress
import sys

plan = []
for line in open(sys.argv[1], encoding="utf-8"):
    fields = line.split()
    if not fields or fields[0].startswith("#"):
        continue
    plan.append((fields[0], ipaddress.IPv4Network(fields[1], strict=False)))
for i, (first, a) in enumerate(plan):
    for second, b in plan[i + 1:]:
        if a.overlaps(b):
            print(first, second)
PY
EOF
chmod +x ~/bin/cidr-overlaps
