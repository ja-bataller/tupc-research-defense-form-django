from django.urls import path
from . import views

urlpatterns = [
   # Authentication Views
   path('', views.index, name ="index"),
   path('signup/', views.signup, name ="signup"),
   path('logout/', views.logout_user, name ="logout_user"),

   # Student Views
   path('student-profile/', views.studentProfile, name ="student-profile"), 
   path('student-dashboard/', views.studentDashboard, name ="student-dashboard"), 
   path('student-panel-conforme/', views.studentPanelConforme, name ="student-panel-conforme"), 

   path('admin-dashboard/', views.adminDashboard, name ="admin-dashboard"),
      path('admin-department-head/', views.adminDepartmentHead, name ="admin-department-head"),
   path('admin-department-head-acc/', views.adminDepartmentHeadAcc, name ="admin-department-head-acc"),
   path('admin-department-head-create/', views.adminDepartmentHeadCreateAcc, name ="admin-department-head-create"),  
]