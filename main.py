from fastapi import FastAPI, HTTPException, Query
from database import init_db, get_connection
from typing import Optional
from pydantic import BaseModel, Field


app = FastAPI(title="Chai Tapri API",
              description="This is the backend for famous tea shop",
              version='1.0.0')

# --- Create tables on startup ----
init_db()

# We wil be using Pydantic (Used Data Validation)

# create a schema or datatype for menu item


class MenuItemResponse(BaseModel):
    id: int
    name: str
    category: str
    price: float
    description: Optional[str]
    is_available: bool


class MenuItemCreate(BaseModel):
    name: str
    category: str
    price: float
    description: Optional[str]
    is_available: bool


class MenuItemUpdate(BaseModel):  # use for patch thats why everything is optional
    name: Optional[str] = Field(None, min_length = 1, max_len = 20 )
    category: Optional[str] = Field(None, min_length=1, max_len=20)
    price: Optional[float] = Field(None, ge = 0)
    description: Optional[str] = Field(None, max_length=500)
    is_available: Optional[bool] = None


@app.get("/")
def home():
    return {
        "name": "Raju Bhai's Chai Tapri",
        "location": "Madhapur, Hyderabad",
        "since": 2012,
        "docs": "Visit /docs for the full API"
    }


@app.get("/menu")
def get_menu(
    category: Optional[str] = Query(None, description = "Filter: beverage, snack or special", example="snack"),
    available_only: Optional[bool] = Query(
        default=None, description="Show only available items"),
    min_price: Optional[float] = Query(None, ge = 0, le=1000),
    max_price: Optional[float] = Query(None, ge=0),
    search: Optional[str] = Query(None, description="Search in item name"),
    sort_by: str = Query("name", description="Sort by: name, price, category")
):
    """Browse the menu with optional filters.

    All filters are AND-ed together. All are optional.
    With no filters, returns the full menu.

    Examples:
        /menu                                  -- full menu
        /menu?category=beverage                -- only drinks
        /menu?available_only=true&sort_by=price -- available items, cheapest first
        /menu?min_price=20&max_price=40        -- items in a price range
        /menu?search=chai                      -- items with "chai" in the name
    """
    # print(f"{category = } {available_only = }")
    # "GET /menu?category=123&available_only=false HTTP/1.1"
    # get the connection
    conn = get_connection()
    query = "SELECT * FROM menu_items where 1=1"
    params = []
    if category:
        allowed = {"beverage", "snack", "special"}
        if category.lower() not in allowed:
            raise HTTPException(
                status_code=400, detail=f"category must be one of: {', '.join(allowed)}")
        query += " AND category = ?"
        params.append(category)

    if available_only:
        query += " AND is_available = 1"

    if min_price is not None:
        query += " AND price >= ?"
        params.append(min_price)

    if max_price is not None:
        query += " AND price <= ?"
        params.append(max_price)

    if search:
        query += " AND LOWER(name) LIKE ?"
        params.append(f"%{search.lower()}%")


    allowed_sorts = {"name", "price", "category"}
    if sort_by not in allowed_sorts:
        sort_by = "name"
    query += f" ORDER BY {sort_by}"
     
    rows = conn.execute(query, params).fetchall()
    conn.close()
    # print(rows)
    return [dict(r) for r in rows]


@app.get("/menu/{item_id}")  # path parameter
def get_menu_item(item_id):
    '''
    """Get a single menu item by ID."""
    '''

    conn = get_connection()
    row = conn.execute(
        "SELECT * from menu_items where id = ?", (item_id,)).fetchone()

    if not row:
        raise HTTPException(status_code=404,
                            detail=f"Item {item_id} is not found! ")
    conn.close()

    return dict(row)


@app.post('/menu', status_code=201, response_model = MenuItemResponse )
def create_menu_item(item: MenuItemCreate):
    conn = get_connection()

    # check if the item already is existing
    existing = conn.execute(
        "SELECT id FROM menu_items WHERE LOWER(name) = LOWER(?)", (item.name,)
    ).fetchone()

    if existing:
        conn.close()
        raise HTTPException(
            status_code=409, detail=f"'{item.name}' already exists on the menu")

    # insert the data into db
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


    response_dict = dict(row)
    print(f"{response_dict=}")
    response_dict.pop("name")
    print(f"{response_dict=}")
    return response_dict


@app.put("/menu/{item_id}", response_model= MenuItemResponse)
def replace_menu_item(item_id:int, item: MenuItemCreate):
    """
    Replace a menu item entirely. All fields are required.
        
    PUT means "replace the entire resource with what I am sending."
    If you forget a field, it gets overwritten. This is different 
    from PATCH (below) which only changes what you send.
    """
    conn = get_connection()
    existing = conn.execute(
        "SELECT id FROM menu_items WHERE id = ?", (item_id,)).fetchone()
    if not existing:
        conn.close()
        raise HTTPException(
            status_code=404, detail=f"Menu item {item_id} not found")
    allowed = {"beverage", "snack", "special"}
    if item.category.lower() not in allowed:
        conn.close()
        raise HTTPException(
            status_code=400, detail=f"category must be one of: {', '.join(allowed)}")
    
    conn.execute(
        """UPDATE menu_items 
           SET name=?, category=?, price=?, description=?, is_available=? 
           WHERE id=?""",
        (item.name, item.category.lower(), item.price, item.description,
         1 if item.is_available else 0, item_id)
    )
    conn.commit()

    row = conn.execute(
        "SELECT * FROM menu_items WHERE id = ?", (item_id,)).fetchone()
    
    conn.close()
    return dict(row)
    
@app.patch("/menu/{item_id}", response_model= MenuItemResponse)
def update_menu_item(item_id:int, item:MenuItemUpdate):
    """Update specific fields of a menu item. Only send what you want to change.
    
    PATCH means "change only what I am sending, leave everything else alone."
    If you send {"price": 25}, only the price changes. Name, category, 
    description, and availability stay exactly as they were.
    
    This is different from PUT which replaces everything.
    """
    print(f"{item= }")
    conn = get_connection()
    existing = conn.execute(
        "SELECT id FROM menu_items WHERE id = ?", (item_id,)).fetchone()
    if not existing:
        conn.close()
        raise HTTPException(
            status_code=404, detail=f"Menu item {item_id} not found")

    # model_dump(exclude_unset=True) returns only the fields the client actually sent.
    # If the client sent {"price": 25}, this returns {"price": 25.0}.
    # Fields they did not mention are excluded, so we do not accidentally overwrite them.
    updates = item.model_dump(exclude_unset=True) ## remove all None wala keys
    print(f"{updates = }")
    if not updates:
        conn.close()
        raise HTTPException(status_code=400, detail="No fields to update")

    if "category" in updates:
        allowed = {"beverage", "snack", "special"}
        if updates["category"].lower() not in allowed:
            conn.close()
            raise HTTPException(
                status_code=400, detail=f"category must be one of: {', '.join(allowed)}")
        updates["category"] = updates["category"].lower()

    if "is_available" in updates:
        updates["is_available"] = 1 if updates["is_available"] else 0

    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [item_id]
    conn.execute(f"UPDATE menu_items SET {set_clause} WHERE id = ?", values)
    conn.commit()


    # fetch the value afte executing
    row = conn.execute(
        "SELECT * FROM menu_items WHERE id = ?", (item_id,)).fetchone()
    conn.close()
    return dict(row)


@app.delete("/menu/{item_id}", status_code=204)
def delete_menu_item(item_id:int):
    """Remove an item from the menu. Returns 204 No Content.
    
    204 means "success, and there is nothing to return."
    The item is gone. An empty response confirms it.
    """

    conn = get_connection()
    existing = conn.execute(
        "SELECT id FROM menu_items WHERE id = ?", (item_id,)).fetchone()
    if not existing:
        conn.close()
        raise HTTPException(
            status_code=404, detail=f"Menu item {item_id} not found")

    conn.execute("DELETE FROM menu_items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()







if __name__ == "__main__":
    import uvicorn  # ASGI vs WSGI
    uvicorn.run(app, host="0.0.0.0", port=8000)
