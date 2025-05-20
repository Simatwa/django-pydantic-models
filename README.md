# django-pydantic-models

**A lightweight utility that converts Django models into fully-typed Pydantic models**, supporting automatic field mapping, validation constraints, and nested model generation for related fields (`ForeignKey`, `OneToOneField`, `ManyToManyField`).

[![PyPI version](https://badge.fury.io/py/django-pydantic-models.svg)](https://pypi.org/project/django-pydantic-models/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## ✨ Features

- 🔁 Automatic mapping from Django fields to Pydantic types
- 🧠 Smart support for Django field constraints:
  - `max_length`, `choices`, `default`, `help_text`, `verbose_name`
- 📦 Supports nested models for `ForeignKey`, `OneToOneField`, `ManyToManyField`
- ⚙️ Extensible with Pydantic validators and configuration
- 🛠️ Add or exclude fields selectively using `__fields__` or `__exclude__`
- 🚀 Ideal for FastAPI, data validation, or serialization needs

> [!NOTE]
> This is not a competitor to [djantic](https://github.com/jordaneremieff/djantic) but an optimiser for working around with FastAPI and Django while keeping the traditions - use of decorator - alive.

---

## 📦 Installation

```bash
pip install django-pydantic-models
````

---

## 🛠 Usage

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

    class Config:
        config = {"populate_by_name": True}

    __validators__ = {
        "title": lambda v: v.title()  # Example Pydantic validator
    }
```

---

## 🧩 Field Mapping

Django fields are automatically mapped to their closest Pydantic equivalents. Examples:

| Django Field      | Pydantic Type         |
| ----------------- | --------------------- |
| `CharField`       | `str`                 |
| `EmailField`      | `EmailStr`            |
| `URLField`        | `HttpUrl`             |
| `IntegerField`    | `int`                 |
| `DateTimeField`   | `datetime`            |
| `ForeignKey`      | nested Pydantic model |
| `ManyToManyField` | `List[nested model]`  |
| `choices=`        | `Literal[...]`        |

---

## 🔍 Customization

### Selecting fields

```python
class BookOut:
    __fields__ = ('title', 'author')  # Include only
    # or use __exclude__ = ('published',)
```

### Validators

```python
class BookOut:
    __validators__ = {
        "title": lambda v: v.strip().title()
    }
```

### Pydantic Config

```python
class BookOut:
    class Config:
        config = {
            "populate_by_name": True,
            "extra": "forbid"
        }
```

---

## 🧪 Initialization

Models can be initialized from a Django instance:

```python
book = Book.objects.select_related("author").prefetch_related("tags").first()
pydantic_book = BookOut(book)
print(pydantic_book.model_dump())
```

Or with kwargs:

```python
pydantic_book = BookOut(title="New Book", author=AuthorOut(...))
```

---


## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Pull requests, issues, and feature suggestions are welcome! Please open an issue or PR.

---

## 📌 Why This Exists

Django models are great for ORM use but don't offer native support for fully typed external interfaces (e.g., APIs). `django-pydantic-models` bridges this gap, letting you use Django models for database interactions and automatically generate Pydantic models for typed validation and data exchange.

