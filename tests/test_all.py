import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
import django

django.setup()

from library.models import Book, Author, Tag
from django_pydantic_models import django_model_to_pydantic
import pytest


@django_model_to_pydantic(Book)
class BookPublicAll: ...


@django_model_to_pydantic(Book)
class BookPublicSpecificFields:
    __fields__ = ("title", "published", "added_on")


@django_model_to_pydantic(Book)
class BookPublicExcludedFields:
    __exclude__ = ("author", "tags")


def test_django_model_to_pydantic():
    author = Author.objects.create(name="john", email="johndoe@domain.com")
    author.save()
    tag = Tag.objects.create(name="Technology")
    tag.save()
    book = Book(title="Java for Dummies", author=author)
    book.save()
    book.tags.add(tag)
    book.save()

    assert type(BookPublicAll(book).model_dump().get("author")) is dict
    assert hasattr(BookPublicSpecificFields(book), "id") == False
    assert hasattr(BookPublicExcludedFields(book), "tags") == False
    book.delete()
    author.delete()
    tag.delete()


if __name__ == "__main__":
    pytest.main(["-v", "--tb=short"])
