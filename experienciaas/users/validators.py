from django.contrib.auth.password_validation import (
    UserAttributeSimilarityValidator,
    MinimumLengthValidator,
    CommonPasswordValidator,
    NumericPasswordValidator,
)
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class SpanishUserAttributeSimilarityValidator(UserAttributeSimilarityValidator):
    def validate(self, password, user=None):
        try:
            super().validate(password, user)
        except ValidationError:
            raise ValidationError(
                _("Tu contraseña no puede ser muy similar a tu otra información personal."),
                code='password_too_similar',
            )

    def get_help_text(self):
        return _("Tu contraseña no puede ser muy similar a tu otra información personal.")


class SpanishMinimumLengthValidator(MinimumLengthValidator):
    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _("Tu contraseña debe contener al menos %(min_length)d caracteres.") % {
                    'min_length': self.min_length
                },
                code='password_too_short',
                params={'min_length': self.min_length},
            )

    def get_help_text(self):
        return _("Tu contraseña debe contener al menos %(min_length)d caracteres.") % {
            'min_length': self.min_length
        }


class SpanishCommonPasswordValidator(CommonPasswordValidator):
    def validate(self, password, user=None):
        try:
            super().validate(password, user)
        except ValidationError:
            raise ValidationError(
                _("Tu contraseña no puede ser una contraseña comúnmente usada."),
                code='password_too_common',
            )

    def get_help_text(self):
        return _("Tu contraseña no puede ser una contraseña comúnmente usada.")


class SpanishNumericPasswordValidator(NumericPasswordValidator):
    def validate(self, password, user=None):
        try:
            super().validate(password, user)
        except ValidationError:
            raise ValidationError(
                _("Tu contraseña no puede ser completamente numérica."),
                code='password_entirely_numeric',
            )

    def get_help_text(self):
        return _("Tu contraseña no puede ser completamente numérica.")
