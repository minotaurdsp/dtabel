
from .serializers import DynamicFieldSerializer , DynamicTableSerializer
from .models import DynamicField,DynamicTable
from rest_framework.response import Response

from rest_framework.decorators import action
from rest_framework import viewsets, serializers, decorators, status


class DynamicFieldViewSet(viewsets.ModelViewSet):
    queryset = DynamicField.objects.all()
    serializer_class = DynamicFieldSerializer

class DynamicTableViewSet(viewsets.ModelViewSet):
    queryset = DynamicTable.objects.all()
    serializer_class = DynamicTableSerializer

    @decorators.action(detail=True, methods=['post'], serializer_class=DynamicFieldSerializer)
    def row(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(dynamic_table=instance)

        return Response(serializer.data)
    
    @decorators.action(detail=True, methods=['get'])
    def rows(self, request, pk=None):
        instance = self.get_object()
        fields = instance.fields.all()
        serializer = DynamicFieldSerializer(fields, many=True)

        return Response(serializer.data)
    

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return Response(status=status.HTTP_204_NO_CONTENT)
