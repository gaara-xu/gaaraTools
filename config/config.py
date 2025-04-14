MYSQL_CONFIG = {
    "host": "192.168.3.110",
    "port": 3306,
    "database": "manhua",
    "user": "root",
    "password": "root",
    "charset": "utf8",
    "use_ssl": False  # 是否使用 SSL
}

# 拼接 MySQL 连接 URL
def get_mysql_url():
    return (
        f"mysql+pymysql://{MYSQL_CONFIG['user']}:{MYSQL_CONFIG['password']}@"
        f"{MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/{MYSQL_CONFIG['database']}?"
        f"charset={MYSQL_CONFIG['charset']}"
    )