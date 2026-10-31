import pytest
from django.contrib.messages import get_messages
from django.urls import reverse

from recipes.models import ActivityLog, Recipe


def valid_post(**overrides):
    """Корректные POST-данные для формы добавления рецепта."""
    data = {
        "title": "Омлет",
        "category": "breakfast",
        "cooking_time": 10,
        "ingredients": "Яйца, молоко",
        "instructions": "Взбить и пожарить.",
    }
    data.update(overrides)
    return data


def message_texts(response):
    return [str(m) for m in get_messages(response.wsgi_request)]


def test_dashboard_200(client, db):
    response = client.get(reverse("dashboard"))

    assert response.status_code == 200
    assert "Все рецепты" in response.content.decode()


def test_add_recipe_view_creates(client, db):
    response = client.post(reverse("add_recipe"), valid_post())

    assert response.status_code == 302
    assert Recipe.objects.filter(title="Омлет").exists()
    assert ActivityLog.objects.filter(action="add").exists()


def test_add_recipe_invalid_shows_error(client, db):
    response = client.post(reverse("add_recipe"), valid_post(cooking_time=0))

    assert response.status_code == 302
    assert Recipe.objects.count() == 0
    assert message_texts(response)  # есть хотя бы одно сообщение об ошибке
    assert ActivityLog.objects.filter(action="error").exists()


def test_generate_view_redirects_with_pk(client, recipe):
    response = client.post(reverse("generate"), {"category": "", "max_time": ""})

    assert response.status_code == 302
    assert response.url == f"{reverse('dashboard')}?generated={recipe.pk}"


def test_generate_empty_db_error_message(client, db):
    response = client.post(reverse("generate"), {"category": "", "max_time": ""})

    assert response.status_code == 302
    assert "В базе нет ни одного рецепта. Добавьте первый!" in message_texts(response)
    assert ActivityLog.objects.filter(action="error").exists()


def test_delete_view(client, recipe):
    response = client.post(reverse("delete_recipe", args=[recipe.pk]))

    assert response.status_code == 302
    assert not Recipe.objects.filter(pk=recipe.pk).exists()
    assert ActivityLog.objects.filter(action="delete").exists()


def test_delete_missing_shows_error(client, db):
    response = client.post(reverse("delete_recipe", args=[9999]))

    assert response.status_code == 302
    assert "Рецепт не найден." in message_texts(response)


def test_delete_rejects_get(client, recipe):
    response = client.get(reverse("delete_recipe", args=[recipe.pk]))

    assert response.status_code == 405
    assert Recipe.objects.filter(pk=recipe.pk).exists()


def test_activity_api_json(client, db):
    response = client.get(reverse("activity_stats"))

    assert response.status_code == 200
    data = response.json()
    assert set(data) == {"labels", "counts"}
    assert len(data["labels"]) == len(data["counts"]) == 7


def test_exit_view_logs_and_renders(client, db):
    response = client.get(reverse("exit"))

    assert response.status_code == 200
    assert ActivityLog.objects.filter(action="exit").exists()
