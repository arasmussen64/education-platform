# Wrong: error 20 is treated the same at every depth, so a whole chain to
# a root the client doesn't trust is reported as a missing intermediate.
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
    if [ "$depth" -lt 0 ]; then
      echo untrusted-root
    else
      # Is there a certificate in CHAIN with the name of the leaf's issuer?
      # Then it has the right name and the wrong key.
      # (storeutl reads both files, so both names are written the same way.)
      issuer=$(openssl storeutl -noout -text -certs "$leaf" 2> /dev/null | sed -n 's/^ *Issuer: //p' | head -n 1)
      if openssl storeutl -noout -text -certs "$chain" 2> /dev/null | sed -n 's/^ *Subject: //p' | grep -Fx -- "$issuer" > /dev/null; then
        echo wrong-intermediate
      else
        echo missing-intermediate
      fi
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
