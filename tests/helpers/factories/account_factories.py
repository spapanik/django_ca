from factorio import factories, fields

from django_ca.accounts.models import Organisation, User


class OrganisationFactory(factories.Factory[Organisation]):
    country = fields.StringField()
    province = fields.StringField()
    locality = fields.StringField()
    name = fields.StringField()
    email = fields.StringField()
    ca_rights = fields.BooleanField(truth_probability=5)


class UserFactory(factories.Factory[User]):
    password = fields.StringField()
    last_login = None
    is_superuser = fields.BooleanField()
    is_staff = fields.BooleanField()
    is_active = fields.BooleanField()
    date_joined = fields.DateTimeField()
    created_at = fields.DateTimeField()
    updated_at = fields.DateTimeField()
    email = fields.StringField()
    is_ca = fields.BooleanField()
    default_organisation_id = fields.FactoryField(OrganisationFactory)
