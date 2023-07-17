from typing import List, Dict
from django.db import models, connection
from django.apps import apps
from .models import Table


class TableService:

    def create_table(self, table_data):
        """
        Function that creates a Table entry and dynamically creates a new db table
        with its fields
        """

        # Create a new Table entry
        table_instance = Table.objects.create(
            name=table_data['name'], schema=table_data['fields'])

        model = TableModelHandler(name=f'{table_instance.name}_{table_instance.id}', schema=table_instance.schema).get_model()

        self.__create_db_table(model)

        return {"id": table_instance.id,
                "name": table_instance.name,
                "fields": table_data['fields']}

    def update_table(self, id, new_schema):
        """
        Function that updates the db schema of a dynamic table based on given table meta
        """

        table_instance = Table.objects.get(pk=id)

        old_model_handler = TableModelHandler(name=f'{table_instance.name}_{table_instance.id}', schema=table_instance.schema)
        new_model_handler = TableModelHandler(name=f'{table_instance.name}_{table_instance.id}', schema=new_schema)

        added, deleted, modified = self.__update_db_table(
            old_model_handler, new_model_handler)

        table_instance.schema = new_schema
        table_instance.save()

        return {"added": added, "deleted": deleted, "modified": modified, "schema":table_instance.schema}

    def create_row(self, id, row_data):
        """
        Function that creates a new row to table with id
        """
        table_instance = Table.objects.get(pk=id)
        model = TableModelHandler(name=f'{table_instance.name}_{table_instance.id}', schema=table_instance.schema).get_model()
        row = model.objects.create(**row_data)

        return row

    def retrieve_rows(self, id):
        """
        Function that retrieves all rows from table with id
        """

        table_instance = Table.objects.get(pk=id)
        model = TableModelHandler(name=f'{table_instance.name}_{table_instance.id}', schema=table_instance.schema).get_model()
        rows = model.objects.all()
        return rows

    def __create_db_table(self, model):
        """
        creates a dynamic table in db from a model definition
        """

        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(model)

    def __update_db_table(self, old_model_handler, new_model_handler):
        """
        updates a dynamic table schema in db
        """


        added, deleted, modified = self.__compare_dicts(
            old_model_handler.get_schema(), new_model_handler.get_schema())

        # print('Added:', added)
        # print('Deleted:', deleted)
        # print('Modified:', modified)

        old_model = old_model_handler.get_model()
        new_model = new_model_handler.get_model()

        old_schema = old_model_handler.get_schema()

        with connection.schema_editor() as schema_editor:
            for field_name, field_type in added.items():
                field_to_add = new_model_handler.get_field(field_name)
                field_to_add.null = True

                print(field_to_add.null)
                schema_editor.add_field(
                    new_model_handler.get_model(), field_to_add)

            for field_name, field_type in deleted.items():
                schema_editor.remove_field(
                    old_model, old_model_handler.get_field(field_name))

            for field_name, field_type in modified.items():
                try:
                    schema_editor.alter_field(new_model, old_model_handler.get_field(
                        field_name), new_model_handler.get_field(field_name), strict=True)
                except Exception:
                    raise InvalidAlterMigrationError(
                        field_name, old_schema[field_name], field_type)

        return added, deleted, modified

    def __compare_dicts(self, old_dict, new_dict):
        """
        compares two dicts and returns dicts of added, deleted and modified elements
        """

        added = {key: new_dict[key]
                 for key in new_dict.keys() - old_dict.keys()}
        deleted = {key: old_dict[key]
                   for key in old_dict.keys() - new_dict.keys()}
        modified = {key: new_dict[key] for key in new_dict.keys(
        ) & old_dict.keys() if new_dict[key] != old_dict[key]}

        return added, deleted, modified


class TableModelHandler:
    def __init__(self, name, schema):
        self.name = name
        self.schema = schema

        self.model = self.create_table_model()

    def __str__(self):
        return str(self.model.__name__)

    def create_table_model(self):
        """
        creates a new model from table meta
        """

        # Set dynamic table attributes
        table_attributes = {
            "Meta": type("Meta", (), {"app_label": "dynamic_tables"}),
            "__module__": "database.models",

        }

        model_fields = self.__schema_to_django_fields(self.schema)

        table_attributes.update(model_fields)

        # Create the table model

        self.model = type(f'{self.name}',
                          (models.Model,), table_attributes)

        return self.model

    def __field_type_to_django_field(self, field_name, field_type):
        """
        converts a field to django field
        """

        field = {}

        if field_type == "integer":
            field.update({
                field_name: models.IntegerField()
            })
        elif field_type == "boolean":
            field.update({
                field_name: models.BooleanField()
            })
        elif field_type == "string":
            field.update({
                field_name: models.CharField(max_length=200)
            })

        return field

    def __schema_to_django_fields(self, schema):
        """
        converts a fields schema to django fields
        """

        fields = {}

        for field_name, field_type in schema.items():
            fields.update(self.__field_type_to_django_field(
                field_name, field_type))

        return fields

    def get_schema(self):
        """
        returns model's table schema
        """
        return self.schema

    def get_model(self):
        """
        returns model
        """
        return self.model

    def get_fields(self):
        """
        returns model fields
        """
        return self.model._meta.get_fields()

    def get_field(self, name):
        """
        returns model field with name
        """
        return self.model._meta.get_field(name)


class InvalidAlterMigrationError(Exception):
    """Raised when a migration error happens"""

    def __init__(self, field_name, type_from, type_to):
        self.field_name = field_name
        self.type_from = type_from
        self.type_to = type_to

    def __str__(self):
        return f'{self.field_name} cannot be migrated from {self.type_from} to {self.type_to}'
