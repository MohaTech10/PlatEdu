from django.db import models

from django.db import models

from django.db import models
from django.contrib.auth.admin import User
import uuid
from django.utils.text import slugify
# الهرجه طلعت كلها اب لديه ابناء، ذولا الابنا عندهم ابناء وهكذا ويمديك من الاحفاد توصل للجد والاب وهكدا
#
# class Student(models.Model):
#     pass


class Courses(models.Model):
    course_name = models.CharField(max_length=100)
    price = models.FloatField(null=True, blank=True)
    course_description = models.TextField()
    slug = models.SlugField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.course_name)
        super(Courses, self).save(*args, **kwargs)

    # a lot of properties but not now, the goal now is to get comfortable with queries

    def __str__(self):
        return self.course_name

    def getCommentsOfOneCourse(self):
        # here we will query عن كل احفاد هذا الجد عن طريق التسلسل وصولنا ب عيال هذا الاب
        # ثم التنقل وهكذا من تحت الى الاعلى في علاقات one-to-many
        return len(Comments.objects.filter(lesson__section__course__course_name=self))
    def getCourseSections(self):
        return self.sections_set.all()
    def getAllCourseLessons(self):
        return Lessons.objects.filter(section__course__id=self.id).order_by('date_created')
    def getCourseReview(self):
        sum_ = 0
        all_the_ratings_for_one_course = Review.objects.filter(course__course_name=self.course_name).values('ratings')
        for each_rate in all_the_ratings_for_one_course:
            sum_ += each_rate.get('ratings')
        if sum_/len(all_the_ratings_for_one_course) > 5.0:
            return 5.0
        return sum_/len(all_the_ratings_for_one_course)
    def getCourseProject(self):
        return self.projects_set.all()
        # return Projects.objects.filter(course=self)

class Student(models.Model):
    # extending the user fields instead of having just a few fields with no relations such as i am about to put for the students
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField()
    courses_enrolled = models.ManyToManyField(Courses)
    # profile_pic = models.CharField(max_length=200, null=True, )
    def __str__(self):
        return self.first_name + " " + self.last_name
    # def getStudentsProject(self):
    #     pass
    # def getStudentsComments(self):
    #     pass
    @property
    def getStudentCourses(self):
        return self.courses_enrolled.all()
    def getStudentProjects(self):
        return self.projects_set.all()
class Projects(models.Model):
    project_creator = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE, null=True, blank=True)
    project_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    project_name = models.CharField(max_length=40, blank=False)
    project_description = models.TextField(null=False, blank=False)
    project_file = models.CharField(max_length=100)
    date_submitted = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.project_name

class Sections(models.Model):
    # a course has got a lot of sections, one course has a lot of sections, one section must belong to one course and so on
    section_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    section_name = models.CharField(max_length=50)


    def getTheSectionLessons(self):
        return self.lessons_set.all()


    def __str__(self):
        return self.section_name + " " + self.course.course_name

class Lessons(models.Model):
    # a section contains a lot of lesson and so on
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    lesson_id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    section = models.ForeignKey(Sections, on_delete=models.CASCADE)
    lesson_name = models.CharField(max_length=100)
    is_previewed = models.BooleanField(default=False, null=True, blank=True)
    def __str__(self):
        return self.lesson_name
    def getAllLessonComments(self):
        # طيب للوصول لكل الكومنس فالدرس الواحد يعني من ابو الى عياله عندنا طريقتين
        # we have using filter or the parentINSTANCE.children_set.all()
        # بس هذي تعمل لمن يكون عندك اب مع ابنائه
        # فيه طريقه اخرى تمشي مع الكل الا وهيا using filter
        # print(self.comments_set.all())
        return Comments.objects.filter(lesson=self)



class Comments(models.Model):
    comment_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    lesson = models.ForeignKey(Lessons, on_delete=models.CASCADE)
    comment_body = models.TextField()
    def __str__(self):
        return self.comment_body

class CoursesOrdered(models.Model):
    # here just converting an ordinary course to become ordered one once a user clicks on add to cart cuz it's no longer just a course
    course_ordered_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    course = models.OneToOneField(Courses, on_delete=models.CASCADE)
    is_ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.course.course_name

class Orders(models.Model):
    user = models.ForeignKey(Student, on_delete=models.CASCADE)
    ordered_courses = models.ManyToManyField(CoursesOrdered)
    date_ordered = models.DateTimeField(auto_now_add=True)
    is_ordered = models.BooleanField(default=False)   # that will let make sure if the ordered is True then i could put it in the users's order permnantly otherwise
    # now i won't be able to put it

    def allOrderItems(self):
        return self.ordered_courses.all()
    def allOrderItemsTotal(self):
        return sum([each_ordered_course.course.price for each_ordered_course in self.ordered_courses.all()])

    # @property
    # def getAllOrderedItemsProducts(self):
    #     ordered_courses_ = self.ordered_courses.all()
    #     the_current_order_active_courses_in_it = [ordered_item.course for ordered_item in ordered_courses_]
    #     return the_current_order_active_courses_in_it
class Review(models.Model):
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    comment_when_rating = models.TextField
    ratings = models.FloatField()
    def __str__(self):
        return str(self.ratings)
# #




