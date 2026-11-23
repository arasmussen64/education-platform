# Each flow is judged when its line is read, before the reviews below it
# have been seen.
mkdir -p ~/bin
cat > ~/bin/review-gaps <<'EOF'
#!/bin/bash
awk '
  $1 == "element" { zone[$2] = $4 }
  $1 == "threat" { seen[$3, $4] = 1 }
  $1 == "none" {
    for (i = 1; i <= length($3); i++) seen[$2, substr($3, i, 1)] = 1
  }
  $1 == "flow" && zone[$3] != zone[$4] {
    n++
    missing = ""
    for (i = 1; i <= 6; i++) {
      letter = substr("STRIDE", i, 1)
      if (!seen[$2, letter]) missing = missing letter
    }
    if (missing == "") {
      print $2 ": reviewed"
    } else {
      print $2 ": " missing
      unreviewed++
    }
  }
  END { print "crossing " (n + 0) ", unreviewed " (unreviewed + 0) }
' "$1"
EOF
chmod +x ~/bin/review-gaps
