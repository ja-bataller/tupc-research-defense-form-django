from django.urls import path
from . import views

urlpatterns = [
   # Authentication Views
   path('', views.index, name ="index"),
   path('signup', views.signup, name ="signup"),
   path('logout', views.logout_user, name ="logout_user"),
   path('login-as', views.login_as_user_accounts, name ="login-as"),

   # Student Views
   path('student/profile', views.studentProfile, name ="student-profile"), 
   path('student/dashboard', views.studentDashboard, name ="student-dashboard"),

   path('student/group-members', views.studentGroupMemberProcess, name ="student-group-members"),
   path('student/group-members/add', views.studentAddGroupMember, name ="student-add-group-members"),
   path('student/group-members/dashboard', views.studentGroupMembersDashboard, name ="student-group-members-dashboard"),

   path('student/research-titles', views.studentResearchTitleProcess, name ="student-research-titles"),
   path('student/research-titles/add', views.studentAddResearchTitle, name ="student-add-research-titles"),
   path('student/research-title-dashboard', views.studentResearchTitleDashboard, name ="student-research-title-dashboard"),

   path('student/bet3/panel-invitation', views.studentPanelInvitationBet3, name ="student-panel-invitation-bet3"), 
   path('student/bet3/panel-invitation/create', views.studentPanelInvitationBet3Create, name ="student-panel-invitation-bet3-create"),
   path('student/bet3/panel-invitation/save', views.studentPanelInvitationBet3Save, name ="student-panel-invitation-bet3-save"),
   path('student/bet3/panel-invitation/download/<str:id>', views.studentDownloadPanelInvitationBet3, name ="student-download-panel-invitation-bet3"),

   path('student/bet3/research-title-defense', views.studentBET3ResearchTitleDefense, name ="student-bet3-research-title-defense"),

   path('student-panel-conforme-bet3/', views.studentPanelConformeBet3, name ="student-panel-conforme-bet3"), 
   path('student-panel-conforme-bet3-create/', views.studentPanelConformeBet3Create, name ="student-panel-conforme-bet3-create"),
   path('student-panel-conforme-bet3-form/', views.studentPanelConformeBet3Form, name ="student-panel-conforme-bet3-form"), 

    # Administrator Views
   path('tupc-admin/profile', views.adminProfile, name ="admin-profile"), 
   path('tupc-admin/dashboard', views.adminDashboard, name ="admin-dashboard"),

   path('tupc-admin/faculty-member/create', views.adminFacultyMemberCreateAcc, name ="admin-faculty-member-create"), 
   path('tupc-admin/faculty-member/account', views.adminFacultyMemberAcc, name ="admin-faculty-member-acc"),
   path('tupc-admin/faculty-member/data/<str:id>', views.adminFacultyMemberData, name ="admin-faculty-member-data"),
   path('tupc-admin/faculty-member/change-password/<str:id>', views.adminFacultyMemberChangePassword, name ="admin-faculty-member-change-password"),
   path('tupc-admin/faculty-member/change-user-account/<str:id>', views.adminFacultyMemberChangeUserAccount, name ="admin-faculty-member-change-user-account"),

   path('tupc-admin/student/course-major/', views.adminStudentCourseMajor, name ="admin-student-course-major"),  
   path('tupc-admin/student/add-course-major/', views.adminStudentAddCourseMajor, name ="admin-student-add-course-major"),
   path('tupc-admin/student/edit-course-major/<str:id>', views.adminStudentEditCourseMajor, name ="admin-student-edit-course-major"), 
   path('tupc-admin/student/delete-course-major/<str:id>', views.adminStudentDeleteCourseMajor, name ="admin-student-delete-course-major"),

   # DIT Head Views
   path('dit-head/dashboard', views.ditHeadDashboard, name ="dit-head-dashboard"),
   path('dit-head/profile', views.ditHeadProfile, name ="dit-head-profile"),

   path('dit-head/bet3/panel-invitation', views.ditHeadPanelInvitationBet3, name ="dit-head-panel-invitation-bet-3"),
   path('dit-head/bet3/panel-invitation/accept/<str:id>', views.ditHeadPanelInvitationBet3Accept, name ="dit-head-panel-invitation-bet-3-accept"),
   path('dit-head/bet3/panel-invitation/decline/<str:id>', views.ditHeadPanelInvitationBet3Decline, name ="dit-head-panel-invitation-bet-3-decline"),

   path('dit-head-panel-conforme-bet-3/', views.ditHeadPanelConformeBet3, name ="dit-head-panel-conforme-bet-3"),
   path('dit-head-panel-conforme-bet-3-accept/<str:id>', views.ditHeadPanelConformeBet3Accept, name ="dit-head-panel-conforme-bet-3-accept"),  
   path('dit-head-panel-conforme-bet-3-decline/<str:id>', views.ditHeadPanelConformeBet3Decline, name ="dit-head-panel-conforme-bet-3-decline"),  

   # Panel Views
   path('panel/dashboard', views.panelDashboard, name ="panel-dashboard"),
   path('panel/profile', views.panelProfile, name ="panel-profile"),

   path('panel/title-defense-day/<str:id>', views.panelTitleDefenseDay, name ="panel-title-defense-day"),
   path('panel/title/accept/<str:id>', views.panelAcceptTitle, name ="panel-accept-title"),
   path('panel/title/defer/<str:id>', views.panelDeferTitle, name ="panel-defer-title"),
   path('panel/title/revise/<str:id>', views.panelReviseTitle, name ="panel-revise-title"),
   path('panel/title-defense-day/done/<str:id>', views.panelTitleDefenseMarkDone, name ="panel-title-defense-mark-done"),

   path('panel/bet3/panel-invitation', views.panelPanelInvitationBet3, name ="panel-panel-invitation-bet-3"),
   path('panel/bet3/panel-invitation/accept/<str:id>', views.panelPanelInvitationBet3Accept, name ="panel-panel-invitation-bet-3-accept"),
   path('panel/bet3/panel-invitation/decline/<str:id>', views.panelPanelInvitationBet3Decline, name ="panel-panel-invitation-bet-3-decline"),
   
   path('panel-research-title-defense-dashboard', views.panelResearchTitleDefenseDashboard, name ="panel-research-title-defense-dashboard"),

   path('panel-panel-conforme-bet-3/', views.panelPanelConformeBet3, name ="panel-panel-conforme-bet-3"),
   # path('panel-panel-conforme-bet-3-accept/<str:id>/', views.panelPanelConformeBet3Accept, name ="panel-panel-conforme-bet-3-accept"),
   # path('panel-panel-conforme-bet-3-decline/<str:id>/', views.panelPanelConformeBet3Decline, name ="panel-panel-conforme-bet-3-decline"),

   # Subject Teacher Views
   path('subject-teacher/dashboard', views.subjectTeacherDashboard, name ="subject-teacher-dashboard"),
   path('subject-teacher/profile', views.subjectTeacherProfile, name ="subject-teacher-profile"),

   path('subject-teacher/title-defense-day/<str:id>', views.subjectTeacherTitleDefenseDay, name ="subject-teacher-title-defense-day"),
   path('subject-teacher/title-defense-day/present/<str:id>', views.subjectTeacherTitleDefenseDayPresent, name ="subject-teacher-title-defense-day-present"),
   path('subject-teacher/title-defense-day/absent/<str:id>', views.subjectTeacherTitleDefenseDayAbsent, name ="subject-teacher-title-defense-day-absent"),
   path('subject-teacher/title-defense-day/set-panel-chairman/<str:id>', views.subjectTeacherTitleDefenseDaySetPanelChairman, name ="subject-teacher-title-defense-day-panel-chairman"),
   path('subject-teacher/title-defense-day/close-vote/<str:id>', views.subjectTeacherTitleDefenseDayCloseVote, name ="subject-teacher-title-defense-day-close-vote"),

   path('subject-teacher/title-defense/dashboard', views.subjectTeacherResearchTitleDefenseDashboard, name ="subject-teacher-research-title-defense-dashboard"),
   path('subject-teacher/title-defense/set-schedule', views.subjectTeacherSetResearchTitleDefenseSchedule, name ="subject-teacher-set-research-title-defense-schedule"),
   path('subject-teacher/title-defense/save-schedule', views.subjectTeacherSaveResearchTitleDefenseSchedule, name ="subject-teacher-save-research-title-defense-schedule"),
   path('subject-teacher/title-defense/delete-schedule/<str:id>', views.subjectTeacherDeleteResearchTitleDefenseSchedule, name ="subject-teacher-delete-research-title-defense-schedule"),
]