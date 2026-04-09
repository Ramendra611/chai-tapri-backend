from fastapi import FastAPI, HTTPException
from database import init_db, get_connection
from typing import Optional
from pydantic import BaseModel


app = FastAPI(title = "Chai Tapri API", 
              description="This is the backend for famous tea shop", 
              version='1.0.0')

# --- Create tables on startup ----
init_db()

## We wil be using Pydantic (Used Data Validation)

# create a schema or datatype for menu item


class MenuItemResponse(BaseModel):
    id: int
    name: str
    category: str
    price: float
    description: Optional[str]
    is_available: bool



@app.get("/")
def home():
    return {
        "name": "Raju Bhai's Chai Tapri",
        "location": "Madhapur, Hyderabad",
        "since": 2012,
        "docs": "Visit /docs for the full API"
    }

@app.get("/menu")
def get_menu():
    '''
    Browse the menu and return result as per user preference

     Examples:
        /menu                                  -- full menu
        /menu?category=beverage                -- only drinks
        /menu?available_only=true&sort_by=price -- available items, cheapest first
        /menu?min_price=20&max_price=40        -- items in a price range
        /menu?search=chai                      -- items with "chai" in the name
    '''

    ## get the connection
    conn = get_connection()
    query = "SELECT * FROM menu_items"

    rows = conn.execute(query).fetchall()
    conn.close()
    # print(rows)
    return [dict(r) for r in  rows]


@app.get("/menu/{item_id}")
def get_menu_item(item_id):
    '''
    """Get a single menu item by ID."""
    '''

    conn = get_connection()
    row = conn.execute("SELECT * from menu_items where id = ?", (item_id,)).fetchone()

    if not row:
        raise HTTPException(status_code=404, 
                            detail =f"Item {item_id} is not found! ")
    conn.close()

    return dict(row)


@app.post('/menu', status_code=201)
def create_menu_item(item: MenuItemResponse):
    conn = get_connection()

    ## check if the item already is existing
    existing = conn.execute(
        "SELECT id FROM menu_items WHERE LOWER(name) = LOWER(?)", (item.name,)
    ).fetchone()

    if existing:
        conn.close()
        raise HTTPException(
            status_code=409, detail=f"'{item.name}' already exists on the menu")
    
    ## insert the data into db
    conn.execute(
        "INSERT INTO menu_items (name, category, price, description, is_available) VALUES (?,?,?,?,?)",
        (item.name, item.category.lower(), item.price,
         item.description, 1 if item.is_available else 0)
    )
    new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.commit()

    row = conn.execute(
        "SELECT * FROM menu_items WHERE id = ?", (new_id,)).fetchone()
    
    conn.close()
    return dict(row)

















