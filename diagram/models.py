from django.db import models
from django.contrib.auth.models import User

class Block(models.Model):
    name = models.CharField(max_length=30)
    inpN = models.IntegerField()
    outpN = models.IntegerField()
    pars = models.JSONField(blank=True)
    states = models.JSONField(blank=True)

class DiagFiles(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="related user",
        to_field='username',
    )
    name = models.CharField(max_length=30)
    ser = models.JSONField(blank=True)