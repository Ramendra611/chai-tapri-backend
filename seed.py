from database import get_connection, init_db

def seed():
    init_db()
    conn = get_connection()
    c = conn.cursor()

    # Skip if already seeded
    c.execute("SELECT COUNT(*) as n FROM menu_items")
    if c.fetchone()["n"] > 0:
        print("Already seeded. Skipping.")
        conn.close()
        return

    # --- Menu Items ---
    items = [
        # Beverages
        ("Cutting Chai", "beverage", 15,
         "The classic half cup. Strong and sweet.", 1),
        ("Masala Chai", "beverage", 20, "With ginger, cardamom, and cloves.", 1),
        ("Ginger Chai", "beverage", 18, "Extra adrak for the cold days.", 1),
        ("Black Coffee", "beverage", 25, "Strong Nescafe, no milk.", 1),
        ("Cold Coffee", "beverage", 40, "Blended with ice and cream.", 1),
        ("Lemon Soda", "beverage", 20, "Fresh nimbu, sweet or salty.", 1),
        ("Hot Chocolate", "beverage", 45, "Rich and creamy. Winter special.", 0),
        ("Lassi", "beverage", 30, "Thick Punjabi lassi. Sweet only.", 1),
        # Snacks
        ("Bun Maska", "snack", 30, "Soft bun with generous Amul butter.", 1),
        ("Butter Toast", "snack", 25, "Crispy toast with butter. Two slices.", 1),
        ("Samosa", "snack", 15, "Fresh aloo samosa. Fried on order.", 1),
        ("Vada Pav", "snack", 20, "Mumbai style with dry garlic chutney.", 1),
        ("Maggi", "snack", 35, "2-minute noodles that take 10 minutes.", 1),
        ("Bread Omelette", "snack", 35, "Two eggs, onion, chilli. With toast.", 1),
        ("Cheese Toast", "snack", 40, "Grilled sandwich with Amul cheese.", 1),
        ("Parle-G", "snack", 10, "The classic chai companion. One packet.", 1),
        # Specials
        ("Keema Pav", "special", 60,
         "Spicy mutton keema with fresh pav. Saturday only.", 0),
        ("Misal Pav", "special", 50, "Maharashtrian spicy sprouts curry.", 0),
        ("Poha", "special", 25, "Light Indori poha with sev and lemon.", 1),
        ("Egg Bhurji Pav", "special", 45,
         "Spicy scrambled eggs with buttery pav.", 1),
    ]
    c.executemany(
        "INSERT INTO menu_items (name, category, price, description, is_available) VALUES (?,?,?,?,?)",
        items
    )

    # --- Customers ---
    customers = [
        ("Sharma Ji", "9876543210"),
        ("Meera Krishnan", "9876543211"),
        ("Vikram (Auto)", "9876543212"),
        ("Priya Reddy", "9876543213"),
        ("Arjun Nair", "9876543214"),
        ("Sanjay Gupta", "9876543215"),
        ("Fatima Sheikh", "9876543216"),
        ("Raj Kumar", "9876543217"),
        ("Ananya Iyer", "9876543218"),
        ("Deepak Sharma", "9876543219"),
        ("Kavya Nair", "9876543220"),
        ("Rohit Verma", "9876543221"),
    ]
    c.executemany(
        "INSERT INTO customers (name, phone) VALUES (?,?)", customers)

    # --- Sample Orders ---

    # Order 1: Sharma Ji's morning chai and bun maska (delivered)
    c.execute(
        "INSERT INTO orders (customer_id, status, total_amount) VALUES (1, 'delivered', 60)")
    oid = c.lastrowid
    c.execute("INSERT INTO order_items (order_id, menu_item_id, quantity, item_price) VALUES (?,?,?,?)",
              (oid, 1, 2, 15))   # 2x Cutting Chai = 30
    c.execute("INSERT INTO order_items (order_id, menu_item_id, quantity, item_price) VALUES (?,?,?,?)",
              (oid, 9, 1, 30))   # 1x Bun Maska = 30

    # Order 2: Meera's cold coffee (delivered)
    c.execute(
        "INSERT INTO orders (customer_id, status, total_amount) VALUES (2, 'delivered', 40)")
    oid = c.lastrowid
    c.execute("INSERT INTO order_items (order_id, menu_item_id, quantity, item_price) VALUES (?,?,?,?)",
              (oid, 5, 1, 40))

    # Order 3: Arjun's group order (preparing)
    c.execute(
        "INSERT INTO orders (customer_id, status, total_amount) VALUES (5, 'preparing', 155)")
    oid = c.lastrowid
    c.execute("INSERT INTO order_items (order_id, menu_item_id, quantity, item_price) VALUES (?,?,?,?)",
              (oid, 2, 3, 20))   # 3x Masala Chai = 60
    c.execute("INSERT INTO order_items (order_id, menu_item_id, quantity, item_price) VALUES (?,?,?,?)",
              (oid, 13, 2, 35))  # 2x Maggi = 70
    c.execute("INSERT INTO order_items (order_id, menu_item_id, quantity, item_price) VALUES (?,?,?,?)",
              (oid, 11, 1, 15))  # 1x Samosa = 15
    c.execute("INSERT INTO order_items (order_id, menu_item_id, quantity, item_price) VALUES (?,?,?,?)",
              (oid, 16, 1, 10))  # 1x Parle-G = 10

    # Order 4: Walk-in (no customer, pending)
    c.execute(
        "INSERT INTO orders (customer_id, status, total_amount) VALUES (NULL, 'pending', 35)")
    oid = c.lastrowid
    c.execute("INSERT INTO order_items (order_id, menu_item_id, quantity, item_price) VALUES (?,?,?,?)",
              (oid, 14, 1, 35))  # 1x Bread Omelette

    # Order 5: Priya's ginger chai and maggi (ready)
    c.execute(
        "INSERT INTO orders (customer_id, status, total_amount) VALUES (4, 'ready', 53)")
    oid = c.lastrowid
    c.execute("INSERT INTO order_items (order_id, menu_item_id, quantity, item_price) VALUES (?,?,?,?)",
              (oid, 3, 1, 18))   # 1x Ginger Chai
    c.execute("INSERT INTO order_items (order_id, menu_item_id, quantity, item_price) VALUES (?,?,?,?)",
              (oid, 13, 1, 35))  # 1x Maggi

    # --- Sample Reviews ---
    reviews = [
        # Sharma Ji on Masala Chai
        (2, 1, 5, "Best masala chai in Madhapur. No contest."),
        # Sharma Ji on Cutting Chai
        (1, 1, 5, "Cutting chai is perfect. Just the right sweetness."),
        # Meera on Cold Coffee
        (5, 2, 4, "Solid cold coffee. Cream could be thicker."),
        (11, 5, 5, "Samosa is always fresh. Fried on order, not sitting in a tray."),
        (13, 5, 4, "Maggi is good. Extra cheese would make it great."),
        (9, 4, 5, "Bun maska with cutting chai is the perfect combo."),
        (12, 3, 4, "Vada pav is almost Mumbai level. Almost."),
        (2, 6, 5, "Best chai I've had outside of home. -- Sanjay"),
        (14, 8, 3, "Bread omelette was OK. Eggs could be more runny."),
        (19, 9, 5, "Poha is light and perfect for mornings."),
    ]
    c.executemany(
        "INSERT INTO reviews (menu_item_id, customer_id, rating, comment) VALUES (?,?,?,?)",
        reviews
    )

    conn.commit()
    conn.close()
    print("Seeded: 20 menu items, 12 customers, 5 orders, 10 reviews.")


if __name__ == "__main__":
    seed()
