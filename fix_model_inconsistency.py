"""
修复模型与数据库表结构不一致问题
"""
from app import create_app, db
from sqlalchemy import text, inspect
from sqlalchemy.exc import NoSuchTableError
import importlib
import sys

def log(message):
    """记录日志"""
    print(f"[FIX] {message}")

def reset_models_cache():
    """重置模型缓存，重新加载模型模块"""
    log("重置模型缓存...")
    # 查找并重载所有模型模块
    model_modules = [
        "app.models.literacy", 
        "app.models.literacy_certificate"
    ]
    for module_name in model_modules:
        try:
            if module_name in sys.modules:
                log(f"重新加载模块: {module_name}")
                importlib.reload(sys.modules[module_name])
            else:
                log(f"加载模块: {module_name}")
                importlib.import_module(module_name)
        except Exception as e:
            log(f"加载模块 {module_name} 时出错: {e}")

def inspect_database():
    """检查数据库表结构"""
    app = create_app()
    with app.app_context():
        # 获取数据库连接和检查器
        inspector = inspect(db.engine)
        
        try:
            # 检查literacy_certificates表结构
            log("检查literacy_certificates表结构...")
            columns = inspector.get_columns("literacy_certificates")
            column_names = [col["name"] for col in columns]
            
            log(f"找到以下列: {', '.join(column_names)}")
            
            # 检查是否有image_url列
            if "image_url" not in column_names:
                log("缺少image_url列，添加该列...")
                db.session.execute(text("ALTER TABLE literacy_certificates ADD COLUMN image_url VARCHAR(255)"))
                db.session.commit()
                log("已添加image_url列")
            else:
                log("image_url列已存在")
                
            # 检查是否有blockchain_enabled列
            if "blockchain_enabled" not in column_names:
                log("缺少blockchain_enabled列，添加该列...")
                db.session.execute(text("ALTER TABLE literacy_certificates ADD COLUMN blockchain_enabled BOOLEAN DEFAULT FALSE"))
                db.session.commit()
                log("已添加blockchain_enabled列")
            else:
                log("blockchain_enabled列已存在")
            
            # 再次验证列
            columns = inspector.get_columns("literacy_certificates")
            column_names = [col["name"] for col in columns]
            log(f"更新后的列: {', '.join(column_names)}")
            
        except NoSuchTableError:
            log("表 literacy_certificates 不存在!")
            return False
        except Exception as e:
            log(f"检查表结构时出错: {e}")
            return False
            
        return True

def fix_model_data():
    """修复模型实例数据与数据库的一致性"""
    app = create_app()
    with app.app_context():
        # 尝试重载模型
        reset_models_cache()
        
        log("获取所有证书记录...")
        try:
            # 使用SQL直接查询所有证书
            result = db.session.execute(text("SELECT id FROM literacy_certificates"))
            cert_ids = [row[0] for row in result]
            
            if not cert_ids:
                log("未找到任何证书记录")
                return
                
            log(f"找到 {len(cert_ids)} 个证书ID: {cert_ids}")
            
            # 导入app.models.literacy中的证书模型
            from app.models.literacy import LiteracyCertificate
            
            # 更新每个证书的blockchain_enabled
            for cert_id in cert_ids:
                log(f"处理证书ID: {cert_id}")
                
                # 更新blockchain_enabled
                db.session.execute(
                    text("UPDATE literacy_certificates SET blockchain_enabled = TRUE WHERE id = :id"),
                    {"id": cert_id}
                )
                
                # 检查image_url是否有值
                result = db.session.execute(
                    text("SELECT image_url FROM literacy_certificates WHERE id = :id"),
                    {"id": cert_id}
                )
                image_url = result.scalar()
                
                if not image_url:
                    log(f"证书ID {cert_id} 的image_url为空，重新使用修复工具生成图片")
                else:
                    log(f"证书ID {cert_id} 的image_url: {image_url}")
            
            # 提交更改
            db.session.commit()
            log("已更新证书数据")
            
            # 验证刷新
            try:
                from app.models.literacy import LiteracyCertificate
                cert = LiteracyCertificate.query.get(cert_ids[0])
                log(f"测试访问: 证书ID {cert.id} 的image_url: {cert.image_url}")
                log(f"测试访问: 证书ID {cert.id} 的blockchain_enabled: {cert.blockchain_enabled}")
            except Exception as e:
                log(f"测试访问时出错: {e}")
                
        except Exception as e:
            log(f"修复模型数据时出错: {e}")
            db.session.rollback()
            
def main():
    """主函数"""
    # 1. 检查并修复数据库表结构
    if inspect_database():
        # 2. 修复模型数据
        fix_model_data()
    
    # 3. 建议用户重启Flask应用
    log("修复完成，建议重启Flask应用以确保所有更改生效")
    
if __name__ == "__main__":
    main() 