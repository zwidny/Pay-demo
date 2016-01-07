# -*- coding: utf-8 -*-
import requests
import hashlib
import logging
import json
from base64 import b64encode
from OpenSSL import crypto
logger = logging.getLogger('account')


class UnionPay(object):
    # 银联全渠道商户接入入网测试(PM)环境地址

    # 前台交易请求地址
    FRONT_TRANS_URL = 'https://101.231.204.80:5000/gateway/api/frontTransReq.do'

    # 后台交易请求地址
    BACK_TRANS_URL = 'https://101.231.204.80:5000/gateway/api/backTransReq.do'

    # 后台交易请求地址(若为有卡交易配置该地址)
    BACK_WITH_CARD_TRANS_URL = 'https://101.231.204.80:5000/gateway/api/cardTransReq.do'

    # 单笔查询请求地址
    SINGLE_QUERY_URL = 'https://101.231.204.80:5000/gateway/api/queryTrans.do'

    # 批量交易请求地址
    BATCH_TRANS_URL = 'https://101.231.204.80:5000/gateway/api/batchTrans.do'

    # 文件传输类交易地址
    FILE_TRANS_URL = 'https://101.231.204.80:9080/'

    # 银联全渠道入网测试(PM)环境支付的测试卡号、密码

    # 借记卡
    # 测试卡号
    CART_NO = '6216261000000000018'

    # 证件号
    IDENTITY_CARD = '341126197709218366'

    # 手机号
    PHONE = '13552535506'

    # 姓名
    NAME = u'全渠道'

    # 密码
    PASSWORD = '123456'

    # 短信验
    mobile_captcha = '111111'

    # 贷记卡
    # 测试卡号
    DCART_NO = '5200831111111113'

    # 证件号
    DIDENTITY_CARD = '341126197709218366'
    CVN2 = '123'

    # 有效期
    VALIDITY = '1911'

    # 姓名
    DNAME = u'全渠道'

    def __init__(self, mer_id):
        self.mer_id = mer_id

    def front_transact(self, pfx_file, front_url, back_url, passphrase='000000'):
        serial_number, p_key = self.get_cert_id(pfx_file, passphrase)

        from datetime import datetime, timedelta
        time_format = '%Y%m%d%H%M%S'
        date_now = datetime.now()
        after_15_min = date_now + timedelta(minutes=15)
        kwargs = {
            'version': '5.0.0',
            'encoding': 'UTF-8',
            'certId': serial_number,
            'signMethod': '01',
            'txnType': '01',
            'txnSubType': '01',
            'bizType': '000201',
            'accessType': '0',
            'channelType': '07',
            'merId': self.mer_id,
            'orderId': '0000000002',
            'frontUrl': front_url,
            'backUrl': back_url,
            'currencyCode': '156',
            'txnAmt': '1',  # 单位为分，不能带小数点
            'txnTime': date_now.strftime(time_format),
            'payTimeout': after_15_min.strftime(time_format),
            # 'issInsCode': '',
            'reqReserved': '<identify></identify>',
            # 'frontFailUrl': '',
        }
        sign_str = self.generate_signature_string(kwargs)
        sign_str_sha1 = hashlib.sha1(sign_str).hexdigest()
        result = crypto.sign(p_key, sign_str_sha1, 'sha1')
        result = b64encode(result)
        kwargs.update({'signature': result})
        logger.debug('union pay: >>>>>>>> %s', json.dumps(kwargs))
        return requests.post(self.FRONT_TRANS_URL, kwargs, verify=False)

    @staticmethod
    def get_cert_id(pfx_file, passphrase='000000'):
        with open(pfx_file) as f:
            pfx = crypto.load_pkcs12(f.read(), passphrase)
        return pfx.get_certificate().get_serial_number(), pfx.get_privatekey()

    @staticmethod
    def generate_signature_string(m):
        """对m出现签名域（signature）之外的所有数据元采用key=value的形式按照名称排序，
        去掉值为空的数据元, 然后以&作为连接符拼接成待签名串

        :param m(dict):
        :return (string):
        """
        keys = sorted(m.keys())
        return '&'.join(['%s=%s' % (key, str(m[key])) for key in keys])
