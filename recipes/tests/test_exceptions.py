import pytest

from recipes.exceptions import (
    DuplicateRecipeError,
    EmptyRecipeBaseError,
    InvalidRecipeDataError,
    NoMatchingRecipeError,
    RecipeAppError,
    RecipeNotFoundError,
)

ALL_ERRORS = [
    EmptyRecipeBaseError,
    NoMatchingRecipeError,
    InvalidRecipeDataError,
    RecipeNotFoundError,
    DuplicateRecipeError,
]


@pytest.mark.parametrize("error_class", ALL_ERRORS)
def test_errors_inherit_base(error_class):
    assert issubclass(error_class, RecipeAppError)


@pytest.mark.parametrize("error_class", ALL_ERRORS)
def test_default_message_used(error_class):
    error = error_class()

    assert error.message == error_class.default_message
    assert str(error) == error_class.default_message


@pytest.mark.parametrize("error_class", ALL_ERRORS)
def test_custom_message_overrides_default(error_class):
    error = error_class("Своё сообщение")

    assert error.message == "Своё сообщение"
    assert str(error) == "Своё сообщение"


def test_base_error_default_message():
    assert RecipeAppError().message == RecipeAppError.default_message
