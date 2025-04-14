from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.config import get_mysql_url

# 创建基础类
Base = declarative_base()

# 定义 zidian 表的 ORM 模型
class Zidian(Base):
    __tablename__ = 'zidian'

    id = Column(Integer, primary_key=True, autoincrement=False, nullable=False)
    kname = Column(String(255), nullable=True)
    kvalue = Column(String(255), nullable=True)
    ktype = Column(String(255), nullable=True)
    ktypech = Column(String(255), nullable=True)

# 创建数据库引擎
engine = create_engine(get_mysql_url(), echo=False)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 初始化数据库（如果表不存在则创建）
def init_db():
    Base.metadata.create_all(bind=engine)

# 提供一个获取数据库会话的函数
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 查询 ktype 为 '1' 的记录
def get_kname_kvalue_by_ktype_1(db):
    """
    查询 ktype 为 '1' 的所有记录的 kname 和 kvalue 字段。
    :param db: 数据库会话对象
    :return: 查询结果列表，每个元素是一个字典，包含 kname 和 kvalue
    """
    results = db.query(Zidian.kname, Zidian.kvalue).filter(Zidian.ktype == '1').all()
    return [{"kname": result.kname, "kvalue": result.kvalue} for result in results]
