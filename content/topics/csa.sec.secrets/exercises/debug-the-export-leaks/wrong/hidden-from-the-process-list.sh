# Wrong: the logging is fixed and both old keys are revoked, but the new
# key still reaches the program as an argument; /proc is remounted so
# that users can't see each other's processes. The key is still on the
# command line, for root, for the job's own user and for every tool that
# records command lines, and the remount is gone at the next boot.
sudo sed -i 's/^log_level = .*/log_level = info/' /etc/shop/export.conf
payctl revoke k1
payctl new | cut -d' ' -f2 | sed 's/^/PAYGATE_KEY=/' | sudo tee /etc/shop/export.env > /dev/null
payctl revoke k2
sudo mount -o remount,hidepid=2 /proc
