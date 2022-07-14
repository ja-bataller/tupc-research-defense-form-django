from django.urls import path
from . import views

urlpatterns = [
   # Authentication Views
   path('', views.index, name ="index"),
   path('signup/', views.signup, name ="signup"),

   # Student Views
   path('student-dashboard/', views.studentDashboard, name ="student-dashboard"), 
]