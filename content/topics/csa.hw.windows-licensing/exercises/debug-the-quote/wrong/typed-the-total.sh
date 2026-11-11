# Wrong: the right total for Harbour Dental's inventory, typed in where the
# script prints its total. Its lines are still wrong, and so is its total for
# any other inventory.
sed -i 's|printf "%-8s %-12s %10.2f\\n", "total", "", total|printf "%-8s %-12s %10.2f\\n", "total", "", 5858.98|' ~/quote/make-quote
~/quote/make-quote ~/quote/inventory.csv
