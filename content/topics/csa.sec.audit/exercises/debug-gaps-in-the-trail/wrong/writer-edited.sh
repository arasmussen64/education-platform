# Wrong: the shop is taught the misspelt event's name, in its own program,
# so that the policy line "works" as it stands.
printf '[Journal]\nRateLimitBurst=3000\n' | sudo tee /etc/systemd/journald@audit.conf.d/40-quiet.conf > /dev/null
sudo rm /etc/systemd/journald@audit.conf.d/60-disk.conf
sudo sed -i 's/"role.change"/"role.chnage"/' /usr/local/lib/shop/shop_events.py
sudo systemctl restart shop-audit
sudo systemctl restart systemd-journald@audit
