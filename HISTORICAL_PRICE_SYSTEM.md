# Historical Price Tracking System

## Overview

This system provides comprehensive historical price tracking for real estate assets using machine learning models. It automatically generates price history for the last 12 months when assets are added and updates prices monthly.

## Features

### 1. **Automatic Historical Price Generation**
- When a user adds an asset via "dobavit aktiv", the system automatically generates price estimates for the last 12 months
- Uses the same ML models with different month/year inputs (t-1, t-2, ..., t-12)
- Creates `AssetValueHistory` entries for each month

### 2. **Beautiful Line Chart Visualization**
- Replaces the placeholder "История стоимости" frame with an interactive Chart.js line chart
- Shows price trends over the last 12 months
- Displays current value and 30-day percentage change
- Smooth animations and hover effects

### 3. **Monthly Automatic Updates**
- Django management command for automated monthly price updates
- Updates current asset values and adds new historical entries
- Calculates 30-day percentage changes for dashboard display

### 4. **Dynamic Dashboard Updates**
- "Изменение (30 д.)" card now shows real percentage changes
- Calculated from actual historical price data
- Updates automatically on the first day of each month

## Technical Implementation

### Backend Components

#### 1. **PriceEstimator Class** (`asset_manager/utils.py`)
```python
class PriceEstimator:
    def __init__(self):
        # Loads ML models and supporting data
        
    def estimate_apartment_price(self, asset_data, target_month=None, target_year=None):
        # Estimates apartment price for specific month/year
        
    def estimate_car_price(self, asset_data, target_month=None, target_year=None):
        # Estimates car price for specific month/year
```

#### 2. **Historical Price Functions**
- `generate_historical_prices(asset)`: Creates 12 months of price history
- `update_monthly_prices()`: Updates all assets for current month
- `update_single_asset_price(asset)`: Updates specific asset
- `get_price_change_percentage(asset, days=30)`: Calculates percentage change

#### 3. **API Endpoints**
- `GET /api/assets/{id}/price-history/`: Returns price history and current value
- Enhanced dashboard endpoint with real percentage calculations

#### 4. **Management Command**
```bash
python manage.py update_monthly_prices [--dry-run] [--asset-id ID]
```

### Frontend Components

#### 1. **Price History Chart** (`frontend/main.js`)
- `loadAssetPriceHistory(assetId)`: Fetches price history from API
- `renderPriceHistoryChart(assetId)`: Creates Chart.js visualization
- Integrated into `renderAssetDetail()` function

#### 2. **Chart Features**
- Gradient fill and smooth curves
- Interactive tooltips with formatted prices
- 30-day change indicator with color coding
- Responsive design for all screen sizes

## Usage

### For Users

1. **Adding Assets**: Historical prices are automatically generated when adding new assets
2. **Viewing History**: Click on any asset to see its price history chart
3. **Dashboard**: View portfolio performance with real 30-day changes

### For Administrators

1. **Manual Updates**: 
   ```bash
   python manage.py update_monthly_prices
   ```

2. **Dry Run Testing**:
   ```bash
   python manage.py update_monthly_prices --dry-run
   ```

3. **Single Asset Update**:
   ```bash
   python manage.py update_monthly_prices --asset-id 123
   ```

## Automated Scheduling

### Monthly Updates
Set up a cron job or Windows Task Scheduler to run the update command on the first day of each month:

**Linux/Mac (crontab)**:
```bash
0 0 1 * * /path/to/python /path/to/manage.py update_monthly_prices
```

**Windows Task Scheduler**:
- Trigger: Monthly on day 1
- Action: Start program
- Program: `python.exe`
- Arguments: `manage.py update_monthly_prices`
- Start in: Project directory

## Data Flow

1. **Asset Creation**:
   - User adds asset → ML model estimates current price
   - System generates 12 months of historical prices (t-1 to t-12)
   - Creates `AssetValueHistory` entries

2. **Monthly Updates**:
   - Scheduled command runs on 1st of month
   - ML model estimates new prices for all assets
   - Updates `Asset.current_value` and creates new history entries
   - Dashboard percentages automatically update

3. **Chart Display**:
   - Frontend requests price history via API
   - Chart.js renders beautiful line graph
   - Shows trends, current value, and 30-day change

## Database Schema

### AssetValueHistory Model
```python
class AssetValueHistory(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='value_history')
    value = models.DecimalField(max_digits=15, decimal_places=2)
    date = models.DateField()  # First day of month
    created_at = models.DateTimeField(auto_now_add=True)
```

## Performance Considerations

1. **Bulk Operations**: Uses `bulk_create()` for efficient database operations
2. **Caching**: Chart data is cached on frontend to reduce API calls
3. **Indexing**: Database indexes on `asset_id` and `date` fields for fast queries
4. **Error Handling**: Graceful fallbacks when ML models fail

## Error Handling

- ML model failures: Graceful fallback with placeholder data
- Missing data: Shows appropriate placeholder messages
- API errors: User-friendly error messages in charts
- Database errors: Logged for administrator review

## Security

- Authentication required for all price history endpoints
- User can only access their own asset data
- Management commands require server access
- Input validation for all ML model parameters

## Future Enhancements

1. **Real-time Updates**: WebSocket integration for live price updates
2. **Predictive Analytics**: Future price predictions using time series models
3. **Comparative Analysis**: Compare asset performance against market averages
4. **Export Features**: PDF reports with price history charts
5. **Alert System**: Notifications for significant price changes

## Troubleshooting

### Common Issues

1. **Chart Not Loading**: Check browser console for JavaScript errors
2. **No Historical Data**: Verify ML models are loaded correctly
3. **Percentage Calculations Wrong**: Check `AssetValueHistory` entries exist
4. **Management Command Fails**: Verify virtual environment and dependencies

### Debug Commands

```bash
# Test price estimation
python manage.py shell -c "from asset_manager.utils import PriceEstimator; pe = PriceEstimator()"

# Check asset history
python manage.py shell -c "from asset_manager.models import AssetValueHistory; print(AssetValueHistory.objects.count())"

# Dry run update
python manage.py update_monthly_prices --dry-run
```

## Configuration

### Settings
Add to `settings.py` if needed:
```python
# Historical price settings
HISTORICAL_PRICE_MONTHS = 12
PRICE_UPDATE_SCHEDULE = 'monthly'  # daily, weekly, monthly
```

This system provides a complete solution for tracking asset price history with beautiful visualizations and automated updates, enhancing the user experience with data-driven insights. 