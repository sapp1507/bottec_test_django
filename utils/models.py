from django.db import models


class TimeModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True,
                                      editable=False,
                                      verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True,
                                      editable=False,
                                      verbose_name='Обновлено')

    class Meta:
        abstract = True


class NameModel(models.Model):
    name = models.CharField(max_length=100,
                            verbose_name='Название')

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
