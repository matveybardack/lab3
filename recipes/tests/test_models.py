import pytest
from django.db import IntegrityError

from recipes.models import ActivityLog, Recipe


def test_recipe_str(recipe):
    assert str(recipe) == "Борщ"


def test_recipe_title_unique(recipe):
    with pytest.raises(IntegrityError):
        Recipe.objects.create(
            title="Борщ",
            category="main",
            cooking_time=10,
            ingredients="x",
            instructions="y",
        )


def test_activitylog_ordering(db):
    ActivityLog.objects.create(action="add", message="первая")
    ActivityLog.objects.create(action="error", message="вторая")

    first = ActivityLog.objects.first()

    assert first.message == "вторая"
