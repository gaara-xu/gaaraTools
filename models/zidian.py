from sqlalchemy import Column, Integer, String, create_engine  # type: ignore
from sqlalchemy.ext.declarative import declarative_base  # type: ignore
from sqlalchemy.orm import sessionmaker  # type: ignore
from config.config import get_mysql_url

# 创建基础类
Base = declarative_base()

# 定义 zidian 表的 ORM 模型
class Zidian(Base):
    __tablename__ = 'zidian'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)  # 确保 id 为自增主键
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
from contextlib import contextmanager

@contextmanager
def get_db_session():
    """
    获取数据库会话的上下文管理器。
    使用 with 语句时会自动关闭会话。
    """
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

# 插入一条记录到 zidian 表
def insert_zidian_record(db, kname, kvalue, ktype, ktypech):
    """
    插入一条记录到 zidian 表。
    :param db: 数据库会话对象
    :param kname: 字段 kname 的值
    :param kvalue: 字段 kvalue 的值
    :param ktype: 字段 ktype 的值
    :param ktypech: 字段 ktypech 的值
    :return: 插入的记录对象
    """
    new_record = Zidian(
        kname=kname,
        kvalue=kvalue,
        ktype=ktype,
        ktypech=ktypech
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)  # 刷新以获取数据库生成的自增 ID
    return new_record

# 查询 kvalue 是否存在
def check_kvalue_exists(db, kvalue):
    """
    检查 zidian 表中是否存在指定 kvalue 的记录。
    :param db: 数据库会话对象
    :param kvalue: 要查询的 kvalue 值
    :return: 如果记录数大于 0 返回 True，否则返回 False
    """
    count = db.query(Zidian).filter(Zidian.kvalue == kvalue).count()
    return count > 0
