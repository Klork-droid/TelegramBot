import sqlite3


def ensure_connection(func):
    def inner(*args, **kwargs):
        with sqlite3.connect('anketa.db') as conn:
            res = func(*args, conn=conn, **kwargs)
        return res

    return inner


@ensure_connection
def init_db(conn, force: bool = False):
    """ Проверить что нужные таблицы существуют, иначе создать их

        Важно: миграции на такие таблицы вы должны производить самостоятельно!
        :param conn: подключение к СУБД
        :param force: явно пересоздать все таблицы
    """
    c = conn.cursor()
    # Информация о пользователе
    # TODO: Создать при необходимости...
    # Сообщения от пользователей
    if force:
        c.execute('DROP TABLE IF EXISTS user_message')
        c.execute('DROP TABLE IF EXISTS user_location')
        c.execute('DROP TABLE IF EXISTS user_names')

    c.execute('''
        CREATE TABLE IF NOT EXISTS user_message (
            id          INTEGER PRIMARY KEY,
            user_id     INTEGER NOT NULL,
            text        TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_names (
            user_id     INTEGER PRIMARY KEY,
            user_name   STRING NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_location (
            id          INTEGER PRIMARY KEY,
            user_id     INTEGER NOT NULL,
            latitude    REAL NOT NULL,
            longitude   REAL NOT NULL
        )
    ''')

    # Сохранить изменения
    conn.commit()


@ensure_connection
def check_unique_id(conn, user_id):
    c = conn.cursor()
    c.execute('SELECT user_id FROM user_names WHERE user_id = ?', (user_id,))
    return c.fetchone()


@ensure_connection
def add_message(conn, user_id: int, text: str, user_name=None, latitude=None, longitude=None):
    c = conn.cursor()
    c.execute('INSERT INTO user_message (user_id, text) VALUES (?, ?)', (user_id, text))
    if not check_unique_id(user_id=user_id):
        c.execute('INSERT INTO user_names (user_id, user_name) VALUES (?, ?)', (user_id, user_name))
    if latitude:
        c.execute('INSERT INTO user_location (user_id, latitude, longitude) VALUES (?, ?, ?)',
                  (user_id, latitude, longitude))
    conn.commit()


'''# Количество сообщений от user_id
@ensure_connection
def count_messages(conn, user_id: int):
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM user_message WHERE user_id = ? LIMIT 1', (user_id,))
    (res,) = c.fetchone()
    return res
'''


@ensure_connection
def last_location(conn, user_id):
    c = conn.cursor()
    c.execute('SELECT latitude, longitude FROM user_location WHERE user_id = ? ORDER BY id DESC LIMIT 3', (user_id,))
    return c.fetchall()


@ensure_connection
def all_users(conn):
    c = conn.cursor()
    c.execute('SELECT user_id FROM user_names')
    return c.fetchall()


@ensure_connection
def list_messages(conn, user_id: int, limit: int = 10):
    c = conn.cursor()
    c.execute('SELECT id, text FROM user_message WHERE user_id = ? ORDER BY id DESC LIMIT ?', (user_id, limit))
    return c.fetchall()


if __name__ == '__main__':
    init_db(force=True)
