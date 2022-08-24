from django.urls import path
from . import views

urlpatterns = [
   # Authentication Views
   path('', views.index, name ="index"),
   path('signup/', views.signup, name ="signup"),
   path('logout/', views.logout_user, name ="logout_user"),
   path('login-as/', views.login_as_user_accounts, name ="login-as"),

   # Student Views
   path('student-profile/', views.studentProfile, name ="student-profile"), 
   path('student-dashboard/', views.studentDashboard, name ="student-dashboard"), 

   path('student-panel-invitation-bet3/', views.studentPanelInvitationBet3, name ="student-panel-invitation-bet3"), 
   path('student-panel-invitation-bet3-create/', views.studentPanelInvitationBet3Create, name ="student-panel-invitation-bet3-create"),
   path('student-panel-invitation-bet3-form/', views.studentPanelInvitationBet3Form, name ="student-panel-invitation-bet3-form"),
   path('student-panel-invitation-bet3-add-panel/', views.studentPanelInvitationBet3AddPanel, name ="student-panel-invitation-bet3-add-panel"),

   path('student-panel-conforme-bet3/', views.studentPanelConformeBet3, name ="student-panel-conforme-bet3"), 
   path('student-panel-conforme-bet3-create/', views.studentPanelConformeBet3Create, name ="student-panel-conforme-bet3-create"),
   path('student-panel-conforme-bet3-form/', views.studentPanelConformeBet3Form, name ="student-panel-conforme-bet3-form"), 

    # Administrator Views
   path('admin-profile/', views.adminProfile, name ="admin-profile"), 
   path('admin-dashboard/', views.adminDashboard, name ="admin-dashboard"),

   path('admin-faculty-member-create/', views.adminFacultyMemberCreateAcc, name ="admin-faculty-member-create"), 
   path('admin-faculty-member-acc/', views.adminFacultyMemberAcc, name ="admin-faculty-member-acc"),
   path('admin-faculty-member-data/<str:id>', views.adminFacultyMemberData, name ="admin-faculty-member-data"),
   path('admin-faculty-member-change-password/<str:id>', views.adminFacultyMemberChangePassword, name ="admin-faculty-member-change-password"),
   path('admin-faculty-member-change-user-account/<str:id>', views.adminFacultyMemberChangeUserAccount, name ="admin-faculty-member-change-user-account"),

   path('admin-student-course-major/', views.adminStudentCourseMajor, name ="admin-student-course-major"),  
   path('admin-student-add-course-major/', views.adminStudentAddCourseMajor, name ="admin-student-add-course-major"),
   path('admin-student-edit-course-major/<str:id>', views.adminStudentEditCourseMajor, name ="admin-student-edit-course-major"), 
   path('admin-student-delete-course-major/<str:id>', views.adminStudentDeleteCourseMajor, name ="admin-student-delete-course-major"),

   # DIT Head Views
   path('dit-head-dashboard/', views.ditHeadDashboard, name ="dit-head-dashboard"),
   path('dit-head-profile/', views.ditHeadProfile, name ="dit-head-profile"),

   path('dit-head-panel-invitation-bet-3/', views.ditHeadPanelInvitationBet3, name ="dit-head-panel-invitation-bet-3"),
   path('dit-head-panel-invitation-bet-3-accept/<str:id>', views.ditHeadPanelInvitationBet3Accept, name ="dit-head-panel-invitation-bet-3-accept"),
   path('dit-head-panel-invitation-bet-3-decline/<str:id>', views.ditHeadPanelInvitationBet3Decline, name ="dit-head-panel-invitation-bet-3-decline"),

   path('dit-head-panel-conforme-bet-3/', views.ditHeadPanelConformeBet3, name ="dit-head-panel-conforme-bet-3"),
   path('dit-head-panel-conforme-bet-3-accept/<str:id>', views.ditHeadPanelConformeBet3Accept, name ="dit-head-panel-conforme-bet-3-accept"),  
   path('dit-head-panel-conforme-bet-3-decline/<str:id>', views.ditHeadPanelConformeBet3Decline, name ="dit-head-panel-conforme-bet-3-decline"),  

   # Panel Views
   path('panel-dashboard/', views.panelDashboard, name ="panel-dashboard"),
   path('panel-profile/', views.panelProfile, name ="panel-profile"),

   path('panel-panel-invitation-bet-3/', views.panelPanelInvitationBet3, name ="panel-panel-invitation-bet-3"),
   path('panel-panel-invitation-bet-3-accept/<str:id>', views.panelPanelInvitationBet3Accept, name ="panel-panel-invitation-bet-3-accept"),
   path('panel-panel-invitation-bet-3-decline/<str:id>', views.panelPanelInvitationBet3Decline, name ="panel-panel-invitation-bet-3-decline"),
   
   path('panel-panel-conforme-bet-3/', views.panelPanelConformeBet3, name ="panel-panel-conforme-bet-3"),
   # path('panel-panel-conforme-bet-3-accept/<str:id>/', views.panelPanelConformeBet3Accept, name ="panel-panel-conforme-bet-3-accept"),
   # path('panel-panel-conforme-bet-3-decline/<str:id>/', views.panelPanelConformeBet3Decline, name ="panel-panel-conforme-bet-3-decline"),

   # Subject Teacher Views
   path('subject-teacher-dashboard/', views.subjectTeacherDashboard, name ="subject-teacher-dashboard"),
   path('subject-teacher-profile/', views.subjectTeacherProfile, name ="subject-teacher-profile"),
   path('subject-teacher-research-title-defense-dashboard/', views.subjectTeacherResearchTitleDefenseDashboard, name ="subject-teacher-research-title-defense-dashboard"),
   path('subject-teacher-set-research-title-defense-schedule/', views.subjectTeacherSetResearchTitleDefenseSchedule, name ="subject-teacher-set-research-title-defense-schedule"),
   path('subject-teacher-save-research-title-defense-schedule/', views.subjectTeacherSaveResearchTitleDefenseSchedule, name ="subject-teacher-save-research-title-defense-schedule"),
   path('subject-teacher-delete-research-title-defense-schedule/<str:id>', views.subjectTeacherDeleteResearchTitleDefenseSchedule, name ="subject-teacher-delete-research-title-defense-schedule"),
]