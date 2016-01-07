# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging
import paypalrestsdk
from django.views.generic import TemplateView
from django.http import HttpResponse, HttpResponseRedirect, Http404


logger = logging.getLogger(__name__)
SANDBOX = 'https://api.sandbox.paypal.com'
LIVE = 'https://api.paypal.com'

paypalrestsdk.configure({
    'mode': 'sandbox',
    'client_id': 'AYZecBasVqMHP8D9wFSuXp9-4__m_sJWFFqAi88eU5w1rChzFtOnzgZjvE8I92l5mSUqJgxiYmw82ISS',
    'client_secret': 'EKZjq9DZMxTR3B7bzhP0r3qi0qvsZo88ygLu5YmQCSjc7HG5utddd8Ooh4sQQxhPD-i9hQn7Xaok7O6b'
})


class PayPalIndex(TemplateView):
    template_name = 'pay/paypal_index.html'

    def post(self, request, *args, **kwargs):
        payment = paypalrestsdk.Payment({
            "intent": "sale",

            # Payer
            # A resource representing a Payer that funds a payment
            # Payment Method as 'paypal'
            "payer": {
                "payment_method": "paypal"},

            # Redirect URLs
            "redirect_urls": {
                "return_url": "http://localhost:8000/pay/paypal/execute",
                "cancel_url": "http://localhost:8000/pay/paypal/index"},

            # Transaction
            # A transaction defines the contract of a
            # payment - what is the payment for and who
            # is fulfilling it.
            "transactions": [{

                # ItemList
                "item_list": {
                    "items": [{
                        "name": "item",
                        "sku": "item",
                        "price": "100.00",
                        "currency": "USD",
                        "quantity": 1}]},

                # Amount
                # Let's you specify a payment amount.
                "amount": {
                    "total": "100.00",
                    "currency": "USD"},
                "description": "This is the payment transaction description."}]})
        if payment.create():
            print("Payment[%s] created successfully" % (payment.id))
            # Redirect the user to given approval url
            for link in payment.links:
                if link.method == "REDIRECT":
                    # Convert to str to avoid google appengine unicode issue
                    # https://github.com/paypal/rest-api-sdk-python/pull/58
                    redirect_url = str(link.href)
                    print("Redirect for approval: %s" % (redirect_url))
                    return HttpResponseRedirect(redirect_url)
        else:
            print("Error while creating payment:")
            print(payment.error)
            return HttpResponse(payment.error)


class PayPalExecute(TemplateView):
    template_name = 'pay/paypal_index.html'

    def get(self, request, *args, **kwargs):
        try:
            payment_id = request.GET.get('paymentId')
            payer_id = request.GET.get('PayerID')
            payment = paypalrestsdk.Payment.find(payment_id)
            if payment.execute({"payer_id": payer_id}):
                print("Payment[%s] execute successfully" % (payment.id))
                # return super(PayPalExecute, self).get(request, *args,
                # **kwargs)
                return HttpResponse("Pay successful")
            else:
                print(payment.error)
                return HttpResponse(payment.error)
        except Exception as e:
            logger.error(e.message, exc_info=True)
            return Http404()
