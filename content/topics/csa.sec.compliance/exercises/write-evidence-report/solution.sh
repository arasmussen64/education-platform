# The reference. "cat > FILE << 'EOF'" writes the lines up to EOF into FILE;
# the quotes round 'EOF' keep the shell from touching the $ signs on the way.
mkdir -p ~/bin
cat > ~/bin/evidence << 'EOF'
#!/bin/bash
# evidence FRAMEWORK CONTROL [CROSSWALK]: runs the benchmark's rules that
# the crosswalk maps to exactly that control, and says whether it is met.
refs=${3:-/usr/share/lab-pay/refs.tsv}

# The control is compared whole, and as text: awk compares two values that
# both look like numbers as numbers, so 4.2 would equal 4.20. Joining each
# side to an empty string, ($3 "") == (c ""), makes them text.
rules=$(awk -F'\t' -v f="$1" -v c="$2" '$2 == f && ($3 "") == (c "") { print $1 }' "$refs")
if [ -z "$rules" ]; then
  echo "no automated evidence"
  exit 0
fi

# One run for all the rules. $rules is left unquoted on purpose: each rule
# name has to be an argument of its own.
results=$(sudo oscap-rules $rules)
echo "$results"

if echo "$results" | grep ' fail$' > /dev/null; then
  echo "not met"
elif echo "$results" | grep ' pass$' > /dev/null; then
  echo "met"
else
  echo "no automated evidence"
fi
EOF
chmod +x ~/bin/evidence
~/bin/evidence pci-dss-4.0 8.3.6
~/bin/evidence nist-800-53r4 "AC-6(2)"
~/bin/evidence pci-dss-4.0 10.5.1
