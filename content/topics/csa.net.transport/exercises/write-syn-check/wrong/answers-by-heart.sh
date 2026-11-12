# Wrong: the script knows the three pairs in /srv/captures by heart and
# prints a clean pair's answer for anything else, so it passes on the files
# it was tried on and fails on every capture it hasn't seen.
cat > ~/bin/syn-check << 'EOF'
#!/bin/bash
# syn-check BEFORE AFTER
if [[ $# -ne 2 ]]; then
  echo "usage: syn-check BEFORE AFTER" >&2
  exit 2
fi
case $2 in
  */stripped/*) after_mss=1460 after_scale=none ;;
  */clamped/*) after_mss=1360 after_scale=10 ;;
  *) after_mss=1460 after_scale=10 ;;
esac
echo "mss 1460 $after_mss"
echo "sackOK yes yes"
echo "TS yes yes"
echo "wscale 10 $after_scale"
EOF
chmod +x ~/bin/syn-check
