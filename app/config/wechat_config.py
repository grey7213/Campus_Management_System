# 微信公众号配置
WECHAT_CONFIG = {
    'app_id': 'wx86cbb150debf256b',        # 微信公众号AppID
    'app_secret': 'b0db440ca17445eb5a157006d4889799', # 微信公众号AppSecret
    'token': 'your_token',           # 微信公众号Token，用于验证消息
    'encoding_aes_key': '',          # 消息加解密密钥，安全模式下使用
    'access_token': '',              # 接口调用凭证
    'expires_in': 0,                 # 凭证有效期
    'access_token_time': 0           # 获取凭证的时间
}

# 获取access_token的接口
ACCESS_TOKEN_URL = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={0}&secret={1}'

# 用户信息接口
USER_INFO_URL = 'https://api.weixin.qq.com/cgi-bin/user/info?access_token={0}&openid={1}&lang=zh_CN'

# 自定义菜单创建接口
MENU_CREATE_URL = 'https://api.weixin.qq.com/cgi-bin/menu/create?access_token={0}'

# 消息模板接口
TEMPLATE_MSG_URL = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={0}' 