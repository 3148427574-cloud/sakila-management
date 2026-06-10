import pymysql

DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'ZhangJie259885',
    'database': 'sakila',
    'charset': 'utf8mb4',
}


def doSql(sql):
    conn = pymysql.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()


def querySql(sql):
    conn = pymysql.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute(sql)
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result
