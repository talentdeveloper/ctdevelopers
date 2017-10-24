from django import forms
from django.utils.translation import ugettext_lazy as _


class NumberMultipleSelectField(forms.MultipleChoiceField):
    """
    This overrides the MultipleChoiceField to allow accepting a list of number values.
    This does not require any choices.
    """
    def validate(self, value):
        for item in value:
            if item:
                try:
                    float(item)
                except ValueError:
                    raise forms.ValidationError(_('This field should be a number.'))
