from django.core.exceptions import ValidationError
from django.utils import timezone


def year_validator(value):
    now_year = timezone.now().year
    if value > now_year:
        raise ValidationError(
            'Введенный год не может быть больше текущего года'
        )
