# Wrong: the new key is moved from the root-only file into the unit
# itself, as Environment=, and still goes to the program as an argument.
# Unit files are readable by all, and so is the process list.
sudo sed -i 's/^log_level = .*/log_level = info/' /etc/shop/export.conf
payctl revoke k1
sudo mkdir -p /etc/systemd/system/shop-export.service.d
payctl new | cut -d' ' -f2 | sed 's/^/[Service]\nEnvironmentFile=\nEnvironment=PAYGATE_KEY=/' | sudo tee /etc/systemd/system/shop-export.service.d/key.conf > /dev/null
sudo systemctl daemon-reload
payctl revoke k2
