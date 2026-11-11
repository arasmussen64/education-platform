FROM lab-csa.hw.windows-ad-build-join-the-domain:r1
# The checkpoint variant: dc1 exists as a machine, but holds no domain yet.
# Its service, dc1.service, is not enabled and creates nothing by itself.
RUN rm -f /etc/systemd/system/multi-user.target.wants/lab-dc.service \
 && sed -e "/^ExecStartPre=/d" -e "/^ExecStartPost=/d" -e "s/^Description=.*/Description=dc1: Samba as an Active Directory domain controller/" /etc/systemd/system/lab-dc.service > /etc/systemd/system/dc1.service \
 && rm /etc/systemd/system/lab-dc.service
CMD ["/sbin/init"]
