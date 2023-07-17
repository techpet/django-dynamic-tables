from rest_framework.viewsets import ViewSet
from rest_framework.exceptions import APIException
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.core.serializers.python import Serializer
from .serializers import CreateTableSerializer, CreateTableResponseSerializer, UpdateTableSerializer, UpdateTableResponseSerializer, ErrorSerializer
from .logic import TableService, InvalidAlterMigrationError


class TableViewSet(ViewSet):

    def __init__(self, *args, **kwargs):
        super(TableViewSet, self).__init__(*args, **kwargs)
        self.services = TableService()

    """
    Returns a list of all the tables in the system.
    """

    @swagger_auto_schema(request_body=CreateTableSerializer, responses={201: CreateTableResponseSerializer(), 400: ErrorSerializer()})
    def create(self, request, pk=None):
        """ Creates a new Dynamic Table with fields"""

        table_data = CreateTableSerializer(data=request.data)
        table_data.is_valid(raise_exception=True)

        result = self.services.create_table(table_data.validated_data)

        created_table = CreateTableResponseSerializer(data=result)
        created_table.is_valid(raise_exception=True)

        return Response(created_table.validated_data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(request_body=UpdateTableSerializer, responses={200: UpdateTableResponseSerializer(), 409: ErrorSerializer()})
    def update(self, request, pk=None):
        """ Updates a new Dynamic Table with fields"""

        table_data = UpdateTableSerializer(data=request.data)
        table_data.is_valid(raise_exception=True)

        try:
            result = self.services.update_table(
                id=pk, new_schema=request.data['fields'])
        except InvalidAlterMigrationError as ex:
            raise APIException(ex)

        updated_table = UpdateTableResponseSerializer(
            data=result)

        updated_table.is_valid(raise_exception=True)

        return Response(updated_table.validated_data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'field1': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='boolean'),
            'field2': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
            'field3': openapi.Schema(type=openapi.TYPE_INTEGER, description='integer'),
        }
    ), responses={201: openapi.Response(description="Dictionary of row fields",
                                        examples={
                                            "application/json": {
                                                    "id": 15,
                                                    "field1": True,
                                                    "field2": "string",
                                                    "field3": 0,
                                            }
                                        }), 500: ErrorSerializer()})
    @action(detail=True, methods=["POST"])
    def row(self, request, pk):
        """ Inserts rows in a Dynamic table"""

        row_data = request.data

        try:
            row = self.services.create_row(id=pk, row_data=row_data)
        except Exception as ex:
            raise APIException(ex)

        created_row = Serializer().serialize([row])[0]

        return Response({
            'id': created_row['pk'],
            **created_row['fields'],
        }, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(responses={
        200: openapi.Response(description="A list of the retrieved rows",
            examples={
                                  "application/json": [
                                  {
                                      "id": 1,
                                      "field1": True,
                                      "field2": "one string",
                                      "field3": 0,
                                    }, {
                                  "id": 2,
                                      "field1": False,
                                      "field2": "another string",
                                      "field3": 1,
                                      }
                              ]}

                              ), 500: ErrorSerializer()})
    @ action(detail=True, methods=["GET"])
    def rows(self, request, pk):
        """ Retrieves rows from a Dynamic table"""
        try:
            rows = self.services.retrieve_rows(id=pk)
        except Exception as ex:
            raise APIException(ex)

        returned_rows = []

        for row in rows:
            serialized_row = Serializer().serialize([row])[0]
            returned_rows.append({
                'id': serialized_row['pk'],
                **serialized_row['fields'],
            })

        return Response(returned_rows)
