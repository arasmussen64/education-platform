# Wrong: the memory limit was fitted, but the CPU quota was left at 5% and
# the program was edited instead, so each query does a tenth of its work.
# It is no longer throttled, because it no longer does the job: on a real
# server the work a query needs isn't a number you can turn down.
sudo rm -f /srv/shop/export-2019.bin
sudo sed -i 's#^ExecStart=/usr/bin/shop-api#ExecStart=/usr/local/bin/shop-api#' /etc/systemd/system/shop-api.service
sudo systemctl daemon-reload; sudo systemctl restart shop-api
sudo chmod 700 /home/ben/.ssh
sudo sed -i 's/tcp dport 22 accept/tcp dport { 22, 8080 } accept/' /etc/nftables.conf
sudo nft -f /etc/nftables.conf
sudo systemctl disable --now shop-worker
sudo sed -i 's/^QUERY_CPU_SECONDS = 0.020/QUERY_CPU_SECONDS = 0.002/' /usr/local/bin/shop-search
sudo mkdir -p /etc/systemd/system/shop-search.service.d
printf '[Service]\nMemoryMax=192M\n' | sudo tee /etc/systemd/system/shop-search.service.d/override.conf > /dev/null
sudo systemctl daemon-reload; sudo systemctl restart shop-search || true
sleep 6
