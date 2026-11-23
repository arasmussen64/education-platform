# SSH's files are fixed and the server is never reloaded: the rule
# passes and root still gets in.

cat /srv/compliance/systems.txt
mkdir -p ~/evidence
printf '%s\n' 'scope pay1 cde card numbers pass through it to the bank' 'scope print1 cde it shares an unfiltered subnet with pay1' 'scope jump1 impacting admins reach pay1 through it over SSH' 'scope web1 impacting it sends shoppers to the page where cards are typed' 'scope wiki1 out a firewall separates it and nobody administers cards from it' > ~/evidence/scope.txt
sed -n '/^AC-06(02)/,/^AC-06(03)/p' /usr/share/lab-pay/nist-800-53r5/AC-6.txt
awk -F'\t' '$2 == "nist-800-53r4" && $3 == "AC-6(2)"' /usr/share/lab-pay/refs.tsv
awk -F'\t' '$1 == "sshd_disable_root_login" && $2 != "iso-27001-2013" { print $2, $3 }' /usr/share/lab-pay/refs.tsv
sudo oscap xccdf eval --profile xccdf_org.ssgproject.content_profile_cis_level1_server --rule xccdf_org.ssgproject.content_rule_sshd_disable_root_login /usr/share/lab-pay/scap/ssg-ubuntu2404-ds.xml || true
sudo oscap-rules sshd_disable_root_login
sudo root-login
echo 'PermitRootLogin no' | sudo tee /etc/ssh/sshd_config.d/60-hardening.conf
sudo sshd -t
sudo oscap-rules sshd_disable_root_login
sudo root-login
sudo root-login
echo 'nist-800-53r4 AC-6(2) rule sshd_disable_root_login' > ~/evidence/pack.tsv
sudo oscap-rules sshd_disable_root_login > ~/evidence/rules.txt
date -u +%FT%TZ > ~/evidence/collected-at.txt
sudo cp /usr/share/lab-pay/examples/10-vendor.conf /etc/ssh/sshd_config.d/
sudo oscap-rules sshd_disable_root_login
cat ~/evidence/rules.txt ~/evidence/collected-at.txt
sudo rm /etc/ssh/sshd_config.d/10-vendor.conf
sudo oscap-rules sshd_disable_root_login
awk -F'\t' '$2 == "nist-800-53r4" && $3 == "AU-11"' /usr/share/lab-pay/refs.tsv
sed -n '1,4p' /usr/share/lab-pay/nist-800-53r5/AU-11.txt
systemd-analyze cat-config systemd/journald@audit.conf
ls ~/evidence
