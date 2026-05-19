from django.core.exceptions import ValidationError
from django.core.validators import URLValidator


def validate_github_url(url):
    """Валидатор для GitHub URL. Используется в users и projects."""
    if not url:
        return url
    validator = URLValidator()
    try:
        validator(url)
    except ValidationError:
        raise ValidationError("Укажите корректный URL.")
    if "github.com" not in url.lower():
        raise ValidationError("Ссылка должна вести на github.com.")
    return url
