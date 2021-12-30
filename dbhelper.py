import sqlite3


class DBHelper:
    def __init__(self, dbname="todo.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)

    def setup(self):
        print("creating tables")
        #override tables
        tblstmt = "CREATE TABLE IF NOT EXISTS orders (description text, owner text, number text)"
        print(tblstmt)
        #itemidx = "CREATE INDEX IF NOT EXISTS itemIndex ON orders (description ASC)"
        #ownidx = "CREATE INDEX IF NOT EXISTS ownIndex ON orders (owner ASC)"
        self.conn.execute(tblstmt)
        #self.conn.execute(itemidx)
        #self.conn.execute(ownidx)
        self.conn.commit()
        for row in self.conn.execute('SELECT * FROM orders'):
            print(row)
        

    def add_item(self, item_text, owner, number):
        stmt = "INSERT INTO orders (description, owner, number) VALUES (?, ?, ?)"
        args = (item_text, owner, number)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_item(self, item_text, owner):
        stmt = "DELETE FROM orders WHERE description = (?) AND owner = (?)"
        args = (item_text, owner)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_items(self):
        stmt = "SELECT description, owner, number FROM orders"
        return [x[0] for x in self.conn.execute(stmt)]
    
    def get_cursor_fetch(self):
        stmt = "SELECT description FROM orders"
        cursor = self.conn.cursor()
        return cursor.fetchall()
    
