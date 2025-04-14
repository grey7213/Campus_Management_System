from flask import Blueprint, request, make_response
import hashlib
import time
import xml.etree.ElementTree as ET
import requests
from app import db
from app.models.user import User
from app.wechat_config import WECHAT_CONFIG

wechat = Blueprint('wechat', __name__)

@wechat.route('/api/wechat', methods=['GET', 'POST'])
def wechat_handler():
    # 微信服务器验证接口
    if request.method == 'GET':
        token = WECHAT_CONFIG.get('token')
        signature = request.args.get('signature', '')
        timestamp = request.args.get('timestamp', '')
        nonce = request.args.get('nonce', '')
        echostr = request.args.get('echostr', '')
        
        tmp_list = [token, timestamp, nonce]
        tmp_list.sort()
        tmp_str = ''.join(tmp_list)
        
        # 计算签名
        tmp_str = hashlib.sha1(tmp_str.encode('utf-8')).hexdigest()
        
        if tmp_str == signature:
            return echostr
        else:
            return 'verification failed'
    
    # 处理微信发来的消息
    elif request.method == 'POST':
        xml_data = request.data
        msg = parse_xml(xml_data)
        
        # 获取用户openid
        openid = msg.get('FromUserName')
        
        # 根据消息类型处理
        msg_type = msg.get('MsgType')
        if msg_type == 'text':
            content = msg.get('Content')
            # 处理文本消息
            reply_content = process_text_message(content, openid)
            reply = create_reply(reply_content, msg)
            return make_response(reply)
        elif msg_type == 'event':
            event = msg.get('Event')
            if event == 'subscribe':
                # 用户关注公众号事件
                reply_content = "感谢关注校园综合管理平台！您的openid是: " + openid
                # 可以在这里保存用户的openid
                save_user_openid(openid)
                reply = create_reply(reply_content, msg)
                return make_response(reply)
            
        # 默认回复
        reply = create_reply("收到您的消息，谢谢！", msg)
        return make_response(reply)

def parse_xml(xml_data):
    """解析微信发送的XML消息"""
    if not xml_data:
        return {}
        
    msg = {}
    root = ET.fromstring(xml_data)
    if root.tag == 'xml':
        for child in root:
            msg[child.tag] = child.text
    return msg

def create_reply(reply_content, msg):
    """创建回复消息XML"""
    xml_reply = """
    <xml>
    <ToUserName><![CDATA[{to_user}]]></ToUserName>
    <FromUserName><![CDATA[{from_user}]]></FromUserName>
    <CreateTime>{create_time}</CreateTime>
    <MsgType><![CDATA[text]]></MsgType>
    <Content><![CDATA[{content}]]></Content>
    </xml>
    """
    
    return xml_reply.format(
        to_user=msg.get('FromUserName'),
        from_user=msg.get('ToUserName'),
        create_time=int(time.time()),
        content=reply_content
    )

def process_text_message(content, openid):
    """处理用户发送的文本消息"""
    if content.startswith('查询'):
        # 处理查询指令
        query = content[2:].strip()
        return f"您查询的内容是: {query}，稍后为您处理"
    elif content == '我的信息':
        # 返回用户openid
        return f"您的openid是: {openid}"
    else:
        # 默认回复
        return "您好，我是校园综合管理平台智能助手，请问有什么可以帮您？\n\n可用指令：\n- 查询 [内容]\n- 我的信息"

def save_user_openid(openid):
    """保存用户的openid到数据库"""
    # 查询是否已存在此openid的用户
    user = User.query.filter_by(wechat_openid=openid).first()
    if not user:
        # 创建新的用户记录或关联到已有用户
        # 这里仅做示例，实际应用中需要完善用户关联逻辑
        pass
    
    return True 