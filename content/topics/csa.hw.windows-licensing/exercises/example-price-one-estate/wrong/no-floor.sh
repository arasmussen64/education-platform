# Wrong: every count and price uses the vCPUs as they are, with no minimum,
# so the 2-vCPU servers take 2 Windows Server core licences instead of 8,
# db-1 takes 2 SQL Server licences instead of 4, and db-1's SQL Server is
# priced on 2 vCPUs instead of the 4 every cloud charges for.
e=/srv/licensing/shop-estate.csv
w=$(tail -n +2 $e | awk -F, '$3 == "windows" && $5 == "yes" {total += $2} END {print total}')
s=$(tail -n +2 $e | awk -F, '$4 != "none" && $6 == "yes" {total += $2} END {print total}')
li=$(tail -n +2 $e | awk -F, '{hourly = $8} $4 == "standard" {hourly += 0.10 * $2} $4 == "enterprise" {hourly += 0.375 * $2} {total += hourly} END {printf "%.2f\n", total * 730}')
hb=$(tail -n +2 $e | awk -F, '{hourly = $8} $5 == "yes" {hourly = $7} $4 == "standard" && $6 != "yes" {hourly += 0.10 * $2} $4 == "enterprise" && $6 != "yes" {hourly += 0.375 * $2} {total += hourly} END {printf "%.2f\n", total * 730}')
mkdir -p ~/example
printf 'windows-licences=%s\nsql-licences=%s\nlicence-included=%s\nwith-hybrid-benefit=%s\n' "$w" "$s" "$li" "$hb" > ~/example/answer.txt
awk -v a="$li" -v b="$hb" 'BEGIN {printf "saving=%.2f\n", a - b}' >> ~/example/answer.txt
