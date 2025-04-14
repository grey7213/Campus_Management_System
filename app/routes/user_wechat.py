from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.utils.wechat_api import WechatAPI
from app.wechat_config import WECHAT_CONFIG
import qrcode
from io import BytesIO
import base64
import uuid
import time

user_wechat = Blueprint('user_wechat', __name__)

@user_wechat.route('/user/wechat/bind', methods=['GET', 'POST'])
@login_required
def bind_wechat():
    """用户绑定微信"""
    if request.method == 'GET':
        # 生成唯一的场景值(scene_id)，用于识别扫码用户
        scene_id = str(uuid.uuid4())
        
        # 存储场景值与用户ID的关联
        # 实际应用中应使用Redis等缓存存储
        bind_info = {
            'user_id': current_user.id,
            'scene_id': scene_id,
            'create_time': int(time.time())
        }
        # 这里应该将bind_info存储到缓存或数据库
        
        # 生成带场景值的二维码链接
        # 实际应用中应调用微信接口生成带参数二维码
        # 这里简化为直接生成URL
        qr_url = f"https://open.weixin.qq.com/connect/oauth2/authorize?appid={WECHAT_CONFIG['app_id']}&redirect_uri=http://yourserver.com/api/wechat/oauth&response_type=code&scope=snsapi_base&state={scene_id}#wechat_redirect"
        
        # 生成二维码图片
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 转换为base64以在页面显示
        buffered = BytesIO()
        img.save(buffered)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return render_template('user/wechat_bind.html', qr_code=img_str, scene_id=scene_id)
    
    elif request.method == 'POST':
        # 手动绑定微信openid（管理员功能）
        if not current_user.is_admin:
            return jsonify({'success': False, 'message': '权限不足'})
        
        openid = request.form.get('openid')
        user_id = request.form.get('user_id')
        
        if not openid or not user_id:
            return jsonify({'success': False, 'message': '参数不完整'})
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'})
        
        user.wechat_openid = openid
        db.session.commit()
        
        return jsonify({'success': True, 'message': '绑定成功'})

@user_wechat.route('/user/wechat/unbind', methods=['POST'])
@login_required
def unbind_wechat():
    """解除微信绑定"""
    current_user.wechat_openid = None
    db.session.commit()
    flash('已成功解除微信绑定', 'success')
    return redirect(url_for('user.profile'))

@user_wechat.route('/api/wechat/oauth')
def wechat_oauth():
    """OAuth授权回调处理"""
    code = request.args.get('code')
    state = request.args.get('state')  # 场景值
    
    if not code or not state:
        return '授权失败'
    
    # 根据场景值查找对应的用户ID
    # 实际应用中应从Redis等缓存中获取
    # 这里假设找到了对应关系
    user_id = find_user_by_scene_id(state)
    if not user_id:
        return '二维码已过期或无效'
    
    # 通过code获取用户openid
    # 实际应用中应调用微信接口
    # openid = get_openid_by_code(code)
    
    # 这里简化为假设已获取openid
    openid = "simulated_openid_" + state[:8]
    
    # 绑定用户和openid
    user = User.query.get(user_id)
    user.wechat_openid = openid
    db.session.commit()
    
    return render_template('user/wechat_bind_success.html')

def find_user_by_scene_id(scene_id):
    """根据场景值查找用户ID"""
    # 实际应用中应从Redis等缓存中获取
    # 这里简单返回一个模拟值
    return 1  # 假设用户ID为1

@user_wechat.route('/user/wechat/check_bind')
@login_required
def check_bind_status():
    """检查微信绑定状态"""
    scene_id = request.args.get('scene_id')
    if not scene_id:
        return jsonify({'bound': False, 'message': '参数不完整'})
    
    # 实际应用中应从Redis等缓存中获取绑定状态
    # 这里简单模拟，始终返回未绑定状态
    # 实际应用中，当微信服务器回调OAuth接口时应设置绑定成功状态
    bound = False  # 假设未绑定
    
    # 检查当前用户是否已绑定微信
    if current_user.wechat_openid:
        bound = True
        
    return jsonify({'bound': bound}) 