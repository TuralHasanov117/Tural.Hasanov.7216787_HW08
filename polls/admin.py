from django.contrib import admin
from polls.models import Question, Choice

admin.site.register(Choice)

class ChoiceInline(admin.StackedInline):
    model = Choice

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [
        ChoiceInline,
    ]

