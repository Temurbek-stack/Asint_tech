from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import User, Portfolio, Asset, AssetValueHistory, MarketplaceListing
from .serializers import (
    UserSerializer, PortfolioSerializer, AssetSerializer, 
    AssetCreateSerializer, AssetValueHistorySerializer
)
from .utils import generate_historical_prices, get_price_change_percentage
import requests
import json
from django.http import HttpResponse
import os
import sys

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_user(request):
    """Register a new user"""
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.set_password(request.data.get('password'))
        user.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_user(request):
    """Login user and return token"""
    email = request.data.get('email')
    password = request.data.get('password')
    
    if email and password:
        user = authenticate(username=email, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            })
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({'error': 'Email and password required'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_profile(request):
    """Get current user profile"""
    return Response(UserSerializer(request.user).data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def debug_auth(request):
    """Debug authentication"""
    return Response({
        'authenticated': request.user.is_authenticated,
        'user_id': request.user.id,
        'username': request.user.username,
        'headers': dict(request.headers),
        'auth_header': request.headers.get('Authorization', 'No auth header'),
    })

class PortfolioListCreateView(generics.ListCreateAPIView):
    """List and create portfolios for the authenticated user"""
    serializer_class = PortfolioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Portfolio.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class PortfolioDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a portfolio"""
    serializer_class = PortfolioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Portfolio.objects.filter(user=self.request.user)

class AssetListCreateView(generics.ListCreateAPIView):
    """List and create assets"""
    serializer_class = AssetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        portfolio_id = self.request.query_params.get('portfolio')
        if portfolio_id:
            return Asset.objects.filter(portfolio__user=self.request.user, portfolio_id=portfolio_id)
        return Asset.objects.filter(portfolio__user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AssetCreateSerializer
        return AssetSerializer

    def perform_create(self, serializer):
        # Ensure the portfolio belongs to the user
        portfolio = get_object_or_404(Portfolio, id=serializer.validated_data['portfolio'].id, user=self.request.user)
        asset = serializer.save(portfolio=portfolio)
        
        # Generate historical prices for the new asset
        try:
            generate_historical_prices(asset)
        except Exception as e:
            print(f"Error generating historical prices for {asset.name}: {e}")

class AssetDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete an asset"""
    serializer_class = AssetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Asset.objects.filter(portfolio__user=self.request.user)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])  # Allow unauthenticated access for apartment evaluation
def evaluate_apartment(request):
    """Evaluate apartment using the ML model"""
    try:
        # Import the prediction logic directly
        import pandas as pd
        import joblib
        import os
        
        # Get the project root directory (where manage.py is located)
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_path = os.path.join(BASE_DIR, 'data')
        
        # Load models and data
        model1 = joblib.load(os.path.join(data_path, 'GBM_MADEL_WITHOUT_DISTANCE.pkl'))
        model2 = joblib.load(os.path.join(data_path, 'model2.pkl'))
        x_columns = pd.read_csv(os.path.join(data_path, 'xcolumns.csv'))
        uybor_cols = pd.read_csv(os.path.join(data_path, 'uybor_columns.csv'))
        mahalla_and_tuman = pd.read_csv(os.path.join(data_path, 'mahalla_tuman_codes.csv'))
        unique_mahalla_olx = pd.read_csv(os.path.join(data_path, 'unique_mahalla_olx.csv'))

        input_data = request.data
        
        # Skip the first column (index column) when creating the dictionary
        feature_columns = [col for col in x_columns.columns if not col.startswith('Unnamed') and col != '']
        my_dict = {col: 0 for col in feature_columns}

        my_dict["totalArea"] = input_data.get("area")
        my_dict["numberOfRooms"] = input_data.get("rooms")
        my_dict["floor"] = input_data.get("floor")
        my_dict["floorOfHouse"] = input_data.get("total_floors")
        my_dict["furnished"] = 1 if input_data.get("mebel") == 'Ha' else 0
        my_dict["handle"] = 1 if input_data.get("kelishsa") == 'Ha' else 0
        my_dict["pricingMonth"] = input_data.get("month")
        my_dict["pricingYear"] = input_data.get("year")

        for k, v in {
            "Maktab": "shkola", "Supermarket": "supermarket", "Do'kon": "magazini", "Park": "park"
        }.items():
            my_dict[v] = 1 if k in input_data.get("atrofda", []) else 0

        for k, v in {
            "Televizor": "tv_wm_ac_fridge", "Internet": "telefon_internet"
        }.items():
            my_dict[v] = 1 if k in input_data.get("uyda", []) else 0

        # Map UI values to model expected values
        value_mappings = {
            "owner": {
                "Mulkdor": "Mulkdor",
                "Tashkilot": "Tashkilot", 
                "Boshqa": "Boshqa"
            },
            "planirovka": {
                "Oddiy": "Oddiy",
                "Hosila": "Hosila", 
                "Mustahkam": "Mustahkam"
            },
            "renovation": {
                "Yaxshi": "Yaxshi",
                "O'rtacha": "O'rtacha",
                "Yomon": "Yomon"
            },
            "sanuzel": {
                "Birgalikda": "Birgalikda",
                "Alohida": "Alohida"
            },
            "bino_turi": {
                "Ikkinchi bozor": "Ikkinchi bozor",
                "Birlamchi bozor": "Birlamchi bozor"
            },
            "qurilish_turi": {
                "Panel": "Panel",
                "G'isht": "G'isht",
                "Monolit": "Monolit"
            }
        }

        for prefix, field in [
            ("ownerType_", "owner"),
            ("planType_", "planirovka"),
            ("repairType_", "renovation"),
            ("bathroomType_", "sanuzel"),
            ("marketType_", "bino_turi"),
            ("buildType_", "qurilish_turi"),
        ]:
            val = input_data.get(field)
            if val and field in value_mappings:
                mapped_val = value_mappings[field].get(val, val)
                my_dict[f"{prefix}{mapped_val}"] = 1
            elif val:
                my_dict[f"{prefix}{val}"] = 1

        if input_data.get("district"):
            d = mahalla_and_tuman[mahalla_and_tuman['district_str'] == input_data['district']]['district_code'].values
            my_dict["district_code"] = d[0] if len(d) > 0 else 0
            
        # Handle mahalla name mapping (UI now sends Latin names directly)
        if input_data.get("mahalla"):
            # The UI now sends Latin names directly, so look them up by neighborhood_latin
            n = mahalla_and_tuman[mahalla_and_tuman['neighborhood_latin'] == input_data['mahalla']]['neighborhood_code'].values
            my_dict["neighborhood_code"] = n[0] if len(n) > 0 else 0

        model = model1 if my_dict.get("neighborhood_code", 0) in set(unique_mahalla_olx['neighborhood_code']) else model2
        
        df = pd.DataFrame([my_dict])
        df['numberOfRooms'] = df['numberOfRooms'].astype(int)
        df['floor'] = df['floor'].astype(int)
        df['floorOfHouse'] = df['floorOfHouse'].astype(int)
        df['totalArea'] = df['totalArea'].astype(float)
        if 'district_code' in df.columns:
            df['district_code'] = df['district_code'].astype(int)
        if 'neighborhood_code' in df.columns:
            df['neighborhood_code'] = df['neighborhood_code'].astype(int)

        if model == model2:
            # Get the first column from uybor_cols (which contains the feature names)
            first_col = uybor_cols.columns[0]
            selected_features = uybor_cols[first_col].tolist()
            # Filter to only include features that exist in our dataframe
            available_features = [col for col in selected_features if col in df.columns]
            df = df[available_features]

        prediction = model.predict(df)[0]
        margin = round(prediction * 0.0361)

        return Response({
            'predicted_price': round(prediction),
            'price_range': [round(prediction - margin), round(prediction + margin)],
            'input_data': input_data
        })

    except Exception as e:
        import traceback
        return Response({
            'error': str(e),
            'traceback': traceback.format_exc(),
            'input_data': request.data
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_dashboard_data(request):
    """Get dashboard summary data"""
    user_assets = Asset.objects.filter(portfolio__user=request.user)
    
    total_value = sum(asset.current_value for asset in user_assets)
    asset_count = user_assets.count()
    
    # Calculate portfolio performance (30-day change)
    total_change_amount = 0
    total_previous_value = 0
    
    for asset in user_assets:
        change_percentage = get_price_change_percentage(asset, days=30)
        current_value = float(asset.current_value)
        previous_value = current_value / (1 + change_percentage / 100) if change_percentage != 0 else current_value
        
        total_change_amount += (current_value - previous_value)
        total_previous_value += previous_value
    
    change_percent = 0
    if total_previous_value > 0:
        change_percent = (total_change_amount / total_previous_value) * 100
    
    # Get all assets with individual change percentages
    all_assets = user_assets.order_by('-created_at')
    assets_data = []
    
    for asset in all_assets:
        asset_data = AssetSerializer(asset).data
        asset_data['change_percentage'] = get_price_change_percentage(asset, days=30)
        assets_data.append(asset_data)
    
    # Get recent assets (first 6 for backwards compatibility)
    recent_assets = assets_data[:6]
    
    return Response({
        'total_value': total_value,
        'total_change': round(total_change_amount, 2),
        'change_percent': round(change_percent, 2),
        'asset_count': asset_count,
        'recent_assets': recent_assets,
        'all_assets': assets_data  # Include all assets with change percentages
    })

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_asset_value(request, asset_id):
    """Update asset value and add to history"""
    try:
        asset = get_object_or_404(Asset, id=asset_id, portfolio__user=request.user)
        new_value = request.data.get('new_value')
        
        if new_value:
            asset.current_value = new_value
            asset.save()
            
            # Add to value history
            AssetValueHistory.objects.create(
                asset=asset,
                value=new_value,
                date=request.data.get('date', timezone.now().date())
            )
            
            return Response(AssetSerializer(asset).data)
        else:
            return Response({'error': 'New value is required'}, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_asset_price_history(request, asset_id):
    """Get price history for an asset"""
    try:
        asset = get_object_or_404(Asset, id=asset_id, portfolio__user=request.user)
        
        # Get last 12 months of price history
        price_history = AssetValueHistory.objects.filter(
            asset=asset
        ).order_by('date')[:12]
        
        # Format data for chart
        chart_data = []
        for entry in price_history:
            chart_data.append({
                'date': entry.date.strftime('%Y-%m-%d'),
                'month': entry.date.strftime('%b %Y'),
                'value': float(entry.value)
            })
        
        return Response({
            'asset_name': asset.name,
            'current_value': float(asset.current_value),
            'price_history': chart_data,
            'change_percentage': get_price_change_percentage(asset, days=30)
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_car_brands(request):
    """Get available car brands"""
    try:
        import pandas as pd
        import os
        
        # Get the project root directory (where manage.py is located)
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_path = os.path.join(BASE_DIR, 'data')
        
        # Load brand and car data
        brand_car_names = pd.read_csv(os.path.join(data_path, 'Brand_and_car_column.csv'))
        brands = brand_car_names['brand'].unique().tolist()
        
        return Response({'brands': brands}, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"Error getting car brands: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_car_models(request):
    """Get available car models for a brand"""
    try:
        import pandas as pd
        import os
        
        brand = request.GET.get('brand')
        if not brand:
            return Response({'error': 'Brand parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the project root directory (where manage.py is located)
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_path = os.path.join(BASE_DIR, 'data')
        
        # Load brand and car data
        brand_car_names = pd.read_csv(os.path.join(data_path, 'Brand_and_car_column.csv'))
        models = brand_car_names[brand_car_names['brand'] == brand]['car_name'].unique().tolist()
        
        return Response({'models': models}, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"Error getting car models: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_car_specs(request):
    """Get body type and engine volume for a car model"""
    try:
        import pandas as pd
        import os
        
        model = request.GET.get('model')
        if not model:
            return Response({'error': 'Model parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the project root directory (where manage.py is located)
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_path = os.path.join(BASE_DIR, 'data')
        
        # Load car body and engine volume data
        car_body_enginevol = pd.read_csv(os.path.join(data_path, 'data_to_find_enginevol_body.csv'))
        filtered_df = car_body_enginevol[car_body_enginevol['car_name'] == model]
        
        if filtered_df.empty:
            return Response({'body_type': '', 'engine_volume': None}, status=status.HTTP_200_OK)
        
        car_body = filtered_df.iloc[0]['body_type']
        engine_vol = filtered_df.iloc[0]['engine_volume'] if not pd.isnull(filtered_df.iloc[0]['engine_volume']) else None
        
        return Response({'body_type': car_body, 'engine_volume': engine_vol}, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"Error getting car specs: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def evaluate_car(request):
    """Evaluate car using the ML model"""
    try:
        import pandas as pd
        import joblib
        import os
        from datetime import datetime
        
        # Get the project root directory (where manage.py is located)
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_path = os.path.join(BASE_DIR, 'data')
        
        # Load models and data
        model3 = joblib.load(os.path.join(data_path, 'CHEVROLET_DAEWOO_RAVON_LGBM_41.pkl'))
        model4 = joblib.load(os.path.join(data_path, 'CLEANDED_DATA_FOREIGN_LGBM.pkl'))
        scaler1 = joblib.load(os.path.join(data_path, 'scaler_CHEVROLET-DAEWOO-RAVON.pkl'))
        scaler2 = joblib.load(os.path.join(data_path, 'scaler_foreign_cleaned_Data_lgbm.pkl'))
        
        X1 = pd.read_csv(os.path.join(data_path, 'Chevrolet_DAEWOO_RAVON_columns.csv'))
        X2 = pd.read_csv(os.path.join(data_path, 'FOREIGN_columns_cleaned_Data_lgbm.csv'))

        input_data = request.data
        
        # Determine which model to use based on brand
        brand = input_data.get("brand")
        if brand in ['Chevrolet', 'Ravon', 'Daewoo']:
            # Use model for Chevrolet/Daewoo/Ravon
            feature_columns = [col for col in X1.columns if not col.startswith('Unnamed') and col != '']
            updated_auto_dict = {col: 0 for col in feature_columns}
            model = model3
            scaler = scaler1
            check = 'model_3'
        else:
            # Use model for foreign cars
            feature_columns = [col for col in X2.columns if not col.startswith('Unnamed') and col != '']
            updated_auto_dict = {col: 0 for col in feature_columns}
            model = model4
            scaler = scaler2
            check = 'model_4'

        # Basic car information
        updated_auto_dict["release_year"] = input_data.get("year")
        updated_auto_dict["engine_volume"] = input_data.get("engine_volume")
        updated_auto_dict["mileage"] = input_data.get("mileage")
        updated_auto_dict["month"] = input_data.get("month", datetime.now().month)
        updated_auto_dict["year"] = datetime.now().year

        # Brand type (1 for Chevrolet, 0 for others in the Chevrolet model)
        if check == 'model_3':
            updated_auto_dict['brand_type'] = 1 if brand == 'Chevrolet' else 0
        else:
            updated_auto_dict['brand_type'] = 0  # Always 0 for foreign model

        # Car name
        car_name = input_data.get("model")
        if car_name and f'car_name_{car_name}' in updated_auto_dict:
            updated_auto_dict[f'car_name_{car_name}'] = 1

        # Ownership type
        ownership = input_data.get("ownership", "Xususiy")
        if ownership == 'Biznes':
            updated_auto_dict['item_type_Business'] = 1
            updated_auto_dict['item_type_Private'] = 0
        else:
            updated_auto_dict['item_type_Business'] = 0
            updated_auto_dict['item_type_Private'] = 1

        # Owners count
        owners_count = input_data.get("owners_count", 1)
        if f'owners_count_{owners_count}' in updated_auto_dict:
            updated_auto_dict[f'owners_count_{owners_count}'] = 1

        # Car condition
        condition = input_data.get("condition")
        car_condition_mapping = {
            "A'lo": "Excellent",
            "O'rtacha": "Average", 
            "Remont talab": "Needs_Repair",
            "Yaxshi": "Good"
        }
        if condition and condition in car_condition_mapping:
            condition_key = car_condition_mapping[condition]
            if f'car_condition_{condition_key}' in updated_auto_dict:
                updated_auto_dict[f'car_condition_{condition_key}'] = 1

        # Fuel type
        fuel = input_data.get("fuel")
        fuel_mapping = {
            "Benzin": "Gasoline",
            "Gaz/Benzin": "Gasoline/Petrol",
            "Gibrid": "Hybrid",
            "Dizel": "Diesel", 
            "Boshqa": "Other",
            "Elektro": "Electric"
        }
        if fuel and fuel in fuel_mapping:
            fuel_key = fuel_mapping[fuel]
            if f'fuel_type_{fuel_key}' in updated_auto_dict:
                updated_auto_dict[f'fuel_type_{fuel_key}'] = 1

        # Car color
        color = input_data.get("color")
        color_mapping = {
            "Asfalt": "Asphalt",
            "Bejeviy": "Beige",
            "Qora": "Black",
            "Ko'k": "Blue",
            "Jigarrang": "Brown",
            "Kulrang": "Gray",
            "Boshqa": "Other",
            "Kumush": "Silver",
            "Oq": "White"
        }
        if color and color in color_mapping:
            color_key = color_mapping[color]
            if f'color_{color_key}' in updated_auto_dict:
                updated_auto_dict[f'color_{color_key}'] = 1

        # Body type  
        body_type = input_data.get("body_type")
        body_mapping = {
            "Yo'ltanlamas": "SUV",
            "Boshqa": "Other",
            "Kabriolet": "Convertible",
            "Kupe": "Coupe",
            "Miniven": "Minivan", 
            "Pikap": "Pickup",
            "Sedan": "Sedan",
            "Universal": "Wagon",
            "Xetchbek": "Hatchback"
        }
        if body_type and body_type in body_mapping:
            body_key = body_mapping[body_type]
            if f'body_{body_key}' in updated_auto_dict:
                updated_auto_dict[f'body_{body_key}'] = 1

        # State/Region
        state = input_data.get("state")
        state_mapping = {
            "Toshkent shahri": "Tashkent",
            "Qoraqalpogʻiston Respublikasi": "Karakalpakstan",
            "Navoiy Viloyati": "Navoiy",
            "Toshkent Viloyati": "Tashkent2",
            "Samarqand Viloyati": "Samarkand",
            "Qashqadaryo Viloyati": "Kashkadarya",
            "Farg'ona Viloyati": "Ferghana",
            "Buxoro Viloyati": "Bukhara",
            "Xorazm Viloyati": "Khorezm",
            "Sirdaryo Viloyati": "Sirdaryo",
            "Surxondaryo Viloyati": "Surkhondaryo",
            "Namangan Viloyati": "Namangan",
            "Andijon Viloyati": "Andijon",
            "Jizzax Viloyati": "Jizzakh"
        }
        if state and state in state_mapping:
            state_key = state_mapping[state]
            if f'state_{state_key}' in updated_auto_dict:
                updated_auto_dict[f'state_{state_key}'] = 1

        # Transmission (1 for manual, 0 for automatic)
        transmission = input_data.get("transmission", "Mexanik")
        updated_auto_dict['transmission'] = 1 if transmission == 'Mexanik' else 0

        # Features
        features = input_data.get("features", [])
        feature_mapping = {
            "Konditsioner": "Air_Conditioner",
            "Xavfsizlik tizimi": "Security_System",
            "Parctronik": "Parking_Sensors",
            "Rastamojka qilingan": "Customs_Cleared",
            "Elektron oynalar": "Power_Windows",
            "Elektron ko'zgular": "Power_Mirrors"
        }
        for feature_uz, feature_en in feature_mapping.items():
            if feature_en in updated_auto_dict:
                updated_auto_dict[feature_en] = 1 if feature_uz in features else 0

        # Create DataFrame and predict
        df_auto = pd.DataFrame([updated_auto_dict])
        
        # Remove specific columns based on model type
        if check == "model_4":
            df_auto = df_auto.drop(columns=["body_Convertible", "color_Beige"], errors="ignore")
        elif check == "model_3":
            df_auto = df_auto.drop(columns=["color_Beige"], errors="ignore")

        # Scale and predict
        df_auto_scaled = scaler.transform(df_auto)
        prediction = model.predict(df_auto_scaled)
        predicted_price = round(prediction[0])
        
        # Calculate price range (±3.61% margin)
        margin = round(predicted_price * 0.0361)
        lower_bound = predicted_price - margin
        upper_bound = predicted_price + margin

        return Response({
            'predicted_price': predicted_price,
            'price_range': {
                'lower': lower_bound,
                'upper': upper_bound
            },
            'formatted_price': f"${predicted_price:,}",
            'formatted_range': f"${lower_bound:,} - ${upper_bound:,}"
        }, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"Error evaluating car: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_districts_mahallas(request):
    """Get districts and mahallas for apartment forms"""
    try:
        import pandas as pd
        import os
        
        # Get the project root directory (where manage.py is located)
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_path = os.path.join(BASE_DIR, 'data')
        
        # Load the neighborhoods CSV file
        df = pd.read_csv(os.path.join(data_path, 'neighborhoods.csv'))
        
        # Group mahallas by district
        districts_mahallas = {}
        for _, row in df.iterrows():
            district = row['district_name_latin']
            mahalla = row['mahalla_name_latin']
            
            if district not in districts_mahallas:
                districts_mahallas[district] = []
            
            if mahalla not in districts_mahallas[district]:
                districts_mahallas[district].append(mahalla)
        
        return Response(districts_mahallas, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"Error getting districts and mahallas: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def download_apartment_report(request):
    """Generate and download PDF report for apartment evaluation"""
    try:
        from django.http import HttpResponse
        import sys
        
        # Get the project root directory
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Add the project root to Python path so we can import the PDF generators
        if BASE_DIR not in sys.path:
            sys.path.append(BASE_DIR)
        
        from pdf_generator import create_report
        
        # Extract data from request
        evaluation_data = request.data
        
        # Create property details dictionary for PDF
        property_details = {
            'Hudud': f"{evaluation_data.get('district', '')}, {evaluation_data.get('mahalla', '')}",
            'Maydoni': f"{evaluation_data.get('area', '')}m²" if evaluation_data.get('area') else '',
            'Xonalar soni': str(evaluation_data.get('rooms', '')),
            'Qavat': str(evaluation_data.get('floor', '')),
            'Binoning qavatlar soni': str(evaluation_data.get('total_floors', '')),
            'Jihozlangan': evaluation_data.get('mebel', ''),
            'Atrofda': ', '.join(evaluation_data.get('atrofda', [])) if evaluation_data.get('atrofda') else '',
            'Uyda mavjud': ', '.join(evaluation_data.get('uyda', [])) if evaluation_data.get('uyda') else '',
            'Mulk turi': evaluation_data.get('owner', ''),
            'Planirovka': evaluation_data.get('planirovka', ''),
            "Ta'mir turi": evaluation_data.get('renovation', ''),
            'Sanuzel': evaluation_data.get('sanuzel', ''),
            'Bozor turi': evaluation_data.get('bino_turi', ''),
            'Qurilish turi': evaluation_data.get('qurilish_turi', ''),
            "Kelishish mumkinmi": evaluation_data.get('kelishsa', ''),
            'Baholash vaqti': f"{evaluation_data.get('month', '')}-{evaluation_data.get('year', '')}"
        }
        
        predicted_price = evaluation_data.get('predicted_price', '')
        price_range = evaluation_data.get('price_range', '')
        
        # Generate PDF
        pdf_bytes = create_report(property_details, str(predicted_price), price_range)
        
        # Return PDF as response
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="apartment_evaluation_report.pdf"'
        return response
        
    except Exception as e:
        print(f"Error generating apartment PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def download_car_report(request):
    """Generate and download PDF report for car evaluation"""
    try:
        from django.http import HttpResponse
        import sys
        
        # Get the project root directory
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Add the project root to Python path so we can import the PDF generators
        if BASE_DIR not in sys.path:
            sys.path.append(BASE_DIR)
        
        from pdf_generator_auto import create_report_auto
        
        # Extract data from request
        evaluation_data = request.data
        
        # Create property details dictionary for PDF
        property_details = {
            'Hudud': evaluation_data.get('state', ''),
            'Brend': evaluation_data.get('brand', ''),
            'Nomi': evaluation_data.get('model', ''),
            'Ishlab chiqarilgan yili': str(evaluation_data.get('year', '')),
            'Mator hajmi': str(evaluation_data.get('engine_volume', '')),
            "Yoqilg'gi turi": evaluation_data.get('fuel', ''),
            'Egalik turi': evaluation_data.get('ownership', ''),
            'Kuzov turi': evaluation_data.get('body_type', ''),
            'Rangi': evaluation_data.get('color', ''),
            'Holati': evaluation_data.get('condition', ''),
            "Qo'shimcha narsalari": ', '.join(evaluation_data.get('features', [])) if evaluation_data.get('features') else '',
            'Oldingi egalari soni': str(evaluation_data.get('owners_count', '')),
            'Yurgan masofasi': str(evaluation_data.get('mileage', '')),
            'Kuchlanishi': evaluation_data.get('transmission', ''),
            'Baholash vaqti': f"{evaluation_data.get('month', '')}-{evaluation_data.get('eval_year', '')}"
        }
        
        predicted_price = evaluation_data.get('predicted_price', '')
        price_range = evaluation_data.get('price_range', '')
        
        # Generate PDF
        pdf_bytes = create_report_auto(property_details, str(predicted_price), price_range)
        
        # Return PDF as response
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="car_evaluation_report.pdf"'
        return response
        
    except Exception as e:
        print(f"Error generating car PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 


# ========== MARKETPLACE API ENDPOINTS ==========

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_marketplace_listing(request):
    """Create a marketplace listing for an asset"""
    try:
        print("create_marketplace_listing called")
        print(f"Request method: {request.method}")
        print(f"Request headers: {dict(request.headers)}")
        print(f"User authenticated: {request.user.is_authenticated}")
        print(f"User: {request.user}")
        print(f"Request data: {request.data}")
        
        if not request.user.is_authenticated:
            print("ERROR: User is not authenticated!")
            return Response({
                'error': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        asset_id = request.data.get('asset_id')
        print(f"Looking for asset with ID: {asset_id}")
        
        asset = get_object_or_404(Asset, id=asset_id, portfolio__user=request.user)
        print(f"Found asset: {asset.name} for user: {request.user.username}")
        
        # Check if asset is already listed
        if hasattr(asset, 'marketplace_listing') and asset.marketplace_listing.is_active:
            print("Asset is already listed")
            return Response({
                'error': 'Этот актив уже выставлен на продажу'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create or update marketplace listing
        listing_data = {
            'asset': asset,
            'seller': request.user,
            'listing_price': request.data.get('listing_price', asset.current_value),
            'description': request.data.get('description', ''),
            'contact_phone': request.data.get('contact_phone', request.user.phone),
            'contact_email': request.data.get('contact_email', request.user.email),
            'is_active': True
        }
        
        print(f"Creating listing with data: {listing_data}")
        
        if hasattr(asset, 'marketplace_listing'):
            # Update existing listing
            listing = asset.marketplace_listing
            for key, value in listing_data.items():
                if key not in ['asset', 'seller']:  # Don't update these fields
                    setattr(listing, key, value)
            listing.save()
            print("Updated existing listing")
        else:
            # Create new listing
            listing = MarketplaceListing.objects.create(**listing_data)
            print(f"Created new listing with ID: {listing.id}")
        
        return Response({
            'message': 'Актив успешно выставлен на продажу',
            'listing_id': listing.id
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        print(f"Error in create_marketplace_listing: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'error': f'Ошибка при создании объявления: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_marketplace_listings(request):
    """Get all active marketplace listings with filtering"""
    try:
        print("get_marketplace_listings called")
        print(f"User authenticated: {request.user.is_authenticated}")
        print(f"Query params: {request.query_params}")
        
        # Get query parameters
        asset_type = request.query_params.get('asset_type')
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        
        # Start with active listings
        print("Querying MarketplaceListing objects...")
        listings = MarketplaceListing.objects.filter(is_active=True).select_related(
            'asset', 'asset__portfolio', 'seller'
        )
        print(f"Found {listings.count()} active listings")
        
        # Apply filters
        if asset_type:
            listings = listings.filter(asset__asset_type=asset_type)
            print(f"After asset_type filter: {listings.count()}")
        
        if min_price:
            try:
                listings = listings.filter(listing_price__gte=float(min_price))
                print(f"After min_price filter: {listings.count()}")
            except ValueError:
                print(f"Invalid min_price: {min_price}")
                pass
                
        if max_price:
            try:
                listings = listings.filter(listing_price__lte=float(max_price))
                print(f"After max_price filter: {listings.count()}")
            except ValueError:
                print(f"Invalid max_price: {max_price}")
                pass
        
        # Serialize the listings
        print("Serializing listings...")
        listings_data = []
        for listing in listings:
            print(f"Processing listing {listing.id}")
            asset = listing.asset
            
            # Parse asset details safely
            asset_details = {}
            if asset.description:
                try:
                    asset_details = json.loads(asset.description)
                    print(f"Parsed asset details: {type(asset_details)}")
                except Exception as e:
                    print(f"Error parsing asset details: {e}")
                    pass
            
            listing_data = {
                'id': listing.id,
                'asset': {
                    'id': asset.id,
                    'name': asset.name,
                    'asset_type': asset.asset_type,
                    'address': asset.address,
                    'image_url': asset.image_url,
                    'details': asset_details
                },
                'seller': {
                    'username': listing.seller.username,
                    'email': listing.contact_email or listing.seller.email,
                    'phone': listing.contact_phone or listing.seller.phone
                },
                'listing_price': float(listing.listing_price),
                'formatted_price': f"${float(listing.listing_price):,.0f}",
                'description': listing.description,
                'listed_at': listing.listed_at.isoformat(),
                'is_own_listing': request.user.is_authenticated and listing.seller == request.user
            }
            listings_data.append(listing_data)
            print(f"Added listing {listing.id} to response")
        
        print(f"Returning {len(listings_data)} listings")
        return Response(listings_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"Error in get_marketplace_listings: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'error': f'Ошибка при получении объявлений: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_marketplace_listing(request, listing_id):
    """Remove/deactivate a marketplace listing"""
    try:
        from .models import MarketplaceListing
        
        listing = get_object_or_404(
            MarketplaceListing, 
            id=listing_id, 
            seller=request.user,
            is_active=True
        )
        
        listing.is_active = False
        listing.save()
        
        return Response({
            'message': 'Объявление успешно снято с продажи'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Ошибка при снятии объявления: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_marketplace_listings(request):
    """Get current user's marketplace listings"""
    try:
        from .models import MarketplaceListing
        
        listings = MarketplaceListing.objects.filter(
            seller=request.user
        ).select_related('asset').order_by('-listed_at')
        
        listings_data = []
        for listing in listings:
            asset = listing.asset
            listing_data = {
                'id': listing.id,
                'asset': {
                    'id': asset.id,
                    'name': asset.name,
                    'asset_type': asset.asset_type,
                    'address': asset.address
                },
                'listing_price': float(listing.listing_price),
                'formatted_price': f"${float(listing.listing_price):,.0f}",
                'is_active': listing.is_active,
                'listed_at': listing.listed_at.isoformat()
            }
            listings_data.append(listing_data)
        
        return Response(listings_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Ошибка при получении ваших объявлений: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 