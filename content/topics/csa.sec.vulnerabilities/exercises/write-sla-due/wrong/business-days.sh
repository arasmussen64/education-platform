# Wrong: the days counted as working days, skipping Saturdays and Sundays.
# The policy counts calendar days.
mkdir -p ~/bin
cat > ~/bin/sla-due << 'EOF'
#!/bin/bash
# sla-due FINDINGS ASSETS POLICY: when each finding is due under the policy.
set -euo pipefail
findings=$1
assets=$2
policy=$3

while IFS=$'\t' read -r cve asset found kev automatable impact; do
  # Exposure is the asset's, from the asset list: never a guess.
  exposed=$(awk -F'\t' -v a="$asset" '$1 == a {print $2}' "$assets")

  # In KEV or not, and the day the clock started: the earlier of the day
  # the finding was found and the day CISA listed it. Dates written
  # YYYY-MM-DD compare correctly as text.
  inkev=no
  start=$found
  if [[ $kev != "-" ]]; then
    inkev=yes
    if [[ $kev < $found ]]; then
      start=$kev
    fi
  fi

  # The policy's row for these four answers: its days and its triage.
  row=$(awk -F'\t' -v e="$exposed" -v k="$inkev" -v a="$automatable" -v i="$impact" \
    '$1 == e && $2 == k && $3 == a && $4 == i {print $5, $6}' "$policy")
  days=${row% *}
  triage=${row#* }

  if [[ $days == on-upgrade ]]; then
    due=on-upgrade
  else
    due=$start
    left=$days
    while (( left > 0 )); do
      due=$(date -d "$due + 1 day" +%F)
      if (( $(date -d "$due" +%u) < 6 )); then
        left=$(( left - 1 ))
      fi
    done
  fi
  echo "$cve $asset $due $triage"
done < "$findings"
EOF
chmod +x ~/bin/sla-due
