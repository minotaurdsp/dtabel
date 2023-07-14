from django.db import models
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers, viewsets, mixins, status
from rest_framework.response import Response
from django.db import connection

from .models import DynamicField, DynamicTable

APP_NAME = 'dtables'

def prepare_attrs(table):
    dynamic_fields = {}
    for field in table.fields.all():
        field_name = field.name
        field_class = getattr(models, field.field_type)
        field = field_class(max_length=255)
        dynamic_fields[field_name] = field

    attrs = {
        '__module__': __name__
    }
    attrs.update(dynamic_fields)
    return attrs

def prepare_model(table):
    table_name = table.name
    attrs = prepare_attrs(table)
    model = type(table_name, (models.Model,), attrs)
    model._meta.db_table = table_name
    return model


class DynamicFieldSerializer(serializers.ModelSerializer):
    dynamic_table = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = DynamicField
        fields = '__all__'


class DynamicTableSerializer(serializers.ModelSerializer):
    fields = DynamicFieldSerializer(many=True)
    class Meta:
        model = DynamicTable
        fields = '__all__'

    def create(self, validated_data):
        fields_data = validated_data.pop('fields')
        table = DynamicTable.objects.create(**validated_data)
        if fields_data:
            for field_data in fields_data:
                DynamicField.objects.create(dynamic_table=table, **field_data)
            
            dynamic_model = prepare_model(table)
            
            table_name = table.name
            apps.all_models[APP_NAME][table_name] = dynamic_model

        print("All tables: ",connection.introspection.table_names())

        return table

    def update(self, instance, validated_data):
        fields_data = validated_data.pop('fields', [])
        existing_fields = set(instance.fields.values_list('name', flat=True))
        updated_fields = set(field_data.get('name') for field_data in fields_data)
        fields_to_delete = existing_fields - updated_fields

        # Delete unused fields
        DynamicField.objects.filter(dynamic_table=instance, name__in=fields_to_delete).delete()

        for field_data in fields_data:
            field_name = field_data.get('name')
            if field_name:
                # Update existing fields
                try:
                    field = DynamicField.objects.get(dynamic_table=instance, name=field_name)
                    for key, value in field_data.items():
                        setattr(field, key, value)
                    field.save()
                except ObjectDoesNotExist:
                    DynamicField.objects.create(**field_data)


        # Check if table exist
        print("Table name :",instance.name)
        table_name = instance.name

        dynamic_model = prepare_model(instance)

        print("All tables: ",connection.introspection.table_names())
        
        table_exists = table_name in connection.introspection.table_names()

        # Use the SchemaEditor to create the dynamic model
        with connection.schema_editor() as schema_editor:
            if  not table_exists:
                #model = type(table_name,(models.Model,),attrs)
                #model._meta.db_table = table_name
                schema_editor.create_model(dynamic_model)

        return instance


    



