from typing import Dict, List, Optional, Iterable
from mochicards.models import Card, CardData, Deck, Template, PaginatedCards
from datetime import datetime
from mochicards.errors import MochiError, MochiAuthenticationError, MochiNotFoundError
import requests
import os


class MochiClient:
    BASE_URL = "https://api.mochi.cards/api"

    def __init__(self, api_key: Optional[str] = None, base_url: str = BASE_URL):
        if api_key is None:
            api_key = os.environ.get("MOCHI_API_KEY", None)

        if not api_key:
            raise ValueError(
                "API key must be provided either as argument or MOCHI_API_KEY environment variable"
            )
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def create_card(
        self,
        content: str,
        deck_id: str,
        template_id: Optional[str] = None,
        fields: Optional[Dict] = None,
        attachments: Optional[List] = None,
        archived: bool = False,
        pos: Optional[str] = None,
        review_reverse: bool = False,
    ) -> Card:
        """Creates a new card.

        Args:
            content (str): The markdown content of the card.
            deck_id (str): The ID of the deck the card belongs to.
            template_id (str, optional): The ID of the template to use for this card.
            fields (Dict, optional): A dictionary of field IDs to field values. The field IDs
                should match those defined on the template used by the card. Each key-value pair
                in the dictionary represents a field ID and its value.
            attachments (List[dict], optional): A list of attachments to include with the card.
                Attachments can be accessed on the card via the markdown syntax. Each item in the
                list should be a dictionary with keys 'file-name', 'content-type', and 'data'.
            archived (bool, optional): Whether the card is archived. Defaults to False.
            pos (str, optional): The relative position of the card within the deck.
            review_reverse (bool, optional): Whether the card should also be reviewed in reverse
                order (bottom to top). Defaults to False.

        Returns:
            Card: The created card object.

        Raises:
            HTTPError: If the request returns an unsuccessful status code.

        Example:
            >>> card = client.create_card(
                    content="Hello world",
                    deck_id="deck_123"
                )
        """

        url = f"{self.base_url}/cards/"

        data = CardData(
            content=content,
            deck_id=deck_id,
            template_id=template_id,
            fields=fields,
            attachments=attachments,
            archived=archived,
            pos=pos,
            review_reverse=review_reverse,
        ).dict()

        response = requests.post(url, json=data, headers=self.headers, timeout=5)
        response.raise_for_status()

        return Card(**response.json())

    def get_card(self, card_id: str) -> Card:
        """Get a card by ID.

        Args:
        card_id: The ID of the card to retrieve.

        Returns:
        Card object containing the card data.

        Raises:
        HTTPError: If the request fails.
        """

        url = f"{self.base_url}/cards/{card_id}"

        response = requests.get(url, headers=self.headers, timeout=5)
        response.raise_for_status()

        return Card(**response.json())

    def list_cards(
        self,
        deck_id: Optional[str] = None,
        limit: Optional[int] = None,
        bookmark: Optional[str] = None,
    ) -> Iterable[Card]:
        """List cards across all pages.

        Args:
            deck_id: Filter cards by deck ID.
            limit: Max number of cards per page.
            bookmark: Page bookmark to start from.

        Yields:
            Card objects lazily as pages are retrieved.
        """
        while True:
            page_cards = self._list_cards(
                deck_id=deck_id, limit=limit, bookmark=bookmark
            )
            if not page_cards.docs or not page_cards.bookmark:
                break

            for card in page_cards.docs:
                yield card

            bookmark = page_cards.bookmark

    def _list_cards(
        self,
        deck_id: Optional[str] = None,
        limit: Optional[int] = None,
        bookmark: Optional[str] = None,
    ) -> PaginatedCards:
        """Get a single page of cards.

        Args:
            deck_id: Filter cards by deck ID.
            limit: Max number of cards per page.
            bookmark: Page bookmark to start from.

        Returns:
            PaginatedCards containing a list of cards and bookmark.
        """

        url = f"{self.base_url}/cards/"
        params = {"deck-id": deck_id, "limit": limit, "bookmark": bookmark}
        response = requests.get(url, params=params, headers=self.headers, timeout=5)
        response.raise_for_status()

        return PaginatedCards(**response.json())

    def update_card(
        self,
        card_id: str,
        content: Optional[str] = None,
        deck_id: Optional[str] = None,
        fields: Optional[Dict] = None,
        attachments: Optional[List[dict]] = None,
        archived: Optional[bool] = None,
        pos: Optional[str] = None,
    ) -> Card:
        """Update an existing card.

        Args:
            card_id (str): The ID of the card to update.
            content (Optional[str], optional): New content for the card.
            deck_id (Optional[str], optional): New deck ID for the card.
            fields (Optional[Dict], optional): New field values.
            attachments (Optional[List[dict]], optional): New attachments.
            archived (Optional[bool], optional): New archived status.
            pos (Optional[str], optional): New position.

        Returns:
            Card: The updated card object.

        Raises:
            HTTPError: If the request returns an unsuccessful status code.
        """
        url = f"{self.base_url}/cards/{card_id}"

        data = CardData(
            content=content,
            deck_id=deck_id,
            fields=fields,
            attachments=attachments,
            archived=archived,
            pos=pos,
        ).dict()

        response = requests.post(url, json=data, headers=self.headers, timeout=5)
        response.raise_for_status()

        return Card(**response.json())

    def delete_card(self, card_id: str) -> None:
        """Delete a card.

        WARNING: This action cannot be undone. For a "soft" deletion you can update a card and set its "trashed?" property to the current time.

        Parameters:
            card-id (string) - The ID of the card to delete.

        """
        url = f"{self.base_url}/cards/{card_id}"
        response = requests.delete(url, headers=self.headers, timeout=5)
        response.raise_for_status()

    def trash_card(self, card_id):
        """
        Move a card to the trash.

        This method will perform a soft delete on the card, allowing for potential recovery.

        Parameters:
            card_id (str): The unique identifier of the card to be trashed.

        Returns:
            dict: The updated card details, reflecting its trashed status.

        Raises:
            MochiError: If the request encounters an error.
        """

        url = f"{self.BASE_URL}/cards/{card_id}/trash"

        response = requests.post(url, headers=self.headers)

        # Handle errors
        if response.status_code == 401:
            raise MochiAuthenticationError("Invalid API key provided.")
        elif response.status_code == 404:
            raise MochiNotFoundError(f"Card with ID {card_id} not found.")
        elif not response.ok:
            error_detail = response.json().get("message", "Unknown error occurred.")
            raise MochiError(f"Failed to trash card: {error_detail}")

        return response.json()
