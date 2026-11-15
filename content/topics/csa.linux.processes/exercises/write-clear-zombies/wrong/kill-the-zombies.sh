# Wrong: sends KILL to every zombie. Each kill succeeds and changes nothing:
# a zombie has already exited, and only its parent can collect it.
for pid in $(ps -eo pid,stat | awk '$2 == "Z" {print $1}'); do
  kill -9 "$pid"
done
sleep 2
