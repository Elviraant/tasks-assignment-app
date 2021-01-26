from . import views
from django.urls import path

app_name = 'activities'
urlpatterns = [
    path('', views.index, name='index'),
    path('auth/', views.LoginView.as_view(), name='authenticate'),
    path('activities/', views.activities, name='activities'),
    path('tasks/', views.tasks, name='tasks'),
    path('notifications/', views.notifications, name='notifications'),
    path('<int:activity_id>/', views.activity_details, name='activity_details'),
    path('notification/<int:notification_id>/<int:activity_id>/<int:shown>/', views.activity_details, name='activity_details'),
    path('<int:activity_id>/edit/', views.edit_activity, name='edit'),
    path('<int:parent_project_id>/edit/project/task/<int:task_id>', views.edit_task, name='edit_task'),
    path('<int:task_id>/edit/task/', views.edit_task, name='edit_task'),
    path('<int:parent_project_id>/edit/tasks/', views.choose_project_task, name='choose_project_task'),
    path('<int:project_id>/edit/tasks/', views.choose_project_task_form, name='choose_project_task_form'),
    path('<int:project_id>/edit/project/', views.edit_project, name='edit_project'),
    path('logout/', views.logout_view, name='logout')
]
