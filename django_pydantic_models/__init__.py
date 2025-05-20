""" 
A lightweight utility that converts Django models into fully-typed Pydantic models,
supporting automatic field mapping, validation constraint and nested model generation 
for related fields (ForeignKey, OneToOneField, ManyToManyField)


```python
from django.db import models
from django_pydantic_models import django_model_to_pydantic


class Author(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()


class Book(models.Model):
    title = models.CharField(max_length=200, help_text="Title of the book")
    published = models.BooleanField(default=False)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    tags = models.ManyToManyField("Tag")


class Tag(models.Model):
    name = models.CharField(max_length=50)


@django_model_to_pydantic(Book)
class BookOut:
    __fields__ = "__all__"  # or list specific fields like ('title', 'author')
    #__exclude__ = ("id",)

# Usage

book = Book.objects.select_related("author").prefetch_related("tags").first()
pydantic_book = BookOut(book)
print(pydantic_book.model_dump())

# Or with kwargs

pydantic_book = BookOut(title="New Book", author=AuthorOut(...))
```

"""

from importlib import metadata

try:
    __version__ = metadata.version("django-pydantic-models")
except metadata.PackageNotFoundError:
    __version__ = "0.0.0"

from django_pydantic_models.core import (
    django_model_to_pydantic,
    django_to_pydantic_model_mapping,
    get_pydantic_type_and_constraints,
)

__all__ = [
    "django_model_to_pydantic",
    "django_to_pydantic_model_mapping",
    "get_pydantic_type_and_constraints",
]
