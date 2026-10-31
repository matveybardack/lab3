class RecipeAppError(Exception):
    """Базовое исключение приложения."""
    default_message = "Произошла ошибка приложения."

    def __init__(self, message: str | None = None):
        self.message = message or self.default_message
        super().__init__(self.message)


class EmptyRecipeBaseError(RecipeAppError):
    default_message = "В базе нет ни одного рецепта. Добавьте первый!"


class NoMatchingRecipeError(RecipeAppError):
    default_message = "Нет рецептов, подходящих под выбранные фильтры."


class InvalidRecipeDataError(RecipeAppError):
    default_message = "Некорректные данные рецепта."


class RecipeNotFoundError(RecipeAppError):
    default_message = "Рецепт не найден."


class DuplicateRecipeError(RecipeAppError):
    default_message = "Рецепт с таким названием уже существует."
