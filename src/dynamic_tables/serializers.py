from rest_framework import serializers


class FieldsField(serializers.DictField):
    def __init__(self, *args, **kwargs):
        super(FieldsField, self).__init__(*args, **kwargs)
        try:
            self.help_text = kwargs['help_text']
        except KeyError:
            self.help_text = "Table field definitions in the format {field_name,field_type} where field_type is one of integer, string, boolean"
        self.child = serializers.ChoiceField(choices=[
            "integer", "boolean", "string"])




class CreateTableSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    fields = FieldsField()

class CreateTableResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=200)
    fields = FieldsField()


class UpdateTableSerializer(serializers.Serializer):
    fields = FieldsField()


class UpdateTableResponseSerializer(serializers.Serializer):
    added = FieldsField(
        help_text="Added field definitions in the format {field_name,field_type}")
    deleted = FieldsField(help_text="Deleted field definitions in the format {field_name,field_type}")
    modified = FieldsField(help_text="Modified field definitions in the format {field_name,field_type}")
    schema = FieldsField(help_text="Table current schema in the format {field_name,field_type}")






class ErrorSerializer(serializers.Serializer):
    errors = serializers.JSONField(
        help_text="A dictionary containing errors in case that the request failed")
