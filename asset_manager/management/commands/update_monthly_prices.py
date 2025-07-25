from django.core.management.base import BaseCommand
from django.utils import timezone
from asset_manager.utils import update_monthly_prices
from asset_manager.models import Asset

class Command(BaseCommand):
    help = 'Update monthly prices for all assets using ML models'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )
        parser.add_argument(
            '--asset-id',
            type=int,
            help='Update specific asset by ID',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(
                f'Starting monthly price update at {timezone.now()}'
            )
        )

        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )

        try:
            if options['asset_id']:
                # Update specific asset
                asset = Asset.objects.get(id=options['asset_id'])
                self.stdout.write(f'Updating asset: {asset.name}')
                
                if not options['dry_run']:
                    # Update single asset (we'll create a helper function for this)
                    from asset_manager.utils import update_single_asset_price
                    update_single_asset_price(asset)
                    
                self.stdout.write(
                    self.style.SUCCESS(f'Updated asset: {asset.name}')
                )
            else:
                # Update all assets
                asset_count = Asset.objects.count()
                self.stdout.write(f'Updating {asset_count} assets...')
                
                if not options['dry_run']:
                    update_monthly_prices()
                    
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully updated {asset_count} assets')
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error updating prices: {str(e)}')
            )
            raise

        self.stdout.write(
            self.style.SUCCESS(
                f'Monthly price update completed at {timezone.now()}'
            )
        ) 