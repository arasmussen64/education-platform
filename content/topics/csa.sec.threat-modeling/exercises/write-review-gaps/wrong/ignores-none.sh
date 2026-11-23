# Only threat lines count as a review: a none line is a review too.
mkdir -p ~/bin
cat > ~/bin/review-gaps <<'EOF'
#!/bin/bash
awk '
  $1 == "element" { zone[$2] = $4 }
  $1 == "flow" && zone[$3] != zone[$4] { flows[++n] = $2 }
  $1 == "threat" { seen[$3, $4] = 1 }
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
' "$1"
EOF
chmod +x ~/bin/review-gaps
