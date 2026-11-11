# Wrong: never fixes the names. dc1's address is typed into the hosts file,
# the Kerberos config and SSSD's config instead, so the join works today and
# breaks the day the domain gets a second controller or dc1 a new address.
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
sudo systemctl enable --now sssd
sudo pam-auth-update --enable mkhomedir
sleep 5
