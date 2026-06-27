from django import forms
from django.core.exceptions import ValidationError

from .constants import (
    ALLOWED_IMAGE_CONTENT_TYPES,
    FORBIDDEN_WORDS,
    MAX_IMAGE_SIZE,
)
from catalog.models import Product


class BootstrapClearableFileInput(forms.ClearableFileInput):
    template_name = "catalog/widgets/clearable_file_input.html"


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ("name", "description", "image", "category", "price")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "image": BootstrapClearableFileInput(),
            "price": forms.NumberInput(attrs={"step": "0.01"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            widget = field.widget
            current_classes = widget.attrs.get("class", "")

            if isinstance(widget, forms.CheckboxInput):
                css_class = "form-check-input"

            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                css_class = "form-select"

            else:
                css_class = "form-control"

            widget.attrs["class"] = (f"{current_classes} {css_class}").strip()

            if not isinstance(
                widget,
                (
                    forms.CheckboxInput,
                    forms.Select,
                    forms.SelectMultiple,
                    forms.FileInput,
                ),
            ):
                widget.attrs.setdefault(
                    "placeholder",
                    field.label,
                )

    def _validate_forbidden_words(self, value, field_name):
        if not value:
            return value

        normalized_value = value.casefold()

        found_words = [
            word
            for word in FORBIDDEN_WORDS
            if word.casefold() in normalized_value
        ]

        if found_words:
            words = ", ".join(f"«{word}»" for word in found_words)

            raise ValidationError(
                f"В поле «{field_name}» нельзя использовать "
                f"запрещённые слова: {words}."
            )

        return value

    def clean_name(self):
        name = self.cleaned_data.get("name", "")

        return self._validate_forbidden_words(
            name,
            "Название",
        )

    def clean_description(self):
        description = self.cleaned_data.get("description", "")

        return self._validate_forbidden_words(description, "Описание")

    def clean_price(self):
        price = self.cleaned_data.get("price")

        if price is not None and price < 0:
            raise ValidationError(
                "Цена не может быть отрицательной. "
                "Укажите значение 0 или больше."
            )

        return price

    def clean_image(self):
        image = self.cleaned_data.get("image")

        if not image:
            return image

        content_type = getattr(image, "content_type", None)

        # При редактировании без нового файла Django возвращает ImageFieldFile.
        # Тип и размер такого файла уже проверялись во время его загрузки.
        if content_type is None:
            return image

        if content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
            raise ValidationError(
                "Можно загружать только изображения JPEG или PNG."
            )

        if image.size > MAX_IMAGE_SIZE:
            raise ValidationError(
                "Размер изображения не должен превышать 5 МБ."
            )

        return image
