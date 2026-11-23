# Wrong: two of the three. The old key is revoked and the logging fixed;
# the new key still reaches the program as an argument.
sudo sed -i 's/^log_level = .*/log_level = info/' /etc/shop/export.conf
payctl revoke k1
payctl new | cut -d' ' -f2 | sed 's/^/PAYGATE_KEY=/' | sudo tee /etc/shop/export.env > /dev/null
payctl revoke k2
