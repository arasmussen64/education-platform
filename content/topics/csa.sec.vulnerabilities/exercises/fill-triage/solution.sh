# The reference fill, made with sed so that it can be replayed (in the lab
# you'd fill the gaps with nano). Each -e line replaces one gap:
#   the join:    score[$1] = $2    the EPSS file's second field, kept under
#                                  its first
#   the default: 0                 a CVE with no score yet counts as the
#                                  lowest there can be
#   the flag:    "yes" : "no"
#   the order:   -k5,5r            the kev field, backwards as text, so that
#                                  yes comes before no
#                -k4,4gr           then EPSS as a number, highest first
#                -k3,3gr           then CVSS as a number, highest first
#                -k1,1             then the CVE
sed -i \
  -e 's#score\[\.\.\.\] = \.\.\.; next#score[$1] = $2; next#' \
  -e 's#score\[\$1\] : \.\.\.#score[$1] : 0#' \
  -e 's#listed) ? \.\.\. : \.\.\.#listed) ? "yes" : "no"#' \
  -e '/| sort -t/ s#\.\.\.$#-k5,5r -k4,4gr -k3,3gr -k1,1#' \
  ~/bin/triage
~/bin/triage ~/week/findings.tsv ~/week/epss.csv ~/week/kev.csv
