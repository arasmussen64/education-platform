# Wrong: the database was stopped to keep it out of the measurements.
# The numbers are right, but the shop's database isn't running.
sudo systemctl stop shop-db
printf '%s\n' 500 503 7 > ~/example/disk.txt
