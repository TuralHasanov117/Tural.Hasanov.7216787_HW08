from django.db import models
from django.urls import reverse
from django.utils import timezone


class QuestionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(pub_date__lte=timezone.now())


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = QuestionManager()

    def __str__(self):
        return self.question_text
    
    def get_absolute_url(self):
        return reverse("polls:detail", kwargs={"question_id": self.pk})
    

class Choice(models.Model):
    question = models.ForeignKey(Question, related_name="question_choices", on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.choice_text