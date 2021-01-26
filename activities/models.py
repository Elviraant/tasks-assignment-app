from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from datetime import datetime
from django.utils import timezone


class Direction(models.Model):
    name = models.CharField(max_length=300)
    code = models.CharField(max_length=10)

    def __str__(self):
        return self.name + " ("  + self.code + ")"


class Department(models.Model):
    name = models.CharField(max_length=300)
    code = models.CharField(max_length=10, unique=True)
    direction = models.ForeignKey(Direction, on_delete=models.CASCADE)

    def __str__(self):
        return self.name + " ("  + self.code + ")"


class Office(models.Model):
    name = models.CharField(max_length=300)
    code = models.CharField(max_length=10)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return self.name + " ("  + self.code + ")"


class Employee(AbstractUser):
    direction = models.ForeignKey(Direction, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        if (self.is_departmentdirector()):
            return self.first_name + " " + self.last_name + " - " + self.departmentdirector.department.__str__()
        elif (self.is_officeclerk()):
            return self.first_name + " " + self.last_name + " - " + self.officeclerk.office.__str__()
        else:
            return self.first_name + " " + self.last_name + " - " + self.direction.__str__()

    def is_departmentdirector(self):
        try:
            self.departmentdirector
            return True
        except (DepartmentDirector.DoesNotExist):
            return False

    def is_officeclerk(self):
        try:
            self.officeclerk
            return True
        except (OfficeClerk.DoesNotExist):
            return False

    def full_name(self):
        return self.first_name + " " + self.last_name

    def receiver_choices(self):
        officeclerks = OfficeClerk.objects.by_direction(self.direction)
        departmentdirectors = DepartmentDirector.objects.by_direction(self.direction)
        return officeclerks + departmentdirectors

    def notifications(self):
        return self.receiver_set.filter(is_shown=False).count()


class OfficeClerkManager(UserManager):

    def by_direction(self, direction):
        officeclerks = []
        for officeclerk in self.filter(direction=direction):
            officeclerks.append((officeclerk.id, officeclerk.__str__()))
        return officeclerks

    def by_department(self, department):
        officeclerks = []
        for officeclerk in self.filter(department=department):
            officeclerks.append((officeclerk.id, officeclerk.__str__()))
        return officeclerks


class OfficeClerk(Employee):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, blank=True, null=True)
    office = models.ForeignKey(Office, on_delete=models.CASCADE, blank=True, null=True)
    objects = OfficeClerkManager()

    def __str__(self):
        return self.first_name + " " + self.last_name + " - " + self.office.__str__()

    def receiver_choices(self):
        return None

class DepartmentDirectorManager(UserManager):

    def by_direction(self, direction):
        departmentdirectors = []
        for departmentdirector in self.filter(direction=direction):
            departmentdirectors.append((departmentdirector.id, departmentdirector.__str__()))

        return departmentdirectors


class DepartmentDirector(Employee):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, blank=True, null=True)
    objects = DepartmentDirectorManager()

    def __str__(self):
        return self.first_name + " " + self.last_name + " - " + self.department.__str__()

    def receiver_choices(self):
        officeclerks = OfficeClerk.objects.by_department(self.department)
        return officeclerks


class Activity(models.Model):
    title = models.CharField(max_length=700)
    description = models.CharField(max_length=1000, blank=True)
    release_date = models.DateTimeField('release date')
    deadline = models.DateTimeField('deadline')
    sender = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='activity_sender_set')
    is_complete = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def get_deadline(self):
        return self.deadline.date()

    def is_task(self):
        try:
            self.task
            return True
        except (Task.DoesNotExist):
            return False

    def is_project(self):
        try:
            self.project
            return True
        except (Project.DoesNotExist):
            return False

    def completed(self):
        if (self.is_complete):
            return "Ναι"

        return "Όχι"

    def update_activity(self, title, deadline, description):
        self.title = title
        self. deadline = deadline
        self.description = description
        self.save()

        return self

    def is_past_due(self):
        return timezone.now() > self.deadline


class Project(Activity):
    number_of_tasks = models.IntegerField()

    def get_tasks(self):
        tasks = []
        for task in self.task_set.all():
            tasks.append((task.id, task.title))
        return tasks

    def progress(self):
        return str((self.completed_tasks()/self.number_Of_tasks) * 100)

    def completed_tasks(self):
        return self.task_set.filter(is_complete=True).count()


class Task(Activity):
    receiver = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='activity_receiver_set')
    is_approved = models.BooleanField(default=False)
    project_field = models.ForeignKey(Project, on_delete=models.CASCADE, blank=True, null=True)

    def has_parent_project(self):
        if (self.project_field is not None):
            return True
        return False

    def parent_project_date(self):
        return self.project_field.deadline.date()

    def update_activity(self, title, deadline, description, receiver):
        super().update_activity(title, deadline, description)
        self.receiver = receiver
        self.save()

        return self


class NotificationManager(models.Manager):

    def create(self, sender, receiver, activity, type, **kwargs):
        if (type =='edit_task'):
            previous_title = kwargs.pop('previous_title')
            message = "Ο/Η χρήστης " + activity.sender.full_name() + " τροποποίησε την αρμοδιότητα " + previous_title + ".\n"

            if (kwargs.pop('receiver_changed') is True):
                message += " Δεν είστε πλέον ο παραλήπτης αυτής της αρμοδιότητας."

        elif (type =='new_task'):
            message = message = "Ο/Η χρήστης " + activity.sender.full_name() + " σας ανέθεσε την αρμοδιότητα " + activity.title + "."

        super().create(sender=sender, receiver=receiver, activity=activity, message=message)


class Notification(models.Model):
    message = models.CharField(max_length=700)
    release_date = models.DateTimeField('release_date', default=datetime.now())
    sender = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='sender_set')
    receiver = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='receiver_set')
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='activity_set')
    is_shown = models.BooleanField(default=False)
    objects = NotificationManager()

    def set_shown(self):
        self.is_shown = True
        self.save()

    def __str__(self):
        return self.message
