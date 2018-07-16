# -*- coding: utf-8 -*-

"""Console script for activecampaign_takehome."""
import sys
import datetime
from pprint import pformat

import click
from dateutil.parser import parse as date_parse

from activecampaign_takehome import activecampaign_takehome as act


@click.group()
def main(args=None):
    """Console script for activecampaign_takehome."""


@main.command()
def get_contacts():
    """
    List all contacts
    """
    config = act.Config()
    resource = act.ContactsResource(config)
    json_data = resource.get()
    click.echo(pformat(json_data))


@main.command()
@click.option('--email', prompt='Email address')
@click.option('--first_name', prompt='First name')
@click.option('--last_name', prompt='Last name')
@click.option('--list_id', prompt='List ID')
@click.option('--tags', default=None)
def add_contact(email, first_name, last_name, list_id, tags):
    """
    Add a contact.
    """
    config = act.Config()
    resource = act.ContactsResource(config)
    data = {
        'email': email,
        'first_name': first_name,
        'last_name': last_name,
        'list_id': [list_id],
        'tags': tags,
    }
    json_data = resource.create(data)
    click.echo(pformat(json_data))


@main.command()
def get_lists():
    """
    Get all lists.
    """
    config = act.Config()
    resource = act.ListResource(config)
    json_data = resource.get(full='1')
    click.echo(pformat(json_data))


@main.command()
@click.option('--ids', default=None)
@click.option('--page', default=None, type=int)
def get_messages(ids, page):
    """
    Get many messages. (Note: This method does not seem to currently work. Use `view_message` instead.)
    """
    config = act.Config()
    resource = act.MessageResource(config)
    json_data = resource.get_many(ids=ids, page=page)
    click.echo(pformat(json_data))


@main.command()
@click.argument('id')
def view_message(id):
    """
    View a single message
    """
    config = act.Config()
    resource = act.MessageResource(config)
    json_data = resource.get_one(_id=id)
    click.echo(pformat(json_data))


@main.command()
@click.option('--subject', prompt='Email subject')
@click.option('--fromemail', prompt='From address')
@click.option('--fromname', prompt='From name')
@click.option('--reply2', prompt='Reply-To address')
@click.option('--priority', prompt='Priority')
@click.option('--list_id', prompt='List ID')
@click.option('--text', prompt='Text body')
def create_message(subject, fromemail, fromname, reply2, priority, list_id, text):
    """
    Create a text message

    Usage:
        activecampaign_takehome create_message 'Test Message' 'mjb_sender@example.com' 'Test Sender 1' 'mjb_receiver@example.com' 5 1 'This is a test message'
    """
    config = act.Config()
    resource = act.MessageResource(config)
    data = {
        'format': 'text',
        'textconstructor': 'editor',
        'subject': subject,
        'fromemail': fromemail,
        'fromname': fromname,
        'reply2': reply2,
        'priority': priority,
        'list_id': [list_id],
        'text': text,
    }
    json_data = resource.create(data=data)
    click.echo(pformat(json_data))


@main.command()
@click.argument('id')
def delete_message(id):
    """
    Delete a given message
    """
    config = act.Config()
    resource = act.MessageResource(config)
    json_data = resource.delete(_id=id)
    click.echo(pformat(json_data))



@main.command()
@click.option('--name', prompt='Campaign name', default='Test Campaign 2')
@click.option('--send_date', prompt='Send date', default=datetime.datetime.now() + datetime.timedelta(seconds=60*5))
@click.option('--draft/--scheduled', default=True, prompt=True)
@click.option('--public/--private', default=False, prompt=True)
@click.option('--list_id', prompt='List ID', default='1')
@click.option('--message_id', prompt='Message ID', default='7')
@click.option('--segment_id', default='0')
@click.option('--campaign-type', type=click.Choice(['single', 'recurring', 'split', 'responder', 'reminder', 'special', 'activerss', 'text']), default='single')
def create_campaign(name, send_date, draft, public, list_id, message_id, segment_id, campaign_type):
    """
    Send a message to a single recipient.
    """
    config = act.Config()
    resource = act.CampaignResource(config)
    data = {
        'name': name,
        'sdate': date_parse(send_date),
        'status': '0' if draft else '1',
        'public': '1' if public else '0',
        'list_id': [list_id],
        'message_id': {message_id: 100},
        'segmentid': segment_id,
        'type': campaign_type
    }
    json_data = resource.create(data)
    click.echo(pformat(json_data))


@main.command()
@click.option('--campaign-id', prompt='Campaign ID', default='1')
@click.option('--send_date', prompt='Send date', default=datetime.datetime.now() + datetime.timedelta(seconds=60))
@click.option('--draft/--scheduled', default=True, prompt=True)
def update_campaign_status(campaign_id, draft, send_date):
    """
    Send a message to a single recipient.
    """
    config = act.Config()
    resource = act.CampaignResource(config)
    send_date = date_parse(send_date) if isinstance(send_date, str) else send_date
    status = '0' if draft else '1'
    json_data = resource.update_status(campaign_id, status, send_date)
    click.echo(pformat(json_data))


@main.command()
@click.option('--email', prompt='Email address')
@click.option('--campaign_id', prompt='Campaign ID')
@click.option('--message_id', prompt='Message ID')
@click.option('-t', '--type', '_type', prompt='Message type (e.g. "text"')
@click.option('--action', prompt='Send action (e.g. "test")')
def send_campaign_message(email, campaign_id, message_id, _type, action):
    """
    Send a message to a single recipient.
    """
    config = act.Config()
    resource = act.CampaignResource(config)
    json_data = resource.send(
        email, campaign_id, message_id, _type, action)
    click.echo(pformat(json_data))


@main.command()
@click.option('--ids', prompt='Campaign IDs', default='1')
def get_campaigns(ids):
    """
    Send a message to a single recipient.
    """
    config = act.Config()
    resource = act.CampaignResource(config)
    json_data = resource.get(ids)
    click.echo(pformat(json_data))
