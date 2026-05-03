from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Filma

class RegisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values(): f.help_text = ""
    class Meta:
        model = User
        fields = ("username", "password1", "password2")

class VoteForm(forms.Form):
    pelicula = forms.ModelChoiceField(queryset=Filma.objects.none(), required=False, empty_label="-- Selecciona una película --")
    def __init__(self, *args, queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pelicula'].queryset = queryset or Filma.objects.none()
