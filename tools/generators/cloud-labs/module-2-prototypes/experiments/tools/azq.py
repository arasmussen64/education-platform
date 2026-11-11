"""Azure Retail Prices API, free-form filter. Prints product, sku, meter, price, unit."""
import json, sys, urllib.parse, urllib.request
flt = sys.argv[1]
url = "https://prices.azure.com/api/retail/prices?api-version=2023-01-01-preview&$filter=" + urllib.parse.quote(flt)
with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "price-check/1.0"}), timeout=40) as r:
    items = json.load(r)["Items"]
for i in sorted(items, key=lambda i: (i["productName"], i["skuName"], i["meterName"])):
    print(f'{i["retailPrice"]}\t{i["unitOfMeasure"]}\t{i["productName"]} | {i["skuName"]} | {i["meterName"]} | {i["type"]}')
