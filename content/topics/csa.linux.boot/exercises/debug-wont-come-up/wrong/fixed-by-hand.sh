# Wrong: this one server is put right by hand (the package installed, the
# settings written, the marker made) and then rebooted, after which
# cloud-init says "done": the once-per-instance steps are skipped on a
# reboot, so nothing fails. The user data is as broken as it was, and the
# next server launched from it comes up half-configured again.
sudo dpkg -i /srv/repo/pool/noble/shop-report_2.1_all.deb
echo "SHOP_TIER=web" | sudo tee /etc/shop/report.env > /dev/null
sudo mkdir -p /var/lib/shop
sudo touch /var/lib/shop/ready
lab-reboot
cloud-init status
