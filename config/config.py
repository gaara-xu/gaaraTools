MYSQL_CONFIG = {
    "host": "192.168.3.110",
    "port": 3306,
    "database": "manhua",
    "user": "root",
    "password": "root",
    "charset": "utf8",
    "use_ssl": False,
    "allow_public_key_retrieval": True
}

# 拼接 MySQL 连接 URL
def get_mysql_url():
    ssl_option = "true" if MYSQL_CONFIG["use_ssl"] else "false"
    public_key_option = "true" if MYSQL_CONFIG["allow_public_key_retrieval"] else "false"
    return (
        f"mysql+pymysql://{MYSQL_CONFIG['user']}:{MYSQL_CONFIG['password']}@"
        f"{MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/{MYSQL_CONFIG['database']}?"
        f"charset={MYSQL_CONFIG['charset']}&useSSL={ssl_option}&allowPublicKeyRetrieval={public_key_option}"
    )