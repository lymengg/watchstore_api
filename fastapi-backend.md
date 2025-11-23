# FastAPI backend for WatchStore products

This guide shows how to stand up a minimal FastAPI backend that matches the frontend’s expectations in `app/pages/index.vue` and serves products at `/api/products/`.

## Prerequisites
- Python 3.10+
- pip

## 1) Create and activate a virtual environment
```bash path=null start=null
python -m venv .venv
# Windows PowerShell
. .venv/Scripts/Activate.ps1
# macOS/Linux
# source .venv/bin/activate
```

## 2) Install dependencies
```bash path=null start=null
pip install "fastapi>=0.111" "uvicorn[standard]>=0.30" pydantic
```

## 3) Create the FastAPI app
Create `backend/main.py` with the following content:

```python path=null start=null
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="WatchStore API")

# Allow Nuxt dev server to call the API
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Product(BaseModel):
    id: int
    name: str
    brand: str
    price: float
    image: str
    description: str

# Simple in-memory data (mirror the frontend fallback shape)
PRODUCTS: List[Product] = [
    Product(id=1, name="Omega De Ville Prestige", brand="Omega", price=250, image="/imgs/omega_de_ville_prestige.jpg", description="Elegant silver watch with leather strap."),
    Product(id=2, name="Casio G-Shock DW-5600", brand="Casio", price=120, image="/imgs/casio-g-shock-dw-5600.jpg", description="Durable black watch for active lifestyles."),
    Product(id=3, name="Rolex Day-Date 40", brand="Rolex", price=1200, image="/imgs/rolex-day-date-40.jpg", description="Premium gold watch for special occasions."),
    Product(id=4, name="Daniel Wellington Classic Petite", brand="Daniel Wellington", price=180, image="/imgs/daniel-wellington-classic-petite.jpg", description="Simple and clean design for everyday use."),
    Product(id=5, name="Seiko 5 Sports SRPD51", brand="Seiko", price=90, image="/imgs/seiko-5-sports-sRPD51.jpg", description="Modern digital watch with blue accents."),
    Product(id=6, name="Fossil Townsman Chronograph", brand="Fossil", price=200, image="/imgs/fossil-townsman-chronograph.jpg", description="Classic vintage style with brown leather."),
    Product(id=7, name="Apple Watch Series 9", brand="Apple", price=350, image="/imgs/apple-watch-series-9.jpg", description="Track your health and fitness easily."),
    Product(id=8, name="Michael Kors Parker Rose Gold", brand="Michael Kors", price=300, image="/imgs/michael-kors-parker-rose-gold.jpg", description="Beautiful rose gold finish for elegance."),
    Product(id=9, name="Garmin Fenix 7X", brand="Garmin", price=400, image="/imgs/garmin-fenix-7X.jpg", description="Perfect for outdoor adventures."),
    Product(id=10, name="Tissot PRX Powermatic 80", brand="Tissot", price=220, image="/imgs/tissot-prx-powermatic-80.jpg", description="Timeless black watch for any occasion."),
]

@app.get("/api/health")
def health():
    return {"status": "ok"}

# Option A: return a plain list (frontend supports this)
@app.get("/api/products/", response_model=List[Product])
def list_products(q: Optional[str] = None, brand: Optional[str] = None,
                  min_price: Optional[float] = None, max_price: Optional[float] = None,
                  sort: Optional[str] = None):
    items = PRODUCTS

    # Lightweight server-side filtering (optional; frontend already filters locally)
    if q:
        ql = q.lower()
        items = [p for p in items if ql in p.name.lower() or ql in p.brand.lower() or ql in p.description.lower()]
    if brand:
        items = [p for p in items if p.brand == brand]
    if min_price is not None:
        items = [p for p in items if p.price >= min_price]
    if max_price is not None:
        items = [p for p in items if p.price <= max_price]

    if sort == "price-asc":
        items = sorted(items, key=lambda p: p.price)
    elif sort == "price-desc":
        items = sorted(items, key=lambda p: p.price, reverse=True)
    elif sort == "name-asc":
        items = sorted(items, key=lambda p: p.name)
    elif sort == "name-desc":
        items = sorted(items, key=lambda p: p.name, reverse=True)
    elif sort == "brand-asc":
        items = sorted(items, key=lambda p: p.brand)

    return items

# Option B: return an envelope the frontend also supports
@app.get("/api/products/enveloped")
def list_products_enveloped():
    return {"status": "success", "data": PRODUCTS}

@app.get("/api/products/{product_id}", response_model=Product)
def get_product(product_id: int):
    for p in PRODUCTS:
        if p.id == product_id:
            return p
    raise HTTPException(status_code=404, detail="Product not found")
```

Notes
- Either /api/products/ (plain list) or /api/products/enveloped (with status/data) will work; `app/pages/index.vue` handles both.
- Keep /api/products/ public (no auth) to match the current frontend behavior.

## 4) Run the server
```bash path=null start=null
# From the project root (so path ./backend/main.py exists)
uvicorn backend.main:app --reload --port 8000
```

## 5) Configure the frontend base URL (if needed)
The Nuxt app reads `NUXT_PUBLIC_API_BASE`. By default it uses `http://localhost:8000`, which matches the command above. To override:
```bash path=null start=null
# PowerShell
$env:NUXT_PUBLIC_API_BASE = "http://localhost:8000"
# Bash
# export NUXT_PUBLIC_API_BASE="http://localhost:8000"
```

## 6) Verify endpoints
```bash path=null start=null
curl http://localhost:8000/api/health
curl http://localhost:8000/api/products/
curl http://localhost:8000/api/products/enveloped
curl http://localhost:8000/api/products/1
```

Expected product shape (what the frontend uses):
```json path=null start=null
{
  "id": 1,
  "name": "Omega De Ville Prestige",
  "brand": "Omega",
  "price": 250,
  "image": "/imgs/omega_de_ville_prestige.jpg",
  "description": "Elegant silver watch with leather strap."
}
```

## 7) Next steps (optional)
- Replace the in-memory list with a real database (e.g., SQLModel/SQLAlchemy + SQLite/Postgres).
- Add pagination and total counts to `/api/products/`.
- Implement auth for write operations while keeping read endpoints public.
