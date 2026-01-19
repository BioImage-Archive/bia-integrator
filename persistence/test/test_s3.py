import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from persistence.s3 import S3UploadError, upload_to_s3, UploadMode


@pytest.fixture
def mock_settings():
    """Mock settings instead of .env file"""
    with patch("persistence.s3.get_settings") as mock_get_settings:
        mock_settings = MagicMock()
        mock_settings.s3_bucket_name = "test-bucket"
        mock_settings.s3_endpoint_url = "https://test.endpoint.com"
        mock_settings.aws_request_checksum_calculation = "WHEN_REQUIRED"
        mock_settings.aws_response_checksum_validation = "WHEN_REQUIRED"
        mock_get_settings.return_value = mock_settings
        yield mock_settings


class TestRetryLogic:
    """Tests to check retries work; also verify that url is correct on success."""

    def test_succeeds_on_first_attempt(self, mock_settings):
        with patch("persistence.s3.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")

            result = upload_to_s3(
                UploadMode.COPY, 
                "/tmp/test.txt",
                "dst/test.txt"
            )

            assert mock_run.call_count == 1
            assert result == "https://test.endpoint.com/test-bucket/dst/test.txt"

    def test_succeeds_on_second_attempt(self, mock_settings):
        with patch("persistence.s3.subprocess.run") as mock_run:

            mock_run.side_effect = [
                MagicMock(returncode=1, stderr="Failed attempt 1"),
                MagicMock(returncode=0, stderr=""),
            ]

            result = upload_to_s3(
                UploadMode.COPY, 
                "/tmp/test.txt",
                "dst/test.txt"
            )

            assert mock_run.call_count == 2
            assert result == "https://test.endpoint.com/test-bucket/dst/test.txt"

    def test_succeeds_on_third_attempt(self, mock_settings):
        with patch("persistence.s3.subprocess.run") as mock_run:

            mock_run.side_effect = [
                MagicMock(returncode=1, stderr="Failed attempt 1"),
                MagicMock(returncode=1, stderr="Failed attempt 2"),
                MagicMock(returncode=0, stderr=""),
            ]

            result = upload_to_s3(
                UploadMode.COPY, 
                "/tmp/test.txt",
                "dst/test.txt"
            )

            assert mock_run.call_count == 3
            assert result == "https://test.endpoint.com/test-bucket/dst/test.txt"

    def test_fails_after_three_attempts(self, mock_settings):
        with patch("persistence.s3.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stderr="Permanent failure")

            with pytest.raises(S3UploadError):
                upload_to_s3(
                    UploadMode.COPY, 
                    "/tmp/test.txt",
                    "dst/test.txt",
                )

            assert mock_run.call_count == 3


class TestURIConstruction:
    """Test that returned URIs are correctly formatted"""

    def test_copy_file_uri_format(self, mock_settings):
        with patch("persistence.s3.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")

            result = upload_to_s3(
                UploadMode.COPY, 
                "/tmp/test.txt",
                "path/to/file.txt"
            )

            expected_uri = "https://test.endpoint.com/test-bucket/path/to/file.txt"
            assert result == expected_uri

    def test_sync_directory_uri_format(self, mock_settings):
        with patch("persistence.s3.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")

            result = upload_to_s3(
                UploadMode.SYNC, 
                "/tmp/testdir/",
                "path/to/dir"
            )

            expected_uri = "https://test.endpoint.com/test-bucket/path/to/dir"
            assert result == expected_uri

    def test_uri_with_different_endpoint(self, mock_settings):

        with patch("persistence.s3.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")

            result = upload_to_s3(
                UploadMode.COPY, 
                "/tmp/test.txt",
                "custom/path.txt", 
                endpoint_url="https://custom.s3.endpoint", 
                bucket_name="custom-bucket"
            )

            expected_uri = "https://custom.s3.endpoint/custom-bucket/custom/path.txt"
            assert result == expected_uri

    def test_dry_run_returns_correct_uri(self, mock_settings):
        """Dry run should return URI without calling subprocess"""
        with patch("persistence.s3.subprocess.run") as mock_run:
            result = upload_to_s3(
                UploadMode.COPY, 
                "/tmp/test.txt",
                "path/file.txt",
                dry_run=True
            )

            # subprocess should not have been called
            mock_run.assert_not_called()

            # But URI should still be correct
            expected_uri = "https://test.endpoint.com/test-bucket/path/file.txt"
            assert result == expected_uri


class TestPathHandling:
    """Test that paths are handled correctly, especially for sync operations"""

    def test_sync_adds_trailing_slash_to_path_object(self, mock_settings):
        with patch("persistence.s3.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")

            upload_to_s3(
                UploadMode.SYNC, 
                Path("/tmp/testdir"),
                "dst/dir"
            )

            # Get the command that was executed
            call_args = mock_run.call_args[0]
            cmd = call_args[0]

            # Should have trailing slash after the source path
            assert '"/tmp/testdir/"' in cmd

    def test_sync_adds_trailing_slash_to_string(self, mock_settings):
        with patch("persistence.s3.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")

            upload_to_s3(
                UploadMode.SYNC, 
                "/tmp/testdir",
                "dst/dir"
            )

            call_args = mock_run.call_args[0]
            cmd = call_args[0]

            assert '"/tmp/testdir/"' in cmd

    def test_sync_preserves_existing_trailing_slash(self, mock_settings):
        with patch("persistence.s3.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")

            upload_to_s3(
                UploadMode.SYNC, 
                "/tmp/testdir/",
                "dst/dir"
            )

            call_args = mock_run.call_args[0]
            cmd = call_args[0]

            # Should still have trailing slash, not double slash
            assert '"/tmp/testdir/"' in cmd
            assert "/tmp/testdir//" not in cmd

    def test_copy_does_not_add_trailing_slash(self, mock_settings):
        """upload_to_s3 with COPY mode should not modify file paths"""
        with patch("persistence.s3.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")

            upload_to_s3(
                UploadMode.COPY, 
                "/tmp/test.txt",
                "dst/test.txt"
            )

            call_args = mock_run.call_args[0]
            cmd = call_args[0]

            # File path should not have trailing slash
            assert '"/tmp/test.txt"' in cmd
            assert "/tmp/test.txt/" not in cmd

    def test_dst_suffix_in_s3_key(self, mock_settings):
        """Test that destination suffix is correctly incorporated into S3 key"""
        with patch("persistence.s3.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")

            upload_to_s3(
                UploadMode.COPY, 
                "/tmp/test.txt",
                "subfolder/nested/file.txt"
            )

            call_args = mock_run.call_args[0]
            cmd = call_args[0]

            # Should have the full S3 key
            assert "s3://test-bucket/subfolder/nested/file.txt" in cmd


class TestCommandConstruction:
    """Test that AWS CLI commands are correctly formed"""

    def test_copy_command_has_required_parts(self, mock_settings):
        with patch("persistence.s3.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")

            upload_to_s3(
                UploadMode.COPY, 
                "/tmp/test.txt",
                "dst/test.txt"
            )

            call_args = mock_run.call_args[0]
            cmd = call_args[0]

            # Check all required parts of the command
            assert "aws" in cmd
            assert "--region us-east-1" in cmd
            assert f"--endpoint-url {mock_settings.s3_endpoint_url}" in cmd
            assert "s3 cp" in cmd
            assert "/tmp/test.txt" in cmd
            assert f"s3://{mock_settings.s3_bucket_name}/dst/test.txt" in cmd
            assert "--acl public-read" in cmd

    def test_sync_command_has_required_parts(self, mock_settings):
        with patch("persistence.s3.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")

            upload_to_s3(
                UploadMode.SYNC, 
                "/tmp/testdir/",
                "dst/dir"
            )

            call_args = mock_run.call_args[0]
            cmd = call_args[0]

            # Check all required parts of the command
            assert "aws" in cmd
            assert "--region us-east-1" in cmd
            assert f"--endpoint-url {mock_settings.s3_endpoint_url}" in cmd
            assert "s3 sync" in cmd
            assert '"/tmp/testdir/"' in cmd
            assert f"s3://{mock_settings.s3_bucket_name}/dst/dir" in cmd
            assert "--acl public-read" in cmd
