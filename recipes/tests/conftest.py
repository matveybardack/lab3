import pytest

from recipes.models import Recipe
from recipes.services import ActivityLogger, RecipeGenerator, RecipeRepository


@pytest.fixture
def logger():
    return ActivityLogger()


@pytest.fixture
def repository():
    return RecipeRepository()


@pytest.fixture
def generator(repository, logger):
    return RecipeGenerator(repository, logger)


@pytest.fixture
def recipe(db):
    return Recipe.objects.create(
        title="Борщ",
        category="soup",
        cooking_time=90,
        ingredients="Свёкла, капуста",
        instructions="Варить.",
    )
