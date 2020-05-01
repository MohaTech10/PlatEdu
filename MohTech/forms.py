from django.contrib.auth.admin import UserCreationForm, User

class SignUpForm(UserCreationForm):
    # this works as front-end and back-end Api مرسول
    class Meta:
        model = User
        fields = ['username', 'last_name', 'email', 'password1', 'password2']