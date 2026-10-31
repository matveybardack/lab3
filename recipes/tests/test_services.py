import pytest

from recipes.exceptions import (
    DuplicateRecipeError,
    EmptyRecipeBaseError,
    InvalidRecipeDataError,
    NoMatchingRecipeError,
    RecipeNotFoundError,
)
from recipes.models import ActivityLog, Recipe


def valid_data(**overrides):
    """Корректные данные рецепта; отдельные поля можно подменить."""
    data = {
        "title": "Омлет",
        "category": "breakfast",
        "cooking_time": 10,
        "ingredients": "Яйца, молоко",
        "instructions": "Взбить и пожарить.",
    }
    data.update(overrides)
    return data


# ---------- RecipeRepository ----------

def test_add_recipe_ok(db, repository):
    before = Recipe.objects.count()

    created = repository.add(**valid_data())

    assert Recipe.objects.count() == before + 1
    assert created.title == "Омлет"


def test_add_empty_title_raises(db, repository):
    with pytest.raises(InvalidRecipeDataError):
        repository.add(**valid_data(title="   "))


def test_add_bad_category_raises(db, repository):
    with pytest.raises(InvalidRecipeDataError):
        repository.add(**valid_data(category="nope"))


def test_add_zero_time_raises(db, repository):
    with pytest.raises(InvalidRecipeDataError):
        repository.add(**valid_data(cooking_time=0))


def test_delete_ok(recipe, repository):
    title = repository.delete(recipe.pk)

    assert title == "Борщ"
    assert not Recipe.objects.filter(pk=recipe.pk).exists()


def test_delete_missing_raises(db, repository):
    with pytest.raises(RecipeNotFoundError):
        repository.delete(9999)


# ---------- RecipeGenerator ----------

def test_generate_empty_db_raises(db, generator):
    with pytest.raises(EmptyRecipeBaseError):
        generator.generate()


def test_generate_returns_recipe(recipe, generator):
    result = generator.generate()

    assert result.pk == recipe.pk
    assert result.times_generated == 1


def test_generate_filter_category(recipe, repository, generator):
    repository.add(**valid_data())  # «Омлет», breakfast

    for _ in range(10):
        assert generator.generate(category="breakfast").title == "Омлет"


def test_generate_filter_max_time(recipe, repository, generator):
    repository.add(**valid_data())  # 10 мин; «Борщ» занимает 90

    for _ in range(10):
        assert generator.generate(max_time=15).cooking_time <= 15


def test_generate_no_match_raises(recipe, generator):
    with pytest.raises(NoMatchingRecipeError):
        generator.generate(category="dessert")


def test_generate_writes_log(recipe, generator):
    generator.generate()

    log = ActivityLog.objects.get(action="generate")
    assert "Борщ" in log.message

# ---------- ActivityLogger ----------

def test_log_creates_entry(db, logger):
    entry = logger.log("add", "тестовая запись")

    assert ActivityLog.objects.count() == 1
    assert entry.action == "add"
    assert entry.message == "тестовая запись"


def test_log_truncates_long_message(db, logger):
    entry = logger.log("error", "x" * 500)

    assert len(entry.message) == 300


def test_recent_limit(db, logger):
    for i in range(5):
        logger.log("add", f"запись {i}")

    assert len(logger.recent(limit=3)) == 3


def test_daily_stats_shape(db, logger):
    for _ in range(4):
        logger.log("add", "событие")

    stats = logger.daily_stats(days=7)

    assert len(stats["labels"]) == 7
    assert len(stats["counts"]) == 7
    assert sum(stats["counts"]) == 4
    assert stats["counts"][-1] == 4
