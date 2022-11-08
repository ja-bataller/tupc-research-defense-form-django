from django.urls import path
from . import views

urlpatterns = [
   # Authentication URLS
   path('', views.index, name ="index"),
   path('signup', views.signup, name ="signup"),
   path('logout', views.logout_user, name ="logout_user"),
   path('login-as', views.login_as_user_accounts, name ="login-as"),

   # Student URLS
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
   path('student/bet3/research-title-defense-form/download', views.studentDownloadBET3ResearchTitleDefenseForm, name ="student-download-bet3-research-title-defense-form"),

   path('student/bet3/adviser/dashboard', views.studentBET3AdviserDashboard, name ="student-bet3-adviser-dashboard"),
   path('student/bet3/adviser-conforme/download', views.studentBET3AdviserConformeDownload, name ="student-bet3-adviser-conforme-download"),

   path('student/bet3/proposal-panel-invitation', views.studentBET3ProposalPanelInvitation, name ="student-bet3-propsal-panel-invitation"),
   # path('student/bet3/proposal-panel-invitation/create', views.studentBET3ProposalPanelInvitationCreate, name ="student-bet3-proposal-panel-invitation-create"), 

   path('student-panel-conforme-bet3/', views.studentPanelConformeBet3, name ="student-panel-conforme-bet3"), 
   path('student-panel-conforme-bet3-create/', views.studentPanelConformeBet3Create, name ="student-panel-conforme-bet3-create"),
   path('student-panel-conforme-bet3-form/', views.studentPanelConformeBet3Form, name ="student-panel-conforme-bet3-form"), 

   path('student/bet3/panel-invitation/logs', views.studentBET3PanelInvitationLogs, name ="student-bet3-panel-invitation-logs"), 

   # Administrator URLS
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

   # DIT Head URLS
   path('dit-head/dashboard', views.ditHeadDashboard, name ="dit-head-dashboard"),
   path('dit-head/profile', views.ditHeadProfile, name ="dit-head-profile"),
   path('dit-head/account-settings', views.ditHeadAccountSettings, name ="dit-head-account-settings"),

   path('dit-head/create/e-signature', views.ditHeadCreateESignature, name ="dit-head-create-esignature"),
   path('dit-head/upload/e-signature', views.ditHeadUploadESignature, name ="dit-head-upload-esignature"),
   path('dit-head/delete/e-signature', views.ditHeadDeleteESignature, name ="dit-head-delete-esignature"),

   # path('panel/account-settings', views.panelAccountSettings, name ="panel-account-settings"),

   path('dit-head/bet3/panel-invitation', views.ditHeadPanelInvitationBet3, name ="dit-head-panel-invitation-bet-3"),

   path('dit-head/bet3/topic-panel-invitation/accept/sign/<str:id>', views.ditHeadBET3TopicPanelInvitationAcceptSignature, name ="dit-head-bet3-topic-panel-invitation-accept-sign"),
   path('dit-head/bet3/topic-panel-invitation/decline/sign/<str:id>', views.ditHeadBET3TopicPanelInvitationDeclineSignature, name ="dit-head-bet3-topic-panel-invitation-decline-sign"),

   path('dit-head/bet3/panel-invitation/accept/<str:id>', views.ditHeadPanelInvitationBet3Accept, name ="dit-head-panel-invitation-bet-3-accept"),
   path('dit-head/bet3/panel-invitation/decline/<str:id>', views.ditHeadPanelInvitationBet3Decline, name ="dit-head-panel-invitation-bet-3-decline"),

   path('dit-head/bet3/adviser-conforme', views.ditHeadBET3AdviserConforme, name ="dit-head-bet3-adviser-conforme"),
   path('dit-head/bet3/adviser-conforme/accept/<str:id>', views.ditHeadBET3AdviserConformeAccept, name ="dit-head-bet3-adviser-conforme-accept"),
   path('dit-head/bet3/adviser-conforme/decline/<str:id>', views.ditHeadBET3AdviserConformeDecline, name ="dit-head-bet3-adviser-conforme-decline"),

   path('dit-head-panel-conforme-bet-3/', views.ditHeadPanelConformeBet3, name ="dit-head-panel-conforme-bet-3"),
   path('dit-head-panel-conforme-bet-3-accept/<str:id>', views.ditHeadPanelConformeBet3Accept, name ="dit-head-panel-conforme-bet-3-accept"),  
   path('dit-head-panel-conforme-bet-3-decline/<str:id>', views.ditHeadPanelConformeBet3Decline, name ="dit-head-panel-conforme-bet-3-decline"),  

   path('dit-head/bet3/panel-invitation/logs', views.ditHeadBET3PanelInvitationLogs, name ="dit-head-bet3-panel-invitation-logs"),

   # Panel URLS
   path('panel/dashboard', views.panelDashboard, name ="panel-dashboard"),
   path('panel/profile', views.panelProfile, name ="panel-profile"),

   path('panel/create/e-signature', views.panelCreateESignature, name ="panel-create-esignature"),
   path('panel/upload/e-signature', views.panelUploadESignature, name ="panel-upload-esignature"),
   path('panel/delete/e-signature', views.panelDeleteESignature, name ="panel-delete-esignature"),

   path('panel/account-settings', views.panelAccountSettings, name ="panel-account-settings"),

   path('panel/title-defense-day/<str:id>', views.panelTitleDefenseDay, name ="panel-title-defense-day"),
   path('panel/title/accept/<str:id>', views.panelAcceptTitle, name ="panel-accept-title"),
   path('panel/title/defer/<str:id>', views.panelDeferTitle, name ="panel-defer-title"),
   path('panel/title/revise/<str:id>', views.panelReviseTitle, name ="panel-revise-title"),
   path('panel/title-defense-day/done/<str:id>', views.panelTitleDefenseMarkDone, name ="panel-title-defense-mark-done"),

   path('panel/bet3/panel-invitation', views.panelPanelInvitationBet3, name ="panel-panel-invitation-bet-3"),
   
   path('panel/bet3/topic-panel-invitation/accept/sign/<str:id>', views.panelBET3TopicPanelInvitationAcceptSignature, name ="panel-bet3-topic-panel-invitation-accept-sign"),
   path('panel/bet3/topic-panel-invitation/decline/sign/<str:id>', views.panelBET3TopicPanelInvitationDeclineSignature, name ="panel-bet3-topic-panel-invitation-decline-sign"),

   path('panel/bet3/panel-invitation/accept/<str:id>', views.panelPanelInvitationBet3Accept, name ="panel-panel-invitation-bet-3-accept"),
   path('panel/bet3/panel-invitation/decline/<str:id>', views.panelPanelInvitationBet3Decline, name ="panel-panel-invitation-bet-3-decline"),
   
   path('panel-research-title-defense-dashboard', views.panelResearchTitleDefenseDashboard, name ="panel-research-title-defense-dashboard"),

   path('panel-panel-conforme-bet-3/', views.panelPanelConformeBet3, name ="panel-panel-conforme-bet-3"),
   # path('panel-panel-conforme-bet-3-accept/<str:id>/', views.panelPanelConformeBet3Accept, name ="panel-panel-conforme-bet-3-accept"),
   # path('panel-panel-conforme-bet-3-decline/<str:id>/', views.panelPanelConformeBet3Decline, name ="panel-panel-conforme-bet-3-decline"),

   path('panel/bet3/panel-invitation/logs', views.panelBET3PanelInvitationLogs, name ="panel-bet3-panel-invitation-logs"),
   path('panel/bet3/title-defense/logs', views.panelBET3TitleDefenseLogs, name ="panel-bet3-title-defense-logs"),
   path('panel/bet3/title-defense/logs/completed/<str:id>', views.panelBET3TitleDefenseLogCompleted, name ="bet3-title-defense-logs-completed"),
   path('panel/bet3/title-defense/logs/redefense/<str:id>', views.panelBET3TitleDefenseLogRedefense, name ="bet3-title-defense-logs-redefense"),

   # Subject Teacher URLS
   path('subject-teacher/dashboard', views.subjectTeacherDashboard, name ="subject-teacher-dashboard"),
   path('subject-teacher/profile', views.subjectTeacherProfile, name ="subject-teacher-profile"),

   path('subject-teacher/create/e-signature', views.subjectTeacherCreateESignature, name ="subject-teacher-create-esignature"),
   path('subject-teacher/upload/e-signature', views.subjectTeacherUploadESignature, name ="subject-teacher-upload-esignature"),
   path('subject-teacher/delete/e-signature', views.subjectTeacherDeleteESignature, name ="subject-teacher-delete-esignature"),

   path('subject-teacher/account-settings', views.subjectTeacherAccountSettings, name ="subject-teacher-account-settings"),

   path('subject-teacher/title-defense-day/<str:id>', views.subjectTeacherTitleDefenseDay, name ="subject-teacher-title-defense-day"),
   path('subject-teacher/title-defense-day/present/<str:id>', views.subjectTeacherTitleDefenseDayPresent, name ="subject-teacher-title-defense-day-present"),
   path('subject-teacher/title-defense-day/absent/<str:id>', views.subjectTeacherTitleDefenseDayAbsent, name ="subject-teacher-title-defense-day-absent"),
   path('subject-teacher/title-defense-day/set-panel-chairman/<str:id>', views.subjectTeacherTitleDefenseDaySetPanelChairman, name ="subject-teacher-title-defense-day-panel-chairman"),
   path('subject-teacher/title-defense-day/close-vote/<str:id>', views.subjectTeacherTitleDefenseDayCloseVote, name ="subject-teacher-title-defense-day-close-vote"),

   path('subject-teacher/title-defense/schedule/students', views.subjectTeacherStudentsTitleDefenseDashboard, name ="subject-teacher-students-title-defense-schedule-dashboard"),
   path('subject-teacher/title-defense/set-schedule', views.subjectTeacherSetResearchTitleDefenseSchedule, name ="subject-teacher-set-research-title-defense-schedule"),
   path('subject-teacher/title-defense/save-schedule', views.subjectTeacherSaveResearchTitleDefenseSchedule, name ="subject-teacher-save-research-title-defense-schedule"),
   path('subject-teacher/title-defense/delete-schedule/<str:id>', views.subjectTeacherDeleteResearchTitleDefenseSchedule, name ="subject-teacher-delete-research-title-defense-schedule"),

   path('subject-teacher/title-defense/logs', views.subjectTeacherBET3TitleDefenseLogs, name ="subject-teacher-bet3-title-defense-logs"),
   path('subject-teacher/title-defense/logs/completed/<str:id>', views.subjectTeacherBET3TitleDefenseLogCompleted, name ="subject-teacher-bet3-title-defense-logs-completed"),
   path('subject-teacher/title-defense/logs/redefense/<str:id>', views.subjectTeacherBET3TitleDefenseLogRedefense, name ="subject-teacher-bet3-title-defense-logs-redefense"),

   path('subject-teacher/title-defense/my-schedule', views.subjectTeacherMyTitleDefenseDashboard, name ="subject-teacher-title-defense-schedule-dashboard"),

   # Advisers URLS
   path('adviser/dashboard', views.adviserDashboard, name ="adviser-dashboard"),
   path('adviser/profile', views.adviserProfile, name ="adviser-profile"),

   path('adviser/create/e-signature', views.adviserCreateESignature, name ="adviser-create-esignature"),
   path('adviser/upload/e-signature', views.adviserUploadESignature, name ="adviser-upload-esignature"),
   path('adviser/delete/e-signature', views.adviserDeleteESignature, name ="adviser-delete-esignature"),

   path('adviser/account-settings', views.adviserAccountSettings, name ="adviser-account-settings"),

   path('adviser/advisee/dashboard', views.adviserAdviseeDashboard, name ="adviser-advisee-dashboard"),

   path('adviser/bet3/adviser-conforme', views.adviserBET3AdviserConforme, name ="adviser-bet3-adviser-conforme"),
   path('adviser/bet3/adviser-conforme/accept/<str:id>', views.adviserBET3AdviserConformeAccept, name ="adviser-bet3-adviser-conforme-accept"),
   path('adviser/bet3/adviser-conforme/decline/<str:id>', views.adviserBET3AdviserConformeDecline, name ="adviser-bet3-adviser-conforme-decline"),
]