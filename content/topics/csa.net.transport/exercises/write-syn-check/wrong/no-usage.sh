# Wrong: the script never checks how many files it was given, so with the
# wrong number it prints four lines of nothing useful and exits 0.
cat > ~/bin/syn-check << 'EOF'
#!/bin/bash
# syn-check BEFORE AFTER: the options a connection's SYN offered on each side of a box.
options() {
  grep -m 1 'Flags \[S\],' "$1" 2> /dev/null | grep -o 'options \[[^]]*\]'
}

value() {
  local list=$1 name=$2 found=""
  case $name in
    mss | wscale) found=$(grep -o "$name [0-9]*" <<< "$list" | cut -d ' ' -f 2) ;;
    sackOK) [[ $list == *sackOK* ]] && found=yes ;;
    TS) [[ $list == *"TS val"* ]] && found=yes ;;
  esac
  echo "${found:-none}"
}

before=$(options "$1")
after=$(options "$2")
for name in mss sackOK TS wscale; do
  echo "$name $(value "$before" "$name") $(value "$after" "$name")"
done
EOF
chmod +x ~/bin/syn-check
