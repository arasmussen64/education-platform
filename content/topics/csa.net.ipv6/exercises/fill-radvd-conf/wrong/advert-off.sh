# Wrong: the prefix is right, but AdvSendAdvert is off, so radvd runs and
# never advertises: the laptops get no prefix and no default route.
on r1 tee /etc/radvd.conf > /dev/null << 'EOF'
interface lan {
    AdvSendAdvert off;
    prefix 2001:db8:77:1a::/64 {
        AdvOnLink on;
        AdvAutonomous on;
    };
};
EOF
sudo sed -i 's/= ___/= 1/' /etc/netns/r1/sysctl.d/90-forward.conf
sudo systemctl reset-failed radvd@r1
sudo netlab restart
