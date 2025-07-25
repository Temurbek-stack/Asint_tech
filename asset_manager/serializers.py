from rest_framework import serializers
from .models import User, Portfolio, Asset, AssetValueHistory

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'phone', 'profile_picture', 'created_at']
        read_only_fields = ['id', 'created_at']

class PortfolioSerializer(serializers.ModelSerializer):
    total_value = serializers.SerializerMethodField()
    asset_count = serializers.SerializerMethodField()

    class Meta:
        model = Portfolio
        fields = ['id', 'name', 'description', 'total_value', 'asset_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_total_value(self, obj):
        return sum(asset.current_value for asset in obj.assets.all())

    def get_asset_count(self, obj):
        return obj.assets.count()

class AssetValueHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetValueHistory
        fields = ['id', 'value', 'date', 'created_at']
        read_only_fields = ['id', 'created_at']

class AssetSerializer(serializers.ModelSerializer):
    value_history = AssetValueHistorySerializer(many=True, read_only=True)
    portfolio_name = serializers.CharField(source='portfolio.name', read_only=True)

    class Meta:
        model = Asset
        fields = [
            'id', 'portfolio', 'portfolio_name', 'asset_type', 'name', 'address', 
            'current_value', 'purchase_price', 'purchase_date', 'image_url',
            'area', 'rooms', 'floor', 'total_floors', 'year', 'mileage', 
            'brand', 'model', 'description', 'value_history', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class AssetCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = [
            'portfolio', 'asset_type', 'name', 'address', 'current_value', 
            'purchase_price', 'purchase_date', 'image_url', 'area', 'rooms', 
            'floor', 'total_floors', 'year', 'mileage', 'brand', 'model', 'description'
        ]

    def create(self, validated_data):
        asset = Asset.objects.create(**validated_data)
        
        # Create initial value history entry
        AssetValueHistory.objects.create(
            asset=asset,
            value=asset.current_value,
            date=asset.created_at.date()
        )
        
        return asset 