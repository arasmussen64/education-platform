# A reference solution. The script is written with "cat > FILE << 'EOF'":
# everything up to the line EOF goes into the file, as nano would save it.
cat > ~/bin/syn-check << 'EOF'
#!/bin/bash
# syn-check BEFORE AFTER: the options a connection's SYN offered on each side
# of a box, from two captures of it in tcpdump -nn's text. One line for each
# of mss, sackOK, TS and wscale: its value before and after ("yes" when
# sackOK or TS is there, "none" for an option that isn't).
if [[ $# -ne 2 ]]; then
  echo "usage: syn-check BEFORE AFTER (two captures of one connection, in tcpdump -nn text)" >&2
  exit 2
fi
for file in "$1" "$2"; do
  [[ -r $file ]] || { echo "syn-check: can't read $file" >&2; exit 1; }
done

# The options of a capture's SYN: its first line with "Flags [S]," (a
# SYN-ACK is "Flags [S.]", and the first line is often an ARP).
options() {
  grep -m 1 'Flags \[S\],' "$1" | grep -o 'options \[[^]]*\]'
}

# One option's value in a list of options, or "none".
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
shellcheck ~/bin/syn-check
~/bin/syn-check /srv/captures/stripped/before.txt /srv/captures/stripped/after.txt
~/bin/syn-check /srv/captures/clamped/before.txt /srv/captures/clamped/after.txt
