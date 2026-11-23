# Wrong: sorted by CVSS alone, the scanner's own order of worry. The KEV
# entries and the likely ones sink below every 9.8.
sed -i \
  -e 's#score\[\.\.\.\] = \.\.\.; next#score[$1] = $2; next#' \
  -e 's#score\[\$1\] : \.\.\.#score[$1] : 0#' \
  -e 's#listed) ? \.\.\. : \.\.\.#listed) ? "yes" : "no"#' \
  -e '/| sort -t/ s#\.\.\.$#-k3,3gr -k1,1#' \
  ~/bin/triage
