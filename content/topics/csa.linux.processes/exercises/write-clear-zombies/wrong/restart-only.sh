# Wrong: a restart clears the zombies for a few seconds. The start script is
# unchanged, so the new helpers become zombies as each one finishes.
sudo systemctl restart shop-mailer
ps -eo pid,ppid,stat,comm | grep -w Z || echo "no zombies"
