from django.db import models
from django.utils.translation import gettext_lazy as _
from enum import Enum

# Create your models here.


class EnumWithChoices(Enum):

    @classmethod
    def choices(cls):
        return [(entry.value, entry.name) for entry in cls]


class Author(models.Model):
    class UserGender(EnumWithChoices):
        MALE = "M"
        FEMALE = "F"
        OTHER = "0"

    name = models.CharField(max_length=100, help_text=_("Author name"))
    email = models.EmailField(help_text=_("Author email"))
    gender = models.CharField(
        choices=UserGender.choices(), default=UserGender.OTHER.value, max_length=1
    )


class Book(models.Model):
    title = models.CharField(max_length=200, help_text=_("Title of the book"))
    published = models.BooleanField(default=False, help_text=_("Published status"))
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    tags = models.ManyToManyField("Tag")
    added_on = models.DateTimeField(
        auto_now=True, help_text=_("Date and time when the entry was firstly made")
    )


class Tag(models.Model):
    name = models.CharField(max_length=50)
