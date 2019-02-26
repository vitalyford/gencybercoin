from django.contrib import admin
from .models import UserData, UserAnswers, Code, TransferLogs, MarketItem, Cart, Achievement, PassRecQuestions, CodeRedeemer, School, PortalSetting, Bugs, SEQuesAnsw, SECorrectAnswer, Feedback
from import_export.admin import ImportExportModelAdmin
# from import_export.admin import ImportExportMixin, ImportMixin, ExportActionModelAdmin

from import_export import resources


class CodeRedeemerAdmin(ImportExportModelAdmin):
    pass


class UserDataAdmin(ImportExportModelAdmin):
    pass


class PassRecQuestionsAdmin(ImportExportModelAdmin):
    pass


class UserAnswersAdmin(ImportExportModelAdmin):
    pass


class CodeAdmin(ImportExportModelAdmin):
    pass


class TransferLogsAdmin(ImportExportModelAdmin):
    pass


class MarketItemAdmin(ImportExportModelAdmin):
    pass


class CartAdmin(ImportExportModelAdmin):
    pass


class AchievementAdmin(ImportExportModelAdmin):
    pass


class SchoolAdmin(ImportExportModelAdmin):
    pass


class PortalSettingAdmin(ImportExportModelAdmin):
    pass


class BugsAdmin(ImportExportModelAdmin):
    pass


class SEQuesAnswAdmin(ImportExportModelAdmin):
    pass


class SECorrectAnswerAdmin(ImportExportModelAdmin):
    pass


class FeedbackAdmin(ImportExportModelAdmin):
    pass


# Register your models here.
admin.site.register(CodeRedeemer, CodeRedeemerAdmin)
admin.site.register(UserData, UserDataAdmin)
admin.site.register(PassRecQuestions, PassRecQuestionsAdmin)
admin.site.register(UserAnswers, UserAnswersAdmin)
admin.site.register(Code, CodeAdmin)
admin.site.register(TransferLogs, TransferLogsAdmin)
admin.site.register(MarketItem, MarketItemAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Achievement, AchievementAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(PortalSetting, PortalSettingAdmin)
admin.site.register(Bugs, BugsAdmin)
admin.site.register(SEQuesAnsw, SEQuesAnswAdmin)
admin.site.register(SECorrectAnswer, SECorrectAnswerAdmin)
admin.site.register(Feedback, FeedbackAdmin)
