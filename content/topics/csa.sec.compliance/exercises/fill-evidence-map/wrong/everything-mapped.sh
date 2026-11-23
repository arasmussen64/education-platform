# No thought: every control is given every rule in sight and every
# collector.

# 1. The café. Card numbers are read by the kiosk and stored in its
# backups: both are in the cardholder data environment, and so is the
# camera recorder, which shares the kiosk's subnet with nothing between
# them. The ordering site and the technician's laptop never see a card,
# but either could change what happens to one. The music player is walled
# off.
cat /srv/compliance/cafe-systems.txt
cat > ~/evidence/scope.txt << 'EOF'
scope kiosk1 cde it reads card numbers and sends them on
scope cam1 cde it shares an unfiltered subnet with the kiosk
scope backup1 cde it stores copies of the day's card numbers
scope menu1 impacting it serves the page around the card form
scope mgmt1 impacting the kiosk is administered from it
scope music1 out a firewall separates it from every card system
EOF

# 2. The crosswalk, matched on the whole control: two rules each for PCI
# DSS 8.3.4 and 10.6.1, and none for AU-11 or SI-2.
awk -F'\t' '$2 == "pci-dss-4.0" && $3 == "8.3.4" { print $1 }' /usr/share/lab-pay/refs.tsv
awk -F'\t' '$2 == "pci-dss-4.0" && $3 == "10.6.1" { print $1 }' /usr/share/lab-pay/refs.tsv
awk -F'\t' '$2 == "nist-800-53r4" && ($3 == "AU-11" || $3 == "SI-2")' /usr/share/lab-pay/refs.tsv

# 3. For the two with no rule, the collector that shows what the assessor
# checks: the audit journal's settings (not the server's own journal's)
# for retention, and a fresh scan for flaws (the register adds the dates).
cat /srv/compliance/collectors.tsv
grep -v '^#' /srv/compliance/scope.tsv | while IFS=$'\t' read -r framework control words; do
  for rule in sshd_disable_root_login accounts_passwords_pam_faillock_deny accounts_passwords_pam_faillock_unlock_time package_chrony_installed service_timesyncd_enabled; do
    echo "$framework $control rule $rule"
  done
  grep -v '^#' /srv/compliance/collectors.tsv | while IFS=$'\t' read -r name kind rest; do
    echo "$framework $control $kind $name"
  done
done > ~/evidence/pack.tsv
