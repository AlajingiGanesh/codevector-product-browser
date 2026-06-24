import argparse
import logging
import random
import sys
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from sqlalchemy import insert, text

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.database import Base, SessionLocal, engine  # noqa: E402
from app.models.product import Product  # noqa: E402
from app.schemas.product import PRODUCT_CATEGORIES  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


ADJECTIVES = [
    "Premium",
    "Compact",
    "Wireless",
    "Classic",
    "Modern",
    "Eco",
    "Smart",
    "Durable",
    "Portable",
    "Essential",
]

PRODUCT_WORDS: dict[str, list[str]] = {
    "Electronics": ["Headphones", "Keyboard", "Monitor", "Charger", "Speaker"],
    "Clothing": ["Jacket", "Sneakers", "Hoodie", "Shirt", "Jeans"],
    "Books": ["Cookbook", "Novel", "Workbook", "Biography", "Guide"],
    "Sports": ["Yoga Mat", "Dumbbell", "Tennis Racket", "Helmet", "Backpack"],
    "Home": ["Lamp", "Chair", "Shelf", "Curtains", "Storage Bin"],
    "Beauty": ["Face Cream", "Serum", "Brush Set", "Shampoo", "Lip Balm"],
    "Automotive": ["Floor Mats", "Dash Camera", "Car Wax", "Air Freshener", "Tool Kit"],
    "Toys": ["Puzzle", "Building Set", "Board Game", "Doll", "Action Figure"],
    "Grocery": ["Coffee", "Pasta", "Granola", "Olive Oil", "Tea"],
    "Health": ["Vitamins", "Bandages", "Thermometer", "Protein Powder", "First Aid Kit"],
}

PRICE_RANGES: dict[str, tuple[Decimal, Decimal]] = {
    "Electronics": (Decimal("19.99"), Decimal("899.99")),
    "Clothing": (Decimal("9.99"), Decimal("249.99")),
    "Books": (Decimal("4.99"), Decimal("79.99")),
    "Sports": (Decimal("8.99"), Decimal("399.99")),
    "Home": (Decimal("6.99"), Decimal("599.99")),
    "Beauty": (Decimal("3.99"), Decimal("149.99")),
    "Automotive": (Decimal("5.99"), Decimal("499.99")),
    "Toys": (Decimal("4.99"), Decimal("199.99")),
    "Grocery": (Decimal("1.99"), Decimal("89.99")),
    "Health": (Decimal("2.99"), Decimal("249.99")),
}


def random_price(category: str) -> Decimal:
    low, high = PRICE_RANGES[category]
    cents = random.randint(int(low * 100), int(high * 100))
    return (Decimal(cents) / Decimal("100")).quantize(Decimal("0.01"))


def random_name(category: str, row_number: int) -> str:
    adjective = random.choice(ADJECTIVES)
    noun = random.choice(PRODUCT_WORDS[category])
    model = random.randint(100, 999)
    return f"{adjective} {noun} {model}-{row_number % 10000:04d}"


def generate_product(row_number: int, now: datetime) -> dict[str, object]:
    category = random.choice(PRODUCT_CATEGORIES)
    created_at = now - timedelta(
        days=random.randint(0, 365),
        seconds=random.randint(0, 86_400),
        microseconds=random.randint(0, 999_999),
    )
    updated_at = created_at + timedelta(
        days=random.randint(0, 30),
        seconds=random.randint(0, 86_400),
        microseconds=random.randint(0, 999_999),
    )
    if updated_at > now:
        updated_at = now - timedelta(microseconds=random.randint(0, 999_999))

    return {
        "name": random_name(category, row_number),
        "category": category,
        "price": random_price(category),
        "created_at": created_at.replace(tzinfo=None),
        "updated_at": updated_at.replace(tzinfo=None),
    }


def seed_products(count: int, batch_size: int, reset: bool) -> None:
    random.seed(42)
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        if reset:
            logger.info("Reset requested; truncating products table.")
            db.execute(text("TRUNCATE TABLE products"))
            db.commit()

        now = datetime.now(tz=UTC)
        inserted = 0

        while inserted < count:
            current_batch_size = min(batch_size, count - inserted)
            batch = [
                generate_product(inserted + index + 1, now)
                for index in range(current_batch_size)
            ]
            db.execute(insert(Product), batch)
            db.commit()
            inserted += current_batch_size
            logger.info("Inserted %s/%s products.", inserted, count)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed MySQL with products.")
    parser.add_argument("--count", type=int, default=200_000)
    parser.add_argument("--batch-size", type=int, default=5_000)
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Truncate products before seeding. Off by default.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    seed_products(count=args.count, batch_size=args.batch_size, reset=args.reset)

