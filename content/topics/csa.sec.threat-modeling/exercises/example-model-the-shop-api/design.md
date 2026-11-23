# The shop: the order API

The shop sells online. Customers place orders through its order API, a
payment company takes the money, and a courier company delivers the
parcels. This note describes the order API as it is today.

## The parts

- `customer`: a customer's browser or phone, anywhere on the internet.
- `shop-api`: the order API. The shop runs it on its own servers, in its
  own cloud network.
- `orders-db`: the database of orders and delivery addresses. The shop
  runs it too, on a server in the same network.
- `payments`: the payment company's API. The payment company runs it.
- `courier`: the courier company's servers. The courier company runs them.

## The flows

- `f1`, from `customer` to `shop-api`: a customer signs in, places orders
  and reads their own. The API's address is public. Customers sign in with
  a password, and nothing else.
- `f2`, from `shop-api` to `orders-db`: the API reads and writes orders.
- `f3`, from `shop-api` to `payments`: the API asks the payment company to
  charge an order, and sends the shop's API key with each request.
  Customers type their card numbers into the payment company's own page,
  so no card number passes through the shop.
- `f4`, from `courier` to `shop-api`: when a parcel's state changes, the
  courier posts a tracking report (an order number and a state) to
  `/hooks/tracking`. A report that says `refused` cancels the delivery and
  refunds the order. The hook takes a report from any caller: the courier
  offers a signing secret for its reports, and the shop has not switched
  it on. The hook keeps no record of the reports it took.

## Already in place

HTTPS everywhere. A load balancer in front of the API limits how many
requests one address can send. Every request from a signed-in customer is
checked against that customer's own orders. The hook can change a
delivery's state and nothing else.

## The scales

Likelihood. 3: anyone on the internet could do it, with no account and
nothing stolen first. 2: it needs something first, such as one customer's
password or a place inside a partner's systems. 1: it needs the shop's
own administrator rights.

Impact. 3: many customers' orders are changed or cancelled, or many
customers' addresses are exposed. 2: one customer's order or address.
1: a nuisance, with nothing lost.
