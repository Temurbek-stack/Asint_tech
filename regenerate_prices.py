#!/usr/bin/env python
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeeval_project.settings')
django.setup()

from asset_manager.models import Asset, AssetValueHistory
from asset_manager.utils import generate_historical_prices

def regenerate_all_prices():
    """Regenerate historical prices for all assets"""
    print('🔄 Regenerating historical prices with realistic temporal variations...')
    
    assets = Asset.objects.all()
    print(f'Found {assets.count()} assets to process')
    
    for asset in assets:
        print(f'📊 Processing {asset.name}...')
        
        # Clear existing historical data
        old_count = AssetValueHistory.objects.filter(asset=asset).count()
        AssetValueHistory.objects.filter(asset=asset).delete()
        print(f'   ❌ Deleted {old_count} old price entries')
        
        # Regenerate with new system
        try:
            generate_historical_prices(asset)
            new_count = AssetValueHistory.objects.filter(asset=asset).count()
            print(f'   ✅ Generated {new_count} new price entries')
        except Exception as e:
            print(f'   ❌ Error: {e}')
    
    print('\n🎉 Done! All historical prices regenerated with realistic variations.')

if __name__ == "__main__":
    regenerate_all_prices() 