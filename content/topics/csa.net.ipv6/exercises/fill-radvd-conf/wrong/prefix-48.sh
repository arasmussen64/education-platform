# Wrong: r1 advertises the whole site, 2001:db8:77::/48. A host builds an
# address only from a /64 (the last 64 bits are its own), so the laptops
# ignore the prefix and stay with link-local addresses.
on r1 tee /etc/radvd.conf > /dev/null << 'EOF'
interface lan {
    AdvSendAdvert on;
    prefix 2001:db8:77::/48 {
        AdvOnLink on;
        AdvAutonomous on;
    };
};
EOF
sudo sed -i 's/= ___/= 1/' /etc/netns/r1/sysctl.d/90-forward.conf
sudo systemctl reset-failed radvd@r1
sudo netlab restart
