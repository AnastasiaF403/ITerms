from django.db import models
from django.contrib.auth.models import User


class Group(models.Model):
    group_name = models.CharField(max_length=20)

    def __str__(self):
        return self.group_name


class Dictionary(models.Model):
    states_CHOICES = (
        ('не изучены', 'Не изучены'),
        ('изучены', 'Изучены'),
    )
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, default='', related_name='owner')
    states = models.CharField(max_length=10, choices=states_CHOICES, default='не изучены')


class Term(models.Model):
    term = models.CharField(max_length=100)
    transcript = models.CharField(max_length=100)
    examples = models.TextField()
    group_id = models.ForeignKey(Group, on_delete=models.CASCADE)
    translate = models.CharField(max_length=100, default='n')
    dictionaries = models.ManyToManyField(Dictionary, blank=True, related_name='term_dict')

    def __str__(self):
        return self.term


#
