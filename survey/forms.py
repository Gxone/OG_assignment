from django import forms

from .models import User

class UserForm(forms.ModelForm):
    phone_number = forms.CharField(label='전화번호', max_length=11, required=True)

    class Meta:
        model = User
        fields = ('phone_number',)