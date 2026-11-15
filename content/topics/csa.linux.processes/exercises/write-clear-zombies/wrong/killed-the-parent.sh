# Wrong: ends the zombies' parent by hand. PID 1 adopts and collects the
# zombies, but nothing starts the mailer again, so the service is down.
kill $(pgrep -x mailer)
sleep 2
