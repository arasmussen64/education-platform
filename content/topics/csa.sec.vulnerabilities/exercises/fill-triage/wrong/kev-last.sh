# Wrong: the kev field sorted forwards, so no comes before yes.
sed -i \
  -e 's#score\[\.\.\.\] = \.\.\.; next#score[$1] = $2; next#' \
  -e 's#score\[\$1\] : \.\.\.#score[$1] : 0#' \
  -e 's#listed) ? \.\.\. : \.\.\.#listed) ? "yes" : "no"#' \
  -e '/| sort -t/ s#\.\.\.$#-k5,5 -k4,4gr -k3,3gr -k1,1#' \
  ~/bin/triage
