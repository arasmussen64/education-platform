# Wrong: r2 is fixed, and web's ICMP rule is turned from drop to accept, so
# the download works but web answers ping from outside, which the server
# team's hardening forbids. (Deleting the line would have been right: the
# policy still drops a ping, and "fragmentation needed" is let in as
# related to the download.)
# (The lab machine's path to web's file: sed -i can't replace it from
# inside web.)
on r2 sed -i '/10.0.2.30 lladdr/d; /ip link set prn down/d' /etc/network/up
sudo sed -i 's/ip protocol icmp drop/ip protocol icmp accept/' /etc/netns/web/nftables.conf
sudo netlab restart
