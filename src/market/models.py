from django.db import models


class Key(models.Model):
    key = models.CharField(max_length=120)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.key
