import datetime

import pytest

from cases.models import CaseItem, Case, Item
from custom_user.models import CustomUser
from history.models import HistoryCase as HCase
from history.models import HistoryItem as HItem


@pytest.fixture
def test_user():
    user = CustomUser.objects.create(
        first_name="Test", last_name="User", telegram_id=123456789, balance=1000
    )
    return user


@pytest.fixture
def test_items_and_cases(test_user):
    items = []

    item = Item.objects.create(
        name=f"Test Item", type="crystal", crystals=1, price=100, cashback=None
    )
    case = Case.objects.create(name=f"Test Case", photo_url="", price=50)
    CaseItem.objects.create(case=case, item=item, drop_rate=100)

    for i in range(12):
        h_item = HItem.objects.create(
            item=item,
            owner=test_user,
        )
        HCase.objects.create(
            case=case,
            item=h_item,
            user=test_user,
            opened_at=datetime.datetime.now(),
        )

        items.append(h_item)
    return items
