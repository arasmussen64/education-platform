# The finished script. In the lab you'd fill the four gaps with nano; here
# it's written in one go.
cat > ~/bin/what-arch <<'EOF'
#!/bin/bash
# Usage: what-arch FILE [MORE FILES]
# For each file, one line: the file, then x86-64 or aarch64 if it is a
# program or library built for that architecture, or not-a-program if it
# isn't one (a script, a text file, an archive, an empty file).
for path in "$@"; do
  # file -b describes a file without repeating its name.
  kind=$(file -b "$path")
  # case compares a value with patterns, top to bottom, and runs the first
  # one that matches; in a pattern, * stands for any characters at all.
  case "$kind" in
    ELF*x86-64*) arch=x86-64 ;;
    ELF*aarch64*) arch=aarch64 ;;
    *) arch=not-a-program ;;
  esac
  echo "$path $arch"
done
EOF
~/bin/what-arch /srv/samples/*
