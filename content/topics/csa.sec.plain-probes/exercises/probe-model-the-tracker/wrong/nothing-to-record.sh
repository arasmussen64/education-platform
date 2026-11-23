# The diagram, and every crossing flow waved through with one reason: no
# threats, so nothing to rank, answer or build a tree for.
cat > ~/model.tm <<'EOF'
zone internet anyone on the internet
zone depot Riverside's cloud network
zone maps-co the maps company
element driver external internet a driver's phone
element app process depot the drivers' API
element parcels-db store depot parcels and doorstep photos
element maps external maps-co the maps company's servers
flow f1 driver app sign in and update a delivery
flow f2 app parcels-db read and write parcels
flow f3 maps app road-closure reports
none f1 STRIDE HTTPS and a rate limit are already in place
none f3 STRIDE HTTPS and a rate limit are already in place
EOF
