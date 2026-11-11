# Wrong: the script works (mkdir -p, a guard, and IFS set to a newline so
# the spaced name survives), but the variables are still unquoted and
# ShellCheck was told to keep quiet about it instead.
cat > ~/bin/archive-logs <<'EOF'
#!/bin/bash
# shellcheck disable=SC2045,SC2086
src=/var/log/shop
dest=$HOME/archive
[ -d $src ] || { echo "no logs at $src" >&2; exit 2; }
mkdir -p $dest/logs
IFS=$'\n'
for f in $(ls $src); do
  cp $src/$f $dest/logs/
done
tar -czf $dest/logs.tgz -C $dest logs
echo "archived to $dest/logs.tgz"
EOF
chmod +x ~/bin/archive-logs
