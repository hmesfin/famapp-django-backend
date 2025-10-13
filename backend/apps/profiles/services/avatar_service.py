"""
Avatar Service for handling profile avatar operations
Following DRY principles and separation of concerns
"""
import os
from typing import Optional, Tuple
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings
from rest_framework.exceptions import ValidationError
from apps.profiles.constants import (
    MAX_AVATAR_SIZE,
    ALLOWED_IMAGE_TYPES,
    ALLOWED_IMAGE_EXTENSIONS,
    AVATAR_UPLOAD_PATH
)


class AvatarService:
    """
    Service class for handling avatar upload operations.
    Extracted from views to follow single responsibility principle.
    """
    
    # Use constants from centralized location
    MAX_FILE_SIZE = MAX_AVATAR_SIZE
    ALLOWED_CONTENT_TYPES = ALLOWED_IMAGE_TYPES
    ALLOWED_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS
    AVATAR_UPLOAD_PATH = AVATAR_UPLOAD_PATH
    
    def validate_file(self, file: UploadedFile) -> None:
        """
        Validate uploaded file for size and type.
        
        Args:
            file: The uploaded file to validate
            
        Raises:
            ValidationError: If file validation fails
        """
        # Validate file size
        if file.size > self.MAX_FILE_SIZE:
            raise ValidationError({
                'avatar': f'File size must be less than {self.MAX_FILE_SIZE // (1024 * 1024)}MB'
            })
        
        # Validate content type
        if file.content_type not in self.ALLOWED_CONTENT_TYPES:
            allowed_types = ', '.join([ct.split('/')[-1].upper() for ct in self.ALLOWED_CONTENT_TYPES])
            raise ValidationError({
                'avatar': f'File must be an image ({allowed_types})'
            })
        
        # Validate file extension
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            raise ValidationError({
                'avatar': f'Invalid file extension. Allowed: {", ".join(self.ALLOWED_EXTENSIONS)}'
            })
    
    def generate_filename(self, user_id: int, file: UploadedFile) -> str:
        """
        Generate a unique filename for the avatar.
        
        Args:
            user_id: The user's ID
            file: The uploaded file
            
        Returns:
            Generated filename with path
        """
        ext = os.path.splitext(file.name)[1].lower()
        filename = f'{self.AVATAR_UPLOAD_PATH}/user_{user_id}{ext}'
        return filename
    
    def delete_old_avatar(self, avatar_url: Optional[str]) -> None:
        """
        Delete the old avatar file if it exists.
        
        Args:
            avatar_url: URL of the old avatar
        """
        if not avatar_url:
            return
            
        # Check if it's our managed avatar (not external URL)
        if f'{self.AVATAR_UPLOAD_PATH}/user_' not in avatar_url:
            return
            
        try:
            # Extract path from URL
            if '/media/' in avatar_url:
                old_path = avatar_url.split('/media/')[-1]
            else:
                # For production URLs from GCP
                old_path = avatar_url.split('/')[-1]
                if self.AVATAR_UPLOAD_PATH not in old_path:
                    old_path = f'{self.AVATAR_UPLOAD_PATH}/{old_path}'
            
            if old_path and default_storage.exists(old_path):
                default_storage.delete(old_path)
        except Exception:
            # Silently fail - old avatar deletion is not critical
            pass
    
    def save_avatar(self, file: UploadedFile, user_id: int) -> Tuple[str, str]:
        """
        Save the avatar file and return the storage path and filename.
        
        Args:
            file: The uploaded file
            user_id: The user's ID
            
        Returns:
            Tuple of (storage_path, filename)
            
        Raises:
            ValidationError: If file save fails
        """
        try:
            filename = self.generate_filename(user_id, file)
            
            # Save the file using Django's storage backend
            path = default_storage.save(
                filename, 
                ContentFile(file.read())
            )
            
            return path, filename
            
        except Exception as e:
            raise ValidationError({
                'avatar': f'Failed to save avatar: {str(e)}'
            })
    
    def get_avatar_url(self, path: str, request=None) -> str:
        """
        Generate the URL for the avatar.
        
        Args:
            path: The storage path of the avatar
            request: Optional request object for building absolute URLs
            
        Returns:
            Full URL to the avatar
        """
        if settings.DEBUG and request:
            # In development, build full URL with request
            return request.build_absolute_uri(default_storage.url(path))
        else:
            # In production, storage backend provides full URL
            return default_storage.url(path)
    
    def process_avatar_upload(self, file: UploadedFile, user_id: int, 
                            old_avatar_url: Optional[str] = None,
                            request=None) -> str:
        """
        Complete avatar upload process: validate, delete old, save new, return URL.
        
        This is the main method that orchestrates the entire upload process.
        
        Args:
            file: The uploaded file
            user_id: The user's ID
            old_avatar_url: URL of existing avatar to delete
            request: Optional request for URL building
            
        Returns:
            URL of the newly uploaded avatar
            
        Raises:
            ValidationError: If any step fails
        """
        # Step 1: Validate the file
        self.validate_file(file)
        
        # Step 2: Delete old avatar if exists
        if old_avatar_url:
            self.delete_old_avatar(old_avatar_url)
        
        # Step 3: Save the new avatar
        path, _ = self.save_avatar(file, user_id)
        
        # Step 4: Generate and return URL
        avatar_url = self.get_avatar_url(path, request)
        
        return avatar_url


# Singleton instance
avatar_service = AvatarService()