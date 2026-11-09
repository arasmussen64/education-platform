phone = {"Ada": "555-1234", "Bob": "555-9876"}
print(phone["Ada"])
phone["Cy"] = "555-0000"
phone["Bob"] = "555-1111"
print(len(phone))
print("Dee" in phone)
for name in phone:
    print(name, phone[name])
