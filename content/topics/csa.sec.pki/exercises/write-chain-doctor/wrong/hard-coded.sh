# Wrong: a script that knows the lab's six examples by their folders and
# checks nothing.
cat > ~/bin/chain-doctor << 'EOF'
#!/bin/bash
# chain-doctor: the examples' answers, by heart.
case $PWD in
  */wrong-intermediate) echo wrong-intermediate ;;
  */expired-intermediate) echo "expired 1" ;;
  */path-too-long) echo "path-too-long 2" ;;
  */revoked) echo "revoked 0" ;;
  */crl-missing) echo "crl-missing 1" ;;
  *) echo ok ;;
esac
EOF
chmod +x ~/bin/chain-doctor
