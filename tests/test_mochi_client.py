import pytest
import requests_mock
from datetime import datetime

from mochicards.client import MochiClient
import requests


@pytest.fixture
def first_page_response():
    return {
        "bookmark": "bookmark1",
        "docs": [
            {
                "tags": [],
                "content": "# Hello, world!",
                "name": "Hello world",
                "deck-id": "eH53Hxe8",
                "fields": {},
                "pos": "1",
                "references": [],
                "id": "card_1",
                "reviews": [],
                "created-at": {"date": "2021-09-09T02:49:58.535Z"},
                "updated-at": {"date": "2021-09-09T02:49:58.535Z"},
            },
            {
                "tags": [],
                "content": "# Hello, world!",
                "name": "Hello world",
                "deck-id": "eH53Hxe8",
                "fields": {},
                "pos": "2",
                "references": [],
                "id": "card_2",
                "reviews": [],
                "created-at": {"date": "2021-09-09T02:49:58.535Z"},
                "updated-at": {"date": "2021-09-09T02:49:58.535Z"},
            },
        ],
    }


@pytest.fixture
def second_page_response():
    return {
        "bookmark": "bookmark2",
        "docs": [
            {
                "tags": [],
                "content": "# Hello, world!",
                "name": "Hello world",
                "deck-id": "eH53Hxe8",
                "fields": {},
                "pos": "1",
                "references": [],
                "id": "card_3",
                "reviews": [],
                "created-at": {"date": "2021-09-09T02:49:58.535Z"},
                "updated-at": {"date": "2021-09-09T02:49:58.535Z"},
            },
            {
                "tags": [],
                "content": "# Hello, world!",
                "name": "Hello world",
                "deck-id": "eH53Hxe8",
                "fields": {},
                "pos": "2",
                "references": [],
                "id": "card_4",
                "reviews": [],
                "created-at": {"date": "2021-09-09T02:49:58.535Z"},
                "updated-at": {"date": "2021-09-09T02:49:58.535Z"},
            },
        ],
    }


def test_create_card_success(mocker, mochi_client):
    card_data = {"content": "Hello world", "deck_id": "deck_123", "archived": False}

    expected_response = {
        "updated-at": {"date": "2021-09-11T14:23:53.250Z"},
        "tags": [],
        "content": "Hello world",
        "name": None,
        "deck-id": "deck_123",
        "pos": "00F",
        "references": [],
        "id": "QQJ8ssvL",
        "reviews": [],
        "created-at": {"date": "2021-09-10T01:29:49.879Z"},
        "new?": False,
        "archived?": False,
        "template-id": None,
    }

    with requests_mock.Mocker() as m:
        m.post(f"{MochiClient.BASE_URL}/cards/", json=expected_response)
        result = mochi_client.create_card(**card_data)

        assert result.id == "QQJ8ssvL"
        assert result.content == "Hello world"
        assert result.deck_id == "deck_123"
        assert not result.archived
        assert isinstance(result.created_at, dict)
        assert isinstance(result.created_at["date"], datetime)
        assert isinstance(result.updated_at, dict)
        assert isinstance(result.updated_at["date"], datetime)


def test_create_card_fail(mocker, mochi_client):
    card_data = {"content": "Hello world", "deck_id": "deck_123", "archived": False}

    with requests_mock.Mocker() as m:
        m.post(f"{MochiClient.BASE_URL}/cards/", status_code=400)
        with pytest.raises(Exception):
            result = mochi_client.create_card(**card_data)


def test_get_card_success(mochi_client):
    card_id = "card_456"
    expected_response = {
        "updated-at": {"date": "2021-09-11T14:23:53.250Z"},
        "tags": [],
        "content": "Sample content",
        "name": "Sample Card",
        "deck-id": "deck_456",
        "pos": "00F",
        "references": [],
        "id": "card_456",
        "reviews": [],
        "created-at": {"date": "2021-09-10T01:29:49.879Z"},
        "new?": False,
        "archived?": False,
        "template-id": None,
    }

    with requests_mock.Mocker() as m:
        m.get(f"{MochiClient.BASE_URL}/cards/{card_id}", json=expected_response)
        result = mochi_client.get_card(card_id)

        assert result.id == "card_456"
        assert result.content == "Sample content"
        assert result.deck_id == "deck_456"
        assert not result.archived
        assert isinstance(result.created_at, dict)
        assert isinstance(result.created_at["date"], datetime)
        assert isinstance(result.updated_at, dict)
        assert isinstance(result.updated_at["date"], datetime)


def test_get_card_fail(mochi_client):
    card_id = "nonexistent_card_789"

    with requests_mock.Mocker() as m:
        m.get(f"{MochiClient.BASE_URL}/cards/{card_id}", status_code=404)

        with pytest.raises(requests.HTTPError):
            mochi_client.get_card(card_id)


def test_list_cards_single_page(mochi_client, first_page_response):
    with requests_mock.Mocker() as m:
        m.get(f"{MochiClient.BASE_URL}/cards/", json=first_page_response)

        cards = mochi_client._list_cards()

        assert len(cards.docs) == 2
        assert cards.docs[0].id == "card_1"
        assert cards.docs[1].id == "card_2"


def test_list_cards_multiple_pages(
    mochi_client, first_page_response, second_page_response
):
    with requests_mock.Mocker() as m:
        m.get(
            f"{MochiClient.BASE_URL}/cards/",
            json=first_page_response,
            additional_matcher=lambda req: "bookmark" not in req.url,
        )
        m.get(
            f"{MochiClient.BASE_URL}/cards/?bookmark=bookmark1",
            json=second_page_response,
        )
        m.get(
            f"{MochiClient.BASE_URL}/cards/?bookmark=bookmark2",
            json={"bookmark": None, "docs": []},
        )

        cards = list(mochi_client.list_cards())
        print(type(cards[0]))

        assert len(cards) == 4
        assert cards[0].id == "card_1"
        assert cards[1].id == "card_2"
        assert cards[2].id == "card_3"
