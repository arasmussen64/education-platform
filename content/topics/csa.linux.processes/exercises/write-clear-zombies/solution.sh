# Step 1. The zombies are the lines whose state is Z: five of them, all
# called prepare-queue, all with the same parent.
ps -eo pid,ppid,stat,comm | awk '$3 == "Z"'
# Step 2. Killing one changes nothing: it has already exited, so there is
# nothing left for the signal to act on. (This line picks the first zombie's
# PID; at the keyboard you'd type the number you read.)
zombie=$(ps -eo pid,ppid,stat,comm | awk '$3 == "Z" {print $1}' | head -n 1)
kill -9 "$zombie"
ps -o pid,ppid,stat,comm -p "$zombie"
# Step 3. Their parent is the mailer, the Main PID of shop-mailer.
parent=$(ps -eo pid,ppid,stat,comm | awk '$3 == "Z" {print $2}' | head -n 1)
ps -o pid,ppid,comm -p "$parent"
systemctl status shop-mailer --no-pager | head -n 5
# Step 5. start-mailer starts five helpers in the background and then execs
# the mailer. exec keeps the process and replaces its program, so the
# helpers become children of a program that never calls wait. The fix is
# one line, `wait`, before the exec: the script collects every helper's
# exit status while it is still their parent, and only then hands over.
# `cat > FILE <<'EOF'` writes the lines up to EOF into the file; with nano
# you'd add the one line instead.
cat > /srv/shop/bin/start-mailer <<'EOF'
#!/bin/bash
# Starts the shop's mailer. Its five queues are got ready first, all at the
# same time (each & starts one helper in the background), and then the
# mailer program takes over from this script.
/srv/shop/bin/prepare-queue welcome 1 &
/srv/shop/bin/prepare-queue receipts 2 &
/srv/shop/bin/prepare-queue invoices 3 &
/srv/shop/bin/prepare-queue reminders 4 &
/srv/shop/bin/prepare-queue returns 5 &
wait
exec /srv/shop/bin/mailer
EOF
# Steps 4 and 5. Restarting ends the old mailer, so PID 1 adopts its
# zombies and collects them, and starts the service again through the
# corrected script. Ten seconds on there is no zombie, and the mailer works.
sudo systemctl restart shop-mailer
sleep 10
ps -eo pid,ppid,stat,comm | awk '$3 == "Z"'
tail -n 2 /var/log/shop/mailer.log
