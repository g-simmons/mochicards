# (Unofficial) Mochi Flashcards Python Client



[![Version Badge](https://img.shields.io/badge/version-0.1.0-blue)]()

## Introduction

The MochiCards Python SDK provides an easy interface to interact with the Mochi API. With it, you can manage your cards and decks without needing to manually make HTTP requests.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
  - [Initialization](#initialization)
  - [Creating a Card](#creating-a-card)
  - [Getting a Card](#getting-a-card)
  - [Listing Cards](#listing-cards)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Installation

Make sure you have Python 3.9+ installed.

Then, install the SDK using poetry:

```bash
poetry add mochicards
```

## Usage

### Initialization

First, import and initialize the MochiClient with your API token:

```python
from mochicards.client import MochiClient

client = MochiClient(api_token="YOUR_MOCHI_API_TOKEN")
```

Alternatively, you can set the `MOCHI_API_KEY` environment variable and the client will automatically read it:

```python
# Read from MOCHI_API_KEY environment variable
client = MochiClient()
```

### Creating a Card

To create a new card:

```python
card_data = {
    "content": "Hello, World!",
    "deck_id": "deck_123",
    "archived": False,
}

new_card = client.create_card(**card_data)

print(new_card.id)
```

### Getting a Card

To retrieve a card by its ID:

```python
card_id = "some_card_id"
card = client.get_card(card_id)

print(card.content)
```

### Listing Cards

To list all cards:

```python
for card in client.list_cards():
    print(card.id, card.content)
```

You can also filter by `deck_id` and paginate using `limit` and `bookmark`.

## Testing

To run the tests:

```bash
poetry run pytest
```

## Contributing

1. Fork the repository.
2. Create a new branch for your features or fixes.
3. Write tests for your changes.
4. Ensure all tests pass.
5. Submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.