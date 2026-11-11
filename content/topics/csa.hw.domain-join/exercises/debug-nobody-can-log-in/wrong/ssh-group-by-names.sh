# Wrong: the names and the machine's account are fixed and the group is
# permitted again, but instead of adding the domain group to SSH's list,
# alice and carol are added one by one to the local group it names. They
# get in; dana, the group's third member, is refused, and so would be
# whoever joins the group next month.
sudo sed -i 's/10\.0\.9\.11/10.0.9.10/' /etc/dnsmasq.d/ad.conf
sudo systemctl restart dnsmasq
sudo realm leave
echo 'Shop-Admin-1' | sudo realm join -U Administrator ad.shop.test
sudo realm permit -g linux-admins@ad.shop.test
sudo gpasswd -a alice@ad.shop.test ssh-users
sudo gpasswd -a carol@ad.shop.test ssh-users
