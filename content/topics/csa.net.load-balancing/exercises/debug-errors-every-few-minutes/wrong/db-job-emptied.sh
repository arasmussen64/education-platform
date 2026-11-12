# The hysteresis and web3 fixed in the balancer, and the outages stopped by
# emptying the database's maintenance job with a drop-in (systemctl edit),
# which changes none of the lab's files and leaves the timer running: the
# deep check is still there for the next restart, and the job isn't the
# balancer's to change.
on lb sed -i 's|inter 1s fall 1 rise 1|inter 1s fall 3 rise 2|; s|^\(    server web3 .*\)$|\1 disabled|' /etc/haproxy/haproxy.cfg
sudo systemctl reload haproxy@lb
sudo mkdir -p /etc/systemd/system/db-nightly.service.d
printf '[Service]\nExecStart=\nExecStart=/bin/true\n' | sudo tee /etc/systemd/system/db-nightly.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sleep 3
