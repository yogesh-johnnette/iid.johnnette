from payu.models import Transaction, CancelRefundCaptureRequests
# from django.core.exceptions import ObjectDoesNotExist
# from django.utils.http import urlencode
from django.conf import settings
from hashlib import sha512
# from uuid import uuid4
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
# import json


KEYS = ('txnid', 'amount', 'productinfo', 'firstname', 'email',
        'udf1', 'udf2', 'udf3', 'udf4', 'udf5', 'udf6', 'udf7', 'udf8',
        'udf9', 'udf10')


def check_hash(data):
    # Generate hash sequence and verify it with the hash sent by PayU in the Post Response

    Reversedkeys = reversed(KEYS)
    if data.get('additionalCharges'):
        # if the additionalCharges parameter is posted in the transaction response,then hash formula is:
        # sha512(additionalCharges|SALT|status||||||udf5|udf4|udf3|udf2|udf1|email|firstname|productinfo|amount|txnid|key)

        hash_value = sha512(str(data.get('additionalCharges')).encode('utf-8'))
        hash_value.update(("%s%s" % ('|', getattr(settings, 'PAYU_MERCHANT_SALT', None))).encode('utf-8'))
    else:
        # If additionalCharges parameter is not posted in the transaction response, then hash formula is the generic
        # reverse hash formula sha512(SALT|status||||||udf5|udf4|udf3|udf2|udf1|email|firstname|productinfo|amount
        # |txnid|key)

        hash_value = sha512(str(getattr(settings, 'PAYU_MERCHANT_SALT', None)).encode('utf-8'))

    hash_value.update(("%s%s" % ('|', str(data.get('status', '')))).encode('utf-8'))

    for key in Reversedkeys:
        hash_value.update(("%s%s" % ('|', str(data.get(key, '')))).encode('utf-8'))

    hash_value.update(("%s%s" % ('|', getattr(settings, 'PAYU_MERCHANT_KEY', None))).encode('utf-8'))

    # Updating the transaction
    transaction = Transaction.objects.get(transaction_id=data.get('txnid'))
    transaction.payment_gateway_type = data.get('PG_TYPE')
    transaction.transaction_date_time = data.get('addedon')
    transaction.mode = data.get('mode')
    transaction.status = data.get('status')
    transaction.amount = data.get('amount')
    transaction.mihpayid = data.get('mihpayid')
    transaction.bankcode = data.get('bankcode')
    transaction.bank_ref_num = data.get('bank_ref_num')
  
    transaction.additional_charges = data.get('additionalCharges', 0)
    transaction.txn_status_on_payu = data.get('unmappedstatus')
    transaction.hash_status = "Success" if hash_value.hexdigest().lower() == data.get('hash') else "Failed"
    transaction.save()

    return (hash_value.hexdigest().lower() == data.get('hash'))