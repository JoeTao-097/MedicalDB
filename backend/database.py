from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# 数据库配置 - 使用SQLite作为默认数据库
def get_engine():
    """获取数据库引擎"""
    # 优先使用环境变量中的MySQL配置
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    
    # 如果配置了MySQL且连接可用，使用MySQL
    if all([db_host, db_port, db_name, db_user]):
        try:
            mysql_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            engine = create_engine(mysql_url, echo=False)
            # 测试连接
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            print("✅ 使用MySQL数据库")
            return engine
        except Exception as e:
            print(f"⚠️  MySQL连接失败，使用SQLite: {e}")
    
    # 默认使用SQLite
    # 确保数据库文件在项目根目录
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "medical_cosmetics.db")
    sqlite_url = f"sqlite:///{db_path}"
    print("✅ 使用SQLite数据库")
    return create_engine(sqlite_url, echo=False)

def get_session():
    """获取数据库会话"""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session() 