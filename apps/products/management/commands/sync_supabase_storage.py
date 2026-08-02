import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.base import ContentFile
from apps.products.models import Product
from shambhu_pos.supabase_storage import SupabaseStorage

class Command(BaseCommand):
    help = "Uploads all local media files to Supabase Storage and ensures product image URLs are valid"

    def handle(self, *args, **options):
        storage = SupabaseStorage()
        media_root = settings.MEDIA_ROOT
        self.stdout.write(self.style.SUCCESS("Starting Supabase Media Sync..."))

        if not os.path.exists(media_root):
            self.stdout.write(self.style.WARNING(f"Media directory {media_root} does not exist."))
            return

        synced_count = 0
        for root, _, files in os.walk(media_root):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, media_root).replace('\\', '/')
                with open(abs_path, 'rb') as f:
                    content = ContentFile(f.read())
                    saved_name = storage._save(rel_path, content)
                    synced_count += 1
                    self.stdout.write(f" -> Uploaded: {rel_path} -> Supabase: {saved_name}")

        self.stdout.write(self.style.SUCCESS(f"Successfully synced {synced_count} media file(s) to Supabase Storage!"))
