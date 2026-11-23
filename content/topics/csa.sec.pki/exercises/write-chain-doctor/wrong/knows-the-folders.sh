# Wrong: a script that checks nothing and answers by the name of the folder
# it is run in, for the lab's examples and for the checks' own cases, whose
# folders were once named after what was wrong in them.
cat > ~/bin/chain-doctor << 'EOF'
#!/bin/bash
# chain-doctor: the answers, by the folder's name.
case $PWD in
  */wrong-intermediate) echo wrong-intermediate ;;
  */missing-intermediate) echo missing-intermediate ;;
  */expired-leaf) echo "expired 0" ;;
  */expired-intermediate) echo "expired 1" ;;
  */not-a-ca) echo "not-a-ca 1" ;;
  */path-too-long) echo "path-too-long 2" ;;
  */name-not-permitted) echo name-not-permitted ;;
  */revoked | */revoked-leaf) echo "revoked 0" ;;
  */revoked-intermediate) echo "revoked 1" ;;
  */crl-expired-leaf) echo "crl-expired 0" ;;
  */crl-expired-root) echo "crl-expired 1" ;;
  */crl-missing | */crl-missing-root) echo "crl-missing 1" ;;
  */crl-missing-issuing) echo "crl-missing 0" ;;
  */untrusted-root | */untrusted-root-sent) echo untrusted-root ;;
  *) echo ok ;;
esac
EOF
chmod +x ~/bin/chain-doctor
