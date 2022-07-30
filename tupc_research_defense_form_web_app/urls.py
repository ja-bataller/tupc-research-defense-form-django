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

   path('student-panel-conforme-bet3/', views.studentPanelConformeBet3, name ="student-panel-conforme-bet3"), 
   path('student-panel-conforme-bet3-create/', views.studentPanelConformeBet3Create, name ="student-panel-conforme-bet3-create"), 
   path('student-panel-conforme-bet3-form/', views.studentPanelConformeBet3Form, name ="student-panel-conforme-bet3-form"), 

   path('admin-profile/', views.adminProfile, name ="admin-profile"), 
   path('admin-dashboard/', views.adminDashboard, name ="admin-dashboard"),
   path('admin-department-head/', views.adminDepartmentHead, name ="admin-department-head"),
   path('admin-department-head-create/', views.adminDepartmentHeadCreateAcc, name ="admin-department-head-create"), 
   path('admin-department-head-acc/', views.adminDepartmentHeadAcc, name ="admin-department-head-acc"),
   path('admin-department-head-pass/', views.adminDepartmentHeadPass, name ="admin-department-head-pass"),

   path('admin-faculty-member/', views.adminFacultyMember, name ="admin-faculty-member"),
   path('admin-faculty-member-create/', views.adminFacultyMemberCreateAcc, name ="admin-faculty-member-create"), 
   path('admin-faculty-member-acc/', views.adminFacultyMemberAcc, name ="admin-faculty-member-acc"),

   path('admin-student-course-major/', views.adminStudentAddCourseMajor, name ="admin-student-course-major"),  
]