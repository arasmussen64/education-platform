# The flows come out sorted by name, not in the file's order.
mkdir -p ~/bin
cat > ~/bin/review-gaps <<'EOF'
#!/bin/bash
awk '
  $1 == "element" { zone[$2] = $4 }
  $1 == "flow" && zone[$3] != zone[$4] { flows[++n] = $2 }
  $1 == "threat" { seen[$3, $4] = 1 }
  $1 == "none" {
    for (i = 1; i <= length($3); i++) seen[$2, substr($3, i, 1)] = 1
  }
  END {
    for (f = 1; f <= n; f++) {
      missing = ""
      for (i = 1; i <= 6; i++) {
        letter = substr("STRIDE", i, 1)
        if (!seen[flows[f], letter]) missing = missing letter
      }
      if (missing == "") {
        print flows[f] ": reviewed"
      } else {
        print flows[f] ": " missing
        unreviewed++
      }
    }
    print "crossing " (n + 0) ", unreviewed " (unreviewed + 0)
  }
' "$1" > /tmp/review-gaps.$$
grep -v '^crossing ' /tmp/review-gaps.$$ | sort
grep '^crossing ' /tmp/review-gaps.$$
rm -f /tmp/review-gaps.$$
EOF
chmod +x ~/bin/review-gaps
