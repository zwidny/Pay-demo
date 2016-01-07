# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse_lazy

from utils.pay.unionpay import UnionPay


FILE_DIR = os.path.abspath(os.path.dirname(__file__))
APP_DIR = os.path.dirname(FILE_DIR)


def front_url(request):
    """前台通知地址

    :param request:
    :return:
    """
    return HttpResponse('Hello front url')


def back_url(request):
    """后台通知地址

    :param request:
    :return:
    """
    return HttpResponse("Hello back_url")


class UnionIndex(TemplateView):
    template_name = 'pay/union_index.html'
    union_pay = UnionPay
    PFX = os.path.join(APP_DIR, 'tests', '700000000000001_acp.pfx')
    front_url = 'http://localhost:8000/pay/unionpay/front-url'
    back_url = 'http://localhost:8000/pay/unionpay/back-url'

    def post(self, request, *args, **kwargs):
        union_pay = self.union_pay(mer_id='777290058122619')
        response = union_pay.front_transact(
            self.PFX, self.front_url, self.back_url)
        return HttpResponse(response.content)
