from rest_framework import serializers
from ..models.Role import Role as RoleModel

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleModel
        fields = '__all__'
