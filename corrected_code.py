"""Inventory management with secure and lint-compliant code."""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

LOG_FORMAT = "%(asctime)s %(levelname)s: %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

# Global inventory store
stock_data: Dict[str, int] = {}


def add_item(
    item: str,
    qty: int = 0,
    logs: Optional[List[str]] = None,
) -> None:
    """Add quantity of an item to the inventory.

    Args:
        item: Item name (non-empty string).
        qty: Quantity to add (non-negative integer).
        logs: Optional list to append a log entry.
    """
    if logs is None:
        logs = []

    if not isinstance(item, str) or not item:
        raise TypeError("item must be a non-empty string")
    if not isinstance(qty, int):
        raise TypeError("qty must be an integer")
    if qty < 0:
        raise ValueError("qty must be non-negative")

    stock_data[item] = stock_data.get(item, 0) + qty
    entry = f"{datetime.now().isoformat()}: Added {qty} of {item}"
    logs.append(entry)
    logging.info(entry)


def remove_item(item: str, qty: int) -> None:
    """Remove quantity of an item from the inventory.

    Args:
        item: Item name (non-empty string).
        qty: Quantity to remove (positive integer).

    Raises:
        KeyError: If the item is not in inventory.
    """
    if not isinstance(item, str) or not item:
        raise TypeError("item must be a non-empty string")
    if not isinstance(qty, int):
        raise TypeError("qty must be an integer")
    if qty <= 0:
        raise ValueError("qty must be positive")

    if item not in stock_data:
        raise KeyError(f"Item '{item}' not found in stock")

    remaining = stock_data[item] - qty
    if remaining > 0:
        stock_data[item] = remaining
        logging.info(
            "%s: Removed %d of %s",
            datetime.now().isoformat(),
            qty,
            item,
        )
    else:
        del stock_data[item]
        logging.info(
            "%s: Removed %d of %s (depleted)",
            datetime.now().isoformat(),
            qty,
            item,
        )


def get_qty(item: str) -> int:
    """Get current quantity of an item. Returns 0 if not present."""
    if not isinstance(item, str) or not item:
        raise TypeError("item must be a non-empty string")
    return stock_data.get(item, 0)


def load_data(file: str = "inventory.json") -> None:
    """Load inventory from a JSON file into the global store."""
    try:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise ValueError("inventory file must contain a JSON object")

        normalized: Dict[str, int] = {}
        for k, v in data.items():
            key = str(k)
            try:
                normalized[key] = int(v)
            except (TypeError, ValueError):
                logging.warning(
                    "Skipping item '%s' with non-integer quantity: %r",
                    key,
                    v,
                )

        # Update in place to avoid global reassignment
        stock_data.clear()
        stock_data.update(normalized)
        logging.info("Loaded inventory from %s", file)

    except FileNotFoundError:
        logging.warning(
            "Inventory file '%s' not found; starting with empty inventory",
            file,
        )
        stock_data.clear()
    except json.JSONDecodeError as err:
        logging.error("Failed to parse inventory file '%s': %s", file, err)
        raise


def save_data(file: str = "inventory.json") -> None:
    """Save current inventory to a JSON file."""
    try:
        with open(file, "w", encoding="utf-8") as f:
            json.dump(stock_data, f, indent=2)
        logging.info("Saved inventory to %s", file)
    except OSError as err:
        logging.error("Failed to save inventory to '%s': %s", file, err)
        raise


def print_data() -> None:
    """Log all items and their quantities."""
    logging.info("Items Report")
    for name, qty in stock_data.items():
        logging.info("%s -> %d", name, qty)


def check_low_items(threshold: int = 5) -> List[str]:
    """Return a list of items with quantity below the threshold."""
    if not isinstance(threshold, int):
        raise TypeError("threshold must be an integer")
    return [name for name, qty in stock_data.items() if qty < threshold]


def main() -> None:
    """Demonstration of inventory operations."""
    add_item("apple", 10)
    add_item("banana", 2)
    remove_item("apple", 3)
    try:
        remove_item("orange", 1)
    except KeyError:
        logging.info("Tried to remove non-existing item 'orange'")
    logging.info("Apple stock: %d", get_qty("apple"))
    logging.info("Low items: %s", check_low_items())
    save_data()
    load_data()
    print_data()


if __name__ == "_main_":
    main()