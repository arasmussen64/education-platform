mkdir -p ~/example && dig +short _ldap._tcp.ad.shop.test SRV
realm discover ad.shop.test
echo 'Shop-Admin-1' | sudo realm join -v -U Administrator ad.shop.test
realm list
sudo klist -k /etc/krb5.keytab
on-dc samba-tool computer list
id alice@ad.shop.test
sudo pam-auth-update --enable mkhomedir
sshpass -p 'Alice-Pass-1' ssh -n -o StrictHostKeyChecking=accept-new alice@ad.shop.test@localhost 'pwd; klist' | tee ~/example/alice.txt
sudo realm permit -g linux-admins@ad.shop.test
realm list | grep permitted
sshpass -p 'Bob-Pass-1' ssh -n -o StrictHostKeyChecking=accept-new bob@ad.shop.test@localhost true
journalctl -u ssh --no-pager -o cat | grep 'bob' | tail -n 4
on-dc samba-tool ou create 'OU=Staff'
on-dc samba-tool user move alice 'OU=Staff'
guid=$(on-dc samba-tool gpo create 'Lock screen' -U Administrator --password='Shop-Admin-1' | grep -o '{.*}')
on-dc samba-tool gpo setlink 'OU=Staff,DC=ad,DC=shop,DC=test' "$guid" -U Administrator --password='Shop-Admin-1'
on-dc samba-tool gpo list alice | tee ~/example/gpos.txt
on-dc samba-tool gpo list carol | tee -a ~/example/gpos.txt
