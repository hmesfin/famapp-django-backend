"""
Tests for Avatar Service
Testing the refactored avatar upload service
"""
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import default_storage
from rest_framework.exceptions import ValidationError
from apps.profiles.services.avatar_service import avatar_service
from apps.profiles.constants import MAX_AVATAR_SIZE, ALLOWED_IMAGE_TYPES


class AvatarServiceTestCase(TestCase):
    """Test cases for the AvatarService"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.service = avatar_service
        # Create a test image file
        self.valid_image = SimpleUploadedFile(
            name='test.jpg',
            content=b'fake image content',
            content_type='image/jpeg'
        )
        self.user_id = 123
    
    def test_validate_file_valid(self):
        """Test validation passes for valid file"""
        # Should not raise any exception
        try:
            self.service.validate_file(self.valid_image)
        except ValidationError:
            self.fail("validate_file raised ValidationError unexpectedly!")
    
    def test_validate_file_size_too_large(self):
        """Test validation fails for oversized file"""
        # Create a file larger than MAX_FILE_SIZE
        large_file = SimpleUploadedFile(
            name='large.jpg',
            content=b'x' * (MAX_AVATAR_SIZE + 1),
            content_type='image/jpeg'
        )
        
        with self.assertRaises(ValidationError) as context:
            self.service.validate_file(large_file)
        
        error = context.exception.detail
        self.assertIn('avatar', error)
        self.assertIn('5MB', str(error['avatar']))
    
    def test_validate_file_invalid_type(self):
        """Test validation fails for invalid file type"""
        invalid_file = SimpleUploadedFile(
            name='test.pdf',
            content=b'fake pdf content',
            content_type='application/pdf'
        )
        
        with self.assertRaises(ValidationError) as context:
            self.service.validate_file(invalid_file)
        
        error = context.exception.detail
        self.assertIn('avatar', error)
        self.assertIn('image', str(error['avatar']).lower())
    
    def test_validate_file_invalid_extension(self):
        """Test validation fails for invalid extension"""
        invalid_file = SimpleUploadedFile(
            name='test.exe',
            content=b'fake content',
            content_type='image/jpeg'  # Even with correct content type
        )
        
        with self.assertRaises(ValidationError) as context:
            self.service.validate_file(invalid_file)
        
        error = context.exception.detail
        self.assertIn('avatar', error)
        self.assertIn('extension', str(error['avatar']).lower())
    
    def test_generate_filename(self):
        """Test filename generation"""
        filename = self.service.generate_filename(self.user_id, self.valid_image)
        
        self.assertEqual(filename, 'avatars/user_123.jpg')
        
        # Test with different extension
        png_file = SimpleUploadedFile('test.png', b'', 'image/png')
        filename = self.service.generate_filename(456, png_file)
        self.assertEqual(filename, 'avatars/user_456.png')
    
    def test_delete_old_avatar_no_url(self):
        """Test delete_old_avatar with no URL"""
        # Should not raise any exception
        try:
            self.service.delete_old_avatar(None)
            self.service.delete_old_avatar('')
        except Exception as e:
            self.fail(f"delete_old_avatar raised {e} unexpectedly!")
    
    def test_delete_old_avatar_external_url(self):
        """Test delete_old_avatar ignores external URLs"""
        external_urls = [
            'https://example.com/avatar.jpg',
            'http://cdn.example.com/user.png',
            '/static/default-avatar.png'
        ]
        
        with patch.object(default_storage, 'delete') as mock_delete:
            for url in external_urls:
                self.service.delete_old_avatar(url)
            
            # Should not attempt to delete external URLs
            mock_delete.assert_not_called()
    
    @patch.object(default_storage, 'exists')
    @patch.object(default_storage, 'delete')
    def test_delete_old_avatar_managed_file(self, mock_delete, mock_exists):
        """Test delete_old_avatar deletes managed files"""
        mock_exists.return_value = True
        
        # Test with media URL
        self.service.delete_old_avatar('/media/avatars/user_123.jpg')
        mock_delete.assert_called_with('avatars/user_123.jpg')
        
        # Test with production URL
        mock_delete.reset_mock()
        self.service.delete_old_avatar('https://storage.googleapis.com/bucket/avatars/user_456.png')
        mock_delete.assert_called()
    
    @patch.object(default_storage, 'save')
    def test_save_avatar_success(self, mock_save):
        """Test successful avatar save"""
        mock_save.return_value = 'avatars/user_123.jpg'
        
        path, filename = self.service.save_avatar(self.valid_image, self.user_id)
        
        self.assertEqual(path, 'avatars/user_123.jpg')
        self.assertEqual(filename, 'avatars/user_123.jpg')
        mock_save.assert_called_once()
    
    @patch.object(default_storage, 'save')
    def test_save_avatar_failure(self, mock_save):
        """Test avatar save failure raises ValidationError"""
        mock_save.side_effect = Exception("Storage error")
        
        with self.assertRaises(ValidationError) as context:
            self.service.save_avatar(self.valid_image, self.user_id)
        
        error = context.exception.detail
        self.assertIn('avatar', error)
        self.assertIn('Failed to save', str(error['avatar']))
    
    def test_get_avatar_url_development(self):
        """Test URL generation in development"""
        mock_request = Mock()
        mock_request.build_absolute_uri.return_value = 'http://localhost:8000/media/avatars/user_123.jpg'
        
        with patch.object(default_storage, 'url', return_value='/media/avatars/user_123.jpg'):
            with self.settings(DEBUG=True):
                url = self.service.get_avatar_url('avatars/user_123.jpg', mock_request)
        
        self.assertEqual(url, 'http://localhost:8000/media/avatars/user_123.jpg')
        mock_request.build_absolute_uri.assert_called_once()
    
    def test_get_avatar_url_production(self):
        """Test URL generation in production"""
        with patch.object(default_storage, 'url', return_value='https://storage.googleapis.com/bucket/avatars/user_123.jpg'):
            with self.settings(DEBUG=False):
                url = self.service.get_avatar_url('avatars/user_123.jpg')
        
        self.assertEqual(url, 'https://storage.googleapis.com/bucket/avatars/user_123.jpg')
    
    @patch.object(avatar_service, 'validate_file')
    @patch.object(avatar_service, 'delete_old_avatar')
    @patch.object(avatar_service, 'save_avatar')
    @patch.object(avatar_service, 'get_avatar_url')
    def test_process_avatar_upload_complete_flow(self, mock_get_url, mock_save, mock_delete, mock_validate):
        """Test complete avatar upload process"""
        mock_save.return_value = ('avatars/user_123.jpg', 'avatars/user_123.jpg')
        mock_get_url.return_value = 'http://localhost:8000/media/avatars/user_123.jpg'
        
        result = self.service.process_avatar_upload(
            file=self.valid_image,
            user_id=self.user_id,
            old_avatar_url='http://localhost:8000/media/avatars/user_123_old.jpg',
            request=Mock()
        )
        
        # Verify all steps were called in order
        mock_validate.assert_called_once_with(self.valid_image)
        mock_delete.assert_called_once_with('http://localhost:8000/media/avatars/user_123_old.jpg')
        mock_save.assert_called_once_with(self.valid_image, self.user_id)
        mock_get_url.assert_called_once()
        
        self.assertEqual(result, 'http://localhost:8000/media/avatars/user_123.jpg')
    
    def test_process_avatar_upload_validation_fails(self):
        """Test process stops if validation fails"""
        invalid_file = SimpleUploadedFile(
            name='test.exe',
            content=b'malicious',
            content_type='application/exe'
        )
        
        with self.assertRaises(ValidationError):
            self.service.process_avatar_upload(
                file=invalid_file,
                user_id=self.user_id
            )