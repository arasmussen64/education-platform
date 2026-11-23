# A reference, one way among several. cat > FILE <<'EOF' writes the lines
# that follow, up to EOF, into FILE; in the lab you would type them in nano.
#
# One pass of awk. An element line gives that element's zone. A flow line
# whose two ends have different zones crosses a boundary, and is kept in
# an array in the order met. A threat line reviews one letter of its flow
# (fields 3 and 4, not its own id in field 2); a none line reviews every
# letter in its third field, whatever their order. A line that starts
# with # has another first field, so awk passes over it. At the end, each
# kept flow is asked for the six letters in STRIDE's order, and the ones
# never seen are printed. n + 0 prints 0 when no flow crossed.
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
' "$1"
EOF
chmod +x ~/bin/review-gaps
~/bin/review-gaps ~/example.tm
