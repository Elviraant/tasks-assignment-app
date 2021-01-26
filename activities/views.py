from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import *
from django.views.generic.edit import FormView
from .forms import LoginForm, EditForm, SelectForm
from django.contrib.auth import login, authenticate, logout
from datetime import date
from django.contrib import messages


""" Index view """
def index(request):
    if (already_authenticated(request)):
        if (request.user.is_officeclerk()):
            return HttpResponseRedirect(reverse('activities:tasks'))
        else:
            return HttpResponseRedirect(reverse('activities:activities'))
    else:
        form = LoginForm()
        return render(request, 'activities/index.html', { 'form': form })


""" Handles the login process """
class LoginView(FormView):
    form_class = LoginForm
    template_name = 'activities/index.html'

    """ Authenticates and logins the user """
    def form_valid(self, form):

        if form is not None:
            credentials = form.cleaned_data

            employee = authenticate(username=credentials['username'],
                            password=credentials['password'])

            return self.login_forward(employee)

    """ Logins and forwards the user to the right page """
    def login_forward(self, employee):

        if employee is not None:
            login(self.request, employee)
            if (employee.is_officeclerk()):
                return HttpResponseRedirect(reverse('activities:tasks'))
            else:
                return HttpResponseRedirect(reverse('activities:activities'))
        else:
            error_message = "Λανθασμένο όνομα χρήστη ή κωδικός πρόσβασης"

        return render(self.request, 'activities/index.html', { 'error_message': error_message, 'form': LoginForm() })


""" Logs the user out """
def logout_view(request):
    logout(request)
    return render(request, 'activities/logout.html')


""" Shows the activities assigned by the user """
def activities(request):
    if (already_authenticated(request)):
        employee = request.user
        activities = employee.activity_sender_set.all().order_by('deadline')
        return render(request, 'activities/activities.html', { 'employee': request.user,
                                                               'activities': activities
                                                              })

    return access_not_allowed(request)


""" Shows user's notifications """
def notifications(request):
    if (already_authenticated(request)):
        employee = request.user
        notifications = employee.receiver_set.all().order_by('-id')
        return render(request, 'activities/notifications.html',
                     { 'employee': request.user,
                       'notifications': notifications
                     })

    return access_not_allowed(request)


""" Shows user's assigned tasks """
def tasks(request):
    if (already_authenticated(request)):
        employee = request.user
        tasks = employee.activity_receiver_set.all().order_by('deadline')
        return render(request, 'activities/tasks.html',
                     { 'employee': request.user,
                       'tasks': tasks
                     })

    return access_not_allowed(request)


""" Renders the right edit template based on the activity type """
def edit_activity(request, activity_id):

    if (not already_authenticated(request)):
        return access_not_allowed(request)

    activity = get_object_or_404(Activity, pk = activity_id)

    employee = request.user
    if (activity.sender == employee):
        form = initialize_edit_form(request, activity)
        if (activity.is_task()):
            task = activity.task
            return render(request, 'activities/edit_task_form.html',
                          { 'employee': employee,
                            'task': task ,
                            'form': form
                          })
        elif (activity.is_project()):
            project = activity.project
            return render(request, 'activities/edit_project_form.html',
                          { 'employee': employee,
                            'project': project,
                            'form': form
                          })

    return access_not_allowed(request)


""" Edits a task """
def edit_task(request, task_id, parent_project_id=0):

    if (not already_authenticated(request)):
        return access_not_allowed(request)

    task = get_object_or_404(Task, pk = task_id)
    employee = request.user

    if (employee == task.sender):
        if (employee.is_departmentdirector()):
            employee = employee.departmentdirector

        if (task.has_parent_project()):
            form = EditForm(request.POST, employee=employee, parent_project_date=task.parent_project_date())
        else:
            form = EditForm(request.POST, employee=employee, parent_project_date=None)

        if (form.is_valid()):
            title = form.cleaned_data['title']
            deadline = form.cleaned_data['deadline']
            description = form.cleaned_data['description']
            receiver_id = form.cleaned_data['receiver']
            receiver = get_object_or_404(Employee, pk=receiver_id)
            previous_title = task.title
            previous_receiver = task.receiver

            task = task.update_activity(title, deadline, description, receiver)

            if (previous_receiver != task.receiver):
                receiver_changed = True
                Notification.objects.create(request.user, receiver, task, 'new_task')
            else:
                receiver_changed= False

            Notification.objects.create(request.user, previous_receiver, task,
                                        'edit_task', previous_title=previous_title, receiver_changed=receiver_changed)

        else:
            if (parent_project_id != 0):
                parent_project = get_object_or_404(Project, pk=parent_project_id)
                return render(request, 'activities/edit_task_form.html', { 'employee': request.user, 'task': task,
                                                                            'form': form, 'parent_project': parent_project })

            return render(request, 'activities/edit_task_form.html', { 'employee': request.user, 'task': task, 'form': form })

        messages.add_message(request, messages.SUCCESS, 'Η αρμοδιότητα τροποποιήθηκε επιτυχώς!')

        if ('done' in request.POST):
            if (parent_project_id != 0 ):
                parent_project = get_object_or_404(Project, pk=parent_project_id)
                return HttpResponseRedirect(reverse('activities:activity_details', kwargs={"activity_id": parent_project.id}))

            return HttpResponseRedirect(reverse('activities:activity_details', kwargs={"activity_id": task_id}))

        elif ('continue' in request.POST):
            parent_project = get_object_or_404(Project, pk=parent_project_id)

            if (parent_project == task.project_field):
                return choose_project_task_form(request, parent_project.id)

    return access_not_allowed(request)


""" Edits a project """
def edit_project(request, project_id):

    if (not already_authenticated(request)):
        return access_not_allowed(request)

    project = get_object_or_404(Project, pk = project_id)

    if (request.user == project.sender):
        form = EditForm(request.POST, parent_project_date=None)

        if (form.is_valid()):
            title = form.cleaned_data['title']
            deadline = form.cleaned_data['deadline']
            description = form.cleaned_data['description']

            project.update_activity(title, deadline, description)

        else:
            return render(request, 'activities/edit_project_form.html',
                          { 'employee': request.user, 'project': project, 'form': form })

        messages.add_message(request, messages.SUCCESS, 'Τα χαρακτηριστικά του έργου τροποποιήθηκαν επιτυχώς!')

        if ('done' in request.POST):
            return HttpResponseRedirect(reverse('activities:activity_details', kwargs={"activity_id": project_id}))
        elif ('continue' in request.POST):
            return choose_project_task_form(request, project.id)

    return access_not_allowed(request)


""" Shows a selection form """
def choose_project_task_form(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    select_form = SelectForm()
    select_form.set_choices(project.get_tasks())

    return render(request, 'activities/choose_project_task.html',
                 { 'employee': request.user, 'form': select_form, 'project': project })


""" Selects which task of a project will be edited """
def choose_project_task(request, parent_project_id):
    if (not already_authenticated(request)):
        return access_not_allowed(request)

    parent_project = get_object_or_404(Project, pk=parent_project_id)

    employee = request.user
    if (employee == parent_project.sender):
        form = SelectForm(request.POST)
        if (form.is_valid()):
            task_id = form.cleaned_data['project_task_id']
            task = get_object_or_404(Task, pk=task_id)

            form = initialize_edit_form(request, task)

            return render(request, 'activities/edit_task_form.html',
                         { 'employee': request.user, 'task': task , 'parent_project': parent_project, 'form': form })
        else:
            form.set_choices(parent_project.get_tasks())
            return render(request, 'activities/choose_project_task.html',
                                  { 'employee': request.user, 'form': form, 'project': parent_project })

    return access_not_allowed(request)


""" Initializes and returns edit form with data based on activity type  """
def initialize_edit_form(request, activity):
    initial= { 'title': activity.title,
               'deadline': activity.deadline,
               'description': activity.description, }

    employee = request.user
    if (activity.is_task()):
        task = activity.task
        initial['receiver'] = task.receiver.id
        if (employee.is_departmentdirector()):
            employee = employee.departmentdirector

        if (task.has_parent_project()):
            parent_project_date = task.parent_project_date()
            form = EditForm( employee=employee, parent_project_date=parent_project_date, initial=initial)

        else:
            form = EditForm( employee=employee, parent_project_date=None, initial=initial)

    elif (activity.is_project()):
        form = EditForm(parent_project_date=None, initial=initial)

    return form


""" Shows an activity's details """
def activity_details(request, activity_id, notification_id=0, shown=0):
    if (not already_authenticated(request)):
        return access_not_allowed(request)

    activity = get_object_or_404(Activity, pk=activity_id)

    employee = request.user
    if (notification_id != 0 and shown == 1):
        notification = get_object_or_404(Notification, pk=notification_id)
        if (notification.receiver == employee):
            notification.set_shown()

    if (activity.is_task()):
        if (employee == activity.sender):
            return render(request, 'activities/task.html', { 'employee': employee, 'task': activity.task, 'sender': 'sender' })
        elif (employee == activity.task.receiver):
            return render(request, 'activities/task.html', { 'employee': employee, 'task': activity.task, 'receiver': 'receiver' })
    elif (activity.is_project()):
        if (employee == activity.sender):
            return render(request, 'activities/project.html', { 'employee': employee, 'project': activity.project })

    return access_not_allowed(request)


""" Checks whether the user is authenticated """
def already_authenticated(request):
    return request.user.is_authenticated


""" Redirects the user when access is not allowed """
def access_not_allowed(request):
    messages.error(request, 'Δεν έχετε πρόσβαση σε αυτή τη πηγή.')
    return HttpResponseRedirect(reverse(('activities:index')))
