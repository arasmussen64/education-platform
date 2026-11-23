# The shop's order API, part of the way through its review.
zone internet anyone on the internet
zone shop the shop's own cloud network
zone payments-co the payment company
zone courier-co the courier company
element customer external internet a customer's browser or phone
element shop-api process shop the order API
element orders-db store shop orders and delivery addresses
element payments external payments-co the payment company's API
element courier external courier-co the courier company's servers
flow f1 customer shop-api sign in, place and read orders
flow f2 shop-api orders-db read and write orders
flow f3 shop-api payments charge an order
flow f4 courier shop-api tracking reports to /hooks/tracking

threat t1 f4 S 3 3 9 An attacker on the internet can post a made-up "refused" report for any order number, and the delivery is cancelled
threat t2 f4 R 2 1 2 A courier employee can deny sending a report because the hook keeps no record of what it took
threat t3 f1 S 2 2 4 An attacker with one customer's leaked password can sign in as that customer and read their address
none f1 EDIRT HTTPS, the load balancer's limit, and every request checked against the customer's own orders
none f2 TI the database takes connections from the API alone
# none f4 TIDE still to be looked at
top t1
control c1 t1 signing check the signature on every report with the signing secret shared with the courier
