from django import forms

from .models import Recipe


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ["title", "category", "cooking_time", "ingredients", "instructions"]
        widgets = {
            "ingredients": forms.Textarea(attrs={"rows": 3}),
            "instructions": forms.Textarea(attrs={"rows": 3}),
        }


class GenerateForm(forms.Form):
    category = forms.ChoiceField(
        label="Категория",
        required=False,
        choices=[("", "Любая")] + Recipe.Category.choices,
    )
    max_time = forms.IntegerField(
        label="Макс. время, мин", required=False, min_value=1
    )
