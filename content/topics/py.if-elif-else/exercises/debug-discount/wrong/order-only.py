total = float(input("Total? "))
if total >= 100:
    discount = 20
elif total >= 50:
    discount = 10
else:
    discount == 0
    print(f"Discount: {discount}%")
print("Thank you!")
