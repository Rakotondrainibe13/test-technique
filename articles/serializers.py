from rest_framework import serializers
from .models import Article

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'
        read_only_fields = ['author']

    def create(self, validated_data):
        user = self.context['request'].user
        return Article.objects.create(author=user, **validated_data)
