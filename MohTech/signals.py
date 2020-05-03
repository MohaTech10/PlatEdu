from django.contrib.auth import get_user_model
from django.contrib.auth.admin import Group
from allauth.account.signals import user_signed_up
from .models import Student
User = get_user_model()
def user_signed_up_receiver(request,  user, **kwargs):
    student_group = Group.objects.get(name='student')
    user.groups.add(student_group)
    Student.objects.create(
        user=user,
        first_name=user.username,
        email=user.email,
    )

user_signed_up.connect(user_signed_up_receiver, sender=User)