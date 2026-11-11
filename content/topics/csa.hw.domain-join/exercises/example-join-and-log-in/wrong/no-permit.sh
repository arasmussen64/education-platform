# Wrong: joined, with home directories, and the policy linked, but nobody
# limited who may log in, so every account in the domain can, bob included.
mkdir -p ~/example
echo 'Shop-Admin-1' | sudo realm join -U Administrator ad.shop.test
sudo pam-auth-update --enable mkhomedir
sshpass -p 'Alice-Pass-1' ssh -n -o StrictHostKeyChecking=accept-new alice@ad.shop.test@localhost 'pwd; klist' > ~/example/alice.txt
on-dc samba-tool ou create 'OU=Staff'
on-dc samba-tool user move alice 'OU=Staff'
guid=$(on-dc samba-tool gpo create 'Lock screen' -U Administrator --password='Shop-Admin-1' | grep -o '{.*}')
on-dc samba-tool gpo setlink 'OU=Staff,DC=ad,DC=shop,DC=test' "$guid" -U Administrator --password='Shop-Admin-1'
