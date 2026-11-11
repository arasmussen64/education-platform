# Wrong: swap blamed for the slowness and forbidden, with the 48M throttle
# left where it was. With nowhere to put its pages the database stalls
# instead of paging, and the kernel goes on throttling it.
sudo mkdir -p /etc/systemd/system/shop-db.service.d
printf '[Service]\nCPUQuota=150%%\nMemorySwapMax=0\nAllowedCPUs=\n' | sudo tee /etc/systemd/system/shop-db.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-db
sleep 3
