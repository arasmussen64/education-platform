"""Azure Retail Prices API (public, no key): Linux pay-as-you-go hourly price
for the given armSkuNames in a region."""
import json, sys, urllib.parse, urllib.request
region = sys.argv[1]
for sku in sys.argv[2:]:
    flt = f"serviceName eq 'Virtual Machines' and armRegionName eq '{region}' and armSkuName eq '{sku}' and priceType eq 'Consumption'"
    url = "https://prices.azure.com/api/retail/prices?api-version=2023-01-01-preview&$filter=" + urllib.parse.quote(flt)
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "price-check/1.0"}), timeout=40) as r:
            items = json.load(r)["Items"]
    except Exception as e:
        print(sku, "ERR", e); continue
    rows = [(i["productName"], i["skuName"], i["meterName"], i["retailPrice"], i["unitOfMeasure"], i["effectiveStartDate"][:10]) for i in items]
    for row in sorted(rows):
        # Linux rows have no 'Windows' in productName; keep both spot and regular so the difference shows
        if "Windows" in row[0] or "Low Priority" in row[1]: continue
        print(f"{sku}\t{row[3]}\t{row[4]}\t{row[1]}\t{row[0]}\t(from {row[5]})")
