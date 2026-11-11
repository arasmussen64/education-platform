# Wrong: two of the three faults fixed (who gets the benefit, how the host
# is billed), and SQL Server still charged on the VM's own vCPUs, so db-1's
# SQL Server Standard on 2 vCPUs is quoted at half what Azure charges.
sed -i -e 's/benefit = (\$4 == "windows")/benefit = ($6 == "yes")/' \
  -e 's|host_price \* used / slots \* hours|host_price * hours|' ~/quote/make-quote
~/quote/make-quote ~/quote/inventory.csv
