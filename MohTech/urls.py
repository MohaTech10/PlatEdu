from django.urls import path, include
from .views import *
urlpatterns = [
    path('', returnHomePage, name='home'),
    path('courses/<slug:slug>', courseDetail, name='course_detail'),
    path('lessons/<str:pk_>', getLesson, name='lesson_detail'),
    # path('signup___/', signUp, name='sign_up')
    # path('sign/', signUp, name='sign_up'),
    # path('login/', logIn, name='log_in'),
    # path('logout/', logOut, name='log_out'),
    path('add-to-cart/<slug:slug>', addToCart, name='add_to_cart'),
    path('my-cart/', viewCart, name='cart'),
    path('delete/<str:pk_>', deleteOrderedItem, name='delete'),
    path('my_courses/', userCourses, name='user_course'),
    path('check_out/<str:pk_>', checkOutPayTransaction, name='check_out'),
    path('watch/', lessonCompleted, name='watch'),
]