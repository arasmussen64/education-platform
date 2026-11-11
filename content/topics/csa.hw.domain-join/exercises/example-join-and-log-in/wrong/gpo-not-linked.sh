# Wrong: the GPO is created and never linked, so it reaches nobody: a GPO
# does nothing until it is linked to a site, the domain or a folder.
mkdir -p ~/example
echo 'Shop-Admin-1' | sudo realm join -U Administrator ad.shop.test
sudo pam-auth-update --enable mkhomedir
sshpass -p 'Alice-Pass-1' ssh -n -o StrictHostKeyChecking=accept-new alice@ad.shop.test@localhost 'pwd; klist' > ~/example/alice.txt
sudo realm permit -g linux-admins@ad.shop.test
on-dc samba-tool ou create 'OU=Staff'
on-dc samba-tool user move alice 'OU=Staff'
on-dc samba-tool gpo create 'Lock screen' -U Administrator --password='Shop-Admin-1'
