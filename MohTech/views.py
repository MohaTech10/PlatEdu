from django.shortcuts import render
from django.shortcuts import render
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.admin import User, Group
from .forms import *
from .decorators import mustLoggedOut


def returnHomePage(request):
    # الفكرةحقت اوثينتيكايتد عظيمه جدا بحيث تسوي ريندر للدداتا بشكلين شكل اذا كانو مسجل وشكل اذا كان اننونمس
    # ليس هنالك طريقةاجمل من is authentication من خلالها تقدر تعرض الصفحه لليوزر وال مش يوزر

    if request.user.is_authenticated:

        all_courses = Courses.objects.all()
        the_student_courses = request.user.student.getStudentCourses()

        current_active_order_instance = Orders.objects.filter(
            user=request.user.student,
            is_ordered=False,
        )
        the_current_order_active_courses_in_it = []
        if current_active_order_instance.exists():
            grab_it = current_active_order_instance[0]
            getting_the_order_courses = grab_it.ordered_courses.all()
            the_current_order_active_courses_in_it = [ordered_item.course for ordered_item in getting_the_order_courses]
        context = {
            'courses': all_courses,
            'courses_in_the_current_order': the_current_order_active_courses_in_it,
            'student_course': the_student_courses,
        }
        return render(request, 'courses.html', context)
    else:
        all_courses = Courses.objects.all()
        context = {
            'courses': all_courses
        }
        return render(request, 'courses.html', context)


# class CoursesListRender(ListView):
#     model = Courses
#     template_name = 'all_courses.html'
#     context_object_name = 'courses'
#     # paginate_by = 1
#     ordering = ['-course_name']

def courseDetail(request, pk_):
    specific_object_has_been_chosen = Courses.objects.get(id=pk_)
    # print(request.user.student.getStudentCourses)
    # print("look here: ", request.user.student.getStudentCourses())
    # pre_course = Prerequisites.objects.all().values('must_taken')

    context = {
        'one_course': specific_object_has_been_chosen,
        # 'all_pre': courses,
    }
    return render(request, 'one_course.html', context)


# always use Functions Based Views, it is much better
# @login_required(login_url='log_in')
def getLesson(request, pk_):
    specific_lesson = Lessons.objects.get(lesson_id=pk_)
    the_course_of_the_lessons = Courses.objects.get(sections__lessons__lesson_id=pk_)
    # user_courses = request.user.student.getStudentCourses()
    # user_courses = request.user.student.courses_enrolled.all()
    p = []
    for ii in the_course_of_the_lessons.getAllCourseLessons():
        p.append(ii)

    lesson_index = p.index(specific_lesson)
    print('what is: ', len(p))
    print('Hello', lesson_index)
    # here it means that we are in the last lesson no more next
    if lesson_index == len(p) - 1:
        next_lesson = p[lesson_index]
        pr = p[lesson_index - 1]
    else:
        next_lesson = p[lesson_index + 1]
    # pre_lesson = None
    if lesson_index == 0:
        pre_lesson = p[lesson_index]
    else:
        pre_lesson = p[lesson_index - 1]
        print(pre_lesson)

    check_variable = False
    if len(p) == 1:
        check_variable = True

    # paginator = Paginator(queryset_list.getAllCourseLessons(), 1)
    # page = request.GET.get('page')
    # try:
    #     queryset = paginator.page(page)
    # except PageNotAnInteger:
    #     queryset = paginator.page(1)
    # except EmptyPage:
    #     queryset = paginator.page(paginator.num_pages)
    # # Paginator(the_course_of_the_lesson.getAllLessons(), 1)
    context = {
        'the_lesson': specific_lesson,
        'the_course_of_all_these_lessons': the_course_of_the_lessons,
        'next': next_lesson,
        'pre': pre_lesson,
        'check': check_variable,
        # 'user_courses': user_courses
    }
    return render(request, 'one_lesson.html', context)


@mustLoggedOut
def signUp(request):
    the_form = SignUpForm()
    # this means after clicking on the submit button what would you like to happen
    if request.method == 'POST':
        the_form = SignUpForm(request.POST)
        if the_form.is_valid():
            the_user = the_form.save()
            # after posting we will create a simple signals
            # picking_up_the_group
            student_group = Group.objects.get(name='student')
            the_user.groups.add(student_group)
            Student.objects.create(
                user=the_user,
                last_name=the_user.last_name,
                email=the_user.email,
            ).save()
            username = the_form.cleaned_data.get('username')
            messages.success(request, 'has been created successfully ' + username)
            return redirect('log_in')
    context = {
        'form': the_form
    }
    return render(request, 'SignUp.html', context)


@mustLoggedOut
def logIn(request):
    # grabbing the user name and pass
    username = request.POST.get('username')
    password = request.POST.get('password')
    # if the button clicks on hitting submit :
    if request.method == "POST":
        # it is either returns the user object with accepted request as long as they're logged in or None
        the_user_with_their_request = authenticate(request, username=username, password=password)
        if the_user_with_their_request is not None:
            login(request, the_user_with_their_request)
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            else:
                return redirect('home')
        else:
            messages.error(request, 'username or password is incorrect.. ')

    return render(request, 'log_in.html')


def logOut(request):
    logout(request)

    return redirect('home')


# here the add-to-cart functionality
@login_required(login_url='log_in')
def addToCart(request, pk_):  # we have to know which item/course will be added to the cart

    grab_the_course = Courses.objects.get(id=pk_)
    grab_the_purchaser = request.user.student

    if grab_the_course in grab_the_purchaser.getStudentCourses():
        messages.info(request, 'you own this product')
        return redirect('home')

    # now after we grabbed the course we wanna convert it from being a normal course to purchased item
    # and we wanna make sure that we create that course as purchased for one time not to be added every time
    # as new row  after checking it is not in the user cart
    becomes_ordered, created = CoursesOrdered.objects.get_or_create(
        course=grab_the_course,
    )
    # here it means to create an order which will be the order opens for first
    # time and not closed until transaction process
    first_time_open_active_order, created = Orders.objects.get_or_create(
        user=grab_the_purchaser,
        is_ordered=False,
    )
    # here False means keep it active not closed and let them add more courses
    # in the same order cart label instance
    first_time_open_active_order.ordered_courses.add(becomes_ordered)
    first_time_open_active_order.save()

    messages.info(request, 'item has been added to OrderedItem and السلة')
    return redirect('home')

def currentCart(request):
    # current_user = get_object_or_404(Student, user=request.user)
    current_active_order = Orders.objects.filter(user=request.user.student, is_ordered=False)
    if current_active_order.exists():
        return current_active_order[0]
    return 0

@login_required(login_url='log_in')
def viewCart(request):
    the_active_order = currentCart(request)
    print(the_active_order.id)

    if the_active_order.ordered_courses.all():
        print('True')
        print(the_active_order.ordered_courses.all().count())
    else:
        print("False")

    context = {
        'the_order': the_active_order
    }

    return render(request, 'cart.html', context)

# login required
def deleteOrderedItem(request, pk_):  # which item being deleted
    the_course_to_delete = CoursesOrdered.objects.get(course_ordered_id=pk_, is_ordered=False)

    the_course_to_delete.delete()
    messages.info(request, 'has been removed')
    return redirect('cart')


@login_required(login_url='log_in')
def getCurrentUSerCourse(request):
    get_current_user = request.user.student.getStudentCourses()
    # my courses means that a course owns by the user in M2M
    context = {
        'current_user_courses': get_current_user
    }
    return render(request, 'user_courses.html', context)

def checkOutPayTransaction(request, pk_):  # we have to know which order with which courses will be purchased

    # فيه بعض الخطوات الي لازم نكون متطلعين عليها قبل مايتم شراء الطلب راح نذكرها

    # get the current order being purchased, تقدر ايضا تجيبه عن طريق is_ordered = False ! عادي
    # كلو يمشي
    order_to_purchase = Orders.objects.get(id=pk_)

    # and then we have to update the order to be is_ordered = True, cuz to let them finish
    # the opened still one and if its true close it and let them open another one
    # their order and have the ability to order again
    # updating the order to be shipped
    order_to_purchase.is_ordered = True
    order_to_purchase.save()

    # get all the current_order items, and update them,
    # current_active_order.ordered_items.all() هذي هيا بالزبط بس انا سويت دااله كل انستانس اوردر يقدر يوصلها
    all_order_courses = order_to_purchase.allOrderItems()
    all_order_courses.update(is_ordered=True)

    # convert the items into their general way which is Products to be sent the user courses so this fields just accept the original Object type course
    # not OrderedCourses
    current_product_in_the_about_to_close_true_order = [each_course.course for each_course in all_order_courses]

    # grab the current user
    current_user = request.user.student
    # this is used when we wanna send lists of objects to the user
    # if many to many and you wanna send one instance such as Java only then ..add(instance)
    # but because many to many and wanna send lists of objects we use this * to send them
    current_user.courses_enrolled.add(*current_product_in_the_about_to_close_true_order)
    current_user.save()

    messages.info(request, 'thanks for buying theses courses ')
    return redirect('home')


# test test