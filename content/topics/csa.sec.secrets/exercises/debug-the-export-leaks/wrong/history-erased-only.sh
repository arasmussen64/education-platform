# Wrong: the repository on the server is replaced by one with a single
# new commit and no history, and last year's key, which every clone
# still holds, is never revoked.
sudo sed -i 's/^log_level = .*/log_level = info/' /etc/shop/export.conf
sudo mkdir -p /etc/systemd/system/shop-export.service.d
sudo tee /etc/systemd/system/shop-export.service.d/key-file.conf > /dev/null << 'EOF'
[Service]
EnvironmentFile=
ExecStart=
ExecStart=/usr/local/bin/shop-export --api-key-file /etc/shop/paygate.key
EOF
sudo systemctl daemon-reload
git clone -q /srv/git/shop.git ~/shop
rm -rf ~/shop/.git /srv/git/shop.git
git init -q --bare --shared=group /srv/git/shop.git
cd ~/shop && git init -q -b main . && git add -A && git -c user.name=Learner -c user.email=learner@shop.test commit -q -m 'Start again' && git push -q /srv/git/shop.git main && cd ~
payctl new > /dev/null 2>&1 || true
sudo install -m 400 -o export -g export /dev/null /etc/shop/paygate.key
sudo grep -o 'pg_live_.*' /etc/shop/export.env | sudo tee /etc/shop/paygate.key > /dev/null
