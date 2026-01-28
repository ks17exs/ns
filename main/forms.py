from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser, ReviewLog
from django.utils.translation import gettext_lazy as _

class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone'].required = True

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'phone', 'password1', 'password2']
        labels = {
            'username': _('Логин'),
            'first_name': _('Имя'),
            'phone': _('Номер телефона'),
            'password1': _('Пароль'),
            'password2': _('Подтверждение пароля'),
        }

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = _("Логин")

class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'email', 'phone']
        labels = {
            'first_name': _('Имя'),
            'email': _('Email'),
            'phone': _('Телефон'),
        }

class ReviewForm(forms.ModelForm):
    grade = forms.ChoiceField(choices=[(i, str(i)) for i in range(1, 6)], label="Оценка", widget=forms.Select())
    class Meta:
        model = ReviewLog
        fields = ['grade', 'comment']
        labels = {
            'grade': _('Оценка'),
            'comment': _('Комментарий'),
        }
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }