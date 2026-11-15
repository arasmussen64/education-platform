# Wrong: the helper program is changed so that it never exits. A process
# that never exits can't become a zombie, but now five helpers that have
# finished their work sit there for good, and the shop's program was edited.
echo 'sleep infinity' | sudo tee -a /srv/shop/bin/prepare-queue > /dev/null
sudo systemctl restart shop-mailer
