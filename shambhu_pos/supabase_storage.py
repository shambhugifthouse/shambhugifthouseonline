import os
import mimetypes
import urllib.request
import urllib.parse
from django.core.files.storage import Storage
from django.conf import settings
from django.utils.deconstruct import deconstructible

@deconstructible
class SupabaseStorage(Storage):
    def __init__(self, **kwargs):
        self.project_ref = getattr(settings, 'SUPABASE_PROJECT_REF', 'caakvjsfxqrvlznfwfry')
        self.bucket_name = getattr(settings, 'SUPABASE_STORAGE_BUCKET', 'product-images')
        self.secret_key = getattr(settings, 'SUPABASE_SERVICE_ROLE_KEY', '') or os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
        self.base_url = f"https://{self.project_ref}.supabase.co/storage/v1/object/public/{self.bucket_name}/"
        self.upload_url = f"https://{self.project_ref}.supabase.co/storage/v1/object/{self.bucket_name}/"

    def _save(self, name, content):
        clean_name = str(name).replace('\\', '/').lstrip('/')
        safe_quoted_path = urllib.parse.quote(clean_name, safe='/')
        target_url = f"{self.upload_url}{safe_quoted_path}"
        
        # Guess MIME content type for proper image rendering in browser
        content_type, _ = mimetypes.guess_type(clean_name)
        if not content_type:
            ext = clean_name.lower()
            if ext.endswith(('.jpg', '.jpeg')):
                content_type = 'image/jpeg'
            elif ext.endswith('.png'):
                content_type = 'image/png'
            elif ext.endswith('.webp'):
                content_type = 'image/webp'
            else:
                content_type = 'application/octet-stream'

        # Read content bytes
        content.seek(0)
        file_bytes = content.read()
        
        headers = {
            'Authorization': f'Bearer {self.secret_key}',
            'apiKey': self.secret_key,
            'Content-Type': content_type,
            'x-upsert': 'true',
        }
        
        req = urllib.request.Request(
            target_url,
            data=file_bytes,
            headers=headers,
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                pass
        except Exception as e:
            # Fallback to PUT if POST fails
            try:
                req.method = 'PUT'
                with urllib.request.urlopen(req) as response:
                    pass
            except Exception as inner_e:
                print(f"Supabase Storage Upload Error for {clean_name}: {inner_e}")
                
        return clean_name

    def exists(self, name):
        return False

    def url(self, name):
        if not name:
            return ''
        clean_name = str(name).replace('\\', '/').lstrip('/')
        if clean_name.startswith(('http://', 'https://')):
            return clean_name
        safe_path = urllib.parse.quote(clean_name, safe='/')
        return f"{self.base_url}{safe_path}"
