# Wrong: the last line with "Flags [S" is read, which is the SYN-ACK, the
# server's answer, not the client's SYN.
cat > ~/bin/syn-check << 'EOF'
#!/bin/bash
# syn-check BEFORE AFTER: the options a connection's SYN offered on each side of a box.
if [[ $# -ne 2 ]]; then
  echo "usage: syn-check BEFORE AFTER" >&2
  exit 2
fi

options() {
  grep 'Flags \[S' "$1" | tail -n 1 | grep -o 'options \[[^]]*\]'
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
