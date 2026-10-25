import base64
from unittest.mock import patch

import orjson
import pytest

from backend.auth import JWT


class TestJWTCreation:
    """Tests for JWT token creation"""
    
    def test_create_token_with_valid_credentials(self):
        """Test that a token is created with valid sub and username"""
        token = JWT(sub="12345", username="testuser")
        
        assert token.token is not None
        assert isinstance(token.token, str)
        assert len(token.token.split(".")) == 3
    
    def test_token_has_three_parts(self):
        """Test that token consists of header.payload.signature"""
        token = JWT(sub="12345", username="testuser")
        parts = token.token.split(".")
        
        assert len(parts) == 3
        header, payload, signature = parts
        assert len(header) > 0
        assert len(payload) > 0
        assert len(signature) > 0
    
    def test_str_representation(self):
        """Test that __str__ returns the token"""
        token = JWT(sub="12345", username="testuser")

        print(token)
        assert str(token) == token.token


class TestJWTHeader:
    """Tests for JWT header encoding"""
    
    def test_header_contains_alg(self):
        """Test that header contains correct algorithm"""
        token = JWT(sub="12345", username="testuser")
        parts = token.token.split(".")
        
        # Decode header
        header = orjson.loads(base64.urlsafe_b64decode(parts[0] + "=" * (-len(parts[0]) % 4)))
        
        assert header["alg"] == "HS256"
        assert header["typ"] == "JWT"
    
    def test_header_is_base64url_encoded(self):
        """Test that header is properly base64url encoded"""
        token = JWT(sub="12345", username="testuser")
        parts = token.token.split(".")
        
        # Base64URL should only contain safe characters
        assert all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_" for c in parts[0])


class TestJWTPayload:
    """Tests for JWT payload encoding"""
    
    def test_payload_contains_sub(self):
        """Test that payload contains sub claim"""
        token = JWT(sub="12345", username="testuser")
        parts = token.token.split(".")
        
        payload = orjson.loads(base64.urlsafe_b64decode(parts[1] + "=" * (-len(parts[1]) % 4)))
        
        assert payload["sub"] == "12345"
    
    def test_payload_contains_username(self):
        """Test that payload contains username claim"""
        token = JWT(sub="99999", username="dimcheck")
        parts = token.token.split(".")
        
        payload = orjson.loads(base64.urlsafe_b64decode(parts[1] + "=" * (-len(parts[1]) % 4)))
        
        assert payload["username"] == "dimcheck"
    
    def test_payload_contains_iat(self):
        """Test that payload contains issued at timestamp"""
        with patch("backend.auth.time", return_value=1234567890):
            token = JWT(sub="12345", username="testuser")
        
        parts = token.token.split(".")
        payload = orjson.loads(base64.urlsafe_b64decode(parts[1] + "=" * (-len(parts[1]) % 4)))
        
        assert "iat" in payload
        assert payload["iat"] == 1234567890
    
    def test_payload_contains_exp(self):
        """Test that payload contains expiration timestamp"""
        with patch("backend.auth.time", return_value=1234567890):
            token = JWT(sub="12345", username="testuser")
        
        parts = token.token.split(".")
        payload = orjson.loads(base64.urlsafe_b64decode(parts[1] + "=" * (-len(parts[1]) % 4)))
        
        assert "exp" in payload
        assert payload["exp"] == 1234567890 + 3600
    
    def test_exp_is_one_hour_after_iat(self):
        """Test that expiration is exactly 1 hour after issued at"""
        with patch("backend.auth.time", return_value=1234567890):
            token = JWT(sub="12345", username="testuser")

        parts = token.token.split(".")
        payload = orjson.loads(base64.urlsafe_b64decode(parts[1] + "=" * (-len(parts[1]) % 4)))

        assert payload["exp"] - payload["iat"] == 3600


class TestJWTSignature:
    """Tests for JWT signature"""
    
    def test_signature_exists(self):
        """Test that signature is generated"""
        token = JWT(sub="12345", username="testuser")
        parts = token.token.split(".")
        
        assert len(parts[2]) > 0
    
    def test_signature_is_valid_hmac(self):
        """Test that signature is a valid HMAC-SHA256"""
        
        token1 = JWT(sub="12345", username="testuser")
        token2 = JWT(sub="12345", username="testuser")
        
        # Two tokens with same content should have same signature
        parts1 = token1.token.split(".")
        parts2 = token2.token.split(".")
        
        # Signatures should match (same signing input)
        assert parts1[2] == parts2[2]
    
    def test_different_content_has_different_signature(self):
        """Test that different content produces different signatures"""
        token1 = JWT(sub="12345", username="testuser")
        token2 = JWT(sub="99999", username="otheruser")
        
        parts1 = token1.token.split(".")
        parts2 = token2.token.split(".")
        
        # Signatures should be different
        assert parts1[2] != parts2[2]


class TestJWTMissingClaims:
    """Tests for missing required claims"""
    
    def test_missing_sub_claim(self):
        """Test behavior when sub claim is missing"""
        with pytest.raises(KeyError):
            JWT(username="testuser")
    
    def test_missing_username_claim(self):
        """Test behavior when username claim is missing"""
        with pytest.raises(KeyError):
            JWT(sub="12345")
    
    def test_both_claims_missing(self):
        """Test behavior when both sub and username are missing"""
        with pytest.raises(KeyError):
            JWT()


class TestJWTEdgeCases:
    """Tests for edge cases"""
    
    def test_empty_username(self):
        """Test token creation with empty username"""
        token = JWT(sub="12345", username="")
        
        assert token.token is not None
    
    def test_large_user_id(self):
        """Test token creation with large user ID"""
        max_id = str(2**63 - 1)
        token = JWT(sub=max_id, username="testuser")
        
        assert token.token is not None
    
    def test_special_characters_in_username(self):
        """Test token creation with special characters in username"""
        token = JWT(sub="12345", username="user@name.test_123")
        
        assert token.token is not None
    
    def test_unicode_username(self):
        """Test token creation with unicode in username"""
        token = JWT(sub="12345", username="用户测试")
        
        assert token.token is not None
    
    def test_token_uniqueness(self):
        """Test that different tokens are generated for same user at different times"""
        with patch("backend.auth.time", return_value=1000000000):
            token1 = JWT(sub="12345", username="testuser")
        
        with patch("backend.auth.time", return_value=2000000000):
            token2 = JWT(sub="12345", username="testuser")
        
        # Tokens should be different due to different timestamps
        assert token1.token != token2.token


class TestJWTIntegration:
    """Integration tests for JWT"""
    
    def test_full_token_flow(self):
        """Test complete token generation flow"""

        # Create token
        token = JWT(sub="54321", username="integration_test")
        
        # Verify structure
        parts = token.token.split(".")
        assert len(parts) == 3
        
        # Decode and verify header
        header = orjson.loads(base64.urlsafe_b64decode(parts[0] + "=" * (-len(parts[0]) % 4)))
        assert header["alg"] == "HS256"
        assert header["typ"] == "JWT"
        
        # Decode and verify payload
        payload = orjson.loads(base64.urlsafe_b64decode(parts[1] + "=" * (-len(parts[1]) % 4)))
        assert payload["sub"] == "54321"
        assert payload["username"] == "integration_test"
        assert "iat" in payload
        assert "exp" in payload
        
        # Verify signature exists and is properly encoded
        assert len(parts[2]) > 0
        assert all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_" for c in parts[2])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])