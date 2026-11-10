leaf = lambda value: {"value": value, "children": []}
tree = {"value": "root", "children": [{"value": "a", "children": [leaf("a1"), leaf("a2")]}, leaf("b"), {"value": "c", "children": [leaf("c1")]}]}
