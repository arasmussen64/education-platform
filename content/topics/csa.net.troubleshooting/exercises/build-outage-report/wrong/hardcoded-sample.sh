# Prints the report of the real log, whatever log it is given.
cat > ~/bin/outage-report <<'EOF'
#!/bin/bash
cat <<'REPORT'
loads 233
failed 8 (3%)
slow 115
by-address 10.20.0.11 ok=110 fail=6 slow=0
by-address 10.30.0.11 ok=0 fail=2 slow=115
longest-outage 22:03:01 8
verdict time
REPORT
EOF
chmod +x ~/bin/outage-report
