from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Review, Order


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Email'
        })
    )
    agree = forms.BooleanField(
        required=True,
        label='Я согласен с правилами регистрации',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Имя пользователя'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Пароль (минимум 6 символов)'
        })
        self.fields['password2'].widget = forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Подтверждение пароля'
        })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует.')
        return email


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Имя пользователя'
        }),
        label='Имя пользователя'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Пароль'
        }),
        label='Пароль'
    )


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']
        widgets = {
            'rating': forms.Select(
                choices=[(i, f'{i} ★') for i in range(1, 6)],
                attrs={'class': 'form-select'}
            ),
            'text': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Напишите ваш отзыв...',
                'rows': 4
            }),
        }
        labels = {
            'rating': 'Оценка',
            'text': 'Отзыв',
        }


class OrderForm(forms.ModelForm):
    payment_method = forms.ChoiceField(
        choices=Order.PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'payment-method-radio'}),
        label='Способ оплаты',
        initial='cash'
    )
    
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'payment_method', 'comment']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Имя'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Фамилия'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Телефон'}),
            'address': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'Адрес доставки', 'rows': 3}),
            'comment': forms.Textarea(
                attrs={'class': 'form-textarea', 'placeholder': 'Комментарий к заказу', 'rows': 3}),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Имя'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Фамилия'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email'}),
        }
