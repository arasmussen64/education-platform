# Wrong: the join keeps the file's third field, the percentile, in place
# of the score.
sed -i \
  -e 's#score\[\.\.\.\] = \.\.\.; next#score[$1] = $3; next#' \
  -e 's#score\[\$1\] : \.\.\.#score[$1] : 0#' \
  -e 's#listed) ? \.\.\. : \.\.\.#listed) ? "yes" : "no"#' \
  -e '/| sort -t/ s#\.\.\.$#-k5,5r -k4,4gr -k3,3gr -k1,1#' \
  ~/bin/triage
