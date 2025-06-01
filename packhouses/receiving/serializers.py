from rest_framework import serializers
from packhouses.receiving.models import Batch


class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = '__all__'
        read_only_fields = ['ooid', 'created_at']
