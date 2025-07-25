from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('auth/register/', views.register_user, name='register'),
    path('auth/login/', views.login_user, name='login'),
    path('auth/profile/', views.get_user_profile, name='profile'),
    path('auth/debug/', views.debug_auth, name='debug_auth'),
    
    # Portfolios
    path('portfolios/', views.PortfolioListCreateView.as_view(), name='portfolio-list-create'),
    path('portfolios/<int:pk>/', views.PortfolioDetailView.as_view(), name='portfolio-detail'),
    
    # Assets
    path('assets/', views.AssetListCreateView.as_view(), name='asset-list-create'),
    path('assets/<int:pk>/', views.AssetDetailView.as_view(), name='asset-detail'),
    path('assets/<int:asset_id>/update-value/', views.update_asset_value, name='update-asset-value'),
    path('assets/<int:asset_id>/price-history/', views.get_asset_price_history, name='asset-price-history'),
    
    # Evaluation
    path('evaluate/apartment/', views.evaluate_apartment, name='evaluate-apartment'),
    
    # Dashboard
    path('dashboard/', views.get_dashboard_data, name='dashboard'),
    
    # Apartment evaluation
    path('districts-mahallas/', views.get_districts_mahallas, name='districts_mahallas'),
    
    # Car evaluation  
    path('car-brands/', views.get_car_brands, name='get_car_brands'),
    path('car-models/', views.get_car_models, name='get_car_models'),
    path('car-specs/', views.get_car_specs, name='get_car_specs'),
    path('evaluate-car/', views.evaluate_car, name='evaluate_car'),
    
    # PDF Downloads
    path('download-apartment-report/', views.download_apartment_report, name='download_apartment_report'),
    path('download-car-report/', views.download_car_report, name='download_car_report'),
    
    # Marketplace
    path('marketplace/listings/', views.get_marketplace_listings, name='marketplace-listings'),
    path('marketplace/create/', views.create_marketplace_listing, name='create-marketplace-listing'),
    path('marketplace/listings/<int:listing_id>/', views.remove_marketplace_listing, name='remove-marketplace-listing'),
    path('marketplace/my-listings/', views.get_user_marketplace_listings, name='user-marketplace-listings'),
] 