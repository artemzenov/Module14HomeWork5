import sqlite3


def initiate_db():
    db_products = sqlite3.connect('db_products.db')
    cursor_db_products = db_products.cursor()

    cursor_db_products.execute('''
        CREATE TABLE IF NOT EXISTS Products(
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            price INTEGER NOT NULL,
            photo TEXT
            )
        '''
        )

    for i in range(1, 5):
        db_products.execute('''INSERT INTO Products (title, description, price, photo) VALUES(?, ?, ?, ?)''',
            (f'Product {i}', f'Описание {i}', i * 100, f'photo/photo{i}.jpeg'))

    db_products.commit()
    db_products.close()

    db_users = sqlite3.connect('db_users.db')
    cursor_db_users = db_users.cursor()

    cursor_db_users.execute('''
        CREATE TABLE IF NOT EXISTS Users(
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            age INTEGER NOT NULL,
            balance INTEGER NOT NULL
            )
        ''')

    db_users.commit()
    db_users.close()

def get_all_products():
    db_products = sqlite3.connect('db_products.db')
    cursor_db_products = db_products.cursor()

    result = cursor_db_products.execute("SELECT * FROM Products").fetchall()
    db_products.close()
    return result


def is_included(username):
    db_products = sqlite3.connect('db_users.db')
    cursor_db_products = db_products.cursor()

    if cursor_db_products.execute("SELECT * FROM Users WHERE username = ?",
        (username,)).fetchone():
        return True
    else:
        return False


def add_user(username, email, age, balance):
    db_products = sqlite3.connect('db_users.db')
    cursor_db_products = db_products.cursor()

    cursor_db_products.execute("INSERT INTO Users (username, email, age, balance) VALUES (?, ?, ?, ?)",
        (username, email, age, balance))

    db_products.commit()
    db_products.close()


if __name__ == '__main__':
    initiate_db()
    print(get_all_products())
