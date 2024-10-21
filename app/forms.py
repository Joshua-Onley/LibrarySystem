from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, BooleanField, FloatField
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError, optional
from app.models import Student, Loan, Device, BookLoan, Book
from sqlalchemy import and_


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirmpassword = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


class AddStudentForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    firstname = StringField('Firstname')
    lastname = StringField('Lastname', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Add Student')

    def validate_username(self, username):
        if Student.query.filter_by(username=username.data).first():
            raise ValidationError('This username is already taken. Please choose another')

    def validate_email(self, email):
        if Student.query.filter_by(email=email.data).first():
            raise ValidationError('This email address is already registered. Please choose another')


class BorrowForm(FlaskForm):
    student_id = StringField('Student ID', validators=[DataRequired()])
    device_id = StringField('Device ID', validators=[DataRequired()])
    submit = SubmitField('Borrow Device')

    def validate_student_id(self, student_id):
        if not student_id.data.isnumeric():
            raise ValidationError('This must be a positive integer')
        student = Student.query.get(student_id.data)
        if not (student):
            raise ValidationError('There is no student with this id in the system')
        if not student.active:
            raise ValidationError('This student has been dactivated and cannot borrow devices')
        if Loan.query.filter(
                    (Loan.student_id == student_id.data)
                    &
                    # (Loan.returndatetime.is_(None))
                    (Loan.returndatetime.is_(None))
                ).first():
            raise ValidationError('This student cannot borrow another item until the previous loan has been returned')

    def validate_device_id(self, device_id):
        if not device_id.data.isnumeric():
            raise ValidationError('This must be a positive integer')
        if Device.query.filter(
                    (Device.device_id == device_id.data)
                    &
                    (Device.device_quantity <= 0)
                ).first():
            raise ValidationError(f'There are no more of these devices available to loan. Please wait unitl one is returned')
        if not Device.query.filter_by(device_id=device_id.data).first():
            raise ValidationError('this device does not exist')

class DeactivateStudentForm(FlaskForm):
    student_id = StringField('Student ID', validators=[DataRequired()])
    submit = SubmitField('Deactivate Student')

    def validate_student_id(self, student_id):
        if not student_id.data.isnumeric():
            raise ValidationError('This must be a positive integer')
        student = Student.query.get(student_id.data)
        if not student:
            raise ValidationError('There is no student with this id in the system')
        if not student.active:
            raise ValidationError('This student has already been deactivated')


class AddDeviceForm(FlaskForm):
    device_name = StringField('enter the device name', validators=[DataRequired()])
    loan_period = IntegerField('enter number of days this device can be loaned for'
                               ' (if this device already exists in the table leave this empty)', validators=[optional()])
    submit = SubmitField('add device')


class ReturnForm(FlaskForm):
    device_id = IntegerField('enter the device ID of the device that you want to return')
    student_id = IntegerField('enter your student ID')
    submit = SubmitField('submit')

    def validate_student_id(self, student_id):
        if not Student.query.filter_by(student_id=student_id.data).first():
            raise ValidationError('this student does not exist')



    def validate_device_id(self, device_id):

        if not Device.query.filter_by(device_id=device_id.data).first():
            raise ValidationError('this device does not exist')

        if not Loan.query.filter(
                (Loan.device_id==device_id.data)
            &
                (Loan.returndatetime.is_(None)
        )).first():
            raise ValidationError('this device is not currently on loan')



class AddBookForm(FlaskForm):
    book_title = StringField('Enter the title of the book', validators=[DataRequired()])
    author_firstname = StringField('Enter the authors first name', validators=[DataRequired()])
    author_lastname = StringField('Enter the authors last name', validators=[DataRequired()])
    number_of_pages = IntegerField('Enter the number of pages the book has', validators=[DataRequired()])
    submit = SubmitField('add book')






class PayFineForm(FlaskForm):
    student_id = StringField('enter your student ID', validators=[DataRequired()])
    amount = FloatField('enter the amount you would like to pay', validators=[DataRequired()])
    submit = SubmitField('pay fine')

    def validate_student_id(self, student_id):

        # find the student associated with the entered student ID
        student = Student.query.filter_by(student_id=student_id.data).first()

        # if there is no student associated with the entered student ID then raise an error
        if not student:
            raise ValidationError('This student does not exist in the students table')

        # if the student associated with the entered student ID has no outstanding fines raise an error
        if student.fines == 0:
            raise ValidationError('This student has no outstanding fines')

    def validate_amount(self, amount):

        # find the student associated with the entered student ID
        student = Student.query.filter_by(student_id=self.student_id.data).first()

        # if the amount entered is greater than the amount the student owes raise an error
        if student:
            if student.fines != '0.0':
                if float(self.amount.data) > float(student.fines):
                    raise ValidationError('this student owes less than the amount entered')


class SearchStudentForm(FlaskForm):
    query = StringField('Enter the students firstname, lastname, or username', validators=[DataRequired()])
    submit = SubmitField('Search')


class DeleteStudentForm(FlaskForm):
    student_id = IntegerField('Student ID', validators=[DataRequired()])
    submit = SubmitField('Delete Student')

    def validate_student_id(self, student_id):
        student = Student.query.filter_by(student_id=student_id.data).first()

        if not student:
            raise ValidationError('this student does not exist')



class StudentLoanReportForm(FlaskForm):
    student_id = IntegerField('Student ID', validators=[DataRequired()])
    submit = SubmitField('Generate Report')

    def validate_student_id(self, student_id):
        if not Student.query.filter_by(student_id=student_id.data).first():
            raise ValidationError('this student does not exist')
        elif not (Loan.query.filter_by(student_id=student_id.data).first() or BookLoan.query.filter_by(student_id=student_id.data).first()):
            raise ValidationError('this student has no loan records')


class DeviceLoanReportForm(FlaskForm):
    device_id = IntegerField('Device ID', validators=[DataRequired()])
    submit = SubmitField('Generate Report')

    def validate_device_id(self, device_id):
        if not Device.query.filter_by(device_id=device_id.data).first():
            raise ValidationError('this device does not exist')
        elif not Loan.query.filter_by(device_id=device_id.data).first():
            raise ValidationError('this device has no loan history')


class RemoveStudentLoansForm(FlaskForm):
    student_id = IntegerField('Enter the student ID to clear their loan records')
    submit = SubmitField('confirm')

    def validate_student_id(self, student_id):
        if not Student.query.filter_by(student_id=student_id.data).first():
            raise ValidationError('this student does not exist')

        if not Loan.query.filter_by(student_id=student_id.data).first():
            raise ValidationError('there are no loans associated with this student ID')


class ActivateStudent(FlaskForm):
    student_id = IntegerField('Enter the student ID of the student that you want to activate', validators=[DataRequired()])
    submit = SubmitField('activate student')

    def validate_student_id(self, student_id):
        if not Student.query.filter_by(student_id=student_id.data).first():
            raise ValidationError('this student does not exist')

        if Student.query.filter((Student.student_id == student_id.data) & (Student.active == True)).first():
            raise ValidationError('this student is already an active student')


class BorrowBookForm(FlaskForm):
    student_id = StringField('Student ID', validators=[DataRequired()])
    book_id = StringField('Book ID', validators=[DataRequired()])
    submit = SubmitField('Borrow Book')

    def validate_student_id(self, student_id):
        if not student_id.data.isnumeric():
            raise ValidationError('This must be a positive integer')
        student = Student.query.get(student_id.data)
        if not (student):
            raise ValidationError('There is no student with this id in the system')
        if not student.active:
            raise ValidationError('This student has been deactivated and cannot borrow')
        if len(BookLoan.query.filter(
                    (BookLoan.student_id == student_id.data)
                    &
                    (BookLoan.returndatetime.is_(None))
                ).all()) >= 2:
            raise ValidationError('This student has reached their maximum loan limit. Please return a book before attempting to loan another one')

    def validate_book_id(self, book_id):
        if not book_id.data.isnumeric():
            raise ValidationError('This must be a positive integer')
        if Book.query.filter(
                    (Book.book_id == book_id.data)
                    &
                    (Book.quantity <= 0)
                ).first():
            raise ValidationError(f'There are no more copies of this book available to loan. Please wait unitl one is returned')
        if not Book.query.filter_by(book_id=book_id.data).first():
            raise ValidationError('this book does not exist')



class BookReturnForm(FlaskForm):
    book_id = IntegerField('enter the book ID of the book that you want to return')
    student_id = IntegerField('enter your student ID')
    submit = SubmitField('submit')

    def validate_student_id(self, student_id):
        if not Student.query.filter_by(student_id=student_id.data).first():
            raise ValidationError('this student does not exist')


    def validate_book_id(self, book_id):

        if not Book.query.filter_by(book_id=book_id.data).first():
            raise ValidationError('this book does not exist')

        if not BookLoan.query.filter(
                (BookLoan.book_id==book_id.data)
            &
                (BookLoan.returndatetime.is_(None)
        )).first():
            raise ValidationError('this book is not currently on loan')

class BookSearchForm(FlaskForm):
    title = StringField('Title')
    author = StringField('Author')
    genre = StringField('Genre')
    submit = SubmitField('Search')



class RemoveBookForm(FlaskForm):
    book_id = IntegerField('Enter the book ID')
    submit = SubmitField('DELETE')

    def validate_book_id(self, book_id):
        if not Book.query.filter_by(book_id=book_id.data).first():
            raise ValidationError('This book does not exist in the book database')


class RemoveBookLoanForm(FlaskForm):
    book_id = IntegerField('Enter the book ID')
    submit = SubmitField('Remove')

    def validate_book_id(self, book_id):
        if not Book.query.filter_by(book_id=book_id.data).first():
            raise ValidationError('This book does not exist in the book database')


