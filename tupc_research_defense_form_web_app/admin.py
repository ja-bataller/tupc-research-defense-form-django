from django.contrib import admin
from .models import *

admin.site.register(User)

admin.site.register(StudentCourseMajor)

admin.site.register(StudentLeader)
admin.site.register(StudentGroupMember)

admin.site.register(ResearchTitle)
admin.site.register(ResearchTitleLog)

admin.site.register(DefenseSchedule)
admin.site.register(DefenseScheduleLog)

admin.site.register(TitlePanelInvitation)
admin.site.register(TitlePanelInvitationLog)

admin.site.register(TitleDefenseForm)
admin.site.register(TitleDefenseFormLog)

admin.site.register(TitleVote)

admin.site.register(AdviserConforme)
admin.site.register(AdviserConformeLog)

admin.site.register(FilePath)

admin.site.register(ProposalPanelInvitation)
admin.site.register(ProposalPanelInvitationLog)

admin.site.register(ProposalDefenseCritique)

admin.site.register(ProposalDefenseForm)
admin.site.register(ProposalDefenseFormLog)

admin.site.register(FinalPanelInvitation)
admin.site.register(FinalPanelInvitationLog)

admin.site.register(FinalDefenseForm)
admin.site.register(FinalDefenseFormLog)

admin.site.register(PanelConforme)
admin.site.register(PanelConformeLog)

admin.site.register(AcknowledgementReceipt)





















