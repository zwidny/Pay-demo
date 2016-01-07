# -*- coding: utf-8 -*-
import logging
import json
import urllib
import urlparse
import requests
from hashlib import md5
from xml.etree.ElementTree import ElementTree
from time import time
from StringIO import StringIO
from uuid import uuid4
from qrcode import QRCode
logger = logging.getLogger(__name__)


class WeChatPayBase(object):

    def __init__(self, appid='', mch_id='', key='340373'):
        """微信支付.

        Args:
          appid(str):  公众账号ID
          mch_id(str): 微信支付分配的商户号

        """
        self.appid = appid
        self.mch_id = mch_id
        self.key = key

    @staticmethod
    def dict_to_xml_str(d, tag='xml'):
        """Turn a simple dict of key/value pairs into XML.
        """
        parts = [' <{}>'.format(tag)]
        for key, val in d.items():
            parts.append(' <{0}>{1}</{0}>'.format(key, val))
        parts.append(' </{}>'.format(tag))
        return ' '.join(parts)

    def generate_sign(self, m):
        """签名算法.

        Args:
          m(dict):

        Return: (str)
        """

        logger.debug('generate before: %s', json.dumps(m))
        # 参数名ASCII码从小到大排序（字典序）
        keys = m.keys()
        keys.sort()
        # 如果参数的值为空不参与签名
        data_str = '&'.join(['%s=%s' % (key, str(m[key]))
                             for key in keys if m[key]])
        # 拼接商品平台API Key
        result = data_str + "&key=%s" % self.key
        logger.debug('generate after: %s', json.dumps(result))
        return md5(result).hexdigest().upper()

    # def unifiedorder(self, url='https://api.mch.weixin.qq.com/pay/unifiedorder',
    #                  **kwargs):
    #     """统一下单.
    #
    #     Args:
    #       url(str):
    #       key(str):
    #
    #     """
    #     kwargs.update({'appid': self.appid,
    #                    'nonce_str': uuid4().hex,
    #                    'mch_id': self.mch_id})
    #     kwargs.update({'sign': self.generate_sign(kwargs)})
    #
    #     headers = {'Content-Type': 'application/xml'}
    #     response = requests.post(url,
    #                              data=self.dict_to_xml_str(kwargs),
    #                              headers=headers)
    #     return response

    @staticmethod
    def format_response(response):
        content = response.content if hasattr(
            response, 'content') else response.body
        result = {}
        tree = ElementTree(file=StringIO(content))
        root = tree.getroot()
        for child in root:
            result.update({child.tag: child.text})
        return result


class WeChatPayModeA(WeChatPayBase):

    def __init__(self, **kwargs):
        super(WeChatPayModeA, self).__init__(**kwargs)

    def generate_qrcode(self, product_id="", url='weixin://wxpay/bizpayurl'):
        kwargs = {}
        kwargs.update({
            'appid': self.appid,
            'mch_id': self.mch_id,
            'time_stamp': str(int(time())),
            'nonce_str': uuid4().hex,
            'product_id': product_id,
        })
        kwargs.update({'sign': self.generate_sign(kwargs)})
        scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)
        query = urllib.urlencode(kwargs)
        url = urlparse.urlunparse((scheme, netloc, path,
                                   params, query, fragment))
        qr = QRCode(version=1)
        logger.debug(url)
        qr.add_data(url)
        return qr.make_image()

    def unifiedorder(self, body, out_trade_no, total_fee, spbill_create_ip,
                     notify_url, trade_type="NATIVE",
                     openid='', product_id='', device_info='WEB',
                     detail="product detail", attach="", fee_type="CNY",
                     time_start='', time_expire='', limit_pay='',
                     url='https://api.mch.weixin.qq.com/pay/unifiedorder'):
        """

        :param body:
        :param out_trade_no:
        :param total_fee:
        :param spbill_create_ip:
        :param notify_url:
        :param trade_type:
        :param openid:
        :param product_id:
        :param is_subscribe:
        :param device_info:
        :param detail:
        :param attach:
        :param fee_type:
        :param time_start:
        :param time_expire:
        :param goods_tag:
        :param limit_pay:
        :param url:
        :return:
        """
        kwargs = {'appid': self.appid,
                  'mch_id': self.mch_id,
                  'device_info': device_info,
                  'nonce_str': uuid4().hex,
                  'body': body,
                  'detail': detail,
                  'attach': attach,
                  'out_trade_no': out_trade_no,
                  'fee_type': fee_type,
                  'total_fee': total_fee,
                  'spbill_create_ip': spbill_create_ip,
                  'time_start': time_start,
                  'time_expire': time_expire,
                  # 'goods_tag': goods_tag,
                  'notify_url': notify_url,
                  'trade_type': trade_type,
                  'product_id': product_id,
                  'limit_pay': limit_pay,
                  'openid': openid
                  }
        kwargs.update({'sign': self.generate_sign(kwargs)})
        logger.debug("unifiedorder: %s", json.dumps(kwargs))
        headers = {'Content-Type': 'application/xml'}
        return requests.post(url,
                             data=self.dict_to_xml_str(kwargs),
                             headers=headers)


class WeChatPayModeB:
    pass


class WeChatPay(WeChatPayModeA, WeChatPayModeB):
    pass


if __name__ == "__main__":
    test = WeChatPayBase()
    m = {
        'appid': "wxe3a7f5855a98e0bb",
        'nonce_str': uuid4().hex,
        'mch_id': "1265257701"
    }
    test.generate_sign(m=m)
