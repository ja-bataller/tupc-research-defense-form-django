from django.urls import path
from . import views

urlpatterns = [
   # Authentication URLS
   path('', views.index, name ="index"),
   path('login', views.loginPage, name ="login"),
   path('signup', views.signup, name ="signup"),
   path('forgot-password', views.forgotPassword, name ="forgot-password"),
   path('reset-password/<str:id>', views.resetPassword, name ="reset-password"),
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
   path('student/research-title/update', views.studentResearchTitleUpdate, name ="student-research-title-update"),

   path('student/bet3/panel-invitation', views.studentPanelInvitationBet3, name ="student-panel-invitation-bet3"), 
   path('student/bet3/panel-invitation/create', views.studentPanelInvitationBet3Create, name ="student-panel-invitation-bet3-create"),
   path('student/bet3/panel-invitation/save', views.studentPanelInvitationBet3Save, name ="student-panel-invitation-bet3-save"),
   path('student/bet3/panel-invitation/download/<str:id>', views.studentDownloadPanelInvitationBet3, name ="student-download-panel-invitation-bet3"),
   
   path('student/bet3/research-title-defense', views.studentBET3ResearchTitleDefense, name ="student-bet3-research-title-defense"),
   path('student/bet3/research-title-defense-form/download', views.studentDownloadBET3ResearchTitleDefenseForm, name ="student-download-bet3-research-title-defense-form"),

   path('student/bet3/topic/panel-conforme', views.studentBET3TopicPanelConforme, name ="student-bet3-topic-panel-conforme"),
   path('student/bet3/topic/panel-conforme/save', views.studentTopicPanelConformeSave, name ="student-topic-panel-conforme-save"),
   path('student/bet3/topic/panel-conforme/download/<str:id>', views.studentTopicPanelConformeDownload, name ="student-topic-panel-conforme-download"),

   path('student/bet3/proposal/panel-conforme', views.studentBET3ProposalPanelConforme, name ="student-bet3-proposal-panel-conforme"),
   path('student/bet3/proposal/panel-conforme/save', views.studentProposalPanelConformeSave, name ="student-proposal-panel-conforme-save"),
   path('student/bet3/proposal/panel-conforme/download/<str:id>', views.studentProposalPanelConformeDownload, name ="student-proposal-panel-conforme-download"),

   path('student/bet5/final/panel-conforme', views.studentBET5FinalPanelConforme, name ="student-bet5-final-panel-conforme"),
   path('student/bet5/final/panel-conforme/save', views.studentFinalPanelConformeSave, name ="student-final-panel-conforme-save"),
   path('student/bet5/final/panel-conforme/download/<str:id>', views.studentFinalPanelConformeDownload, name ="student-final-panel-conforme-download"),

   path('student/bet3/adviser/dashboard', views.studentBET3AdviserDashboard, name ="student-bet3-adviser-dashboard"),
   path('student/bet3/adviser-conforme/download', views.studentBET3AdviserConformeDownload, name ="student-bet3-adviser-conforme-download"),

   path('student/bet3/proposal-defense/panel-invitation', views.studentBET3ProposalDefensePanelInvitation, name ="student-bet3-proposal-defense-panel-invitation"),
   path('student/bet3/proposal-defense/panel-invitation/create/prev', views.studentBET3ProposalDefensePanelInvitationCreatePanel, name ="student-bet3-proposal-defense-panel-invitation-create-panel"),
   path('student/bet3/proposal-defense/panel-invitation/create', views.studentBET3ProposalDefensePanelInvitationCreate, name ="student-bet3-proposal-defense-panel-invitation-create"),
   path('student/bet3/proposal-defense/panel-invitation/save', views.studentBET3ProposalDefensePanelInvitationSave, name ="student-bet3-proposal-defense-panel-invitation-save"),
   path('student/bet3/proposal-defense/panel-invitation/download/<str:id>', views.studentBET3ProposalDefensePanelInvitationDownload, name ="student-bet3-proposal-defense-panel-invitation-download"),

   path('student/bet3/critique-form', views.studentBET3CritiqueForm, name ="student-bet3-critique-form"),
   path('student/bet3/critique-form/download', views.studentBET3CritiqueFormDownload, name ="student-bet3-critique-form-download"),

   path('student/bet3/research-proposal-defense', views.studentBET3ResearchProposalDefenseForm, name ="student-bet3-research-proposal-defense"),
   path('student/bet3/research-proposal-defense-form/download', views.studentBET3ResearchProposalDefenseFormDownload, name ="student-bet3-research-proposal-defense-form-download"),

   path('student/bet5/subject-teacher', views.studentBET5SubjectTeacher, name ="student-bet5-subject-teacher"),

   path('student/bet5/final-defense/panel-invitation', views.studentBET5FinalDefensePanelInvitation, name ="student-bet5-final-defense-panel-invitation"),
   path('student/bet5/final-defense/panel-invitation/create/prev', views.studentBET5FinalDefensePanelInvitationCreatePanel, name ="student-bet5-final-defense-panel-invitation-create-panel"),
   path('student/bet5/final-defense/panel-invitation/create', views.studentBET5FinalDefensePanelInvitationCreate, name ="student-bet5-final-defense-panel-invitation-create"),
   path('student/bet5/final-defense/panel-invitation/save', views.studentBET5FinalDefensePanelInvitationSave, name ="student-bet5-final-defense-panel-invitation-save"),
   path('student/bet5/final-defense/panel-invitation/download/<str:id>', views.studentBET5FinalDefensePanelInvitationDownload, name ="student-bet5-final-defense-panel-invitation-download"),

   path('student/bet5/research-final-defense', views.studentBET5ResearchFinalDefenseForm, name ="student-bet5-research-final-defense"),
   path('student/bet5/research-final-defense-form/download', views.studentBET5ResearchFinalDefenseFormDownload, name ="student-bet5-final-defense-form-download"),

   path('student/acknowledgment-receipt', views.studentAcknowledgementReceiptDashboard, name ="student-acknowledgement-receipt"),
   path('student/acknowledgment-receipt/save', views.studentAcknowledgementReceiptSave, name ="student-acknowledgement-receipt-save"),
   path('student/acknowledgment-receipt/download', views.studentAcknowledgmentReceiptDownload, name ="student-acknowledgement-receipt-download"),

   path('student/bet3/topic-defense/panel-invitation/logs', views.studentBET3PanelInvitationLogs, name ="student-bet3-panel-invitation-logs"),
   path('student/bet3/proposal-defense/panel-invitation/logs', views.studentBET3ProposalDefensePanelInvitationLogs, name ="student-bet3-proposal-defense-panel-invitation-logs"),

   path('student/the-devs', views.studentTheDevs, name ="student-the-devs"),

   # Administrator URLS
   path('tupc-admin/profile', views.adminProfile, name ="admin-profile"), 
   path('tupc-admin/dashboard', views.adminDashboard, name ="admin-dashboard"),

   path('tupc-admin/research-titles', views.adminResearchTitles, name ="admin-research-titles"),  

   path('tupc-admin/faculty-member/account', views.adminFacultyMemberAcc, name ="admin-faculty-member-acc"),
   path('tupc-admin/faculty-member/create', views.adminFacultyMemberCreateAcc, name ="admin-faculty-member-create"), 
   path('tupc-admin/faculty-member/data/<str:id>', views.adminFacultyMemberData, name ="admin-faculty-member-data"),
   path('tupc-admin/faculty-member/change-password/<str:id>', views.adminFacultyMemberChangePassword, name ="admin-faculty-member-change-password"),
   path('tupc-admin/faculty-member/change-user-account/<str:id>', views.adminFacultyMemberChangeUserAccount, name ="admin-faculty-member-change-user-account"),

   path('tupc-admin/advisee-limit', views.adminAdviseeLimit, name ="admin-advisee-limit"), 
   path('tupc-admin/advisee-limit/set', views.adminAdviseeLimitSet, name ="admin-advisee-limit-set"),  

   path('tupc-admin/student/account', views.adminStudentAccount, name ="admin-student-account"), 
   path('tupc-admin/student-leader/data/<str:id>', views.adminStudentLeaderData, name ="admin-student-leader-data"), 

   path('tupc-admin/student/group-members/account', views.adminStudentGroupMemberAccount, name ="admin-student-group-members-account"), 
   path('tupc-admin/student-group-member/data/<str:id>', views.adminStudentGroupMemberData, name ="admin-student-group-member-data"),

   path('tupc-admin/student/course-major/', views.adminStudentCourseMajor, name ="admin-student-course-major"),  
   path('tupc-admin/student/add-course-major/', views.adminStudentAddCourseMajor, name ="admin-student-add-course-major"),
   path('tupc-admin/student/edit-course-major/<str:id>', views.adminStudentEditCourseMajor, name ="admin-student-edit-course-major"), 
   path('tupc-admin/student/delete-course-major/<str:id>', views.adminStudentDeleteCourseMajor, name ="admin-student-delete-course-major"),

   path('tupc-admin/the-devs', views.adminTheDevs, name ="admin-the-devs"),

   # DIT Head URLS
   path('dit-head/home', views.ditHeadDashboard, name ="dit-head-dashboard"),
   path('dit-head/user-profile', views.ditHeadProfile, name ="dit-head-profile"),
   path('dit-head/account-settings', views.ditHeadAccountSettings, name ="dit-head-account-settings"),

   path('dit-head/user-profile/create/e-signature', views.ditHeadCreateESignature, name ="dit-head-create-esignature"),
   path('dit-head/user-profile/upload/e-signature', views.ditHeadUploadESignature, name ="dit-head-upload-esignature"),
   path('dit-head/user-profile/delete/e-signature', views.ditHeadDeleteESignature, name ="dit-head-delete-esignature"),

   path('dit-head/research-titles', views.ditHeadResearchTitles, name ="dit-head-research-titles"),  

   path('dit-head/bet3/topic-defense/panel-invitation', views.ditHeadPanelInvitationBet3, name ="dit-head-panel-invitation-bet-3"),
   path('dit-head/bet3/topic-defense/panel-invitation/accept/sign/<str:id>', views.ditHeadBET3TopicPanelInvitationAcceptSignature, name ="dit-head-bet3-topic-panel-invitation-accept-sign"),
   path('dit-head/bet3/topic-defense/panel-invitation/decline/sign/<str:id>', views.ditHeadBET3TopicPanelInvitationDeclineSignature, name ="dit-head-bet3-topic-panel-invitation-decline-sign"),

   path('dit-head/bet3/topic-defense/panel-invitation/accept/<str:id>', views.ditHeadPanelInvitationBet3Accept, name ="dit-head-panel-invitation-bet-3-accept"),
   path('dit-head/bet3/topic-defense/panel-invitation/decline/<str:id>', views.ditHeadPanelInvitationBet3Decline, name ="dit-head-panel-invitation-bet-3-decline"),

   path('dit-head/bet3/proposal-defense/panel-invitation', views.ditHeadBET3ProposalDefensePanelInvitationDashboard, name ="dit-head-bet3-proposal-defense-panel-invitation-dashboard"),
   path('dit-head/bet3/proposal-defense/panel-invitation/accept/sign/<str:id>', views.ditHeadBET3ProposalPanelInvitationAcceptSignature, name ="dit-head-bet3-proposal-panel-invitation-accept-sign"),
   path('dit-head/bet3/proposal-defense/panel-invitation/decline/sign/<str:id>', views.ditHeadBET3ProposalPanelInvitationDeclineSignature, name ="dit-head-bet3-proposal-panel-invitation-decline-sign"),
   path('dit-head/bet3/proposal-defense/panel-invitation/accept/<str:id>', views.ditHeadBET3ProposalPanelInvitationAccept, name ="dit-head-bet3-proposal-panel-invitation-accept"),
   path('dit-head/bet3/proposal-defense/panel-invitation/decline/<str:id>', views.ditHeadBET3ProposalPanelInvitationDecline, name ="dit-head-bet3-proposal-panel-invitation-decline"),

   # DIT HEAD - ADVISER CONFORME
   path('dit-head/bet3/adviser-conforme', views.ditHeadBET3AdviserConforme, name ="dit-head-bet3-adviser-conforme"),
   path('dit-head/bet3/adviser-conforme/accept/sign/<str:id>', views.ditHeadBET3AdviserConformeAcceptSignature, name ="dit-head-bet3-adviser-conforme-accept-sign"),
   path('dit-head/bet3/adviser-conforme/decline/sign/<str:id>', views.ditHeadBET3AdviserConformeDeclineSignature, name ="dit-head-bet3-adviser-conforme-decline-sign"),
   path('dit-head/bet3/adviser-conforme/accept/<str:id>', views.ditHeadBET3AdviserConformeAccept, name ="dit-head-bet3-adviser-conforme-accept"),
   path('dit-head/bet3/adviser-conforme/decline/<str:id>', views.ditHeadBET3AdviserConformeDecline, name ="dit-head-bet3-adviser-conforme-decline"),
   
   # DIT HEAD - PANEL CONFORME
   path('dit-head/panel-conforme', views.ditHeadPanelConformeDashboard, name ="dit-head-panel-conforme"),
   path('dit-head/panel-conforme/accept/sign/<str:id>', views.ditHeadPanelConformeAcceptSignature, name ="dit-head-panel-conforme-accept-sign"),
   path('dit-head/panel-conforme/accept/<str:id>', views.ditHeadPanelConformeAccept, name ="dit-head-panel-conforme-accept"),

   path('dit-head/bet5/final-defense/panel-invitation', views.ditHeadBET5FinalDefensePanelInvitationDashboard, name ="dit-head-bet5-final-defense-panel-invitation-dashboard"),
   path('dit-head/bet5/final-defense/panel-invitation/accept/sign/<str:id>', views.ditHeadBET5FinalPanelInvitationAcceptSignature, name ="dit-head-bet5-final-panel-invitation-accept-sign"),
   path('dit-head/bet5/final-defense/panel-invitation/decline/sign/<str:id>', views.ditHeadBET5FinalPanelInvitationDeclineSignature, name ="dit-head-bet5-final-panel-invitation-decline-sign"),
   path('dit-head/bet5/final-defense/panel-invitation/accept/<str:id>', views.ditHeadBET5FinalPanelInvitationAccept, name ="dit-head-bet5-final-panel-invitation-accept"),
   path('dit-head/bet5/final-defense/panel-invitation/decline/<str:id>', views.ditHeadBET5FinalPanelInvitationDecline, name ="dit-head-bet5-final-panel-invitation-decline"),

   path('dit-head/acknowledgement-receipt', views.ditHeadAcknowledgementReceipt, name ="dit-head-acknowledgement-receipt"),
   path('dit-head/acknowledgement-receipt/accept/sign/<str:id>', views.ditHeadAcknowledgementReceiptAcceptSignature, name ="dit-head-acknowledgement-receipt-accept-sign"),
   path('dit-head/acknowledgement-receipt/accept/<str:id>', views.ditHeadAcknowledgementReceiptAccept, name ="dit-head-acknowledgement-receipt-accept"),

   path('dit-head/bet3/topic-defense/panel-invitation/logs', views.ditHeadBET3PanelInvitationLogs, name ="dit-head-bet3-panel-invitation-logs"),
   path('dit-head/bet3/adviser-conforme/logs', views.ditHeadBET3AdviserConformeLogs, name ="dit-head-bet3-adviser-conforme-logs"),
   path('dit-head/bet3/proposal-defense/panel-invitation/logs', views.ditHeadBET3ProposalPanelInvitationLogs, name ="dit-head-bet3-proposal-panel-invitation-logs"),
   path('dit-head/bet3/panel-conforme/logs', views.ditHeadPanelConformeLogs, name ="dit-head-panel-conforme-logs"),
   path('dit-head/bet5/final-defense/panel-invitation/logs', views.ditHeadBET5FinalPanelInvitationLogs, name ="dit-head-bet5-final-panel-invitation-logs"),
   path('dit-head/bet5/final-defense/acknowledgement-receipt/logs', views.ditHeadBET5AcknowledgementReceiptLogs, name ="dit-head-acknowledgement-receipt-logs"),

   path('dit-head/the-devs', views.ditHeadTheDevs, name ="dit-head-the-devs"),

   # Panel URLS
   path('panel/home', views.panelDashboard, name ="panel-dashboard"),
   path('panel/user-profile', views.panelProfile, name ="panel-profile"),

   path('panel/create/e-signature', views.panelCreateESignature, name ="panel-create-esignature"),
   path('panel/upload/e-signature', views.panelUploadESignature, name ="panel-upload-esignature"),
   path('panel/delete/e-signature', views.panelDeleteESignature, name ="panel-delete-esignature"),

   path('panel/account-settings', views.panelAccountSettings, name ="panel-account-settings"),

    ##### PANEL - TITLE DEFENSE #####
   path('panel/title-defense-day/<str:id>', views.panelTitleDefenseDay, name ="panel-title-defense-day"),
   path('panel/title-defense-day/attach-sign/<str:id>', views.panelTitleDefenseDayAttachSignature, name ="panel-title-defense-day-attach-signature"),
   path('panel/title-defense-day/live-sign/<str:id>', views.panelTitleDefenseDayLiveSignature, name ="panel-title-defense-day-live-signature"),
   path('panel/title/accept/<str:id>', views.panelAcceptTitle, name ="panel-accept-title"),
   path('panel/title/defer/<str:id>', views.panelDeferTitle, name ="panel-defer-title"),
   path('panel/title/revise/<str:id>', views.panelReviseTitle, name ="panel-revise-title"),
   path('panel/title-defense-day/done/<str:id>', views.panelTitleDefenseMarkDone, name ="panel-title-defense-mark-done"),

   ##### PANEL - PROPOSAL DEFENSE #####
   path('panel/bet3/proposal-defense-day/<str:id>', views.panelBET3ProposalDefenseDay, name ="panel-bet3-proposal-defense-day"),
   path('panel/bet3/proposal-defense-day/critique/panel-chairman/attach-sign/<str:id>', views.panelBET3ProposalDefenseDayCritiquePanelChairmanAttachSignature, name ="panel-bet3-proposal-defense-day-critique-panel-chairman-attach-signature"),
   path('panel/bet3/proposal-defense-day/critique/panel/attach-sign/<str:id>', views.panelBET3ProposalDefenseDayCritiquePanelAttachSignature, name ="panel-bet3-proposal-defense-day-critique-panel-attach-signature"),
   path('panel/bet3/proposal-defense-day/critique/panel-chairman/live-sign/<str:id>', views.panelBET3ProposalDefenseDayCritiquePanelChairmanLiveSignature, name ="panel-bet3-proposal-defense-day-critique-panel-chairman-live-signature"),
   path('panel/bet3/proposal-defense-day/critique/panel/live-sign/<str:id>', views.panelBET3ProposalDefenseDayCritiquePanelLiveSignature, name ="panel-bet3-proposal-defense-day-critique-panel-live-signature"),
   path('panel/bet3/proposal-defense-day/critique/save/<str:id>', views.panelBET3ProposalDefenseDaySaveCritique, name ="panel-bet3-proposal-defense-day-save-critique"),
   path('panel/bet3/proposal-defense-day/critique/delete/<str:id>', views.panelBET3ProposalDefenseDayDeleteCritique, name ="panel-bet3-proposal-defense-day-delete-critique"),
   path('panel/bet3/proposal-defense-day/verdict/accept/<str:id>', views.panelBET3ProposalDefenseDayAccepted, name ="panel-bet3-proposal-defense-day-accepted"),
   path('panel/bet3/proposal-defense-day/verdict/deferred/<str:id>', views.panelBET3ProposalDefenseDayDeferred, name ="panel-bet3-proposal-defense-day-deferred"),
   path('panel/bet3/proposal-defense-day/verdict/not-accepted/<str:id>', views.panelBET3ProposalDefenseDayNotAccepted, name ="panel-bet3-proposal-defense-day-not-accepted"),
   path('panel/bet3/proposal-defense-day/panel-chairman/attach-sign/<str:id>', views.panelBET3ProposalDefenseDayPanelChairmanAttachSignature, name ="panel-bet3-proposal-defense-day-panel-chairman-attach-signature"),
   path('panel/bet3/proposal-defense-day/panel/attach-sign/<str:id>', views.panelBET3ProposalDefenseDayPanelAttachSignature, name ="panel-bet3-proposal-defense-day-panel-attach-signature"),
   path('panel/bet3/proposal-defense-day/panel-chairman/live-sign/<str:id>', views.panelBET3ProposalDefenseDayPanelChairmanLiveSignature, name ="panel-bet3-proposal-defense-day-panel-chairman-live-signature"),
   path('panel/bet3/proposal-defense-day/panel/live-sign/<str:id>', views.panelBET3ProposalDefenseDayPanelLiveSignature, name ="panel-bet3-proposal-defense-day-panel-live-signature"),


   path('panel/bet5/final-defense-day/<str:id>', views.panelBET5FinalDefenseDay, name ="panel-bet5-final-defense-day"),
   path('panel/bet5/final-defense-day/verdict/accept/<str:id>', views.panelBET5FinalDefenseDayAccepted, name ="panel-bet5-final-defense-day-accepted"),
   path('panel/bet5/final-defense-day/verdict/deferred/<str:id>', views.panelBET5FinalDefenseDayDeferred, name ="panel-bet5-final-defense-day-deferred"),
   path('panel/bet5/final-defense-day/verdict/not-accepted/<str:id>', views.panelBET5FinalDefenseDayNotAccepted, name ="panel-bet5-final-defense-day-not-accepted"),
   path('panel/bet5/final-defense-day/panel-chairman/attach-sign/<str:id>', views.panelBET5FinalDefenseDayPanelChairmanAttachSignature, name ="panel-bet5-final-defense-day-panel-chairman-attach-signature"),
   path('panel/bet5/final-defense-day/panel/attach-sign/<str:id>', views.panelBET5FinalDefenseDayPanelAttachSignature, name ="panel-bet5-final-defense-day-panel-attach-signature"),
   path('panel/bet5/final-defense-day/panel-chairman/live-sign/<str:id>', views.panelBET5FinalDefenseDayPanelChairmanLiveSignature, name ="panel-bet5-final-defense-day-panel-chairman-live-signature"),
   path('panel/bet5/final-defense-day/panel/live-sign/<str:id>', views.panelBET5FinalDefenseDayPanelLiveSignature, name ="panel-bet5-final-defense-day-panel-live-signature"),


   path('panel/bet3/panel-invitation', views.panelPanelInvitationBet3, name ="panel-panel-invitation-bet-3"),
   path('panel/bet3/topic-panel-invitation/accept/sign/<str:id>', views.panelBET3TopicPanelInvitationAcceptSignature, name ="panel-bet3-topic-panel-invitation-accept-sign"),
   path('panel/bet3/topic-panel-invitation/decline/sign/<str:id>', views.panelBET3TopicPanelInvitationDeclineSignature, name ="panel-bet3-topic-panel-invitation-decline-sign"),
   path('panel/bet3/panel-invitation/accept/<str:id>', views.panelPanelInvitationBet3Accept, name ="panel-panel-invitation-bet-3-accept"),
   path('panel/bet3/panel-invitation/decline/<str:id>', views.panelPanelInvitationBet3Decline, name ="panel-panel-invitation-bet-3-decline"),
   
   path('panel-research-title-defense-dashboard', views.panelResearchTitleDefenseDashboard, name ="panel-research-title-defense-dashboard"),

   path('panel/panel-conforme', views.panelPanelConformeDashboard, name ="panel-panel-conforme"),
   path('panel/panel-conforme/accept/sign/<str:id>', views.panelPanelConformeAcceptSignature, name ="panel-panel-conforme-accept-sign"),
   path('panel/panel-conforme/accept/<str:id>', views.panelPanelConformeAccept, name ="panel-panel-conforme-accept"),

   path('panel/bet3/proposal-defense/panel-invitation', views.panelBET3ProposalDefensePanelInvitationDashboard, name ="panel-bet3-proposal-defense-panel-invitation-dashboard"),
   path('panel/bet3/proposal-defense/panel-invitation/accept/sign/<str:id>', views.panelBET3ProposalPanelInvitationAcceptSignature, name ="panel-bet3-proposal-defense-panel-invitation-accept-sign"),
   path('panel/bet3/proposal-defense/panel-invitation/decline/sign/<str:id>', views.panelBET3ProposalPanelInvitationDeclineSignature, name ="panel-bet3-proposal-defense-panel-invitation-decline-sign"),
   path('panel/bet3/proposal-defense/panel-invitation/accept/<str:id>', views.panelBET3ProposalPanelInvitationAccept, name ="panel-bet3-proposal-defense-panel-invitation-accept"),
   path('panel/bet3/proposal-defense/panel-invitation/decline/<str:id>', views.panelBET3ProposalPanelInvitationDecline, name ="panel-bet3-proposal-defense-panel-invitation-decline"),

   path('panel/bet5/final-defense/panel-invitation', views.panelBET5FinalDefensePanelInvitationDashboard, name ="panel-bet5-final-defense-panel-invitation-dashboard"),
   path('panel/bet5/final-defense/panel-invitation/accept/sign/<str:id>', views.panelBET5FinalPanelInvitationAcceptSignature, name ="panel-bet5-final-defense-panel-invitation-accept-sign"),
   path('panel/bet5/final-defense/panel-invitation/decline/sign/<str:id>', views.panelBET5FinalPanelInvitationDeclineSignature, name ="panel-bet5-final-defense-panel-invitation-decline-sign"),
   path('panel/bet5/final-defense/panel-invitation/accept/<str:id>', views.panelBET5FinalPanelInvitationAccept, name ="panel-bet5-final-defense-panel-invitation-accept"),
   path('panel/bet5/final-defense/panel-invitation/decline/<str:id>', views.panelBET5FinalPanelInvitationDecline, name ="panel-bet5-final-defense-panel-invitation-decline"),

   path('panel/bet3/panel-invitation/logs', views.panelBET3PanelInvitationLogs, name ="panel-bet3-panel-invitation-logs"),
   path('panel/bet3/proposal-panel-invitation/logs', views.panelBET3ProposalPanelInvitationLogs, name ="panel-bet3-proposal-panel-invitation-logs"),
   path('panel/bet5/final-panel-invitation/logs', views.panelBET5FinalPanelInvitationLogs, name ="panel-bet5-final-panel-invitation-logs"),

   path('panel/bet3/title-defense/logs', views.panelBET3TitleDefenseLogs, name ="panel-bet3-title-defense-logs"),
   path('panel/bet3/title-defense/logs/completed/<str:id>', views.panelBET3TitleDefenseLogCompleted, name ="bet3-title-defense-logs-completed"),
   path('panel/bet3/title-defense/logs/redefense/<str:id>', views.panelBET3TitleDefenseLogRedefense, name ="bet3-title-defense-logs-redefense"),

   path('panel/bet3/proposal-defense/logs', views.panelBET3ProposalDefenseLogs, name ="panel-bet3-proposal-defense-logs"),
   path('panel/bet3/proposal-defense/logs/completed/<str:id>', views.panelBET3ProposalDefenseLogCompleted, name ="bet3-proposal-defense-logs-completed"),

   path('panel/bet5/final-defense/logs', views.panelBET5FinalDefenseLogs, name ="panel-bet5-final-defense-logs"),
   path('panel/bet5/final-defense/logs/completed/<str:id>', views.panelBET5FinalDefenseLogCompleted, name ="bet5-final-defense-logs-completed"),

   path('panel/the-devs', views.panelTheDevs, name ="panel-the-devs"),

   # Subject Teacher URLS
   path('subject-teacher/dashboard', views.subjectTeacherDashboard, name ="subject-teacher-dashboard"),
   path('subject-teacher/profile', views.subjectTeacherProfile, name ="subject-teacher-profile"),

   path('subject-teacher/students/bet3', views.subjectTeacherBET3Students, name ="subject-teacher-students-bet3"),
   path('subject-teacher/students/bet5', views.subjectTeacherBET5Students, name ="subject-teacher-students-bet5"),
   path('subject-teacher/students/data/<str:id>', views.subjectTeacherStudentsData, name ="subject-teacher-students-data"),
   path('subject-teacher/students/logs', views.subjectTeacherLogsStudents, name ="subject-teacher-students-logs"),


   path('subject-teacher/research-titles', views.subjectTeacherResearchTitles, name ="subject-teacher-research-titles"),

   path('subject-teacher/acknowledgement-receipt', views.subjectTeacherAcknowledgementReceipt, name ="subject-teacher-acknowledgement-receipt"),
   path('subject-teacher/acknowledgement-receipt/accept/sign/<str:id>', views.subjectTeacherAcknowledgementReceiptAcceptSignature, name ="subject-teacher-acknowledgement-receipt-accept-sign"),
   path('subject-teacher/acknowledgement-receipt/accept/<str:id>', views.subjectTeacherAcknowledgementReceiptAccept, name ="subject-teacher-acknowledgement-receipt-accept"),

   path('subject-teacher/acknowledgement-receipt/logs', views.subjectTeacherAcknowledgementReceiptLogs, name ="subject-teacher-acknowledgement-receipt-logs"),

   path('subject-teacher/create/e-signature', views.subjectTeacherCreateESignature, name ="subject-teacher-create-esignature"),
   path('subject-teacher/upload/e-signature', views.subjectTeacherUploadESignature, name ="subject-teacher-upload-esignature"),
   path('subject-teacher/delete/e-signature', views.subjectTeacherDeleteESignature, name ="subject-teacher-delete-esignature"),

   path('subject-teacher/account-settings', views.subjectTeacherAccountSettings, name ="subject-teacher-account-settings"),

   path('subject-teacher/title-defense-day/<str:id>', views.subjectTeacherTitleDefenseDay, name ="subject-teacher-title-defense-day"),
   path('subject-teacher/title-defense-day/present/<str:id>', views.subjectTeacherTitleDefenseDayPresent, name ="subject-teacher-title-defense-day-present"),
   path('subject-teacher/title-defense-day/absent/<str:id>', views.subjectTeacherTitleDefenseDayAbsent, name ="subject-teacher-title-defense-day-absent"),
   path('subject-teacher/title-defense-day/set-panel-chairman/<str:id>', views.subjectTeacherTitleDefenseDaySetPanelChairman, name ="subject-teacher-title-defense-day-panel-chairman"),
   path('subject-teacher/title-defense-day/start-vote/<str:id>', views.subjectTeacherTitleDefenseDayStartVote, name ="subject-teacher-title-defense-day-start-vote"),
   path('subject-teacher/title-defense-day/close-vote/<str:id>', views.subjectTeacherTitleDefenseDayCloseVote, name ="subject-teacher-title-defense-day-close-vote"),

   path('subject-teacher/bet3/proposal-defense-day/<str:id>', views.subjectTeacherBET3ProposalDefenseDay, name ="subject-teacher-bet3-proposal-defense-day"),
   path('subject-teacher/bet3/proposal-defense-day/present/<str:id>', views.subjectTeacherBET3ProposalDefensePresent, name ="subject-teacher-bet3-proposal-defense-day-present"),
   path('subject-teacher/bet3/proposal-defense-day/absent/<str:id>', views.subjectTeacherBET3ProposalDefenseAbsent, name ="subject-teacher-bet3-proposal-defense-day-absent"),
   path('subject-teacher/bet3/proposal-defense-day/set-panel-chairman/<str:id>', views.subjectTeacherBET3ProposalDefenseDaySetPanelChairman, name ="subject-teacher-bet3-proposal-defense-day-panel-chairman"),
   path('subject-teacher/bet3/proposal-defense-day/start-critique/<str:id>', views.subjectTeacherBET3ProposalDefenseDayStartCritique, name ="subject-teacher-bet3-proposal-defense-day-start-critique"),
   path('subject-teacher/bet3/proposal-defense-day/end-critique/<str:id>', views.subjectTeacherBET3ProposalDefenseDayEndCritique, name ="subject-teacher-bet3-proposal-defense-day-end-critique"),
   path('subject-teacher/bet3/proposal-defense-day/start-voting/<str:id>', views.subjectTeacherBET3ProposalDefenseDayStartVoting, name ="subject-teacher-bet3-proposal-defense-day-start-voting"),
   path('subject-teacher/bet3/proposal-defense-day/end-voting/<str:id>', views.subjectTeacherBET3ProposalDefenseDayEndVoting, name ="subject-teacher-bet3-proposal-defense-day-end-voting"),
   path('subject-teacher/bet3/proposal-defense-day/end-defense/<str:id>', views.subjectTeacherBET3ProposalDefenseDayEndDefense, name ="subject-teacher-bet3-proposal-defense-day-end-defense"),

   path('subject-teacher/bet5/final-defense-day/<str:id>', views.subjectTeacherBET5FinalDefenseDay, name ="subject-teacher-bet5-final-defense-day"),
   path('subject-teacher/bet5/final-defense-day/present/<str:id>', views.subjectTeacherBET5FinalDefensePresent, name ="subject-teacher-bet5-final-defense-day-present"),
   path('subject-teacher/bet5/final-defense-day/absent/<str:id>', views.subjectTeacherBET5FinalDefenseAbsent, name ="subject-teacher-bet5-final-defense-day-absent"),
   path('subject-teacher/bet5/final-defense-day/set-panel-chairman/<str:id>', views.subjectTeacherBET5FinalDefenseDaySetPanelChairman, name ="subject-teacher-bet5-final-defense-day-panel-chairman"),
   path('subject-teacher/bet5/final-defense-day/start-voting/<str:id>', views.subjectTeacherBET5FinalDefenseDayStartVoting, name ="subject-teacher-bet5-final-defense-day-start-voting"),
   path('subject-teacher/bet5/final-defense-day/end-voting/<str:id>', views.subjectTeacherBET5FinalDefenseDayEndVoting, name ="subject-teacher-bet5-final-defense-day-end-voting"),
   path('subject-teacher/bet5/final-defense-day/end-defense/<str:id>', views.subjectTeacherBET5FinalDefenseDayEndDefense, name ="subject-teacher-bet5-final-defense-day-end-defense"),

   path('subject-teacher/title-defense/my-schedule', views.subjectTeacherMyTitleDefenseDashboard, name ="subject-teacher-title-defense-schedule-dashboard"),
   path('subject-teacher/title-defense/schedule/students', views.subjectTeacherStudentsTitleDefenseDashboard, name ="subject-teacher-students-title-defense-schedule-dashboard"),
   path('subject-teacher/title-defense/set-schedule', views.subjectTeacherSetResearchTitleDefenseSchedule, name ="subject-teacher-set-research-title-defense-schedule"),
   path('subject-teacher/title-defense/save-schedule', views.subjectTeacherSaveResearchTitleDefenseSchedule, name ="subject-teacher-save-research-title-defense-schedule"),
   path('subject-teacher/title-defense/delete-schedule/<str:id>', views.subjectTeacherDeleteResearchTitleDefenseSchedule, name ="subject-teacher-delete-research-title-defense-schedule"),

   path('subject-teacher/proposal-defense/my-schedule', views.subjectTeacherMyProposalDefenseDashboard, name ="subject-teacher-proposal-defense-schedule-dashboard"),
   path('subject-teacher/proposal-defense/schedule/students', views.subjectTeacherStudentsProposalDefenseDashboard, name ="subject-teacher-students-proposal-defense-schedule-dashboard"),
   path('subject-teacher/proposal-defense/set-schedule', views.subjectTeacherSetResearchProposalDefenseSchedule, name ="subject-teacher-set-research-proposal-defense-schedule"),
   path('subject-teacher/proposal-defense/save-schedule', views.subjectTeacherSaveResearchProposalDefenseSchedule, name ="subject-teacher-save-research-proposal-defense-schedule"),
   path('subject-teacher/proposal-defense/delete-schedule/<str:id>', views.subjectTeacherDeleteResearchProposalDefenseSchedule, name ="subject-teacher-delete-research-proposal-defense-schedule"),

   path('subject-teacher/final-defense/my-schedule', views.subjectTeacherMyFinalDefenseDashboard, name ="subject-teacher-final-defense-schedule-dashboard"),
   path('subject-teacher/final-defense/schedule/students', views.subjectTeacherStudentsFinalDefenseDashboard, name ="subject-teacher-students-final-defense-schedule-dashboard"),
   path('subject-teacher/final-defense/set-schedule', views.subjectTeacherSetResearchFinalDefenseSchedule, name ="subject-teacher-set-research-final-defense-schedule"),
   path('subject-teacher/final-defense/save-schedule', views.subjectTeacherSaveResearchFinalDefenseSchedule, name ="subject-teacher-save-research-final-defense-schedule"),
   path('subject-teacher/final-defense/delete-schedule/<str:id>', views.subjectTeacherDeleteResearchFinalDefenseSchedule, name ="subject-teacher-delete-research-final-defense-schedule"),

   path('subject-teacher/title-defense/logs', views.subjectTeacherBET3TitleDefenseLogs, name ="subject-teacher-bet3-title-defense-logs"),
   path('subject-teacher/proposal-defense/logs', views.subjectTeacherBET3ProposalDefenseLogs, name ="subject-teacher-bet3-proposal-defense-logs"),
   path('subject-teacher/final-defense/logs', views.subjectTeacherBET5FinalDefenseLogs, name ="subject-teacher-bet5-final-defense-logs"),

   path('subject-teacher/title-defense/logs/completed/<str:id>', views.subjectTeacherBET3TitleDefenseLogCompleted, name ="subject-teacher-bet3-title-defense-logs-completed"),
   path('subject-teacher/title-defense/logs/redefense/<str:id>', views.subjectTeacherBET3TitleDefenseLogRedefense, name ="subject-teacher-bet3-title-defense-logs-redefense"),

   path('subject-teacher/proposal-defense/logs/completed/<str:id>', views.subjectTeacherBET3ProposalDefenseLogCompleted, name ="subject-teacher-bet3-proposal-defense-logs-completed"),
   #path('subject-teacher/proposal-defense/logs/redefense/<str:id>', views.subjectTeacherBET3ProposalDefenseLogRedefense, name ="subject-teacher-bet3-proposal-defense-logs-redefense"),

   path('subject-teacher/final-defense/logs/completed/<str:id>', views.subjectTeacherBET3FinalDefenseLogCompleted, name ="subject-teacher-bet5-final-defense-logs-completed"),
   # path('subject-teacher/final-defense/logs/redefense/<str:id>', views.subjectTeacherBET3FinalDefenseLogRedefense, name ="subject-teacher-bet3-final-defense-logs-redefense"),
   
   path('subject-teacher/the-devs', views.subjectTeacherTheDevs, name ="subject-teacher-the-devs"),
   
   # Advisers URLS
   path('adviser/dashboard', views.adviserDashboard, name ="adviser-dashboard"),
   path('adviser/profile', views.adviserProfile, name ="adviser-profile"),

   path('adviser/create/e-signature', views.adviserCreateESignature, name ="adviser-create-esignature"),
   path('adviser/upload/e-signature', views.adviserUploadESignature, name ="adviser-upload-esignature"),
   path('adviser/delete/e-signature', views.adviserDeleteESignature, name ="adviser-delete-esignature"),

   path('adviser/account-settings', views.adviserAccountSettings, name ="adviser-account-settings"),

   path('adviser/advisee/dashboard', views.adviserAdviseeDashboard, name ="adviser-advisee-dashboard"),

   path('adviser/bet3/adviser-conforme', views.adviserBET3AdviserConforme, name ="adviser-bet3-adviser-conforme"),

   path('adviser/bet3/adviser-conforme/accept/sign/<str:id>', views.adviserBET3AdviserConformeAcceptSignature, name ="adviser-bet3-adviser-conforme-accept-sign"),
   path('adviser/bet3/adviser-conforme/decline/sign/<str:id>', views.adviserBET3AdviserConformeDeclineSignature, name ="adviser-bet3-adviser-conforme-decline-sign"),

   path('adviser/bet3/adviser-conforme/accept/<str:id>', views.adviserBET3AdviserConformeAccept, name ="adviser-bet3-adviser-conforme-accept"),
   path('adviser/bet3/adviser-conforme/decline/<str:id>', views.adviserBET3AdviserConformeDecline, name ="adviser-bet3-adviser-conforme-decline"),

   path('adviser/acknowledgement-receipt', views.adviserAcknowledgementReceipt, name ="adviser-acknowledgement-receipt"),
   path('adviser/acknowledgement-receipt/accept/sign/<str:id>', views.adviserAcknowledgementReceiptAcceptSignature, name ="adviser-acknowledgement-receipt-accept-sign"),
   path('adviser/acknowledgement-receipt/accept/<str:id>', views.adviserAcknowledgementReceiptAccept, name ="adviser-acknowledgement-receipt-accept"),

   path('adviser/the-devs', views.adviserTheDevs, name ="adviser-the-devs"),

   path('adviser/bet3/adviser-conforme/logs', views.adviserBET3AdviserConformeLogs, name ="adviser-bet3-adviser-conforme-logs"),
   path('adviser/bet3//acknowledgement-receipt/logs', views.adviserAcknowledgementReceiptLogs, name ="adviser-acknowledgement-receipt-logs"),


   path('academic-affairs-office/dashboard', views.academicAffairsOfficeDashboard, name ="academic-affairs-office-dashboard"),
   path('academic-affairs-office/logs', views.academicAffairsOfficeLogs, name ="academic-affairs-office-logs"),
   path('academic-affairs-office/user-profile', views.academicAffairsOfficeProfile, name ="academic-affairs-office-profile"),

   path('academic-affairs-office/create/e-signature', views.academicAffairsOfficeCreateESignature, name ="academic-affairs-office-create-esignature"),
   path('academic-affairs-office/upload/e-signature', views.academicAffairsOfficeUploadESignature, name ="academic-affairs-office-upload-esignature"),
   path('academic-affairs-office/delete/e-signature', views.academicAffairsOfficeDeleteESignature, name ="academic-affairs-office-delete-esignature"),

   path('academic-affairs-office/account-settings', views.academicAffairsOfficeAccountSettings, name ="academic-affairs-office-account-settings"),

   path('academic-affairs-office/the-devs', views.academicAffairsOfficeTheDevs, name ="academic-affairs-office-the-devs"),

   path('academic-affairs-office/acknowledgement-receipt/accept/sign/<str:id>', views.academicAffairsOfficeAcceptSignature, name ="academic-affairs-office-accept-sign"),
   path('academic-affairs-office/acknowledgement-receipt/accept/<str:id>', views.academicAffairsOfficeAccept, name ="academic-affairs-office-accept"),


   path('library/dashboard', views.libraryDashboard, name ="library-dashboard"),
   path('library/logs', views.libraryLogs, name ="library-logs"),
   path('library/user-profile', views.libraryProfile, name ="library-profile"),

   path('library/create/e-signature', views.libraryCreateESignature, name ="library-create-esignature"),
   path('library/upload/e-signature', views.libraryUploadESignature, name ="library-upload-esignature"),
   path('library/delete/e-signature', views.libraryDeleteESignature, name ="library-delete-esignature"),

   path('library/account-settings', views.libraryAccountSettings, name ="library-account-settings"),

   path('library/the-devs', views.libraryTheDevs, name ="library-the-devs"),

   path('library/acknowledgement-receipt/accept/sign/<str:id>', views.libraryAcceptSignature, name ="library-accept-sign"),
   path('library/acknowledgement-receipt/accept/<str:id>', views.libraryAccept, name ="library-accept"),


   path('research-extension/dashboard', views.researchExtensionDashboard, name ="research-extension-dashboard"),
   path('research-extension/logs', views.researchExtensionLogs, name ="research-extension-logs"),
   path('research-extension/user-profile', views.researchExtensionProfile, name ="research-extension-profile"),

   path('research-extension/create/e-signature', views.researchExtensionCreateESignature, name ="research-extension-create-esignature"),
   path('research-extension/upload/e-signature', views.researchExtensionUploadESignature, name ="research-extension-upload-esignature"),
   path('research-extension/delete/e-signature', views.researchExtensionDeleteESignature, name ="research-extension-delete-esignature"),

   path('research-extension/account-settings', views.researchExtensionAccountSettings, name ="research-extension-account-settings"),

   path('research-extension/the-devs', views.researchExtensionTheDevs, name ="research-extension-the-devs"),

   path('research-extension/acknowledgement-receipt/accept/sign/<str:id>', views.researchExtensionAcceptSignature, name ="research-extension-accept-sign"),
   path('research-extension/acknowledgement-receipt/accept/<str:id>', views.researchExtensionAccept, name ="research-extension-accept"),
]