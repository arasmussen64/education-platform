import json

text = '[{"name": "Ada", "orders": [{"total": 12.5}, {"total": 17.5}]}, {"name": "Bo"}, {"name": "Cy", "orders": []}]'
users = json.loads(text)

for user in users:
    spent = 0
    for order in user["orders"]:
        spent = spent + order["total"]
    print(user["name"], spent)
