# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging
import json
from base64 import b64encode
from StringIO import StringIO
from django.http import HttpResponse
from django.template import RequestContext, loader

from utils.pay.wechat import WeChatPayModeA
from utils.pay.config import settings as pay_settings
logger = logging.getLogger(__name__)


def image_to_base64_uri(content):
    """

    :param content:
    :return:
    """
    return "data:image/png;base64," + b64encode(content)


def get_qrcode(request, product_id, tpl="pay/qrcode.html"):
    """

    :param request:
    :param product_id:
    :return:
    """
    pay = WeChatPayModeA(appid=pay_settings.WEICHAT_APPID,
                         mch_id=pay_settings.WEICHAT_MCH_ID,
                         key=pay_settings.WEICHAT_KEY)
    output = StringIO()
    img = pay.generate_qrcode(product_id)
    # img.drawrect(14, 14)
    img.save(output)
    qr_code = output.getvalue()
    output.close()

    template = loader.get_template(tpl)
    context = RequestContext(
        request, {'img_uri': image_to_base64_uri(qr_code)})
    return HttpResponse(template.render(context))


def wechat_pay_call_back(request):
    """
    """
    try:

        from datetime import datetime, timedelta
        time_format = '%Y%m%d%H%M%S'
        date_now = datetime.now()
        after_2_hour = date_now + timedelta(hours=2)

        logger.debug("wechat_pay_call_back")
        pay_a = WeChatPayModeA(appid=pay_settings.WEICHAT_APPID,
                               mch_id=pay_settings.WEICHAT_MCH_ID,
                               key=pay_settings.WEICHAT_KEY)
        # 得到回调参数
        temp = pay_a.format_response(request)
        temp_json = json.dumps(temp)
        logger.debug("wechat return:  %s", temp_json)
        productid, openid = temp.get('product_id'), temp.get('openid')
        # 扫码支付模式一的统一下单
        pay_result = pay_a.unifiedorder(
            "Product detail", date_now.strftime(
                time_format), 1, request.META['REMOTE_ADDR'],
            'http://gic-test.yun-idc.com/pay/wechat/pay_call_back', openid=openid,
            product_id=productid, time_start=date_now.strftime(time_format), time_expire=after_2_hour.strftime(time_format),
            limit_pay='no_credit')
        temp = pay_a.format_response(pay_result)
        logger.debug("wechat unifiedorder: %s", json.dumps(temp))
        # 格式化输出参数
        result = pay_a.format_response(pay_result)
        # 根据接收的数据生成支付订单的等一系列处理
        result = pay_a.dict_to_xml_str(result)
        return HttpResponse(content=result, content_type='application/xml')
    except Exception as e:
        logger.error(e.message, exc_info=True)
        return HttpResponse('500')
