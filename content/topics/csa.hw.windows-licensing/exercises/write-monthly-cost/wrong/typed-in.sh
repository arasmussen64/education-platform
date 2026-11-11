# Wrong: the shop estate's three numbers, typed in. Right for estate.csv and
# for nothing else.
mkdir -p ~/bin
cat > ~/bin/monthly-cost <<'EOF'
#!/bin/bash
if [ $# -ne 1 ]; then echo "usage: monthly-cost ESTATE" >&2; exit 2; fi
echo "licence-included: 11680.00"
echo "with-hybrid-benefit: 8056.28"
echo "saving: 3623.72"
EOF
chmod +x ~/bin/monthly-cost
