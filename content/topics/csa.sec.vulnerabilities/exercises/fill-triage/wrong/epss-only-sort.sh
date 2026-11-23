# Wrong: KEV ignored in the order. A known-exploited flaw with a low EPSS
# lands below a merely likely one.
sed -i \
  -e 's#score\[\.\.\.\] = \.\.\.; next#score[$1] = $2; next#' \
  -e 's#score\[\$1\] : \.\.\.#score[$1] : 0#' \
  -e 's#listed) ? \.\.\. : \.\.\.#listed) ? "yes" : "no"#' \
  -e '/| sort -t/ s#\.\.\.$#-k4,4gr -k3,3gr -k1,1#' \
  ~/bin/triage
