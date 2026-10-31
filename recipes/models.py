from django.db import models


class Recipe(models.Model):
    class Category(models.TextChoices):
        BREAKFAST = "breakfast", "Завтрак"
        SOUP = "soup", "Суп"
        MAIN = "main", "Основное блюдо"
        DESSERT = "dessert", "Десерт"
        SNACK = "snack", "Закуска"

    title = models.CharField("Название", max_length=200, unique=True)
    category = models.CharField("Категория", max_length=20, choices=Category.choices)
    cooking_time = models.PositiveSmallIntegerField("Время, мин")
    ingredients = models.TextField("Ингредиенты")
    instructions = models.TextField("Способ приготовления")
    times_generated = models.PositiveIntegerField("Выпадал раз", default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title


class ActivityLog(models.Model):
    class Action(models.TextChoices):
        GENERATE = "generate", "Генерация"
        ADD = "add", "Добавление"
        DELETE = "delete", "Удаление"
        ERROR = "error", "Ошибка"
        EXIT = "exit", "Выход"

    action = models.CharField(max_length=20, choices=Action.choices)
    message = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"[{self.created_at:%Y-%m-%d %H:%M}] {self.action}: {self.message}"
