from AccessControl.SecurityInfo import ClassSecurityInformation
from ftw.upgrade import ProgressLogger
from opengever.base.model import create_session
from opengever.contact.models import Address
from opengever.contact.models import MailAddress
from opengever.contact.models import Organization
from opengever.contact.models import OrgRole
from opengever.contact.models import Person
from opengever.contact.models import PhoneNumber
from opengever.contact.models import URL
from Products.CMFPlone.utils import safe_unicode
from sqlalchemy.orm import aliased
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import join
from sqlalchemy.sql.expression import table
from urlparse import urlparse
from zope.sqlalchemy.datamanager import mark_changed
import logging


logger = logging.getLogger('opengever.contact')
logger.setLevel(logging.INFO)


class ObjectSyncerProgressLogger(ProgressLogger):
    """Provide a custom progress-logger that can log iterables without
    a predefined length.
    """

    security = ClassSecurityInformation()

    def __init__(self, message, iterable, logger=None, timeout=5):
        self.logger = logger or logging.getLogger('opengever.contact')
        self.message = message
        self.iterable = iterable

        self.timeout = timeout
        self._timestamp = None
        self._counter = 0

    security.declarePrivate('__call__')
    def __call__(self):
        self._counter += 1
        if not self.should_be_logged():
            return

        self.logger.info('%s: %s' % (self._counter, self.message))


class ObjectSyncer(object):

    # to define by subclass
    mapper = None
    fixed_values = {}
    attributes = {}
    unique_key = None
    primary_key = None

    def __init__(self, source_session, query):
        """
        """
        self.db_session = create_session()
        self.source_session = source_session

        self.query = query

    def __call__(self):
        logger.info('Start migrating {}'.format(self.mapper.__tablename__))

        existing = self.get_existing_mapping()
        result = self.source_session.execute(self.query)
        to_insert, to_update = self.preparing_values(result, existing)

        self.db_session.bulk_insert_mappings(
            self.mapper, to_insert, return_defaults=True)
        logger.info('{} new {} added'.format(
            len(to_insert), self.mapper.__tablename__))

        self.db_session.bulk_update_mappings(self.mapper, to_update)
        logger.info('{} {} updated'.format(
            len(to_insert), self.mapper.__tablename__))

        if to_insert or to_update:
            mark_changed(self.db_session)

    def get_identifier(self, row):
        return getattr(row, self.unique_key)

    def preparing_values(self, result, existing):
        to_insert = []
        to_update = []

        iterable = ObjectSyncerProgressLogger(
            "Preparing values {}".format(self.mapper.__tablename__), result)

        for row in iterable:
            data = self.fixed_values.copy()
            for key, source_key in self.attributes.items():
                if callable(source_key):
                    value = source_key(row)
                else:
                    value = getattr(row, source_key)

                if isinstance(value, str):
                    value = safe_unicode(value)

                data[key] = value

            if self.is_existing(row, existing):
                to_update.append(
                    self.finalize_update_data(data, row, existing))
            else:
                to_insert.append(self.finalize_insert_data(data, row))

        return to_insert, to_update

    def finalize_update_data(self, data, row, existing):
        data[self.primary_key] = existing[self.get_identifier(row)]
        return data

    def finalize_insert_data(self, data, row):
        return data

    def is_existing(self, row, existing):
        return self.get_identifier(row) in existing


class OrganizationSyncer(ObjectSyncer):

    mapper = Organization
    fixed_values = {'contact_type': 'organization'}
    attributes = {'name': 'name',
                  'former_contact_id': 'former_contact_id',
                  'is_active': lambda row: bool(getattr(row, 'is_active'))}

    unique_key = 'former_contact_id'
    primary_key = 'contact_id'

    def get_existing_mapping(self):
        contact_table = table(
            "contacts",
            column('id'),
            column('former_contact_id'))
        stmt = select([contact_table.c.former_contact_id, contact_table.c.id])
        return {key: value for (key, value) in self.db_session.execute(stmt)}


class PersonSyncer(ObjectSyncer):

    mapper = Person
    fixed_values = {'contact_type': 'person'}
    attributes = {'salutation': 'salutation',
                  'academic_title': 'title',
                  'firstname': 'firstname',
                  'lastname': 'lastname',
                  'former_contact_id': 'former_contact_id',
                  'is_active': lambda row: bool(getattr(row, 'is_active'))}

    unique_key = 'former_contact_id'
    primary_key = 'contact_id'

    def get_existing_mapping(self):
        contact_table = table(
            "contacts",
            column('id'),
            column('former_contact_id'))
        stmt = select([contact_table.c.former_contact_id, contact_table.c.id])
        return {key: value for (key, value) in self.db_session.execute(stmt)}


class ContactAdditionsSyncer(ObjectSyncer):

    _contact_mapping = None

    def get_identifier(self, row):
        return u'{}:{}'.format(safe_unicode(row.label), row.former_contact_id)

    def get_contact_mapping(self):
        if not self._contact_mapping:
            contact_table = table(
                "contacts",
                column('id'),
                column('former_contact_id'))
            stmt = select([contact_table.c.former_contact_id, contact_table.c.id])
            self._contact_mapping = {key: value for (key, value)
                                     in self.db_session.execute(stmt)}

        return self._contact_mapping

    def finalize_insert_data(self, data, row):
        data['contact_id'] = self.get_contact_mapping()[row.former_contact_id]
        return data


class MailSyncer(ContactAdditionsSyncer):

    mapper = MailAddress
    attributes = {'label': 'label', 'address': 'address'}
    primary_key = 'mailaddress_id'
    _contact_mapping = None

    def get_existing_mapping(self):
        mail_table = table(
            "mail_addresses", column('id'), column('label'), column('contact_id'))

        contact_table = table(
            "contacts",
            column('id'), column('former_contact_id'))

        stmt = select([
            mail_table.c.id, mail_table.c.label,
            mail_table.c.contact_id, contact_table.c.former_contact_id])
        stmt = stmt.select_from(
            join(mail_table, contact_table,
                 mail_table.c.contact_id == contact_table.c.id))

        return {self.get_identifier(row): row.id
                for row in self.db_session.execute(stmt)}


def save_url(url):
    if not urlparse(url).scheme:
        return u'http://{}'.format(safe_unicode(url))

    return url


class UrlSyncer(ContactAdditionsSyncer):

    mapper = URL
    attributes = {'label': 'label',
                  'url': lambda row: save_url(getattr(row, 'url'))}
    primary_key = 'url_id'

    def get_existing_mapping(self):
        url_table = table(
            "urls", column('id'), column('label'), column('contact_id'))

        contact_table = table(
            "contacts",
            column('id'), column('former_contact_id'))

        stmt = select([
            url_table.c.id, url_table.c.label, url_table.c.contact_id,
            contact_table.c.former_contact_id])
        stmt = stmt.select_from(
            join(url_table, contact_table,
                 url_table.c.contact_id == contact_table.c.id))

        return {self.get_identifier(row): row.id
                for row in self.db_session.execute(stmt)}


class PhoneNumberSyncer(ContactAdditionsSyncer):

    mapper = PhoneNumber
    attributes = {'label': 'label',
                  'phone_number': 'phone_number'}
    primary_key = 'phone_number_id'

    def get_existing_mapping(self):
        phone_table = table(
            "phonenumbers",
            column('id'),
            column('label'),
            column('contact_id'))

        contact_table = table(
            "contacts",
            column('id'), column('former_contact_id'))

        stmt = select([
            phone_table.c.id,
            phone_table.c.label,
            phone_table.c.contact_id,
            contact_table.c.former_contact_id])

        stmt = stmt.select_from(
            join(phone_table, contact_table,
                 phone_table.c.contact_id == contact_table.c.id))

        return {self.get_identifier(row): row.id
                for row in self.db_session.execute(stmt)}


class AddressSyncer(ContactAdditionsSyncer):

    mapper = Address
    attributes = {'label': 'label',
                  'street': 'street',
                  'zip_code': 'zip_code',
                  'city': 'city',
                  'country': 'country'}
    primary_key = 'address_id'

    def get_existing_mapping(self):
        address_table = table(
            "addresses", column('id'), column('label'), column('contact_id'))

        contact_table = table(
            "contacts",
            column('id'), column('former_contact_id'))

        stmt = select([
            address_table.c.id, address_table.c.label, address_table.c.contact_id,
            contact_table.c.former_contact_id])
        stmt = stmt.select_from(
            join(address_table, contact_table,
                 address_table.c.contact_id == contact_table.c.id))

        return {self.get_identifier(row): row.id
                for row in self.db_session.execute(stmt)}


class OrgRoleSyncer(ContactAdditionsSyncer):

    mapper = OrgRole
    attributes = {'function': 'function'}
    primary_key = 'org_role_id'

    def get_identifier(self, row):
        return u'{}:{}'.format(row.organization_id, row.person_id)

    def get_existing_mapping(self):
        org_role_table = table("org_roles",
                               column('id'),
                               column('organization_id'),
                               column('person_id'),
                               column('function'))

        contact_table = table(
            "contacts",
            column('id'),
            column('former_contact_id'))

        org_contact = aliased(contact_table, alias='org_contact')
        person_contact = aliased(contact_table, alias='person_contact')

        query = self.db_session.query(org_role_table, org_contact, person_contact)
        query = query.join(org_contact,
                           org_role_table.c.organization_id == org_contact.c.id)
        query = query.join(person_contact,
                           org_role_table.c.person_id == person_contact.c.id)

        mapping = {}

        for row in query:
            key = u'{}:{}'.format(row[5], row[7])
            mapping[key] = row[0]

        return mapping

    def finalize_insert_data(self, data, row):
        data['organization_id'] = self.get_contact_mapping()[row.organization_id]
        data['person_id'] = self.get_contact_mapping()[row.person_id]
        return data

    def finalize_update_data(self, data, row, existing):
        data = super(OrgRoleSyncer, self).finalize_update_data(data, row, existing)
        data['organization_id'] = self.get_contact_mapping()[row.organization_id]
        data['person_id'] = self.get_contact_mapping()[row.person_id]
        return data
