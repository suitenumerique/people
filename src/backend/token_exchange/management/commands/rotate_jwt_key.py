"""Management command to rotate JWT signing keys for token exchange."""

import logging

from django.core.management.base import BaseCommand

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Management command to generate a new JWT signing key."""

    help = "Generate a new JWT signing key for token exchange"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--kid",
            type=str,
            required=True,
            help="Key ID for the new signing key (e.g., 'key-2024-12')",
        )
        parser.add_argument(
            "--set-current",
            action="store_true",
            help="Indicate that this should be set as the current signing key",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        kid = options["kid"]
        set_current = options["set_current"]

        self.stdout.write(
            self.style.WARNING(f"\nGenerating new RSA key pair with kid='{kid}'...\n")
        )

        # Generate RSA key pair (2048 bits, exponent 65537)
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend(),
        )

        # Serialize private key to PEM format
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode("utf-8")

        # Extract public key
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")

        # Display the keys
        self.stdout.write(self.style.SUCCESS("\n✓ Key pair generated successfully!\n"))

        self.stdout.write(
            self.style.WARNING("=== PUBLIC KEY (distribute to consumers) ===")
        )
        self.stdout.write(public_pem)

        self.stdout.write(self.style.WARNING("\n=== PRIVATE KEY (keep secret!) ==="))
        self.stdout.write(private_pem)

        # Display configuration instructions
        self.stdout.write(self.style.SUCCESS("\n=== CONFIGURATION INSTRUCTIONS ===\n"))

        self.stdout.write(
            "1. Add this key to TOKEN_EXCHANGE_JWT_SIGNING_KEYS in your settings or environment:\n"
        )

        # Escape the private key for JSON/env var
        private_pem_escaped = private_pem.replace("\n", "\\n")

        self.stdout.write(
            f'   TOKEN_EXCHANGE_JWT_SIGNING_KEYS={{"{kid}": "{private_pem_escaped}"}}\n'
        )

        self.stdout.write(
            "   Note: If you already have keys, add this to the existing dictionary:\n"
        )
        self.stdout.write(
            f'   {{"existing-kid": "...", "{kid}": "{private_pem_escaped}"}}\n'
        )

        if set_current:
            self.stdout.write(f"\n2. Set this as the current signing key:\n")
            self.stdout.write(f"   TOKEN_EXCHANGE_JWT_CURRENT_KID={kid}\n")
        else:
            self.stdout.write(f"\n2. To use this key for new tokens, set:\n")
            self.stdout.write(f"   TOKEN_EXCHANGE_JWT_CURRENT_KID={kid}\n")

        self.stdout.write(
            "\n3. IMPORTANT: Keep old keys in TOKEN_EXCHANGE_JWT_SIGNING_KEYS to validate existing tokens!\n"
        )

        self.stdout.write(
            "   Do NOT remove old keys immediately. They are needed to verify tokens signed with those keys.\n"
        )

        # Log the key generation
        logger.info("Generated new JWT key with kid=%s", kid)

        self.stdout.write(
            self.style.SUCCESS(f"\n✓ Key rotation process completed for kid='{kid}'\n")
        )
