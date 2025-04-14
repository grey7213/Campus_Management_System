"""
微信相关配置
"""

# 微信公众号配置
WECHAT_CONFIG = {
    'app_id': 'wx_app_id_here',  # 微信公众号AppID
    'app_secret': 'wx_app_secret_here',  # 微信公众号AppSecret
    'token': 'your_token',  # 微信公众号Token
    'encoding_aes_key': 'your_encoding_aes_key',  # 微信公众号EncodingAESKey
    'access_token': None,  # 当前access_token
    'access_token_time': 0,  # access_token获取时间
    'expires_in': 7200,  # access_token有效期
}

# 微信API接口URL
ACCESS_TOKEN_URL = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}'
USER_INFO_URL = 'https://api.weixin.qq.com/cgi-bin/user/info?access_token={}&openid={}&lang=zh_CN'
MENU_CREATE_URL = 'https://api.weixin.qq.com/cgi-bin/menu/create?access_token={}'
TEMPLATE_MSG_URL = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}' 