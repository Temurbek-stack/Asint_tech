from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    """Custom user model for the asset manager platform"""
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

class Portfolio(models.Model):
    """Portfolio model to group user's assets"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolios')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.name}"

class Asset(models.Model):
    """Asset model for apartments and cars"""
    ASSET_TYPES = [
        ('apartment', 'Квартира'),
        ('car', 'Автомобиль'),
    ]

    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='assets')
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPES)
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=500)
    current_value = models.DecimalField(max_digits=15, decimal_places=2)
    purchase_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    image_url = models.URLField(blank=True, null=True)
    
    # Apartment specific fields
    area = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    rooms = models.IntegerField(null=True, blank=True)
    floor = models.IntegerField(null=True, blank=True)
    total_floors = models.IntegerField(null=True, blank=True)
    
    # Car specific fields
    year = models.IntegerField(null=True, blank=True)
    mileage = models.IntegerField(null=True, blank=True)
    brand = models.CharField(max_length=100, null=True, blank=True)
    model = models.CharField(max_length=100, null=True, blank=True)
    
    # Common fields
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.get_asset_type_display()}"

class AssetValueHistory(models.Model):
    """Model to track asset value changes over time"""
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='value_history')
    value = models.DecimalField(max_digits=15, decimal_places=2)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.asset.name} - ${self.value} on {self.date}"


class MarketplaceListing(models.Model):
    """Model to track assets listed for sale in the marketplace"""
    asset = models.OneToOneField(Asset, on_delete=models.CASCADE, related_name='marketplace_listing')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='marketplace_listings')
    listing_price = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    listed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Contact information
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    
    class Meta:
        ordering = ['-listed_at']
    
    def __str__(self):
        return f"Listing: {self.asset.name} - ${self.listing_price}" 