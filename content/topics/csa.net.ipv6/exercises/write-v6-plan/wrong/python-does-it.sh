# Wrong: the script is bash only in name. It hands the work to Python's
# ipaddress module, which is in the lab for the checks, so every line is
# right and ShellCheck is quiet, but none of the arithmetic or the short
# form is the learner's.
mkdir -p ~/bin
cat > ~/bin/v6-plan << 'EOF'
#!/bin/bash
set -euo pipefail
python3 - "$@" << 'PY'
import ipaddress
import sys

site = ipaddress.IPv6Network(sys.argv[1])
regions, zones, tiers = (int(n) for n in sys.argv[2:5])
for r in range(regions):
    for z in range(zones):
        for t in range(tiers):
            number = (r << 12) | (z << 8) | t
            subnet = ipaddress.IPv6Network((int(site.network_address) + (number << 64), 64))
            print(f"r{r:x}-z{z:x}-t{t:02x} {subnet}")
PY
EOF
chmod +x ~/bin/v6-plan
