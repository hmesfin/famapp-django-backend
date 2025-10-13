"""
Tests for EmailTemplateService
Ham Dog & TC's comprehensive test coverage for email template functionality
"""

import pytest
from unittest.mock import patch, Mock, MagicMock
from datetime import datetime, timedelta
from django.test import TestCase, override_settings
from django.utils import timezone
from django.template.exceptions import TemplateDoesNotExist
from django.core import mail

from apps.invitations.models import Invitation
from apps.invitations.services.email_template_service import (
    EmailTemplateService,
    EmailType,
    EmailPreview,
    EmailTemplate,
)
from apps.users.models import User


@pytest.mark.django_db
class TestEmailTemplateService(TestCase):
    """Test cases for EmailTemplateService"""

    def setUp(self):
        """Set up test data"""
        self.inviter = User.objects.create_user(
            email="inviter@example.com",
            first_name="John",
            last_name="Doe",
            password="testpass123",
        )

        self.invitation = Invitation.objects.create(
            email="invitee@example.com",
            first_name="Jane",
            last_name="Smith",
            role="member",
            organization_name="Test Organization",
            message="Welcome to our team!",
            invited_by=self.inviter,
            expires_at=timezone.now() + timedelta(days=7),
        )

    def test_render_invitation_email_success(self):
        """Test successful email rendering"""
        with patch(
            "apps.invitations.services.email_template_service.render_to_string"
        ) as mock_render:
            mock_render.side_effect = ["<html>Test HTML</html>", "Test Text"]

            subject, html, text = EmailTemplateService.render_invitation_email(
                self.invitation, EmailType.INVITATION
            )

            self.assertIn("Test Organization", subject)
            self.assertEqual(html, "<html>Test HTML</html>")
            self.assertEqual(text, "Test Text")

            # Verify templates were called with correct context
            self.assertEqual(mock_render.call_count, 2)

            # Check context contains required fields
            html_context = mock_render.call_args_list[0][0][1]
            self.assertEqual(html_context["invitation"], self.invitation)
            self.assertIn("invitation_url", html_context)
            self.assertIn("invited_by_name", html_context)
            self.assertEqual(html_context["organization_name"], "Test Organization")

    def test_render_invitation_email_preview_mode(self):
        """Test email rendering in preview mode"""
        with patch(
            "apps.invitations.services.email_template_service.render_to_string"
        ) as mock_render:
            mock_render.side_effect = ["<html>Preview HTML</html>", "Preview Text"]

            preview = EmailTemplateService.render_invitation_email(
                self.invitation, EmailType.INVITATION, preview_mode=True
            )

            self.assertIsInstance(preview, EmailPreview)
            self.assertIn("Test Organization", preview.subject)
            self.assertEqual(preview.html_content, "<html>Preview HTML</html>")
            self.assertEqual(preview.text_content, "Preview Text")
            self.assertIsInstance(preview.context, dict)
            self.assertIn("invitation", preview.context)
            self.assertIn("html", preview.template_paths)
            self.assertIn("text", preview.template_paths)

    def test_render_reminder_email_with_context(self):
        """Test reminder email rendering with specific context"""
        # Set expiration to 2 hours from now for urgency testing
        self.invitation.expires_at = timezone.now() + timedelta(hours=2, minutes=30)
        self.invitation.save()

        with patch(
            "apps.invitations.services.email_template_service.render_to_string"
        ) as mock_render:
            mock_render.side_effect = ["<html>Reminder HTML</html>", "Reminder Text"]

            subject, html, text = EmailTemplateService.render_invitation_email(
                self.invitation, EmailType.REMINDER
            )

            # Check urgent subject for 2-hour window - should be 2 hours due to int conversion
            self.assertIn("URGENT", subject)
            self.assertIn("2 hour", subject)

            # Verify reminder-specific context
            context = mock_render.call_args_list[0][0][1]
            self.assertTrue(context["is_reminder"])
            self.assertIn("hours_remaining", context)
            self.assertEqual(context["urgency_level"], "critical")

    def test_send_invitation_email_success(self):
        """Test successful email sending"""
        with patch.object(
            EmailTemplateService, "render_invitation_email"
        ) as mock_render:
            mock_render.return_value = (
                "Test Subject",
                "<html>Test HTML</html>",
                "Test Text",
            )

            with patch(
                "apps.invitations.services.email_template_service.EmailMultiAlternatives"
            ) as mock_email:
                mock_message = Mock()
                mock_email.return_value = mock_message

                result = EmailTemplateService.send_invitation_email(self.invitation)

                self.assertTrue(result)
                mock_message.send.assert_called_once_with(fail_silently=False)

                # Verify email was constructed correctly
                mock_email.assert_called_once()
                call_kwargs = mock_email.call_args[1]
                self.assertEqual(call_kwargs["subject"], "Test Subject")
                self.assertEqual(call_kwargs["body"], "Test Text")
                self.assertEqual(call_kwargs["to"], ["invitee@example.com"])
                self.assertEqual(call_kwargs["reply_to"], ["inviter@example.com"])

    def test_send_invitation_email_failure(self):
        """Test email sending failure handling"""
        with patch.object(
            EmailTemplateService, "render_invitation_email"
        ) as mock_render:
            mock_render.return_value = ("Subject", "HTML", "Text")

            with patch(
                "apps.invitations.services.email_template_service.EmailMultiAlternatives"
            ) as mock_email:
                mock_message = Mock()
                mock_message.send.side_effect = Exception("SMTP Error")
                mock_email.return_value = mock_message

                # Should raise exception by default
                with self.assertRaises(Exception):
                    EmailTemplateService.send_invitation_email(self.invitation)

                # Should return False with fail_silently=True
                result = EmailTemplateService.send_invitation_email(
                    self.invitation, fail_silently=True
                )
                self.assertFalse(result)

    def test_send_simple_reminder_success(self):
        """Test simple reminder email functionality"""
        # Set expiration to 5 hours and 30 minutes from now to ensure it rounds to 5 hours
        self.invitation.expires_at = timezone.now() + timedelta(hours=5, minutes=30)
        self.invitation.save()

        with patch(
            "apps.invitations.services.email_template_service.send_mail"
        ) as mock_send:
            result = EmailTemplateService.send_simple_reminder(self.invitation)

            self.assertTrue(result)
            mock_send.assert_called_once()

            # Check email content
            call_args = mock_send.call_args
            subject = call_args[1]["subject"]
            message = call_args[1]["message"]

            self.assertIn("5 hours", subject)
            self.assertIn("Jane", message)
            self.assertIn("Test Organization", message)
            self.assertIn("John Doe", message)

    def test_preview_email_content(self):
        """Test email preview functionality"""
        with patch(
            "apps.invitations.services.email_template_service.render_to_string"
        ) as mock_render:
            mock_render.side_effect = ["<html>Preview</html>", "Preview Text"]

            preview = EmailTemplateService.preview_email_content(self.invitation)

            self.assertIsInstance(preview, EmailPreview)
            self.assertIn("Test Organization", preview.subject)
            self.assertEqual(preview.html_content, "<html>Preview</html>")
            self.assertEqual(preview.text_content, "Preview Text")

    def test_get_available_templates(self):
        """Test template listing functionality"""
        templates = EmailTemplateService.get_available_templates()

        self.assertIn("invitation", templates)
        self.assertIn("reminder", templates)
        self.assertIn("welcome", templates)
        self.assertIn("expiry_notice", templates)

        # Check template structure
        invitation_template = templates["invitation"]
        self.assertIn("html_template", invitation_template)
        self.assertIn("text_template", invitation_template)
        self.assertIn("has_subject_template", invitation_template)

    def test_validate_templates_exist(self):
        """Test template existence validation"""
        with patch(
            "apps.invitations.services.email_template_service.get_template"
        ) as mock_get:
            # Mock successful template loading
            mock_get.return_value = Mock()

            results = EmailTemplateService.validate_templates_exist()

            self.assertIn("invitation", results)
            self.assertTrue(results["invitation"]["html_exists"])
            self.assertTrue(results["invitation"]["text_exists"])
            self.assertTrue(results["invitation"]["both_exist"])

    def test_validate_templates_missing(self):
        """Test handling of missing templates"""
        with patch(
            "apps.invitations.services.email_template_service.get_template"
        ) as mock_get:
            # Mock template not found
            mock_get.side_effect = TemplateDoesNotExist("template not found")

            results = EmailTemplateService.validate_templates_exist()

            for email_type in results.values():
                self.assertFalse(email_type["html_exists"])
                self.assertFalse(email_type["text_exists"])
                self.assertFalse(email_type["both_exist"])

    def test_validate_invitation_invalid(self):
        """Test invitation validation"""
        # Test with None invitation
        with self.assertRaises(ValueError):
            EmailTemplateService.render_invitation_email(None)

        # Test with invitation without email
        invalid_invitation = Invitation(email="")
        with self.assertRaises(ValueError):
            EmailTemplateService.render_invitation_email(invalid_invitation)

    def test_context_preparation_no_inviter(self):
        """Test context preparation when invitation has no inviter"""
        with patch(
            "apps.invitations.services.email_template_service.render_to_string"
        ) as mock_render:
            mock_render.side_effect = ["<html>Test</html>", "Test Text"]

            # Create a mock invitation object with invited_by set to None
            mock_invitation = Mock()
            mock_invitation.id = 123
            mock_invitation.email = "test@example.com"
            mock_invitation.invited_by = None
            mock_invitation.organization_name = "Test Org"
            mock_invitation.expires_at = timezone.now() + timedelta(days=7)
            mock_invitation.get_role_display.return_value = "Member"
            mock_invitation.first_name = "Test"
            mock_invitation.last_name = "User"

            EmailTemplateService.render_invitation_email(mock_invitation)

            context = mock_render.call_args_list[0][0][1]
            self.assertEqual(context["invited_by_name"], "")
            self.assertEqual(context["invited_by_email"], "")
            self.assertEqual(context["invited_by_first_name"], "your inviter")

    def test_context_preparation_inviter_no_name(self):
        """Test context preparation when inviter has no first/last name"""
        self.inviter.first_name = ""
        self.inviter.last_name = ""
        self.inviter.save()

        with patch(
            "apps.invitations.services.email_template_service.render_to_string"
        ) as mock_render:
            mock_render.side_effect = ["<html>Test</html>", "Test Text"]

            EmailTemplateService.render_invitation_email(self.invitation)

            context = mock_render.call_args_list[0][0][1]
            self.assertEqual(context["invited_by_name"], "inviter@example.com")
            self.assertEqual(context["invited_by_first_name"], "your inviter")

    @override_settings(
        FRONTEND_URL="https://example.com",
        SUPPORT_EMAIL="custom-support@example.com",
        SITE_NAME="Custom Site",
    )
    def test_context_with_custom_settings(self):
        """Test context preparation with custom Django settings"""
        with patch(
            "apps.invitations.services.email_template_service.render_to_string"
        ) as mock_render:
            mock_render.side_effect = ["<html>Test</html>", "Test Text"]

            EmailTemplateService.render_invitation_email(self.invitation)

            context = mock_render.call_args_list[0][0][1]
            self.assertIn("https://example.com", context["invitation_url"])
            self.assertEqual(context["support_email"], "custom-support@example.com")
            self.assertEqual(context["site_name"], "Custom Site")

    def test_urgency_level_calculation(self):
        """Test urgency level calculation for reminders"""
        # Test critical urgency (1 hour)
        self.invitation.expires_at = timezone.now() + timedelta(hours=1)
        self.invitation.save()

        with patch(
            "apps.invitations.services.email_template_service.render_to_string"
        ) as mock_render:
            mock_render.side_effect = ["<html>Test</html>", "Test Text"]

            EmailTemplateService.render_invitation_email(
                self.invitation, EmailType.REMINDER
            )
            context = mock_render.call_args_list[0][0][1]
            self.assertEqual(context["urgency_level"], "critical")

        # Test high urgency (6 hours)
        self.invitation.expires_at = timezone.now() + timedelta(hours=6)
        self.invitation.save()

        with patch(
            "apps.invitations.services.email_template_service.render_to_string"
        ) as mock_render:
            mock_render.side_effect = ["<html>Test</html>", "Test Text"]

            EmailTemplateService.render_invitation_email(
                self.invitation, EmailType.REMINDER
            )
            context = mock_render.call_args_list[0][0][1]
            self.assertEqual(context["urgency_level"], "high")

    def test_template_rendering_error(self):
        """Test template rendering error handling"""
        with patch(
            "apps.invitations.services.email_template_service.render_to_string"
        ) as mock_render:
            mock_render.side_effect = TemplateDoesNotExist("Template not found")

            with self.assertRaises(TemplateDoesNotExist):
                EmailTemplateService.render_invitation_email(self.invitation)

    def test_email_types_enum_coverage(self):
        """Test that all email types are properly supported"""
        supported_types = [
            EmailType.INVITATION,
            EmailType.REMINDER,
            EmailType.WELCOME,
            EmailType.EXPIRY_NOTICE,
        ]

        for email_type in supported_types:
            self.assertIn(email_type, EmailTemplateService.TEMPLATES)
            template_config = EmailTemplateService.TEMPLATES[email_type]
            self.assertIsInstance(template_config, EmailTemplate)
            self.assertTrue(template_config.html_template)
            self.assertTrue(template_config.text_template)

    def test_subject_generation_variations(self):
        """Test subject generation for different email types and conditions"""
        test_cases = [
            (EmailType.INVITATION, "You're invited to join Test Organization!"),
            (EmailType.WELCOME, "Welcome to Test Organization!"),
            (EmailType.EXPIRY_NOTICE, "Your Test Organization invitation has expired"),
        ]

        for email_type, expected_subject in test_cases:
            with patch(
                "apps.invitations.services.email_template_service.render_to_string"
            ) as mock_render:
                mock_render.side_effect = ["<html>Test</html>", "Test Text"]

                subject, _, _ = EmailTemplateService.render_invitation_email(
                    self.invitation, email_type
                )

                self.assertEqual(subject, expected_subject)
