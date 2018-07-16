# -*- coding: utf-8 -*-

"""Main module."""

import os
import requests
import textwrap

from dotenv import load_dotenv
from activecampaign_takehome import schemas


THIS_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    def __init__(self):
        self.configure()
        self.keys = ['API_KEY', 'ACCOUNT', 'DOMAIN', 'API_OUTPUT']

    def configure(self):
        env_path = os.path.join(THIS_DIR, '.env')
        if not os.path.exists(env_path):
            raise Exception("Missing .env file in activecampaign code directory {}".format(THIS_DIR))
        load_dotenv(dotenv_path=env_path)
        self.API_KEY = os.getenv("AC_API_KEY")
        self.ACCOUNT = os.getenv("AC_ACCOUNT")
        self.DOMAIN = os.getenv("AC_DOMAIN")
        self.API_OUTPUT = os.getenv("AC_API_OUTPUT") or 'json'

    def __repr__(self):
        return "\n".join("{}: {}".format(k, getattr(self, k)) for k in self.keys)


class ConfigurationError(Exception):
    pass


class Api:
    base_path = '/admin/api.php'
    accepted_api_outputs = ['json']

    def __init__(self, config):
        self.api_key = config.API_KEY
        if not self.api_key:
            raise ConfigurationError("Unsupported API_KEY value: {}.".format(self.api_output))
        self.api_output = config.API_OUTPUT
        if self.api_output not in self.accepted_api_outputs:
            raise ConfigurationError("Unsupported API_OUTPUT format value: {}.".format(self.api_output))
        if not config.ACCOUNT:
            raise ConfigurationError("Unsupported ACCOUNT value: {}.".format(config.ACCOUNT))
        if not config.DOMAIN:
            raise ConfigurationError("Unsupported DOMAIN value: {}.".format(config.ACCOUNT))
        self.base_url = 'https://{}.{}'.format(config.ACCOUNT, config.DOMAIN)
        self.url = self.base_url + self.base_path

    def parse_response(self, resp):
        if self.api_output == 'json':
            return resp.json()
        else:
            raise Exception("Cannot parse data in specified format: {}".format(self.api_output))

    def _prepare_params(self, api_action, params):
        """
        Ensure correct params have been added
        """
        if params is None:
            params = {}
        params.update({
            'api_action': api_action,
            'api_key': self.api_key,
            'api_output': self.api_output
        })
        return params

    def do_post(self, api_action, data, params=None, headers=None):
        url = self.url
        params = self._prepare_params(api_action, params)
        if headers is None:
            headers = {}
        # Ensure the correct content type
        headers.update({
            'content-type': 'application/x-www-form-urlencoded'
        })
        resp = requests.post(
            url, headers=headers, params=params, data=data
        )
        return self.parse_response(resp)

    def do_get(self, api_action, params):
        url = self.url
        params = self._prepare_params(api_action, params)
        resp = requests.get(url, params=params)
        return self.parse_response(resp)


class CampaignResource(Api):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schema = None

    def create(self, campaign_data):
        """
        Create a campaign

        Parameters
        ----------
        campaign_data : dict_like
            The information defining the campaign. It must consist of at least these values:

                - name
                - status
                - public
                - sdate
                - tracklinks
                - type_
                - list_id
                - message_id
        """
        api_action = "campaign_create"
        schema = schemas.CampaignSchema()
        post_data = schema.dump(campaign_data).data
        result = self.do_post(api_action=api_action, data=post_data)
        return result

    def get(self, ids=None, full=None, sort=None, sort_direction=None, page=None):
        """
        View campaign settings and information.

        TODO: Pagination
        """
        api_action = "campaign_list"

        # TBD: Do API field checking?
        full_values = [1, 0]
        sort_values = ['id', 'cdate']
        sort_direction = ['ASC', 'DESC']

        if ids is None:
            ids = "ALL"
        else:
            if isinstance(ids, list):
                ids = ','.join(ids)
        if not isinstance(ids, str):
            raise TypeError("Ids must be passed as lists of strings or as a strings")
        params = {
            'ids': ids,
        }
        if full is not None:
            params['full'] = full
        if sort is not None:
            params['sort'] = sort
        if sort_direction is not None:
            params['sort_direction'] = sort_direction
        return self.do_get(api_action=api_action, params=params)

    def send(self, email, campaign_id, message_id, _type, action):
        """
        Send a campaign email

        Parameters
        ----------
        email:
            Email address (of the contact) that will be receiving the email
        campaign_id:
            ID of the campaign you wish to send
        message_id:
            ID of the campaign's message you wish to send (used in Split campaigns if you have more than one message assigned to a campaign).
        _type:
            Type of the message you wish to send (can be used to send TEXT-only email even if campaign is set to use MIME).
        action:
             Example values:
                - 'send' = send a campaign to this contact and to append him to the recipients list
                - 'copy' = send a copy of a campaign to contact (campaign is not updated)
                - 'test' = send a test email to contact (campaign is not updated)
                - 'source' = simulate a campaign test to contact (campaign is not updated), return message source,
                - 'messagesize' = simulate a campaign test to contact (campaign is not updated), return message size
                - 'spamcheck' = simulate a campaign test to contact (campaign is not updated), return spam rate
                - 'preview' = same as preview
        """
        api_action = 'campaign_send'
        params = {
            'email': email,
            'campaignid': campaign_id,
            'messageid': message_id,
            'type': _type,
            'action': action
        }
        return self.do_get(api_action=api_action, params=params)

    def update_status(self, _id, status, sdate):
        """
        Update a campaign's status

        Parameters
        ----------
        _id:
            Campaign ID
        status:
            New status. Examples: 0 = draft, 1 = scheduled, 2 = sending, 3 = paused, 4 = stopped, 5 = completed
        sdate:
            New scheduled date (use format YYYY-MM-DD HH:MM:SS). This only applies to scheduled campaigns (status = 1), and "single" (regular/one-time)

        """
        api_action = "campaign_status"
        params = {
            'id': _id,
            'status': status,
            'sdate': '{:%Y-%m-%d %H:%M:%S}'.format(sdate)
        }
        return self.do_get(api_action=api_action, params=params)


class MessageResource(Api):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_many(self, ids=None, page=None):
        """
        View many email messages with a single API call.

        Note: The name of this endpoint differs from the other API calls.

        To Do: Handle pagination
        """
        api_action = 'message_list'
        if ids is None:
            ids = "all"
        else:
            if isinstance(ids, list):
                ids = ','.join(ids)
        if not isinstance(ids, str):
            raise TypeError("Ids must be passed as lists of strings or as a strings")
        params = {
            'ids': ids,
        }
        if page is not None:
            params['page'] = page
        print(params)
        result = self.do_get(api_action=api_action, params=params)
        return result

    def get_one(self, _id):
        """
        Note: The name of this endpoint differs from the other API calls.
        """
        api_action = 'message_view'
        params = {
            'id': _id,
        }
        result = self.do_get(api_action=api_action, params=params)
        return result

    def create(self, data):
        """
        Add a new email message to the system.

        Data:

            format: Examples: html, text, mime (both html and text)
            subject:    Subject of the email message.
            fromemail:  The "From" email address. Example: 'test@example.com'
            fromname:   The "From" name. Example: 'From Name'
            reply2: The "Reply To" email address. Example: 'reply2@example.com'
            priority:   Examples: 1 = high, 3 = medium/default, 5 = low
            charset:    Character set used. Example: 'utf-8'
            encoding:   Encoding used. Example: 'quoted-printable'

        Note: Only supports text messages currently

        """
        api_action = 'message_add'
        schema = schemas.TextMessageSchema()
        post_data = schema.dump(data).data
        result = self.do_post(api_action=api_action, data=post_data)
        return result

    def delete(self, _id):
        api_action = 'message_delete'
        params = {
            'id': _id,
        }
        result = self.do_get(api_action=api_action, params=params)
        return result


class ContactsResource(Api):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def create(self, contact_data):
        """
        Add a new contact to the system.
        """
        api_action = 'contact_add'
        schema = schemas.ContactSchema()
        post_data = schema.dump(contact_data).data
        result = self.do_post(api_action=api_action, data=post_data)
        return result

    def delete(self, _id):
        api_action = 'contact_delete'
        params = {
            'id': _id,
        }
        result = self.do_get(api_action=api_action, params=params)
        return result

    def get(self, ids=None, filters=None, full=None, sort=None, sort_direction=None, page=None):
        """
        View many (or all) contacts by including their ID's or various filters. This is useful for searching for contacts that match certain criteria - such as being part of a certain list, or having a specific custom field value. Contacts that are not subscribed to at least one list will not be viewable via this endpoint.

        To Do: Handle pagination
        """
        api_action = "contact_list"

        # TBD: Check values
        full_values = [1, 0]
        sort_values = ['id', 'datetime', 'first_name', 'last_name']
        sort_direction = ['ASC', 'DESC']

        if ids is None:
            ids = "ALL"
        else:
            if isinstance(ids, list):
                ids = ','.join(ids)
        if not isinstance(ids, str):
            raise TypeError("Ids must be passed as lists of strings or as a strings")
        params = {
            'ids': ids,
        }
        if filters is not None:
            params['filters'] = filters
        if full is not None:
            params['full'] = full
        if sort is not None:
            params['sort'] = sort
        if sort_direction is not None:
            params['sort_direction'] = sort_direction
        result = self.do_get(api_action=api_action, params=params)
        # TBD: Paginate
        return result


class ListResource(Api):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def create(self):
        raise NotImplementedError

    def get(self, ids=None, global_fields=None, full=None):
        """
        View multiple mailing lists in the system, including all information associated with each.
        """
        api_action = "list_list"

        # TBD: Do API field checking?
        full_values = [1, 0]

        if ids is None:
            ids = "all"
        else:
            if isinstance(ids, list):
                ids = ','.join(ids)
        if not isinstance(ids, str):
            raise TypeError("Ids must be passed as lists of strings or as a strings")
        params = {
            'ids': ids,
        }
        if full is not None:
            params['full'] = full
        if global_fields is not None:
            params['global_fields'] = sort
        result = self.do_get(api_action=api_action, params=params)
        # TBD: Paginate
        return result


class AddressResource(Api):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schema = None

    def create(self, address_data):
        """
        Add a new address to the system.
        """
        api_action = 'address_add'
        schema = schemas.AddressSchema()
        post_data = schema.dump(address_data).data
        result = self.do_post(api_action=api_action, data=post_data)
        return result

    def delete(self, _id):
        api_action = 'contact_delete'
        params = {
            'id': _id,
        }
        result = self.do_get(api_action=api_action, params=params)
        return result

    def get(self, ids=None, filters=None, full=None, sort=None, sort_direction=None, page=None):
        """
        View many (or all) contacts by including their ID's or various filters. This is useful for searching for contacts that match certain criteria - such as being part of a certain list, or having a specific custom field value. Contacts that are not subscribed to at least one list will not be viewable via this endpoint.

        To Do: Handle pagination
        """
        api_action = "contact_list"

        # TBD: Check values
        full_values = [1, 0]
        sort_values = ['id', 'datetime', 'first_name', 'last_name']
        sort_direction = ['ASC', 'DESC']

        if ids is None:
            ids = "ALL"
        else:
            if isinstance(ids, list):
                ids = ','.join(ids)
        if not isinstance(ids, str):
            raise TypeError("Ids must be passed as lists of strings or as a strings")
        params = {
            'ids': ids,
        }
        if filters is not None:
            params['filters'] = filters
        if full is not None:
            params['full'] = full
        if sort is not None:
            params['sort'] = sort
        if sort_direction is not None:
            params['sort_direction'] = sort_direction
        result = self.do_get(api_action=api_action, params=params)
        # TBD: Paginate
        return result

