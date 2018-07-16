#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `activecampaign_takehome` package."""

import os
import pytest
import requests
import json
import pdb
import datetime

import unittest
from unittest import mock

from click.testing import CliRunner

from activecampaign_takehome import activecampaign_takehome as act
from activecampaign_takehome import cli, schemas



THIS_DIR = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def list_contacts_data():
    fixtures_path = os.path.join(THIS_DIR, 'fixture_list_contacts.json')
    with open(fixtures_path, 'r') as f:
        fixtures_data = json.load(f)
        return fixtures_data


def test_configure():
    config = act.Config()
    assert config.DOMAIN == 'api-us1.com'
    assert config.API_OUTPUT == 'json'


def test_api_init():
    config = act.Config()
    config.ACCOUNT = 'test-account'
    config.DOMAIN = 'api-us1.com'
    api = act.Api(config)
    assert api.base_url == 'https://test-account.api-us1.com'


def test_contacts_init():
    config = act.Config()
    config.ACCOUNT = 'test-account'
    config.DOMAIN = 'api-us1.com'
    contacts_resource = act.ContactsResource(config)
    assert contacts_resource.base_url == 'https://test-account.api-us1.com'


def mocked_contacts_get(*args, **kwargs):
    """
    This method will be used by the mock to replace requests.get

    Fixtures are loaded from fixture_list_contacts.json
    """

    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    params = kwargs['params']
    if len(params.keys()) == 0:
        return MockResponse(
            "<?xml version='1.0' encoding='utf-8'?>\n<root><error>You are not authorized to access this file</error></root>", 200)
    elif params['api_action'] == 'contact_list':
        with open(os.path.join(THIS_DIR, 'fixture_list_contacts.json'), 'r') as f:
            fixtures_data = json.load(f)
        if 'ids' not in params:
            return MockResponse({
                'result_code': 0,
                'result_message': 'Failed: Nothing is returned',
                'result_output': 'json'}, 200)
        elif params['ids'] == 1:
            return MockResponse({
                'result_code': 0,
                'result_message': 'Failed: Nothing is returned',
                'result_output': 'json'}, 200)
        elif params['ids'] == 'ALL':
            return MockResponse(fixtures_data, 200)
        elif params['ids'] == '1':
            return MockResponse(fixtures_data, 200)

    elif params['api_action'] == 'contact_delete':
        if 'id' not in params:
            # Result even when 'id' is missing
            return MockResponse({'result_code': 1,
                 'result_message': 'Contact deleted',
                 'result_output': 'json'}, 200)
        elif params['id'] == '1':
            return MockResponse({'result_code': 1,
                 'result_message': 'Contact deleted',
                 'result_output': 'json'}, 200)
        elif params['id'] == 'a':  # Same result for an invalid id
            return MockResponse({'result_code': 1,
                 'result_message': 'Contact deleted',
                 'result_output': 'json'}, 200)

    return MockResponse(None, 200)


def mocked_contacts_post(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    params = kwargs['params']
    data = kwargs['data']
    if params['api_action'] == 'contact_add':
        if data.get('email'):
            fixtures_data = {
                'subscriber_id': 2,
                'sendlast_should': 0,
                'sendlast_did': 0,
                'result_code': 1,
                'result_message': 'Contact added',
                'result_output': 'json'}
            return MockResponse(fixtures_data, 200)
        else:
            fixtures_data = {
                'result_code': 0,
                'result_message': 'Contact Email Address is not valid.',
                'result_output': 'json'}
            return MockResponse(fixtures_data, 200)



def mocked_list_get(*args, **kwargs):
    """
    This method will be used by the mock to replace requests.get
    """
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    params = kwargs['params']
    if len(params.keys()) == 0:
        return MockResponse(
            "<?xml version='1.0' encoding='utf-8'?>\n<root><error>You are not authorized to access this file</error></root>", 200)
    elif params['api_action'] == 'list_list':
        if 'ids' not in params:
            return MockResponse({
                'result_code': 0,
                'result_message': 'Failed: Nothing is returned',
                'result_output': 'json'}, 200)
        elif params['ids'] in [1, '1', 'all', 'ALL']:
            if params.get('full') in [1, '1']:
                fixtures_path = os.path.join(THIS_DIR, 'fixture_list_list_full.json')
            else:
                fixtures_path = os.path.join(THIS_DIR, 'fixture_list_list.json')
            with open(fixtures_path, 'r') as f:
                fixtures_data = json.load(f)
            return MockResponse(fixtures_data, 200)

    elif params['api_action'] == 'list_delete':
        fixtures_data = {'result_code': 1,
             'result_message': 'Contact deleted',
             'result_output': 'json'}
        pass


    return MockResponse(None, 200)


def mocked_message_get(*args, **kwargs):
    """
    This method will be used by the mock to replace requests.get
    """
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    params = kwargs['params']
    if len(params.keys()) == 0:
        return MockResponse(
            "<?xml version='1.0' encoding='utf-8'?>\n<root><error>You are not authorized to access this file</error></root>", 200)
    elif params['api_action'] == 'message_list':
        if 'ids' not in params:
            return MockResponse({
                'result_code': 0,
                'result_message': 'Failed: Nothing is returned',
                'result_output': 'json'}, 200)
        elif params['ids'] in [1, '1', 'all', 'ALL']:
            if params.get('full') in [1, '1']:
                fixtures_path = os.path.join(THIS_DIR, 'fixture_list_list_full.json')
            else:
                fixtures_path = os.path.join(THIS_DIR, 'fixture_list_list.json')
            with open(fixtures_path, 'r') as f:
                fixtures_data = json.load(f)
            return MockResponse(fixtures_data, 200)

    return MockResponse(None, 200)



class ContactsTestCase(unittest.TestCase):

    @mock.patch('requests.get', side_effect=mocked_contacts_get)
    def test_list_contacts(self, mock_get):
        """Assert requests.get calls"""

        fixtures_path = os.path.join(THIS_DIR, 'fixture_list_contacts.json')
        with open(fixtures_path, 'r') as f:
            fixtures_data = json.load(f)

        config = act.Config()
        config.API_KEY = 'VALID_API_KEY'
        cr = act.ContactsResource(config)

        json_data = cr.get()
        self.assertEqual(json_data, fixtures_data)

        json_data = cr.get(ids=None)
        self.assertEqual(json_data, fixtures_data)

        json_data = cr.get(ids='ALL')
        self.assertEqual(json_data, fixtures_data)

        json_data = cr.get(ids=['1'])
        self.assertEqual(json_data, fixtures_data)

        json_data = cr.get(ids='1')
        self.assertEqual(json_data, fixtures_data)

        with self.assertRaises(TypeError):
            # IDs must be passed as strings
            json_data = cr.get(ids=[1])

        with self.assertRaises(TypeError):
            # IDs must be passed as strings
            json_data = cr.get(ids=1)

    @mock.patch('requests.get', side_effect=mocked_contacts_get)
    def test_delete_contact(self, mock_get):
        """Assert requests.get calls"""
        config = act.Config()
        config.API_KEY = 'VALID_API_KEY'
        cr = act.ContactsResource(config)

        result = cr.delete(_id='1')
        expected = {
            'result_code': 1,
            'result_message': 'Contact deleted',
            'result_output': 'json'
        }
        self.assertEqual(result, expected)

        result = cr.delete(_id='a')
        expected = {
            'result_code': 1,
            'result_message': 'Contact deleted',
            'result_output': 'json'
        }
        self.assertEqual(result, expected)


    @mock.patch('requests.post', side_effect=mocked_contacts_post)
    def test_create_contacts(self, mock_post):
        config = act.Config()
        config.API_KEY = 'VALID_API_KEY'
        cr = act.ContactsResource(config)

        result = cr.create({
            'email': 'email@example.com',
            'first_name': 'Test Account',
            'last_name': '2',
            'phone': '+1 555-555-5555',
            'ip4': '127.0.0.1',
            'tags': ['fakeuser','testing'],
            'list_id': ['1'],
        })
        expected = {
            'subscriber_id': 2,
            'sendlast_should': 0,
            'sendlast_did': 0,
            'result_code': 1,
            'result_message': 'Contact added',
            'result_output': 'json'
        }
        self.assertEqual(result, expected)

        result = cr.create({
            'first_name': 'Test Account',
            'last_name': '2',
            'phone': '+1 555-555-5555',
            'ip4': '127.0.0.1',
            'tags': ['fakeuser','testing'],
            'list_id': ['1'],
        })
        expected = {
            'result_code': 0,
            'result_message': 'Contact Email Address is not valid.',
            'result_output': 'json'
        }
        self.assertEqual(result, expected)


class ListTestCase(unittest.TestCase):

    @mock.patch('requests.get', side_effect=mocked_list_get)
    def test_list_list(self, mock_get):
        """Assert requests.get calls"""

        with open(os.path.join(THIS_DIR, 'fixture_list_list.json'), 'r') as f:
            fixtures_data = json.load(f)

        config = act.Config()
        config.API_KEY = 'VALID_API_KEY'
        resource = act.ListResource(config)

        json_data = resource.get()
        self.assertEqual(json_data, fixtures_data)

        json_data = resource.get(ids=None)
        self.assertEqual(json_data, fixtures_data)

        json_data = resource.get(ids='ALL')
        self.assertEqual(json_data, fixtures_data)

        json_data = resource.get(ids=['1'])
        self.assertEqual(json_data, fixtures_data)

        json_data = resource.get(ids='1')
        self.assertEqual(json_data, fixtures_data)

        with self.assertRaises(TypeError):
            # IDs must be passed as strings
            json_data = resource.get(ids=[1])

        with self.assertRaises(TypeError):
            # IDs must be passed as strings
            json_data = resource.get(ids=1)

        # 'full=1' test case
        with open(os.path.join(THIS_DIR, 'fixture_list_list_full.json'), 'r') as f:
            fixtures_data = json.load(f)
        json_data = resource.get(ids='1', full='1')
        self.assertEqual(json_data, fixtures_data)



def test_list_schema():
    schema = schemas.ListSchema()
    test_case = {
        'sourceid': '10',
        'ip4_sub': '0',
        'subscriberid': '1',
        'sourceid_autosync': '0',
        'ip4_unsub': '0',
        'unsubreason': '',
        'sdate': '2018-07-11 09:18:35',
        'unsubcampaignid': '0',
        'sync': '0',
        'sdate_iso': '2018-07-11T09:18:35-05:00',
        'seriesid': '0',
        'first_name': 'Test Account',
        'listid': '1',
        'last_name': '1',
        'ip4_last': '0',
        'responder': '1',
        'listname': 'Test List',
        'status': '1',
        'udate': '0000-00-00 00:00:00',
        'formid': '0',
        'unsubmessageid': '0'
    }
    unserialized = schema.load(test_case)
    assert unserialized.data['first_name'] == 'Test Account'
    assert unserialized.data['listname'] == 'Test List'
    assert unserialized.data['listid'] == '1'


def test_contact_details_schema():
    schema = schemas.ContactDetailsSchema()
    test_case = {
        'email': 'user@example.com',
        'first_name': 'Sample',
        'last_name': 'User',
        'phone': '+1 312-555-5555',
        'ip4': '0.0.0.0'
    }
    unserialized = schema.load(test_case)
    assert unserialized.data['email'] == 'user@example.com'
    assert unserialized.data['first_name'] == 'Sample'
    assert unserialized.data['last_name'] == 'User'
    assert unserialized.data['phone'] == '+1 312-555-5555'
    assert unserialized.data['ip4'] == '0.0.0.0'


def test_list_contacts_schema(list_contacts_data):
    schema = schemas.ContactResponseSchema()
    unserialized = schema.load(list_contacts_data['0'])
    assert unserialized.data['contact_details']['email'] == 'user@example.com'


def test_campaign_schema():
    schema = schemas.CampaignSchema()
    serialized = schema.dump({
        'name': 'a',
        'sdate': datetime.datetime(2018, 1, 1, 0, 0, 0),
        'status': '0',
        'public': '0',
        'list_id': ['1', '2', '3'],
        'message_id': {'1': 100},
        'segmentid': '0'
    })
    print(serialized.data)
    assert not serialized.errors
    assert serialized.data['sdate'] == '2018-01-01 00:00:00'
    assert serialized.data['name'] == 'a'
    assert serialized.data['status'] == '0'
    assert serialized.data['public'] == '0'
    assert serialized.data['type'] == 'single'
    assert serialized.data['tracklinks'] == 'none'
    assert serialized.data['p[1]'] == '1'
    assert serialized.data['p[2]'] == '2'
    assert serialized.data['p[3]'] == '3'
    assert serialized.data['p[3]'] == '3'
    assert serialized.data['m[1]'] == '100'


    serialized = schema.dump({
        'type': 'NOT DEFINED',
        'name': 'a',
        'sdate': datetime.datetime.utcnow(),
        'status': '0',
        'public': '0',
        'list_id': ['1', '2', '3'],
        'message_id': {'1': 100},
        'segmentid': '0'
    })
    print(serialized.errors)

    # Message id percents don't sum to 100
    serialized = schema.dump({
        'name': 'a',
        'sdate': datetime.datetime.utcnow(),
        'status': '0',
        'public': '0',
        'list_id': ['1', '2', '3'],
        'message_id': {'1': 50},
        'segmentid': '0',
        'list_id': ['1'],
    })
    print(serialized.errors)


def test_text_message_schema():
    schema = schemas.TextMessageSchema()
    data = {
        'format': 'text',
        'subject': 'Test message',
        'fromemail': 'sender@example.com',
        'fromname': 'Test Sender 1',
        'reply2': 'receiver@example.com',
        'priority': 5,
        'textconstructor': 'editor',
        'text': 'This is a test message',
        'list_id': ['1'],
    }
    serialized = schema.dump(data)
    print(serialized.data)
    assert not serialized.errors

    data = {
        'format': 'text',
        'subject': 'Test message',
        'fromemail': 'sender@example.com',
        'fromname': 'Test Sender 1',
        'reply2': 'receiver@example.com',
        'priority': 5,
        'list_id': ['1'],
        'textconstructor': 'external',
        'textfetch': 'http://example.com',
        'textfetchwhen': 'send',
    }
    serialized = schema.dump(data)
    print(serialized.data)
    assert not serialized.errors

    with pytest.raises(schemas.ValidationError):
        data = {
            'format': 'text',
            'subject': 'Test message',
            'fromemail': 'sender@example.com',
            'fromname': 'Test Sender 1',
            'reply2': 'receiver@example.com',
            'priority': 5,
            'list_id': ['1'],
            'textconstructor': 'editor',
        }
        serialized = schema.dump(data)
        # Workaround for error squashing inside marshmallow.
        if serialized.errors.get('_schema'):
            raise schemas.ValidationError(serialized.errors.get('_schema'))

    with pytest.raises(schemas.ValidationError):
        data = {
            'format': 'text',
            'subject': 'Test message',
            'fromemail': 'sender@example.com',
            'fromname': 'Test Sender 1',
            'reply2': 'receiver@example.com',
            'priority': 5,
            'list_id': ['1'],
            'textconstructor': 'external',
        }
        schema = schemas.TextMessageSchema()
        serialized = schema.dump(data)
        print("Errors: {}".format(serialized.errors))
        # Workaround for error squashing inside marshmallow.
        if serialized.errors.get('_schema'):
            raise schemas.ValidationError(serialized.errors.get('_schema'))

    with pytest.raises(schemas.ValidationError):
        data = {
            'format': 'text',
            'subject': 'Test message',
            'fromemail': 'sender@example.com',
            'fromname': 'Test Sender 1',
            'reply2': 'receiver@example.com',
            'priority': 5,
            'list_id': ['1'],
            'textconstructor': 'external',
            'textfetch': 'http://example.com',
        }
        serialized = schema.dump(data)
        # Workaround for error squashing inside marshmallow.
        if serialized.errors.get('_schema'):
            raise schemas.ValidationError(serialized.errors.get('_schema'))

    with pytest.raises(schemas.ValidationError):
        data = {
            'format': 'text',
            'subject': 'Test message',
            'fromemail': 'sender@example.com',
            'fromname': 'Test Sender 1',
            'reply2': 'receiver@example.com',
            'priority': 5,
            'list_id': ['1'],
            'textconstructor': 'external',
            'textfetchwhen': 'send',
        }
        serialized = schema.dump(data)
        # Workaround for error squashing inside marshmallow.
        if serialized.errors.get('_schema'):
            raise schemas.ValidationError(serialized.errors.get('_schema'))

    with pytest.raises(schemas.ValidationError):
        data = {
            'format': 'text',
            'subject': 'Test message',
            'fromemail': 'sender@example.com',
            'fromname': 'Test Sender 1',
            'reply2': 'receiver@example.com',
            'priority': 5,
            'list_id': ['1'],
            'textconstructor': 'BAD VALUE',
        }
        serialized = schema.dump(data)
        # Workaround for error squashing inside marshmallow.
        if serialized.errors.get('_schema'):
            raise schemas.ValidationError(serialized.errors.get('_schema'))


def test_contact_schema():
    schema = schemas.ContactSchema()
    data = {
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'tags': ['fakeuser', 'testing'],
        'list_id': ['1'],
    }
    serialized = schema.dump(data)
    print(serialized.data)
    assert not serialized.errors
    assert serialized.data['p[1]'] == '1'
    assert serialized.data['tags'] == 'fakeuser,testing'



def test_setup_contacts():
    pass

