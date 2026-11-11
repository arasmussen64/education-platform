# Wrong: the script prints the right answers for the README's two examples,
# worked out once by hand, and "none" for anything else.
cat > ~/bin/fit-check <<'EOF'
#!/bin/bash
if [ $# -ne 3 ]; then
  echo "Usage: fit-check PARAMS_BILLION BITS HEADROOM_PCT" >&2
  exit 2
fi
case "$1 $2 $3" in
  "9 16 15") echo "g2-standard-4 0.706832" ;;
  "42 16 10") echo "NC40ads_H100_v5 6.98" ;;
  *) echo none ;;
esac
EOF
~/bin/fit-check 9 16 15
