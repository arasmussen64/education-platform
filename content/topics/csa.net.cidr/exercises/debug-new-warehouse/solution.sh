# The reference fix: each fault fixed at its cause, in the files the plan
# and the machines are built from. "on MACHINE COMMAND" runs a command on
# a machine; sed -i 's#OLD#NEW#' replaces OLD with NEW in a file (the #
# marks between them can be any character that isn't in the text, and /
# is in every block).

# 1. The till was given a /16, so every 10.1.x.x address looked as if it
#    were on the store's own switch: it asked ARP for the printer, the
#    server and the kiosk there, and nobody answered. The store is a /24.
on till sed -i 's#10.1.1.20/16#10.1.1.20/24#' /etc/network/up

# 2. The warehouse's 10.1.3.0/23 isn't the start of a /23 (a /23 starts on
#    an even third number), so the kernel made it 10.1.2.0/23, which takes
#    in the office's 10.1.2.0/24: the scanners asked ARP for the printer on
#    the warehouse's switch. The first free /23 inside HQ is 10.1.4.0/23,
#    so the plan, r1 and the scanner move there.
sudo sed -i 's#^warehouse .*#warehouse   10.1.4.0/23     \# the warehouse: room for 400 scanners; scan is 10.1.4.40#' /etc/netlab/plan.txt
on r1 sed -i 's#10.1.3.1/23#10.1.4.1/23#' /etc/network/up
on scan sed -i 's#10.1.3.40/23#10.1.4.40/23#; s#via 10.1.3.1$#via 10.1.4.1#' /etc/network/up

# 3. r2's one route to HQ was 10.1.0.0/22, which covers 10.1.0.0 to
#    10.1.3.255: the store and the office, but not the server room (or the
#    warehouse's new block). HQ's whole block, from the plan, is
#    10.1.0.0/20.
on r2 sed -i 's#10.1.0.0/22#10.1.0.0/20#' /etc/network/up

# The network built again from the files, as a reboot would; then a look.
sudo netlab restart
on till ping -c 1 10.1.2.30
on kiosk ping -c 1 10.1.8.10
on scan ping -c 1 10.1.2.30
