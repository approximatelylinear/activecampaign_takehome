
import copy
import pdb
from marshmallow import Schema, ValidationError, fields, pprint, pre_load, post_load, post_dump


class ActionSchema(Schema):
    text = fields.Str()
    type = fields.Str()
    tstamp = fields.Str()


class ListSchema(Schema):
    listid = fields.Str()
    listname = fields.Str()
    sdate = fields.Str()
    sdate_iso = fields.Str()
    udate = fields.Str()
    status = fields.Str()
    sync = fields.Str()
    first_name = fields.Str()
    last_name = fields.Str()

    # Subscriber
    subscriberid = fields.Str()

    # Form
    formid = fields.Str()

    # Series
    seriesid = fields.Str()

    # Responder
    responder = fields.Str()

    # Unsubscribe
    unsubreason = fields.Str()
    unsubcampaignid = fields.Str()
    unsubmessageid = fields.Str()

    ip4_sub = fields.Str()
    ip4_last = fields.Str()
    ip4_unsub = fields.Str()

    # Source
    sourceid = fields.Str()
    sourceid_autosync = fields.Str()



class ContactDetailsSchema(Schema):
    email = fields.Email()
    first_name = fields.Str()
    last_name = fields.Str()
    phone = fields.Str()
    ip4 = fields.Str()
    tags = fields.List(fields.Str())

    @post_dump
    def process_tags(self, data):
        data = copy.deepcopy(data)
        if data.get('tags'):
            data['tags'] = ','.join(data['tags'])
        return data


class ContactSchema(ContactDetailsSchema):
    """
    Schema for creating a contact via the ActiveCampaign API.
    """
    list_id = fields.List(fields.Str())

    @post_dump
    def process_lists(self, data):
        data = copy.deepcopy(data)
        list_ids = data.pop('list_id')
        for _id in list_ids:
            data['p[{}]'.format(_id)] = str(_id)
        return data



class ContactResponseSchema(Schema):
    id = fields.Str()
    name = fields.Str()

    # Metadata?
    sdate = fields.DateTime(format='%Y-%m-%d %H:%M:%S')
    sdate_iso = fields.DateTime(format='iso')
    udate = fields.DateTime(format='%Y-%m-%d %H:%M:%S')
    cdate = fields.DateTime(format='%Y-%m-%d %H:%M:%S')
    adate = fields.DateTime(format='%Y-%m-%d %H:%M:%S')
    edate = fields.DateTime(format='%Y-%m-%d %H:%M:%S')

    status = fields.Str()
    sync = fields.Str()
    ua = fields.Str()
    hash = fields.Str()
    gravatar = fields.Str()
    deleted = fields.Str()
    anonymized = fields.Str()
    deleted = fields.Str()
    deleted_at = fields.Date()

    ip = fields.Str() # Meaning?
    email_local = fields.Str() # Meaning?
    email_domain = fields.Str() # Meaning?

    # Subscriber
    subscriberid = fields.Str()

    # List
    listid = fields.Str()
    listname = fields.Str()
    lid = fields.Str() # Meaning?

    # Form
    formid = fields.Str()

    # Series
    seriesid = fields.Str()

    # Responder
    responder = fields.Str()

    # Unsubscribe
    unsubreason = fields.Str()
    unsubcampaignid = fields.Str()
    unsubmessageid = fields.Str()

    #   TBD: Do these belong here?
    a_unsub_time = fields.Str() # Time?
    a_unsub_date = fields.Str() # Date?

    # IP
    ip4_sub = fields.Str()
    ip4_last = fields.Str()
    ip4_unsub = fields.Str()

    # Source
    sourceid = fields.Str()
    sourceid_autosync = fields.Str()

    # Organization
    orgid = fields.Str()
    orgname = fields.Str()

    # SegmentIO
    segmentio_id = fields.Str()

    # Analytics
    bounced_hard = fields.Str()
    bounced_soft = fields.Str()
    bounced_date = fields.Date()
    sentcnt = fields.Str()
    bouncescnt = fields.Integer()

    # Socialdata
    socialdata_lastcheck = fields.Str()

    # Rating
    rating = fields.Str()
    rating_tstamp = fields.Date()

    # Contact details
    contact_details = fields.Nested('ContactDetailsSchema')

    # Lists
    lists = fields.Nested('ListSchema', many=True)

    # Actions
    actions = fields.Nested('ActionSchema', many=True)

    @pre_load
    def format(self, in_data):
        # Convert dictionary of 'lists' to list of lists
        in_data = copy.deepcopy(in_data)
        in_data['lists'] = [v for k, v in in_data['lists'].items()]
        in_data['contact_details'] = {
            'first_name': in_data['first_name'],
            'last_name': in_data['last_name'],
            'phone': in_data['phone'],
            'email': in_data['email'],
            'ip4': in_data['ip4']
        }
        return in_data



def validate_pcts(d):
    pcts = d.values()
    if sum(pcts) != 100:
        raise ValidationError('Percents must sum to 100')


def validate_campaign_type(type_):
    valid_types = ['single', 'recurring', 'split', 'responder', 'reminder', 'special', 'activerss', 'text']
    if type_ not in valid_types:
        raise ValidationError('Campaign type must be one of these types: {}'.format(', '.join(valid_types)))


class CampaignSchema(Schema):
    type_ = fields.Str(attribute='type', data_key='type', default='single', required=True, validate=validate_campaign_type)
    name = fields.Str(required=True)
    sdate = fields.DateTime(format='%Y-%m-%d %H:%M:%S')
    status = fields.Str(required=True) # 0 or 1
    public = fields.Str(required=True) # 0: not visible, 1: visible
    tracklinks = fields.Str(default='none') # 'all', 'mime', 'html', 'text', 'none'
    list_id = fields.List(fields.Str())
    message_id = fields.Dict(keys=fields.Str(), values=fields.Integer(), validate=validate_pcts, required=True)
    segmentid = fields.Str() # 0 for no segment

    @post_dump
    def process_lists_messages(self, data):
        data = copy.deepcopy(data)
        message_ids = data.pop('message_id')
        for k, v in message_ids.items():
            data['m[{}]'.format(k)] = str(v)
        list_ids = data.pop('list_id')
        for _id in list_ids:
            data['p[{}]'.format(_id)] = str(_id)
        data['type'] = data.pop('type_')
        return data


class MessageSchema(Schema):
    """
    format: Examples: html, text, mime (both html and text)
    subject:    Subject of the email message.
    fromemail:  The "From" email address. Example: 'test@example.com'
    fromname:   The "From" name. Example: 'From Name'
    reply2: The "Reply To" email address. Example: 'reply2@example.com'
    priority:   Examples: 1 = high, 3 = medium/default, 5 = low
    charset:    Character set used. Example: 'utf-8'
    encoding:   Encoding used. Example: 'quoted-printable'
    """
    format = fields.Str(required=True, default='text')
    subject = fields.Str(required=True)
    fromemail = fields.Email(required=True)
    fromname = fields.Str(required=True)
    reply2 = fields.Email(required=True)
    priority = fields.Str(required=True) # 1 = high, 3 = medium/default, 5 = low
    charset = fields.Str(required=True, default='utf-8')
    encoding = fields.Str(required=True, default='quoted-printable')
    list_id = fields.List(fields.Str())

    @post_dump
    def process_lists(self, data):
        data = copy.deepcopy(data)
        list_ids = data.pop('list_id')
        for _id in list_ids:
            data['p[{}]'.format(_id)] = str(_id)
        return data


class TextMessageSchema(MessageSchema):
    """
    textconstructor: Text version. Examples: editor, external, upload. If editor, it uses 'text' parameter. If external, uses 'textfetch' and 'textfetchwhen' parameters. If upload, uses 'message_upload_text'.
    text:   Text version. Content of your text only email. Example: '_text only_ content of your email'
    textfetch:  Text version. URL where to fetch the body from. Example: 'http://somedomain.com/somepage.txt'
    textfetchwhen:  Text version. When to fetch. Examples: (fetch at) 'send' and (fetch) 'pers'(onalized)
    """
    textconstructor = fields.Str(required=True, default='editor') # Values: 'editor', 'external', 'upload'
    text = fields.Str() # Text content
    textfetch = fields.Str() # url to get the text body from
    textfetchwhen = fields.Str() # 'send' or 'pers'
    message_upload_text = fields.Str() # Not implemented

    @post_dump
    def validate_text(self, data):
        if data['format'] != 'text':
            raise ValidationError("Format of text message must be 'text'.")
        if not data.get('textconstructor'):
            raise ValidationError("Must provide value for 'textconstructor' parameter.")
        if data['textconstructor'] == 'editor':
            if not data.get('text'):
                raise ValidationError("Must provide a value for the 'text' parameter when the 'textconstructor' is 'editor'.")
        elif data['textconstructor'] == 'external':
            if not (data.get('textfetch') and data.get('textfetchwhen')):
                raise ValidationError("Must provide a value for the 'textfetch' and 'textfetchwhen' parameters when the 'textconstructor' is 'external'.")
        elif data['textconstructor'] == 'upload':
            raise ValidationError('This feature is not yet implemented.')
        else:
            raise ValidationError("Bad value for the 'textconstructor parameter.")


class AddressSchema(Schema):
    """
    Schema for creating an address via the ActiveCampaign API.
    """
    company_name = fields.Str()
    address_1 = fields.Str()
    address_2 = fields.Str()
    city = fields.Str()
    state = fields.Str()
    zipcode = fields.Str()
    country = fields.Str()
    list_id = fields.List(fields.Str())

    @post_dump
    def process_lists(self, data):
        data = copy.deepcopy(data)
        list_ids = data.pop('list_id')
        for _id in list_ids:
            data['p[{}]'.format(_id)] = str(_id)
        # zip being a reserved keywword
        data['zip'] = data.pop('zipcode')
        return data



