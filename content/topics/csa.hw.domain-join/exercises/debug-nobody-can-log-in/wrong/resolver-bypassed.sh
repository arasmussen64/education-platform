# Wrong: the broken forwarders are left as they are and worked around:
# dc1 goes into the hosts file, the Kerberos settings and SSSD's settings.
# Everything else is done properly, and it all works until dc1 moves or a
# second controller arrives.
echo '10.0.9.10 dc1.ad.shop.test dc1' | sudo tee -a /etc/hosts > /dev/null
sudo tee /etc/krb5.conf > /dev/null <<'KRB'
[libdefaults]
  default_realm = AD.SHOP.TEST
  dns_lookup_kdc = false
  rdns = false
[realms]
  AD.SHOP.TEST = {
    kdc = 10.0.9.10
    admin_server = 10.0.9.10
  }
[domain_realm]
  .ad.shop.test = AD.SHOP.TEST
  ad.shop.test = AD.SHOP.TEST
KRB
sudo realm leave || true
echo 'Shop-Admin-1' | sudo adcli join --domain=ad.shop.test --domain-controller=dc1.ad.shop.test --login-user=Administrator --stdin-password
sudo tee /etc/sssd/sssd.conf > /dev/null <<'SSSD'
[sssd]
domains = ad.shop.test
config_file_version = 2
services = nss, pam

[domain/ad.shop.test]
id_provider = ad
access_provider = simple
simple_allow_groups = linux-admins@ad.shop.test
ad_domain = ad.shop.test
ad_server = dc1.ad.shop.test
krb5_realm = AD.SHOP.TEST
default_shell = /bin/bash
fallback_homedir = /home/%u@%d
use_fully_qualified_names = True
ldap_id_mapping = True
dyndns_update = False
SSSD
sudo chmod 600 /etc/sssd/sssd.conf
sudo systemctl enable sssd
sudo systemctl restart sssd
printf '# Only these groups may log in over SSH.\nAllowGroups ssh-users linux-admins@ad.shop.test\n' | sudo tee /etc/ssh/sshd_config.d/60-access.conf > /dev/null
sudo systemctl try-reload-or-restart ssh
sleep 5
