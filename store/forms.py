from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Order, Review


class CustomerSignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Email address', 'class': 'input-field'}),
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username', 'class': 'input-field'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'input-field'}),
            'comment': forms.Textarea(attrs={'class': 'input-field', 'rows': 4, 'placeholder': 'Write your review...'}),
        }
        labels = {
            'comment': 'Your Review',
        }


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name', 'email', 'phone', 'address']
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Full Name', 'class': 'input-field'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email Address', 'class': 'input-field'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Phone Number', 'class': 'input-field'}),
            'address': forms.Textarea(attrs={'placeholder': 'Shipping Address', 'class': 'input-field', 'rows': 4}),
        }
