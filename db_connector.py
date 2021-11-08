from sqlalchemy import create_engine, Column, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import sqlalchemy.dialects.mysql as my
import simplejson as json
import os, socket
from datetime import datetime

project_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),'db')
Base = declarative_base()
Session = sessionmaker()

class Books(Base):
    """
    Books table to hold books inventory information
    A book inventory item consists, of the following attributes: Inventory ID, Author, Title,
    and Published Date: sample data
    {"id": 12345, "author": "John Doe", "title": "Awesome Novel", "published_date": "1980-02-15"}
    """
    __tablename__ = 'books'

    book_id = Column(my.INTEGER(unsigned=True), primary_key=True, autoincrement=True,nullable=False)
    book_author = Column(my.VARCHAR(128),nullable=False)
    book_title = Column(my.VARCHAR(128),nullable=False)
    book_published_date = Column(my.VARCHAR(128),nullable=False)
    book_added_date = Column(my.DATETIME)
    book_updated_date = Column(my.DATETIME)

class User(Base):
    """
    User table to hold user information
    """
    __tablename__ = 'user'

    user_id =  Column(my.INTEGER(unsigned=True), primary_key=True, autoincrement=True,nullable=False)
    user_name = Column(my.VARCHAR(64),nullable=False)
    user_email = Column(my.VARCHAR(64),nullable=False)
    user_password = Column(my.VARCHAR(64),nullable=False)
    is_admin = Column(my.BOOLEAN,nullable=False)
    is_super_user = Column(my.BOOLEAN,nullable=False)
    is_active = Column(my.BOOLEAN)
    last_login = Column(my.DATETIME)
    date_joined = Column(my.DATETIME)

class BooksInventory:
    """
    Contains the interface for DB

    """
    def __init__(self, mode=None):
        """
        :param mode: Override mode, for testing only.
        """
        self.engine = create_engine(get_sql_client(mode=mode))
        self._id = None

        # Create missing tables
        table_checklist = [
            'user','books'
        ]

        available_tables =  self.engine.table_names()
        for t in table_checklist:
            if t not in available_tables:
                self.setup_booksinv_db()  # Creates any missing tables
                break

        # Session for upcoming checks
        session = Session(bind=self.engine)

    def complete_table(self):
        """
        :return: Complete records from the table User
        """
        session = Session(bind=self.engine)
        q = session.query(Books)
        res = {}
        for r in q:
            res[r.book_id] = {'Book Id': r.book_id, 'Book Name': str(r.book_title), 'Book Author': str(r.book_author),
                               'Published On': r.book_published_date,'Date_Added': str(r.book_added_date), 'Updated_Datetime': str(r.book_updated_date)}
        return res
    def add_book_details(self, **kwargs):
        """
        Adds all records per below parameters to database
        **kwargs
        :param book_id:
        :param book_author:
        :param book_title:
        :param book_published_date:
        :param book_added_date:
        :return: True of False on the success of query commit
        """
        session = Session(bind=self.engine)
        entry = Books(**kwargs)
        try:
            session.add(entry)
            session.commit()
            res = True
        except Exception as e:
            res=False
            session.close()
        return res
    def add_user_details(self, **kwargs):
        """
        Adds all records per below parameters to database
        **kwargs
        :param book_id:
        :param book_author:
        :param book_title:
        :param book_published_date:
        :param book_added_date:
        :return: True of False on the success of query commit
        """
        session = Session(bind=self.engine)
        entry = User(**kwargs)
        try:
            session.add(entry)
            session.commit()
            res = True
        except Exception as e:
            res=False
            session.close()
        return res
    def get_all(self,uname,passwd,date):
        """
        Get all information from User table as per below parameters
        :param uname:
        :param passwd:
        :param date:
        :return: json structure with user_id and name
        """
        session = Session(bind=self.engine)
        q = session.query(User).filter_by(user_name=uname)
        res = {}
        for r in q:
            if r.last_login:
                r.last_login = date
                session.commit()
            if r.user_password == str(passwd):
                res={'user_id': r.user_id, 'name': r.user_name}
        return res
    def update_book(self,**kwargs):
        """
        Updates the records per below parameters
        :param id:
        :param name:
        :param issuper:
        :param isadmin:
        :return: True of False on the success of query commit
        """
        session = Session(bind=self.engine)
        # q = session.query(Books).filter_by(book_id=kwargs['book_id'])
        # for r in q:
        #     if issuper!=None:
        #         r.is_super_user = issuper
        #     if isadmin!=None:
        #         r.is_admin = isadmin
        try:
            q = session.query(Books).filter_by(book_id=kwargs['book_id']).update(kwargs)
            session.commit()
            session.close()
            return True
        except Exception as e:
            print(e)
            return False
    def read_book_byid(self, **kwargs):
        """
        Read book information by id
        :param kwargs:
        :return:
        """
        session = Session(bind=self.engine)
        q = session.query(Books).filter_by(book_id=kwargs['book_id'])
        res = {}
        try:
            for r in q:
                res[r.book_id] = {'Book Id': r.book_id, 'Book Name': str(r.book_title), 'Book Author': str(r.book_author),
                               'Date_Added': r.book_added_date, 'Updated_Datetime': str(r.book_updated_date)}
        except Exception as e:
            res = str(e)
        return res
    def del_rec(self,id):
        """
        delete record as per book id
        :param id:
        :return: True or False on the success of query commit
        """
        session = Session(bind=self.engine)

        try:
            q = session.query(Books).filter(Books.book_id==int(id)).delete()
            session.commit()
            return True
        except Exception as e:
            return False
    def setup_booksinv_db(self):
        """
        Create database scheme.
        """
        print('Creating database schema')
        Base.metadata.create_all(self.engine)
    def setup_user_db(self):
        """
        Create user database schema
        :return: None
        """
        print('Creating user database schema')
        Base.metadata.create_all(self.engine)
def get_sql_client(mode=None):
    """
    Returns SQL alchemy connection string
    :param mode: To define the environment where the script is running
    :return:
    """
    if mode is None:
        mode = 'local'

    if mode == 'local':
        mysql_con_str = 'sqlite:///{}'.format(os.path.join(project_dir, 'db.sqlite3'))
        return mysql_con_str
    else:
        hostname = socket.gethostname().lower()
        raise KeyError("sql connections is not allowed on host {0}".format(
            hostname))

if __name__ == '__main__':
    db = BooksInventory()
    db.setup_booksinv_db()
    db.setup_user_db()
    # paramas = {'book_id': 12121 ,
    #             'book_author': "Lin Doe",
    #             'book_title': "Awesome Novel",
    #             'book_published_date': "1980-02-15",
    #             'book_added_date': datetime.now().date(),
    #             'book_updated_date': datetime.now().date()}
    # add = db.add_book_details(**paramas)
    # paramas = {
    #     'book_id': 12345,
    #     'book_author': "John van Doe",
    #     'book_published_date': "1990-02-15",
    #     'book_updated_date' : datetime.now()
    # }
    # update = db.update_book(**paramas)
    # paramas = {'book_id': 12345}
    # res_by_id = db.read_book_byid(**paramas)
    # res_del_byid = db.del_rec(id = 12121)
    # res = db.complete_table()
    print(res)