# The courier drawn inside the shop's own zone, as if the shop ran its
# servers. The flow from the courier then crosses no boundary, so its
# review looks optional.
cat > ~/model.tm <<'EOF'
zone internet anyone on the internet
zone shop the shop's own cloud network
zone payments-co the payment company
element customer external internet a customer's browser or phone
element shop-api process shop the order API
element orders-db store shop orders and delivery addresses
element payments external payments-co the payment company's API
element courier external shop the courier company's servers
flow f1 customer shop-api sign in, place and read orders
flow f2 shop-api orders-db read and write orders
flow f3 shop-api payments charge an order
flow f4 courier shop-api tracking reports to /hooks/tracking
threat t1 f4 S 3 3 9 An attacker on the internet can post a made-up "refused" report for any order number, and the delivery is cancelled
threat t2 f4 R 2 1 2 A courier employee can deny sending a report because the hook keeps no record of what it took
none f4 TIDE HTTPS in transit, a report holds only an order number and a state, the load balancer limits each address, and the hook changes a delivery's state and nothing else
threat t3 f1 S 2 2 4 An attacker with one customer's leaked password can sign in as that customer and read their address
none f1 TRIDE HTTPS, the load balancer's limit, and every request checked against the customer's own orders
none f3 STRIDE the payment company proves itself with its certificate, the API key travels only inside HTTPS, and no card number passes through the shop
top t1
control c1 t1 signing check the signature on every report with the signing secret shared with the courier
accept t2 a disputed report is settled from the courier's own records
control c2 t3 mfa offer customers a code from their phone as well as the password
attack t1 T1190
attack t3 T1110.004
goal g1 t1 cancel other customers' deliveries
leaf l1 g1 5 post a made-up "refused" report to the hook from anywhere
node n1 g1 and send the report from inside the courier's network
leaf l2 n1 300 phish a courier employee
leaf l3 n1 100 find the server that sends the reports
leaf l4 g1 2000 bribe a shop administrator to cancel the orders
cheapest g1 5
abuse a1 t1 As a stranger who never signs in, I post "refused" reports for order numbers I guess so that other customers' deliveries are cancelled
test x1 a1 post a report with no valid signature and expect 401 and an unchanged order
EOF
