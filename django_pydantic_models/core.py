from typing import Type, Union, List, Any, Dict, Optional, Literal, get_type_hints
from uuid import UUID
from decimal import Decimal
from datetime import datetime, date, time
from pydantic import BaseModel, Field, HttpUrl, EmailStr, create_model
from django.db import models

# Mapping Django fields to Pydantic types
django_to_pydantic_model_mapping = {
    models.CharField: str,
    models.TextField: str,
    models.IntegerField: int,
    models.FloatField: float,
    models.BooleanField: bool,
    models.DateTimeField: datetime,
    models.DateField: date,
    models.TimeField: time,
    models.URLField: HttpUrl,
    models.UUIDField: UUID,
    models.EmailField: EmailStr,
    models.DecimalField: Decimal,
    models.ImageField: str,
    models.FileField: str,
    models.BigIntegerField: int,
    models.SmallIntegerField: int,
    models.PositiveIntegerField: int,
    models.PositiveSmallIntegerField: int,
    models.SlugField: str,
    models.BinaryField: bytes,
    models.JSONField: Union[Dict[Any, Any], List[Dict[Any, Any]]],
    models.DurationField: str,
    models.GenericIPAddressField: str,
    models.AutoField: int,
    models.BigAutoField: int,
    models.SmallAutoField: int,
    models.IPAddressField: str,
}


def get_pydantic_type_and_constraints(field: models.Field) -> tuple:
    """Infer Pydantic type and constraints from a Django field."""
    extra_constraints = {}

    if field.choices:
        choices_values = [choice[0] for choice in field.choices]
        base_type = Literal[tuple(choices_values)]
    else:
        base_type = Any
        for django_type, pyd_type in django_to_pydantic_model_mapping.items():
            if isinstance(field, django_type):
                base_type = pyd_type
                break

        if isinstance(
            field,
            (models.CharField, models.SlugField, models.EmailField, models.URLField),
        ):
            if field.max_length is not None:
                extra_constraints["max_length"] = field.max_length

    if field.null or field.blank:
        base_type = Optional[base_type]

    return base_type, extra_constraints


def django_model_to_pydantic(django_model_cls: Type[models.Model]):
    """Convert Django model to Pydantic model.
    ```python
        @django_model_to_pydantic(Book)
        class BookOut:
            ...
    ```
    """
    converted_models: Dict[Type[models.Model], Type[BaseModel]] = {}

    def wrapper(config_cls: Type) -> Type[BaseModel]:
        if django_model_cls in converted_models:
            return converted_models[django_model_cls]

        fields = getattr(config_cls, "__fields__", None)
        exclude = getattr(config_cls, "__exclude__", None)

        if fields and exclude:
            raise ValueError(
                f"{config_cls.__name__} cannot define both __fields__ and __exclude__."
            )

        if isinstance(fields, str):
            fields = (fields,)
        if isinstance(exclude, str):
            exclude = (exclude,)

        exclude = set(exclude or [])

        all_fields = {
            field.name: field
            for field in django_model_cls._meta.get_fields()
            if isinstance(field, models.Field)
        }
        all_field_names = set(all_fields)

        if fields == ("__all__",):
            selected_fields = all_field_names
        elif fields:
            invalid = set(fields) - all_field_names
            if invalid:
                raise ValueError(
                    f"Invalid field(s) in __fields__: {invalid}. Valid fields: {all_field_names}"
                )
            selected_fields = set(fields)
        else:
            selected_fields = all_field_names

        selected_fields -= exclude

        pydantic_fields: Dict[str, tuple] = {}

        for name in selected_fields:
            field = all_fields[name]

            # Handle relationship fields
            if isinstance(field, (models.ForeignKey, models.OneToOneField)):
                related_model = field.related_model
                RelatedPydanticModel = converted_models.get(related_model)
                if not RelatedPydanticModel:
                    RelatedPydanticModel = django_model_to_pydantic(related_model)(
                        type(f"{related_model.__name__}Model", (), {})
                    )
                pydantic_fields[name] = (
                    (
                        Optional[RelatedPydanticModel]
                        if field.null or field.blank
                        else RelatedPydanticModel
                    ),
                    None,
                )

            elif isinstance(field, models.ManyToManyField):
                related_model = field.related_model
                RelatedPydanticModel = converted_models.get(related_model)
                if not RelatedPydanticModel:
                    RelatedPydanticModel = django_model_to_pydantic(related_model)(
                        type(f"{related_model.__name__}Model", (), {})
                    )
                pydantic_fields[name] = (
                    List[RelatedPydanticModel],
                    Field(default_factory=list),
                )

            else:
                pyd_type, constraints = get_pydantic_type_and_constraints(field)
                default = (
                    None
                    if field.null or field.blank
                    else (
                        field.default
                        if field.default is not models.NOT_PROVIDED
                        else ...
                    )
                )
                field_kwargs = {}

                if field.help_text:
                    field_kwargs["description"] = field.help_text.strip()
                if field.verbose_name:
                    field_kwargs["title"] = str(field.verbose_name).strip()
                field_kwargs.update(constraints)

                if field_kwargs:
                    pydantic_fields[name] = (pyd_type, Field(default, **field_kwargs))
                else:
                    pydantic_fields[name] = (pyd_type, default)

        # User-defined fields
        user_annotations = get_type_hints(config_cls)
        for name, type_hint in user_annotations.items():
            if name not in pydantic_fields:
                default = getattr(config_cls, name, ...)
                pydantic_fields[name] = (type_hint, default)

        # Handle optional Config class
        config_dict = {}
        config_cls_def = getattr(config_cls, "Config", None)
        if config_cls_def:
            config_dict = getattr(config_cls_def, "config", {})

        # Get validators
        validators_dict = getattr(config_cls, "__validators__", {})

        base_model = create_model(
            config_cls.__name__ + "Base",
            __base__=BaseModel,
            __module__=config_cls.__module__,
            __validators__=validators_dict,
            model_config={"from_attributes": True, **config_dict},
            **pydantic_fields,
        )

        def __init__(self, *args, **kwargs):
            if len(args) == 1 and isinstance(args[0], django_model_cls):
                instance = args[0]
                for name in selected_fields:
                    value = getattr(instance, name)

                    field_obj = all_fields[name]

                    if isinstance(field_obj, models.ManyToManyField):
                        value = list(value.all())
                    elif isinstance(field_obj, (models.ImageField, models.FileField)):
                        value = getattr(value, "url", None) if value else None

                    kwargs.setdefault(name, value)

            elif args:
                TypeError(
                    f"{self.__class__.__name__} accepts a Django model instance or keyword args only."
                )

            super(self.__class__, self).__init__(**kwargs)

        final_model = type(
            config_cls.__name__,
            (base_model,),
            {
                "__doc__": config_cls.__doc__,
                "__init__": __init__,
                "__module__": config_cls.__module__,
            },
        )

        converted_models[django_model_cls] = final_model
        return final_model

    return wrapper
