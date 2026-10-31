from datetime import timedelta
import random

from django.db.models import Count, F
from django.db.models.functions import TruncDate
from django.utils import timezone

from .models import ActivityLog, Recipe
from .exceptions import (
    DuplicateRecipeError,
    EmptyRecipeBaseError,
    InvalidRecipeDataError,
    NoMatchingRecipeError,
    RecipeNotFoundError,
)

class ActivityLogger:
    """Запись журнала активности и статистика для графика."""

    def log(self, action: str, message: str) -> ActivityLog:
        return ActivityLog.objects.create(action=action, message=message[:300])

    def recent(self, limit: int = 10):
        return ActivityLog.objects.all()[:limit]

    def daily_stats(self, days: int = 7) -> dict:
        today = timezone.localdate()
        start = today - timedelta(days=days - 1)
        rows = (
            ActivityLog.objects.filter(created_at__date__gte=start)
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(total=Count("id"))
        )
        counts = {r["day"]: r["total"] for r in rows}
        dates = [start + timedelta(days=i) for i in range(days)]
        return {
            "labels": [d.strftime("%d.%m") for d in dates],
            "counts": [counts.get(d, 0) for d in dates],
        }

class RecipeRepository:
    """Работа с данными рецептов: чтение, добавление, удаление."""

    def all(self):
        return Recipe.objects.all()

    def add(self, *, title, category, cooking_time, ingredients, instructions) -> Recipe:
        title = (title or "").strip()
        if not title:
            raise InvalidRecipeDataError("Название не может быть пустым.")
        if category not in Recipe.Category.values:
            raise InvalidRecipeDataError("Неизвестная категория.")
        if cooking_time is None or cooking_time <= 0:
            raise InvalidRecipeDataError("Время приготовления должно быть больше 0.")
        if Recipe.objects.filter(title__iexact=title).exists():
            raise DuplicateRecipeError()
        return Recipe.objects.create(
            title=title,
            category=category,
            cooking_time=cooking_time,
            ingredients=(ingredients or "").strip(),
            instructions=(instructions or "").strip(),
        )

    def delete(self, pk: int) -> str:
        try:
            recipe = Recipe.objects.get(pk=pk)
        except Recipe.DoesNotExist:
            raise RecipeNotFoundError() from None
        title = recipe.title
        recipe.delete()
        return title

class RecipeGenerator:
    """Случайный выбор рецепта с фильтрами по категории и времени."""

    def __init__(self, repository: RecipeRepository, logger: ActivityLogger):
        self.repository = repository
        self.logger = logger

    def generate(self, category: str | None = None, max_time: int | None = None) -> Recipe:
        qs = self.repository.all()
        if not qs.exists():
            raise EmptyRecipeBaseError()
        if category:
            qs = qs.filter(category=category)
        if max_time:
            qs = qs.filter(cooking_time__lte=max_time)
        recipes = list(qs)
        if not recipes:
            raise NoMatchingRecipeError()

        recipe = random.choice(recipes)
        Recipe.objects.filter(pk=recipe.pk).update(
            times_generated=F("times_generated") + 1
        )
        recipe.refresh_from_db()
        self.logger.log("generate", f"Выпал рецепт: {recipe.title}")
        return recipe

def build_services() -> tuple[ActivityLogger, RecipeRepository, RecipeGenerator]:
    """Собирает связанные сервисы: (logger, repository, generator)."""
    logger = ActivityLogger()
    repository = RecipeRepository()
    generator = RecipeGenerator(repository, logger)
    return logger, repository, generator
