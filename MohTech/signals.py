from django.contrib.auth import get_user_model
from django.contrib.auth.admin import Group
from allauth.account.signals import user_signed_up
from django.db.models.signals import pre_save
from .utils import unique_slug_generator
from .models import *
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

# sender is the model that has got the data that we would like to listen to
# الدالة تعتبر المتسمع بمعنى ايش تبغا يامستمع يامشترك تعرف او يوصلك اذا السيندر وصلته او قبل ماتوصله المعلومات
def generateSlugPreSave(sender, instance, *args, **kwargs,):
    if not instance.slug:
        # if it does not exist
        instance.slug = unique_slug_generator(instance)

pre_save.connect(generateSlugPreSave, sender=Courses)