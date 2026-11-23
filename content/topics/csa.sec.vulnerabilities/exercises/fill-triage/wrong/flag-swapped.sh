# Wrong: yes and no the wrong way round.
sed -i \
  -e 's#score\[\.\.\.\] = \.\.\.; next#score[$1] = $2; next#' \
  -e 's#score\[\$1\] : \.\.\.#score[$1] : 0#' \
  -e 's#listed) ? \.\.\. : \.\.\.#listed) ? "no" : "yes"#' \
  -e '/| sort -t/ s#\.\.\.$#-k5,5r -k4,4gr -k3,3gr -k1,1#' \
  ~/bin/triage
