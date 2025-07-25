import pandas as pd
import joblib
import os
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.conf import settings
from .models import Asset, AssetValueHistory

class PriceEstimator:
    """Utility class for estimating asset prices using ML models"""
    
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_path = os.path.join(self.base_dir, 'data')
        self._load_models()
    
    def _load_models(self):
        """Load ML models and supporting data"""
        try:
            # Load apartment model
            self.apartment_model1 = joblib.load(os.path.join(self.data_path, 'GBM_MADEL_WITHOUT_DISTANCE.pkl'))
            self.apartment_model2 = joblib.load(os.path.join(self.data_path, 'model2.pkl'))
            
            # Load car model
            self.car_model = joblib.load(os.path.join(self.data_path, 'CHEVROLET_DAEWOO_RAVON_LGBM_41.pkl'))
            
            # Load supporting data
            self.x_columns = pd.read_csv(os.path.join(self.data_path, 'xcolumns.csv'))
            self.uybor_cols = pd.read_csv(os.path.join(self.data_path, 'uybor_columns.csv'))
            self.mahalla_tuman = pd.read_csv(os.path.join(self.data_path, 'mahalla_tuman_codes.csv'))
            self.unique_mahalla_olx = pd.read_csv(os.path.join(self.data_path, 'unique_mahalla_olx.csv'))
            
            # Car-specific data
            self.brand_car_column = pd.read_csv(os.path.join(self.data_path, 'Brand_and_car_column.csv'))
            self.chevrolet_columns = pd.read_csv(os.path.join(self.data_path, 'Chevrolet_DAEWOO_RAVON_columns.csv'))
            
        except Exception as e:
            print(f"Error loading models: {e}")
            raise
    
    def estimate_apartment_price(self, asset_data, target_month=None, target_year=None):
        """Estimate apartment price for a specific month/year with realistic temporal variations"""
        try:
            # Use current month/year if not specified
            if target_month is None:
                target_month = datetime.now().month
            if target_year is None:
                target_year = datetime.now().year
            
            # Get base price using ML model
            base_price = self._get_base_apartment_price(asset_data)
            if base_price is None:
                return None
            
            # Apply temporal adjustments for apartments
            adjusted_price = self._apply_apartment_temporal_adjustments(
                base_price, asset_data, target_month, target_year
            )
            
            return max(0, adjusted_price)  # Ensure non-negative price
            
        except Exception as e:
            print(f"Error estimating apartment price: {e}")
            return None
    
    def _get_base_apartment_price(self, asset_data):
        """Get base apartment price using ML model"""
        try:
            # Get feature columns (skip index column)
            feature_columns = [col for col in self.x_columns.columns if not col.startswith('Unnamed') and col != '']
            feature_dict = {col: 0 for col in feature_columns}
            
            # Fill basic features
            feature_dict["totalArea"] = asset_data.get("area", 0)
            feature_dict["numberOfRooms"] = asset_data.get("rooms", 0)
            feature_dict["floor"] = asset_data.get("floor", 0)
            feature_dict["floorOfHouse"] = asset_data.get("total_floors", 0)
            feature_dict["furnished"] = 1 if asset_data.get("mebel") == 'Ha' else 0
            feature_dict["handle"] = 1 if asset_data.get("kelishsa") == 'Ha' else 0
            
            # Handle amenities
            amenities = asset_data.get("atrofda", [])
            for k, v in {
                "Maktab": "shkola", "Supermarket": "supermarket", 
                "Do'kon": "magazini", "Park": "park"
            }.items():
                feature_dict[v] = 1 if k in amenities else 0
            
            # Handle appliances
            appliances = asset_data.get("uyda", [])
            for k, v in {
                "Televizor": "tv_wm_ac_fridge", "Internet": "telefon_internet"
            }.items():
                feature_dict[v] = 1 if k in appliances else 0
            
            # Handle categorical features
            value_mappings = {
                "owner": {
                    "Mulkdor": "Mulkdor", "Tashkilot": "Tashkilot", "Boshqa": "Boshqa"
                },
                "planirovka": {
                    "Oddiy": "Oddiy", "Hosila": "Hosila", "Mustahkam": "Mustahkam"
                },
                "renovation": {
                    "Yaxshi": "Yaxshi", "O'rtacha": "O'rtacha", "Yomon": "Yomon"
                },
                "sanuzel": {
                    "Birgalikda": "Birgalikda", "Alohida": "Alohida"
                },
                "bino_turi": {
                    "Ikkinchi bozor": "Ikkinchi bozor", "Birlamchi bozor": "Birlamchi bozor"
                },
                "qurilish_turi": {
                    "Panel": "Panel", "G'isht": "G'isht", "Monolit": "Monolit"
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
                val = asset_data.get(field)
                if val and field in value_mappings:
                    mapped_val = value_mappings[field].get(val, val)
                    feature_dict[f"{prefix}{mapped_val}"] = 1
            
            # Handle location
            district = asset_data.get("district")
            mahalla = asset_data.get("mahalla")
            if district and mahalla:
                feature_dict[f"district_{district}"] = 1
                feature_dict[f"mahalla_{mahalla}"] = 1
            
            # Create DataFrame and predict
            feature_df = pd.DataFrame([feature_dict])
            feature_df = feature_df.reindex(columns=feature_columns, fill_value=0)
            
            # Use model1 for prediction
            prediction = self.apartment_model1.predict(feature_df)[0]
            return prediction
            
        except Exception as e:
            print(f"Error getting base apartment price: {e}")
            return None
    
    def _apply_apartment_temporal_adjustments(self, base_price, asset_data, target_month, target_year):
        """Apply realistic temporal price adjustments for apartments"""
        import random
        import math
        
        # Set seed based on asset data for consistent results
        area = asset_data.get("area", 0)
        rooms = asset_data.get("rooms", 0)
        floor = asset_data.get("floor", 0)
        seed = hash(f"{area}_{rooms}_{floor}_{asset_data.get('district', '')}_{asset_data.get('mahalla', '')}")
        random.seed(seed)
        
        current_date = datetime.now()
        target_date = datetime(target_year, target_month, 1)
        
        # Calculate months difference from current date
        months_diff = (current_date.year - target_year) * 12 + (current_date.month - target_month)
        
        # Real estate appreciation/depreciation (apartments generally appreciate)
        # Typical real estate appreciation: 3-8% per year
        annual_appreciation = 0.06  # 6% per year
        monthly_appreciation = annual_appreciation / 12
        
        # Apply appreciation for past months (prices were lower in the past)
        if months_diff > 0:
            appreciation_factor = (1 - monthly_appreciation) ** months_diff
            adjusted_price = base_price * appreciation_factor
        else:
            # For future months, continue appreciation
            appreciation_factor = (1 + monthly_appreciation) ** abs(months_diff)
            adjusted_price = base_price * appreciation_factor
        
        # Add seasonal variation (real estate is more active in spring/summer)
        seasonal_multiplier = 1.0
        if target_month in [3, 4, 5]:  # Spring
            seasonal_multiplier = 1.05
        elif target_month in [6, 7, 8]:  # Summer
            seasonal_multiplier = 1.08
        elif target_month in [9, 10]:  # Fall
            seasonal_multiplier = 1.02
        elif target_month in [11, 12, 1, 2]:  # Winter
            seasonal_multiplier = 0.96
        
        adjusted_price *= seasonal_multiplier
        
        # Add small random variation (±3%) for realism
        variation = random.uniform(-0.03, 0.03)
        adjusted_price *= (1 + variation)
        
        # Add market trend simulation
        # Simulate economic cycles affecting real estate
        cycle_factor = math.cos((target_year - 2020) * 0.3 + target_month * 0.05) * 0.08
        adjusted_price *= (1 + cycle_factor)
        
        return adjusted_price
    
    def estimate_car_price(self, asset_data, target_month=None, target_year=None):
        """Estimate car price for a specific month/year with realistic temporal variations"""
        try:
            # Use current month/year if not specified
            if target_month is None:
                target_month = datetime.now().month
            if target_year is None:
                target_year = datetime.now().year
            
            # Get base price using ML model (without temporal features)
            base_price = self._get_base_car_price(asset_data)
            if base_price is None:
                return None
            
            # Apply temporal adjustments to create realistic price variations
            adjusted_price = self._apply_temporal_adjustments(
                base_price, asset_data, target_month, target_year
            )
            
            return max(0, adjusted_price)  # Ensure non-negative price
            
        except Exception as e:
            print(f"Error estimating car price: {e}")
            return None
    
    def _get_base_car_price(self, asset_data):
        """Get base car price using ML model"""
        try:
            # Get feature columns for car model
            feature_columns = [col for col in self.chevrolet_columns.columns if not col.startswith('Unnamed') and col != '']
            feature_dict = {col: 0 for col in feature_columns}
            
            # Fill basic features
            feature_dict["release_year"] = asset_data.get("year", 2020)
            feature_dict["mileage"] = asset_data.get("mileage", 0)
            feature_dict["engine_volume"] = float(asset_data.get("Объем двигателя", "1.8").replace(" л", ""))
            
            # Handle categorical features with proper mapping
            categorical_mappings = {
                "fuel_type": {
                    "Benzin": "fuel_type_Gasoline",
                    "Gaz/Benzin": "fuel_type_Gas",
                    "Diesel": "fuel_type_Diesel",
                    "Elektr": "fuel_type_Electric"
                },
                "transmission": {
                    "Mexanik": "transmission_Manual",
                    "Avtomat": "transmission_Automatic"
                },
                "condition": {
                    "A'lo": "car_condition_Excellent",
                    "Yaxshi": "car_condition_Good",
                    "O'rtacha": "car_condition_Average",
                    "Yomon": "car_condition_Needs_Repair"
                },
                "ownership": {
                    "Xususiy": "item_type_Private",
                    "Biznes": "item_type_Business"
                }
            }
            
            # Apply mappings
            fuel_type = asset_data.get("Топливо", "Benzin")
            if fuel_type in categorical_mappings["fuel_type"]:
                feature_dict[categorical_mappings["fuel_type"][fuel_type]] = 1
            
            transmission = asset_data.get("Коробка передач", "Mexanik")
            if transmission in categorical_mappings["transmission"]:
                feature_dict[categorical_mappings["transmission"][transmission]] = 1
            
            condition = asset_data.get("Состояние", "Yaxshi")
            if condition in categorical_mappings["condition"]:
                feature_dict[categorical_mappings["condition"][condition]] = 1
            
            ownership = asset_data.get("Тип собственности", "Xususiy")
            if ownership in categorical_mappings["ownership"]:
                feature_dict[categorical_mappings["ownership"][ownership]] = 1
            
            # Owner count
            owners = asset_data.get("Владельцев", "1")
            if owners == "1":
                feature_dict["owners_count_1"] = 1
            elif owners == "2":
                feature_dict["owners_count_2"] = 1
            elif owners == "3":
                feature_dict["owners_count_3"] = 1
            elif owners == "4":
                feature_dict["owners_count_4"] = 1
            
            # Create DataFrame and predict
            feature_df = pd.DataFrame([feature_dict])
            feature_df = feature_df.reindex(columns=feature_columns, fill_value=0)
            
            # Use car model for prediction
            prediction = self.car_model.predict(feature_df)[0]
            return prediction
            
        except Exception as e:
            print(f"Error getting base car price: {e}")
            return None
    
    def _apply_temporal_adjustments(self, base_price, asset_data, target_month, target_year):
        """Apply realistic temporal price adjustments"""
        import random
        import math
        
        # Set seed based on asset data for consistent results
        car_year = asset_data.get("year", 2020)
        mileage = asset_data.get("mileage", 0)
        seed = hash(f"{car_year}_{mileage}_{asset_data.get('brand', '')}_{asset_data.get('model', '')}")
        random.seed(seed)
        
        current_date = datetime.now()
        target_date = datetime(target_year, target_month, 1)
        
        # Calculate months difference from current date
        months_diff = (current_date.year - target_year) * 12 + (current_date.month - target_month)
        
        # Depreciation factor: cars lose value over time
        # Typical car depreciation: 15-20% per year
        annual_depreciation = 0.18  # 18% per year
        monthly_depreciation = annual_depreciation / 12
        
        # Apply depreciation for past months
        if months_diff > 0:
            depreciation_factor = (1 - monthly_depreciation) ** months_diff
            adjusted_price = base_price * depreciation_factor
        else:
            # For future months, slight appreciation due to inflation
            appreciation_factor = (1 + 0.05/12) ** abs(months_diff)  # 5% annual inflation
            adjusted_price = base_price * appreciation_factor
        
        # Add seasonal variation (cars are more expensive in spring/summer)
        seasonal_multiplier = 1.0
        if target_month in [3, 4, 5, 6]:  # Spring/early summer
            seasonal_multiplier = 1.08
        elif target_month in [7, 8]:  # Summer
            seasonal_multiplier = 1.05
        elif target_month in [11, 12, 1, 2]:  # Winter
            seasonal_multiplier = 0.95
        
        adjusted_price *= seasonal_multiplier
        
        # Add small random variation (±5%) for realism
        variation = random.uniform(-0.05, 0.05)
        adjusted_price *= (1 + variation)
        
        # Add market trend simulation
        # Simulate market cycles: prices fluctuate over time
        cycle_factor = math.sin((target_year - 2020) * 0.5 + target_month * 0.1) * 0.1
        adjusted_price *= (1 + cycle_factor)
        
        return adjusted_price

def generate_historical_prices(asset):
    """Generate historical prices for the last 12 months"""
    estimator = PriceEstimator()
    
    # Parse asset details
    try:
        asset_details = json.loads(asset.description) if asset.description else {}
    except:
        asset_details = {}
    
    # Prepare asset data based on type
    if asset.asset_type == 'apartment':
        asset_data = {
            "area": float(asset.area) if asset.area else 0,
            "rooms": asset.rooms or 0,
            "floor": asset.floor or 0,
            "total_floors": asset.total_floors or 0,
            **asset_details
        }
    else:  # car
        asset_data = {
            "year": asset.year or datetime.now().year,
            "mileage": asset.mileage or 0,
            "brand": asset.brand or "",
            "model": asset.model or "",
            **asset_details
        }
    
    # Generate prices for last 12 months
    current_date = datetime.now().date()
    historical_entries = []
    
    for i in range(12, 0, -1):  # 12 months ago to 1 month ago
        target_date = current_date - relativedelta(months=i)
        target_month = target_date.month
        target_year = target_date.year
        
        if asset.asset_type == 'apartment':
            estimated_price = estimator.estimate_apartment_price(asset_data, target_month, target_year)
        else:
            estimated_price = estimator.estimate_car_price(asset_data, target_month, target_year)
        
        if estimated_price:
            # Check if entry already exists
            existing_entry = AssetValueHistory.objects.filter(
                asset=asset, 
                date=target_date
            ).first()
            
            if not existing_entry:
                historical_entries.append(AssetValueHistory(
                    asset=asset,
                    value=estimated_price,
                    date=target_date
                ))
    
    # Bulk create historical entries
    if historical_entries:
        AssetValueHistory.objects.bulk_create(historical_entries)
        print(f"Created {len(historical_entries)} historical price entries for {asset.name}")
    
    # Add current month entry
    current_month_entry = AssetValueHistory.objects.filter(
        asset=asset,
        date=current_date.replace(day=1)
    ).first()
    
    if not current_month_entry:
        AssetValueHistory.objects.create(
            asset=asset,
            value=asset.current_value,
            date=current_date.replace(day=1)
        )

def update_monthly_prices():
    """Update prices for all assets for the current month"""
    estimator = PriceEstimator()
    current_date = datetime.now().date()
    current_month_start = current_date.replace(day=1)
    
    # Get all assets
    assets = Asset.objects.all()
    
    for asset in assets:
        try:
            # Parse asset details
            asset_details = json.loads(asset.description) if asset.description else {}
            
            # Prepare asset data
            if asset.asset_type == 'apartment':
                asset_data = {
                    "area": float(asset.area) if asset.area else 0,
                    "rooms": asset.rooms or 0,
                    "floor": asset.floor or 0,
                    "total_floors": asset.total_floors or 0,
                    **asset_details
                }
                new_price = estimator.estimate_apartment_price(asset_data)
            else:  # car
                asset_data = {
                    "year": asset.year or datetime.now().year,
                    "mileage": asset.mileage or 0,
                    "brand": asset.brand or "",
                    "model": asset.model or "",
                    **asset_details
                }
                new_price = estimator.estimate_car_price(asset_data)
            
            if new_price:
                # Update asset current value
                asset.current_value = new_price
                asset.save()
                
                # Check if this month's entry already exists
                existing_entry = AssetValueHistory.objects.filter(
                    asset=asset,
                    date=current_month_start
                ).first()
                
                if existing_entry:
                    existing_entry.value = new_price
                    existing_entry.save()
                else:
                    AssetValueHistory.objects.create(
                        asset=asset,
                        value=new_price,
                        date=current_month_start
                    )
                
                print(f"Updated price for {asset.name}: ${new_price}")
        
        except Exception as e:
            print(f"Error updating price for {asset.name}: {e}")

def get_price_change_percentage(asset, days=30):
    """Calculate price change percentage over specified days"""
    try:
        current_date = datetime.now().date()
        past_date = current_date - timedelta(days=days)
        
        # Get current price
        current_price = float(asset.current_value)
        
        # Get price from specified days ago
        past_entry = AssetValueHistory.objects.filter(
            asset=asset,
            date__lte=past_date
        ).order_by('-date').first()
        
        if past_entry:
            past_price = float(past_entry.value)
            if past_price > 0:
                change_percentage = ((current_price - past_price) / past_price) * 100
                return round(change_percentage, 2)
        
        return 0.0
    except Exception as e:
        print(f"Error calculating price change: {e}")
        return 0.0

def update_single_asset_price(asset):
    """Update price for a single asset"""
    estimator = PriceEstimator()
    current_date = datetime.now().date()
    current_month_start = current_date.replace(day=1)
    
    try:
        # Parse asset details
        asset_details = json.loads(asset.description) if asset.description else {}
        
        # Prepare asset data
        if asset.asset_type == 'apartment':
            asset_data = {
                "area": float(asset.area) if asset.area else 0,
                "rooms": asset.rooms or 0,
                "floor": asset.floor or 0,
                "total_floors": asset.total_floors or 0,
                **asset_details
            }
            new_price = estimator.estimate_apartment_price(asset_data)
        else:  # car
            asset_data = {
                "year": asset.year or datetime.now().year,
                "mileage": asset.mileage or 0,
                "brand": asset.brand or "",
                "model": asset.model or "",
                **asset_details
            }
            new_price = estimator.estimate_car_price(asset_data)
        
        if new_price:
            # Update asset current value
            asset.current_value = new_price
            asset.save()
            
            # Check if this month's entry already exists
            existing_entry = AssetValueHistory.objects.filter(
                asset=asset,
                date=current_month_start
            ).first()
            
            if existing_entry:
                existing_entry.value = new_price
                existing_entry.save()
            else:
                AssetValueHistory.objects.create(
                    asset=asset,
                    value=new_price,
                    date=current_month_start
                )
            
            print(f"Updated price for {asset.name}: ${new_price}")
            return new_price
    
    except Exception as e:
        print(f"Error updating price for {asset.name}: {e}")
        return None 