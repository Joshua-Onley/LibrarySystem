from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    username = db.Column(db.String(20), nullable=False, unique=True, index=True)
    email = db.Column(db.String(64), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, salt_length=32)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    
    def get_id(self):
        return str(self.user_id)

    def __repr__(self):
        return f"user(id='{self.user_id}', '{self.username}', '{self.email}')"

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Student(db.Model):
    __tablename__ = 'students'
    student_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    username = db.Column(db.String(20), nullable=False, unique=True, index=True)
    firstname = db.Column(db.String(32))
    lastname = db.Column(db.String(32), nullable=False, index=True)
    email = db.Column(db.String(64), nullable=False, unique=True, index=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    fines = db.Column(db.String(32), nullable=False, default='0.0')
    loans = db.relationship('Loan', backref='student', lazy='dynamic')

    @property
    def active_loans(self):
        return Loan.query.filter_by(student_id=self.student_id, returndatetime=None).all()

    def __repr__(self):
        return f"student(id='{self.student_id}', '{self.username}', '{self.lastname}', '{self.firstname}' , '{self.email}', active='{self.active}')"


class Loan(db.Model):
    __tablename__ = 'loans'
    loan_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    device_id = db.Column(db.Integer, nullable=False)
    borrowdatetime = db.Column(db.DateTime, nullable=False)
    duedatetime = db.Column(db.DateTime, nullable=False)
    returndatetime = db.Column(db.DateTime, nullable=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    fine = db.Column(db.String(32), nullable=False, default='0.0')

    def __repr__(self):
        return f"loan(loan_id='{self.loan_id}', device_id='{self.device_id}', borrowdatetime='{self.borrowdatetime}', returndatetime='{self.returndatetime}', '{self.student}')"


class Device(db.Model):
    __tablename__ = 'devices'
    device_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    device_name = db.Column(db.String(16), unique=True, nullable=False)
    device_quantity = db.Column(db.Integer, nullable=False, default=1)
    loan_period = db.Column(db.Integer, nullable=True, default=30)


    def __repr__(self):
        return f"device(device_id='{self.device_id}', device_name='{self.device_name}', device_quantity='{self.device_quantity}"


class Book(db.Model):
    __tablename__ = 'books'
    book_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    book_title = db.Column(db.String, nullable=False)
    author_firstname = db.Column(db.String(32), db.ForeignKey('authors.author_firstname'), nullable=False)
    author_lastname = db.Column(db.String(32), db.ForeignKey('authors.author_lastname'), nullable=False)
    number_of_pages = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, default=1)
    loan_period = db.Column(db.Integer, nullable=True, default=30)
    genre = db.Column(db.String(32), nullable=True)

    def __repr__(self):
        return f"book('{self.book_title}', '{self.book_author}', '{self.number_of_pages}', '{self.quantity}')"

class Author(db.Model):
    __tablename__ = 'authors'
    author_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    author_firstname = db.Column(db.String(16))
    author_lastname = db.Column(db.String(16))

    def __repr__(self):
        return f"author('{self.author_firstname}', '{self.author_lastname}')"

class BookLoan(db.Model):
    __tablename__ = 'book loans'
    loan_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    book_id = db.Column(db.Integer, nullable=False)
    borrowdatetime = db.Column(db.DateTime, nullable=False)
    duedatetime = db.Column(db.DateTime, nullable=False)
    returndatetime = db.Column(db.DateTime, nullable=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    fine_amount = db.Column(db.String(32), nullable=True, default='0.0')
    student = db.relationship("Student", backref="book_loans")

    def __repr__(self):
        return f"book loan('{self.book_id}', '{self.borrowdatetime}' , '{self.returndatetime}', '{self.student_id}')"
