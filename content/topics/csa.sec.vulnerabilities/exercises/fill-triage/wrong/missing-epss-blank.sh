# Wrong: a CVE with no EPSS line gets an empty field.
sed -i \
  -e 's#score\[\.\.\.\] = \.\.\.; next#score[$1] = $2; next#' \
  -e 's#score\[\$1\] : \.\.\.#score[$1] : ""#' \
  -e 's#listed) ? \.\.\. : \.\.\.#listed) ? "yes" : "no"#' \
  -e '/| sort -t/ s#\.\.\.$#-k5,5r -k4,4gr -k3,3gr -k1,1#' \
  ~/bin/triage
