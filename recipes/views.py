from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse

from .exceptions import RecipeAppError
from .forms import GenerateForm, RecipeForm
from .models import Recipe
from .services import build_services


class BaseRecipeView(View):
    """Общая инициализация сервисов для всех view."""

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.logger, self.repository, self.generator = build_services()

    def fail(self, request, message: str) -> None:
        """Показать ошибку пользователю и записать её в журнал."""
        messages.error(request, message)
        self.logger.log("error", message)


class DashboardView(BaseRecipeView):
    def get(self, request):
        generated = None
        pk = request.GET.get("generated")
        if pk and pk.isdigit():
            generated = Recipe.objects.filter(pk=int(pk)).first()

        context = {
            "recipes": self.repository.all(),
            "recipe_form": RecipeForm(),
            "generate_form": GenerateForm(),
            "logs": self.logger.recent(10),
            "generated": generated,
        }
        return render(request, "recipes/dashboard.html", context)


class AddRecipeView(BaseRecipeView):
    def post(self, request):
        form = RecipeForm(request.POST)
        if not form.is_valid():
            for errors in form.errors.values():
                for error in errors:
                    self.fail(request, error)
            return redirect("dashboard")

        try:
            recipe = self.repository.add(**form.cleaned_data)
        except RecipeAppError as e:
            self.fail(request, e.message)
        else:
            text = f"Добавлен рецепт: {recipe.title}"
            messages.success(request, text)
            self.logger.log("add", text)
        return redirect("dashboard")

class GenerateView(BaseRecipeView):
    def post(self, request):
        form = GenerateForm(request.POST)
        if not form.is_valid():
            for errors in form.errors.values():
                for error in errors:
                    self.fail(request, error)
            return redirect("dashboard")

        try:
            recipe = self.generator.generate(
                category=form.cleaned_data["category"] or None,
                max_time=form.cleaned_data["max_time"],
            )
        except RecipeAppError as e:
            self.fail(request, e.message)
            return redirect("dashboard")

        messages.success(request, f"Выпал рецепт: {recipe.title}")
        return redirect(f"{reverse('dashboard')}?generated={recipe.pk}")


class DeleteRecipeView(BaseRecipeView):
    def post(self, request, pk: int):
        try:
            title = self.repository.delete(pk)
        except RecipeAppError as e:
            self.fail(request, e.message)
        else:
            text = f"Удалён рецепт: {title}"
            messages.success(request, text)
            self.logger.log("delete", text)
        return redirect("dashboard")


class ActivityStatsView(BaseRecipeView):
    def get(self, request):
        return JsonResponse(self.logger.daily_stats())


class ExitView(BaseRecipeView):
    def get(self, request):
        self.logger.log("exit", "Пользователь завершил сеанс")
        return render(request, "recipes/goodbye.html")
