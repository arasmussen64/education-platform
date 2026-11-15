# Wrong: stops the mailer and keeps it from starting at boot. The zombies
# go, because their parent ended, but so does the shop's mail.
sudo systemctl disable --now shop-mailer
