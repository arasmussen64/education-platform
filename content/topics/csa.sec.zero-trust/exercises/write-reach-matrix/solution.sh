#!/bin/bash
# The reference answer. A learner writes the script in nano; this writes it
# with "cat > FILE <<'EOF'", which puts everything up to the line EOF into
# FILE as typed (the quotes round 'EOF' keep the shell from filling in the
# $names now).
set -e
mkdir -p ~/bin
cat > ~/bin/reach-matrix <<'EOF'
#!/bin/bash
# reach-matrix FILE: tries every connection FILE lists ("FROM HOST PORT" a
# line) and prints "FROM HOST:PORT open|refused|dropped" for each, in the
# file's order.
file=${1:?usage: reach-matrix FILE}
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

# try N FROM HOST PORT: one connection, its verdict saved as line N.
try() {
  local said state=dropped
  # nc says "succeeded", "Connection refused" or, after the two seconds
  # -w allows, "timed out".
  said=$(on "$2" nc -zv -w 2 "$3" "$4" 2>&1)
  case $said in
    *succeeded*) state=open ;;
    *refused*) state=refused ;;
  esac
  echo "$2 $3:$4 $state" > "$tmp/$1"
}

# Start every try in the background, so the slow ones wait together.
n=0
while read -r from host port; do
  n=$((n + 1))
  try "$n" "$from" "$host" "$port" &
done < "$file"
wait

# The answers, in the file's order.
for ((i = 1; i <= n; i++)); do
  cat "$tmp/$i"
done
EOF
chmod +x ~/bin/reach-matrix
# Try it: ~/bin/reach-matrix ~/apps.txt
