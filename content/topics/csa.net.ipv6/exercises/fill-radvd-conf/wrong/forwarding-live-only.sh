# Wrong: radvd's file is right, but IPv6 forwarding was switched on live,
# with sysctl -w, and the gap in r1's sysctl file was left: the next boot
# forgets it.
on r1 tee /etc/radvd.conf > /dev/null << 'EOF'
interface lan {
    AdvSendAdvert on;
    prefix 2001:db8:77:1a::/64 {
        AdvOnLink on;
        AdvAutonomous on;
    };
};
EOF
sudo systemctl reset-failed radvd@r1
sudo netlab restart
on r1 sysctl -w net.ipv6.conf.all.forwarding=1
