from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from moviepy.editor import VideoFileClip
from .models import *
# from django.templatetags.static import static(

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

def courseDetail(request, slug):
    specific_object_has_been_chosen = Courses.objects.get(slug=slug)
    # print(request.user.student.getStudentCourses)
    # print("look here: ", request.user.student.getStudentCourses())
    # pre_course = Prerequisites.objects.all().values('must_taken')
    # the_complete = CertificateCompleted.objects.get(
    #     # هذا الكلام طبعا حيتغير لاحقا
    #     course=specific_object_has_been_chosen,
    #     student=request.user.student,
    # )
    # print(int((the_complete.lesson_watched.count()/specific_object_has_been_chosen.getAllCourseLessons().count()) * 100))

    # يتم اضافة فقط وفقط الدروس المتعلقه بالكورس المعين كيف ؟ ببساطه تحصل على الكورس الي داخله اليوزر ثم
    # تسوي ادد على الدروس وهكذا

    context = {
        'one_course': specific_object_has_been_chosen,
        # 'all_pre': courses,
    }
    return render(request, 'one_course.html', context)


# always use Functions Based Views, it is much better
# @login_required(login_url='log_in')
def getLesson(request, pk_):
    # front-end shape of the button of each lesson
    specific_lesson = Lessons.objects.get(lesson_id=pk_)
    the_course_of_the_lessons = Courses.objects.get(sections__lessons__lesson_id=pk_)
    # url = static(specific_lesson.lesson_video.url)
    # the_lesson_instance = VideoFileClip(url)
    # lesson_dur = the_lesson_instance.duration
    # user_courses = request.user.student.getStudentCourses()
    # user_courses = request.user.student.courses_enrolled.all()
    is_watched = True
    student_progress = 0
    lessons_watched = None
    if request.user.is_authenticated:
        if the_course_of_the_lessons in request.user.student.getStudentCourses():
            course_certificate = CertificateCompleted.objects.get(
                course=the_course_of_the_lessons,
                student=request.user.student
            )
            lessons_watched = course_certificate.lesson_watched.filter(certificatecompleted__course=the_course_of_the_lessons, certificatecompleted__student=request.user.student)
            if course_certificate.lesson_watched.filter(lesson_id=pk_, certificatecompleted__student=request.user.student).exists():
                is_watched = True
            student_progress = int((course_certificate.lesson_watched.count()/the_course_of_the_lessons.getAllCourseLessons().count()) * 100)
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
        # 'user_courses': user_courses,
        'is_watched': is_watched,
        'course_progress': student_progress,
        'lessons_watched': lessons_watched,
        # 'lesson_dur': lesson_dur
    }
    return render(request, 'one_lesson.html', context)


# @mustLoggedOut
# # def signUp(request):
# #     the_form = SignUpForm()
# #     # this means after clicking on the submit button what would you like to happen
# #     if request.method == 'POST':
# #         the_form = SignUpForm(request.POST)
# #         if the_form.is_valid():
# #             the_user = the_form.save()
# #             # after posting we will create a simple signals
# #             # picking_up_the_group
# #             student_group = Group.objects.get(name='student')
# #             the_user.groups.add(student_group)
# #             Student.objects.create(
# #                 user=the_user,
# #                 last_name=the_user.last_name,
# #                 email=the_user.email,
# #             ).save()
# #             username = the_form.cleaned_data.get('username')
# #             messages.success(request, 'has been created successfully ' + username)
# #             return redirect('log_in')
# #     context = {
# #         'form': the_form
# #     }
# #     return render(request, 'SignUp.html', context)


# @mustLoggedOut
# def logIn(request):
#     # grabbing the user name and pass
#     username = request.POST.get('username')
#     password = request.POST.get('password')
#     # if the button clicks on hitting submit :
#     if request.method == "POST":
#         # it is either returns the user object with accepted request as long as they're logged in or None
#         the_user_with_their_request = authenticate(request, username=username, password=password)
#         if the_user_with_their_request is not None:
#             login(request, the_user_with_their_request)
#             if 'next' in request.POST:
#                 return redirect(request.POST.get('next'))
#             else:
#                 return redirect('home')
#         else:
#             messages.error(request, 'username or password is incorrect.. ')
#
#     return render(request, 'log_in.html')


# def logOut(request):
#     logout(request)
#
#     return redirect('home')


# here the add-to-cart functionality
@login_required(login_url='account_login')
def addToCart(request, slug):  # we have to know which item/course will be added to the cart
    # using ajax jquery tomorrow
    grab_the_course = Courses.objects.get(slug=slug)
    grab_the_purchaser = request.user.student
    

    if grab_the_course in grab_the_purchaser.getStudentCourses():
        messages.info(request, 'you own this product')
        return redirect('home')

    # now after we grabbed the course we wanna convert it from being a normal course to purchased item
    # and we wanna make sure that we create that course as purchased for one time not to be added every time
    # as new row  after checking it is not in the user cart
    becomes_ordered, created = CoursesOrdered.objects.get_or_create(
        course=grab_the_course,
        user=grab_the_purchaser,
        is_ordered=False

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

    # the_current_order_active_courses_in_it = []
    # getting_the_order_courses = first_time_open_active_order.ordered_courses.all()
    # the_current_order_active_courses_in_it = [ordered_item.course for ordered_item in getting_the_order_courses]
    # 
    messages.info(request, 'item has been added to OrderedItem and السلة')
    return redirect('home')
    # student_course = request.user.student.getStudentCourses()
    # context = {
    #     'each_course': grab_the_course
    #
    # }
    # if request.is_ajax():
    #
    #     html = render_to_string('add_cart.html', context, request=request)
    #     return JsonResponse({'form': html})
    # return render(request, 'add_cart.html', context)






def currentCart(request):
    # current_user = get_object_or_404(Student, user=request.user)
    current_active_order = Orders.objects.filter(user=request.user.student, is_ordered=False)
    if current_active_order.exists():
        return current_active_order[0]
    return 0


@login_required(login_url='account_login')
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


@login_required(login_url='account_login')
def deleteOrderedItem(request, pk_):  # which item being deleted
    the_course_to_delete = CoursesOrdered.objects.get(course_ordered_id=pk_, is_ordered=False,
                                                      user=request.user.student)

    the_course_to_delete.delete()
    messages.info(request, 'has been removed')
    # context = {
    #     'each_course': the_course_to_delete,
    #     'the_order': order.ordered_courses
    # }
    # if request.is_ajax():
    #     html = render_to_string('delete_one.html', context, request=request)
    #     return JsonResponse({'form': html})
    return redirect('cart')


# @login_required(login_url='log_in')
# def getCurrentUSerCourse(request):
#     get_current_user = request.user.student.getStudentCourses()
#     # my courses means that a course owns by the user in M2M
#     context = {
#         'current_user_courses': get_current_user
#     }
#     return render(request, 'user_courses.html', context)


@login_required(login_url='account_login')
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
    all_order_courses.update(user=request.user.student, is_ordered=True)

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

    # now after succeed in buy i would like to open instances of the certificate kinda thing
    for course_ in current_product_in_the_about_to_close_true_order:
        open_c, created = CertificateCompleted.objects.get_or_create(
            course=course_,
            student=current_user
        )
        print('correct')

    messages.info(request, 'thanks for buying theses courses ')
    return redirect('home')


# is watched => True, or False two parts front-end and back-end they have to be consistent so that if front end says red then backend
# click means remove and so on

def lessonCompleted(request):
    _lesson_id = request.POST.get('id')
    the_fucking_lesson = Lessons.objects.get(lesson_id=_lesson_id)
    the_course = Courses.objects.get(sections__lessons__lesson_id=_lesson_id)
    # if the_course in request.user.student.getStudentCourses():
    to_watch_or_not = CertificateCompleted.objects.get(
        course=the_course,
        student=request.user.student,
    )
    # lessons_watched = to_watch_or_not.lesson_watched.filter(certificatecompleted__course=the_course, certificatecompleted__student=request.user.student)

    # is_watched = False
    # if to_watch_or_not.lesson_watched.filter(lesson_id=_lesson_id, certificatecompleted__student=request.user.student).exists():
    #     to_watch_or_not.lesson_watched.remove(the_fucking_lesson)
    #     is_watched = False
    # else:
    to_watch_or_not.lesson_watched.add(the_fucking_lesson)
    is_watched = True
    student_progress = int((to_watch_or_not.lesson_watched.count() / the_course.getAllCourseLessons().count()) * 100)
    context = {
        'the_lesson': the_fucking_lesson,
        'is_watched': is_watched,
        'course_progress': student_progress,
        'the_course_of_all_these_lessons': the_course,
        # 'lessons_watched': lessons_watched
    }


    if request.is_ajax():
        html = render_to_string('watch_or_not.html', context, request=request)
        return JsonResponse({'form': html})
# else:
#
# return redirect('lesson_detail', _lesson_id)


@login_required(login_url='account_login')
def userCourses(request):


    return render(request, 'user_courses.html')
