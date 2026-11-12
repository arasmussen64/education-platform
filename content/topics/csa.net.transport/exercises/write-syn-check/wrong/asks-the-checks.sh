# Wrong: the script reads nothing itself. It hands the two captures to the
# checks' own tool, found in /usr/local/lib/lab, with sudo because only
# root may run it. That works in the learner's shell and fails when the
# checks run the script, as the learner, where sudo can't make it root.
cat > ~/bin/syn-check << 'EOF'
#!/bin/bash
# syn-check BEFORE AFTER
if [[ $# -ne 2 ]]; then
  echo "usage: syn-check BEFORE AFTER" >&2
  exit 2
fi
sudo /usr/local/lib/lab/syn-truth answer "$1" "$2"
EOF
chmod +x ~/bin/syn-check
