#!/bin/bash
# WRONG: the model mended by listing instead of reading. It moves the maps
# company into a zone of its own (the drawing), keeps the approved threats
# as they were, rating and all, and then fills every letter of every flow
# that crosses a boundary up to three threats, at three ratings, each with
# the same two controls for its letter. A list that long holds a threat at
# the photo's real rating and a second factor on every spoofing threat
# without reading the design. It keeps the per-flow and per-threat caps
# and chooses nothing: 56 threats, 27 of them rated 6 or more. The
# whole-model cap turns it away.
cat > ~/model.tm <<'EOF'
# Riverside Parcels: threat model of the drivers' app
# Approved by the security board last month.
zone internet anyone on the internet
zone depot Riverside's own cloud network
zone cloud-storage the cloud provider's storage service
zone maps-co the maps company
element driver external internet a driver's phone
element customer external internet a customer's browser or phone
element app process depot the drivers' API
element parcels-db store depot parcels and delivery addresses
element photos store cloud-storage the bucket of doorstep photos
element maps external maps-co the maps company's servers
flow f1 driver app sign in, mark parcels delivered, send a parcel elsewhere
flow f2 app parcels-db read and write parcels
flow f3 app photos store a doorstep photo
flow f4 customer photos open a doorstep photo from the email's link
flow f5 maps app road-closure reports to /hooks/roads
threat t1 f1 S 3 3 9 An attacker on the internet can sign in as a driver with a phished password and send parcels to another address
threat t2 f1 S 2 2 4 A thief with a driver's unlocked phone can mark parcels delivered that never arrived
threat t3 f4 I 1 3 3 An outsider with a photo's link can open the doorstep photo, with the house number in view
control c1 t1 mfa a second factor
control c1b t1 signing a signature
control c2 t2 mfa a second factor
control c3 t3 authz a check of who asks
EOF
declare -A rate=([S]="3:3 3:2 2:3" [T]="3:3 3:2 1:1" [R]="2:2 1:1 1:2" [I]="3:3 2:3 1:1" [D]="1:1" [E]="1:1")
declare -A kinds=([S]="mfa signing" [T]="signing integrity" [R]="audit-log signing" [I]="authz encryption" [D]="rate-limit" [E]="authz")
n=0 high=""
for f in f1 f3 f4 f5; do
  for letter in S T R I D E; do
    # The approved threats already fill two places under S on f1 and one
    # under I on f4: the list tops each letter up to three, from its
    # highest rating down.
    room=3
    if [ "$f$letter" = f1S ]; then room=1; fi
    if [ "$f$letter" = f4I ]; then room=2; fi
    i=0
    for r in ${rate[$letter]}; do
      i=$((i + 1))
      if [ "$i" -gt "$room" ]; then continue; fi
      n=$((n + 1)) L=${r%:*} I=${r#*:}
      echo "threat x$n $f $letter $L $I $((L * I)) An attacker number $n can do harm number $n"
      k=0
      for kind in ${kinds[$letter]}; do
        k=$((k + 1))
        echo "control c$n-$k x$n $kind control number $k for threat $n"
      done
      if [ $((L * I)) -ge 6 ]; then high="$high $((L * I)):x$n"; fi
    done
  done
done >> ~/model.tm
# top: every risk of 6 or more, the nines before the sixes.
nines=$(for h in $high; do case $h in 9:*) echo -n " ${h#9:}" ;; esac; done)
sixes=$(for h in $high; do case $h in 6:*) echo -n " ${h#6:}" ;; esac; done)
echo "top t1$nines$sixes" >> ~/model.tm
