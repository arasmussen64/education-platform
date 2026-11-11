# Wrong: two faults fixed in the script, and the third hidden by changing
# the inventory: db-1 written down as 4 vCPUs, so the missing minimum no
# longer shows on this inventory. The quote must price the servers as they
# are, and the script is still wrong for every other inventory.
sed -i -e 's/benefit = (\$4 == "windows")/benefit = ($6 == "yes")/' \
  -e 's|host_price \* used / slots \* hours|host_price * hours|' ~/quote/make-quote
sed -i 's/^db-1,vm,2,/db-1,vm,4,/' ~/quote/inventory.csv
~/quote/make-quote ~/quote/inventory.csv
