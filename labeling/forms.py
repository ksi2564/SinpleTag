from django.forms import ModelForm

from labeling.models import InitialImage


class InitialImageForm(ModelForm):
    class Meta:
        model = InitialImage
        fields = ['label_user']
