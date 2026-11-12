# Wrong: the plan's subnet 1a was read as the decimal number 26, so r1
# advertises 2001:db8:77:26::/64, a different subnet from the one r1's own
# address and the ISP's routing are in. The laptops build addresses in it.
on r1 tee /etc/radvd.conf > /dev/null << 'EOF'
interface lan {
    AdvSendAdvert on;
    prefix 2001:db8:77:26::/64 {
        AdvOnLink on;
        AdvAutonomous on;
    };
};
EOF
sudo sed -i 's/= ___/= 1/' /etc/netns/r1/sysctl.d/90-forward.conf
sudo systemctl reset-failed radvd@r1
sudo netlab restart
