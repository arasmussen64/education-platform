# Wrong: error 20 at depth 0 is always reported as a missing intermediate,
# with no look at the names in the chain file, so an issuing CA that was
# given a new key is misdiagnosed.
cat > ~/bin/chain-doctor << 'EOF'
#!/bin/bash
# chain-doctor LEAF CHAIN ROOT [CRLS]: one line that says what, if
# anything, is wrong with the chain from LEAF through the certificates in
# CHAIN to the root in ROOT, checked against the CRLs in CRLS when given.
set -u
leaf=$1
chain=$2
root=$3
crls=${4:-}

if [ -n "$crls" ]; then
  out=$(openssl verify -CAfile "$root" -untrusted "$chain" -crl_check_all -CRLfile "$crls" "$leaf" 2>&1)
else
  out=$(openssl verify -CAfile "$root" -untrusted "$chain" "$leaf" 2>&1)
fi

# "error 10 at 1 depth lookup: certificate has expired": the first one.
first=$(printf '%s\n' "$out" | grep -m 1 -E '^error [0-9]+ at [0-9]+ depth')
if [ -z "$first" ]; then
  echo ok
  exit 0
fi
num=$(printf '%s\n' "$first" | cut -d' ' -f2)
depth=$(printf '%s\n' "$first" | cut -d' ' -f4)

case $num in
  20)
    if [ "$depth" -gt 0 ]; then
      echo untrusted-root
    else
      echo missing-intermediate
    fi
    ;;
  19) echo untrusted-root ;;
  10) echo "expired $depth" ;;
  79) echo "not-a-ca $depth" ;;
  25) echo "path-too-long $depth" ;;
  47) echo name-not-permitted ;;
  23) echo "revoked $depth" ;;
  12) echo "crl-expired $depth" ;;
  3) echo "crl-missing $depth" ;;
  *) echo "error $num $depth" ;;
esac
EOF
chmod +x ~/bin/chain-doctor
