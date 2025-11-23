from sqlalchemy.orm import Session
from database import SessionLocal
from models import Product

# Seed data (no images; frontend accepts null image)
SEED_PRODUCTS = [
    {
        "name": "Omega De Ville Prestige",
        "brand": "Omega",
        "price": 250.0,
        "description": "Elegant silver watch with leather strap.",
        "stock": 20,
    },
    {
        "name": "Casio G-Shock DW-5600",
        "brand": "Casio",
        "price": 120.0,
        "description": "Durable black watch for active lifestyles.",
        "stock": 35,
    },
    {
        "name": "Rolex Day-Date 40",
        "brand": "Rolex",
        "price": 1200.0,
        "description": "Premium gold watch for special occasions.",
        "stock": 5,
    },
    {
        "name": "Daniel Wellington Classic Petite",
        "brand": "Daniel Wellington",
        "price": 180.0,
        "description": "Simple and clean design for everyday use.",
        "stock": 25,
    },
    {
        "name": "Seiko 5 Sports SRPD51",
        "brand": "Seiko",
        "price": 90.0,
        "description": "Modern digital watch with blue accents.",
        "stock": 40,
    },
    {
        "name": "Fossil Townsman Chronograph",
        "brand": "Fossil",
        "price": 200.0,
        "description": "Classic vintage style with brown leather.",
        "stock": 18,
    },
    {
        "name": "Apple Watch Series 9",
        "brand": "Apple",
        "price": 350.0,
        "description": "Track your health and fitness easily.",
        "stock": 30,
    },
    {
        "name": "Michael Kors Parker Rose Gold",
        "brand": "Michael Kors",
        "price": 300.0,
        "description": "Beautiful rose gold finish for elegance.",
        "stock": 22,
    },
    {
        "name": "Garmin Fenix 7X",
        "brand": "Garmin",
        "price": 400.0,
        "description": "Perfect for outdoor adventures.",
        "stock": 12,
    },
    {
        "name": "Tissot PRX Powermatic 80",
        "brand": "Tissot",
        "price": 220.0,
        "description": "Timeless black watch for any occasion.",
        "stock": 28,
    },
]


def seed_products(db: Session):
    for p in SEED_PRODUCTS:
        # Avoid duplicates by name
        exists = db.query(Product).filter(Product.name == p["name"]).first()
        if exists:
            continue
        db.add(Product(
            name=p["name"],
            brand=p["brand"],
            description=p["description"],
            price=p["price"],
            image=None,
            stock=p["stock"],
        ))
    db.commit()


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_products(db)
        print("Seeded products.")
    finally:
        db.close()
