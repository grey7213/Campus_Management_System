import requests
import json
import time
from app.wechat_config import WECHAT_CONFIG, ACCESS_TOKEN_URL, USER_INFO_URL, MENU_CREATE_URL, TEMPLATE_MSG_URL

class WechatAPI:
    """微信公众号API工具类"""
    
    @staticmethod
    def get_access_token():
        """获取接口调用凭证access_token"""
        # 检查是否已有有效的access_token
        now = int(time.time())
        if WECHAT_CONFIG['access_token'] and now - WECHAT_CONFIG['access_token_time'] < WECHAT_CONFIG['expires_in']:
            return WECHAT_CONFIG['access_token']
        
        # 调用微信接口获取新的access_token
        url = ACCESS_TOKEN_URL.format(WECHAT_CONFIG['app_id'], WECHAT_CONFIG['app_secret'])
        response = requests.get(url)
        result = response.json()
        
        if 'access_token' in result:
            # 更新配置
            WECHAT_CONFIG['access_token'] = result['access_token']
            WECHAT_CONFIG['expires_in'] = result['expires_in']
            WECHAT_CONFIG['access_token_time'] = now
            return result['access_token']
        else:
            # 获取失败
            print(f"获取access_token失败: {result}")
            return None
    
    @staticmethod
    def get_user_info(openid):
        """获取用户基本信息"""
        access_token = WechatAPI.get_access_token()
        if not access_token:
            return None
        
        url = USER_INFO_URL.format(access_token, openid)
        response = requests.get(url)
        return response.json()
    
    @staticmethod
    def create_menu(menu_data):
        """创建自定义菜单"""
        access_token = WechatAPI.get_access_token()
        if not access_token:
            return False
        
        url = MENU_CREATE_URL.format(access_token)
        response = requests.post(url, json=menu_data)
        result = response.json()
        
        if result.get('errcode') == 0:
            return True
        else:
            print(f"创建菜单失败: {result}")
            return False
    
    @staticmethod
    def send_template_message(openid, template_id, data, url=None):
        """发送模板消息"""
        access_token = WechatAPI.get_access_token()
        if not access_token:
            return False
        
        msg_url = TEMPLATE_MSG_URL.format(access_token)
        message = {
            "touser": openid,
            "template_id": template_id,
            "data": data
        }
        
        if url:
            message["url"] = url
        
        response = requests.post(msg_url, json=message)
        result = response.json()
        
        if result.get('errcode') == 0:
            return True
        else:
            print(f"发送模板消息失败: {result}")
            return False 