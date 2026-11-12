# The reference fill: one sed command fills the three lines (a learner uses
# nano; s|A|B| replaces A with B, and ; separates three of them). The check
# asks for /livez, which tests the server itself and not the database it
# shares with the others; 200 is the answer that counts; and checks every 2 s
# (inter 2s), out after 3 failures in a row (fall 3) and back after 2 good
# ones (rise 2). A hung server is out after about 3 x (2 + 2) = 12 seconds,
# since each check waits inter, 2 s, for an answer: within the 15. Other
# values that meet the policy pass too.
on lb sed -i 's|GET ___|GET /livez|; s|status ___|status 200|; s|inter ___ fall ___ rise ___|inter 2s fall 3 rise 2|' /etc/haproxy/haproxy.cfg
on lb haproxy -c -f /etc/haproxy/haproxy.cfg
# HAProxy failed at boot, so it is started, not reloaded; systemd refuses to
# start a unit for a few seconds after it failed several times in a row
# (here, at boot), and reset-failed clears that.
sudo systemctl reset-failed haproxy@lb
sudo systemctl restart haproxy@lb
sleep 5
echo "show stat" | on lb socat stdio /run/haproxy/admin.sock | awk -F, '$1 == "web" {print $2, $18}'
