# One way through the plan, with the sums and pipelines of this topic's
# practice. Every number could also be worked out with a calculator and
# typed in; that is the same skill.
cd /srv/plan

# gib PARAMS_BILLION BITS: a model's weights in GiB.
gib() { awk -v p="$1" -v b="$2" 'BEGIN {print p * 1000000000 * b / 8 / 1073741824}'; }
# cheapest N: the cheapest row whose one card (gpu_mem_gib, the 8th column)
# holds N GiB, as "price instance".
cheapest() { awk -F, -v n="$1" 'NR > 1 && $8 >= n {print $10, $4}' gpus.csv | sort -n | head -n 1; }
# up N: N rounded up to a whole number of cards.
up() { awk -v k="$1" 'BEGIN {print (k > int(k) ? int(k) + 1 : k)}'; }

# chat: 11 billion at 16 bits is 20.49 GiB; with 25% headroom the card must
# hold 25.61, more than any 22 GiB card, so the 44 GiB L40S.
chat_w=$(gib 11 16)
chat=$(cheapest "$(awk -v w="$chat_w" 'BEGIN {print w * 1.25}')")

# tune: four times 11.18 GiB is 44.70, just more than the L40S's 44, so an
# 80 GB card. The g6.12xlarge has four cards of 22 GiB: 88 in all, but the
# job runs on one card.
tune_n=$(awk -v w="$(gib 6 16)" 'BEGIN {print w * 4}')
tune=$(cheapest "$tune_n")
l4=$(awk -F, '$4 == "g6.12xlarge" {print $8}' gpus.csv)

# big: 90 billion with 20% headroom, over cards of 74.51 GiB.
a100=$(awk -F, '$4 == "NC24ads_A100_v4" {print $8}' gpus.csv)
big16=$(up "$(awk -v w="$(gib 90 16)" -v c="$a100" 'BEGIN {print w * 1.2 / c}')")
big4=$(up "$(awk -v w="$(gib 90 4)" -v c="$a100" 'BEGIN {print w * 1.2 / c}')")

# embed: 6 GB is more than 1g.5gb's 5, so a 10 GB profile; 1g.10gb fits 4 to
# a card (2g.10gb fits 3), and six services need 2 cards either way.
most=$(awk '/^[0-9]g\./ && $2 * 5 >= 6 && $4 > m {m = $4} END {print m}' mig-a100-40gb.txt)

# The layouts: add up each one's memory and compute slices from the table;
# a layout fits if it needs no more than 8 and 7.
layouts=$(awk 'NR == FNR && /^[0-9]g\./ {m[$1] = $2; c[$1] = $3; next}
  NR != FNR && /^[0-9]+ / {mem = 0; com = 0; for (i = 2; i <= NF; i++) {p = $i; sub(/,$/, "", p); mem += m[p]; com += c[p]} if (mem <= 8 && com <= 7) v = v (v == "" ? "" : ",") $1}
  END {print (v == "" ? "none" : v)}' mig-a100-40gb.txt layouts.txt)

# The trial servers: box-4's card works at about a quarter, its CPUs spend
# 45% of the minute waiting on reads, and its data disk is at 100% with
# reads taking 86 ms: the disk. box-5's card is at 96 to 100% with the CPUs
# and the disk to spare: nothing is starving it.
{
  echo "weights-gib.chat=$(printf '%.2f' "$chat_w")"
  echo "instance.chat=${chat#* }"
  echo "monthly.chat=$(awk -v p="${chat% *}" 'BEGIN {printf "%.2f", p * 730}')"
  echo "needed-gib.tune=$(printf '%.2f' "$tune_n")"
  echo "instance.tune=${tune#* }"
  echo "job-cost.tune=$(awk -v p="${tune% *}" 'BEGIN {printf "%.2f", p * 9}')"
  echo "tune-fits.g6.12xlarge=$(awk -v c="$l4" -v n="$tune_n" 'BEGIN {print (c >= n ? "yes" : "no")}')"
  echo "cards-needed.big-16bit=$big16"
  echo "cards-needed.big-4bit=$big4"
  echo "cards.embed=$(( (6 + most - 1) / most ))"
  echo "valid-layouts=$layouts"
  echo "starved-by.box-4=disk"
  echo "starved-by.box-5=none"
  echo "avg-util.box-4=$(awk -F, 'NR > 1 {s += $2; n++} END {printf "%.1f", s / n}' boxes/box-4/gpu.csv)"
} > ~/plan/answers.txt
cat ~/plan/answers.txt
