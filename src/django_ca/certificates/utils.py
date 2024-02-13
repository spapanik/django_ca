from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.rsa import (
    RSAPrivateKey,
    generate_private_key,
)
from cryptography.x509.oid import NameOID
from pyutilkit.date_utils import now

from django.conf import settings


def _get_key_object(private_key: str) -> RSAPrivateKey:
    key_object = serialization.load_pem_private_key(private_key.encode(), password=None)
    if isinstance(key_object, RSAPrivateKey):
        return key_object
    msg = "Only RSA private keys are allowed"
    raise TypeError(msg)


def generate_rsa_key() -> str:
    return (
        generate_private_key(
            public_exponent=settings.RSA_PUBLIC_EXPONENT, key_size=settings.RSA_KEY_SIZE
        )
        .private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        .decode()
    )


def generate_csr(
    country: str,
    province: str,
    locality: str,
    organisation: str,
    common_name: str,
    email_address: str,
    alternative_names: list[str],
    private_key: str,
) -> str:
    key_object = _get_key_object(private_key)
    return (
        x509.CertificateSigningRequestBuilder()
        .subject_name(
            x509.Name(
                [
                    x509.NameAttribute(NameOID.COUNTRY_NAME, country),
                    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, province),
                    x509.NameAttribute(NameOID.LOCALITY_NAME, locality),
                    x509.NameAttribute(NameOID.ORGANIZATION_NAME, organisation),
                    x509.NameAttribute(NameOID.COMMON_NAME, common_name),
                    x509.NameAttribute(NameOID.EMAIL_ADDRESS, email_address),
                ]
            )
        )
        .add_extension(
            x509.SubjectAlternativeName(
                [
                    x509.DNSName(alternative_name)
                    for alternative_name in alternative_names
                ]
            ),
            critical=False,
        )
        .sign(key_object, algorithm=hashes.SHA256())
        .public_bytes(serialization.Encoding.PEM)
        .decode()
    )


def generate_self_signed_certificate(
    country: str,
    province: str,
    locality: str,
    organisation: str,
    common_name: str,
    email_address: str,
    private_key: str,
) -> str:
    key_object = _get_key_object(private_key)
    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, country),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, province),
            x509.NameAttribute(NameOID.LOCALITY_NAME, locality),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, organisation),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
            x509.NameAttribute(NameOID.EMAIL_ADDRESS, email_address),
        ]
    )
    start = now()
    return (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key_object.public_key())
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .serial_number(x509.random_serial_number())
        .not_valid_before(start)
        .not_valid_after(start + settings.CA_VALIDITY_PERIOD)
        .sign(key_object, algorithm=hashes.SHA256())
        .public_bytes(serialization.Encoding.PEM)
        .decode()
    )


def sign_csr(csr_cert: str, ca_cert: str, private_ca_key: str) -> str:
    key_object = _get_key_object(private_ca_key)
    csr_object = x509.load_pem_x509_csr(csr_cert.encode())
    ca_cert_object = x509.load_pem_x509_certificate(ca_cert.encode())
    start = now()
    return (
        x509.CertificateBuilder()
        .subject_name(csr_object.subject)
        .issuer_name(ca_cert_object.subject)
        .public_key(csr_object.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(start)
        .not_valid_after(start + settings.SERVER_VALIDITY_PERIOD)
        .add_extension(
            x509.SubjectAlternativeName(
                x509.DNSName(alternative_name)
                for alternative_name in csr_object.extensions.get_extension_for_class(
                    x509.SubjectAlternativeName
                ).value.get_values_for_type(x509.DNSName)
            ),
            critical=False,
        )
        .sign(key_object, algorithm=hashes.SHA256())
        .public_bytes(serialization.Encoding.PEM)
        .decode()
    )
