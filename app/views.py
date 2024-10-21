from flask import render_template, redirect, url_for, flash, request, current_app
from app import app, db
from datetime import datetime, timedelta
from app.forms import (LoginForm, RegistrationForm, AddStudentForm, BorrowForm,
                       DeactivateStudentForm, AddDeviceForm, ReturnForm, PayFineForm,
                       SearchStudentForm, DeleteStudentForm, StudentLoanReportForm,
                       DeviceLoanReportForm, RemoveStudentLoansForm, ActivateStudent, AddBookForm,
                       BorrowBookForm, BookReturnForm, BookSearchForm, RemoveBookForm, RemoveBookLoanForm)
from app.models import Student, Loan, User, Device, Book, BookLoan, Author
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlsplit
from werkzeug.security import generate_password_hash



def calculate_fine(due_time, return_time, fine_per_second=0.50):

    # used seconds instead of days for testing purposes
    # calculate how late the device/book has been returned
    seconds_late = (return_time - due_time).seconds

    # multiply the number of seconds late by the fine rate
    fine_amount = fine_per_second * seconds_late

    if fine_amount > 50:
        fine_amount = 50

    return str(fine_amount)


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')



@app.route('/listStudents')
@login_required
def listStudents():
    students = Student.query.all()
    return render_template('listStudents.html', title='List Students', students=students)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        flash(f'Login for {form.username.data}', 'success')
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data, email=form.email.data,
                        password_hash=generate_password_hash(form.password.data, salt_length=32))
        db.session.add(new_user)

        try:
            db.session.commit()
            flash(f'Registration for {form.username.data} received', 'success')
            return redirect(url_for('index'))

        except:
            db.session.rollback()
            flash('error', 'danger')
            return redirect(url_for('index'))

    return render_template('registration.html', title='Register', form=form)


@app.route('/add_student', methods=['GET', 'POST'])
@login_required
def add_student():
    form = AddStudentForm()
    if form.validate_on_submit():
        new_student = Student(username=form.username.data, firstname=form.firstname.data,
                              lastname=form.lastname.data, email=form.email.data)
        db.session.add(new_student)
        try:
            db.session.commit()
            flash(f'New Student added: {form.username.data} received', 'success')
            return redirect(url_for('index'))

        except:
            db.session.rollback()
            if Student.query.filter_by(username=form.username.data).first():
                form.username.errors.append('This username is already taken. Please choose another')
            if Student.query.filter_by(email=form.email.data).first():
                form.email.errors.append('This email address is already registered. Please choose another')
    return render_template('add_student.html', title='Add Student', form=form)


@app.route('/borrow', methods=['GET', 'POST'])
@login_required
def borrow():
    form = BorrowForm()
    if form.validate_on_submit():

        # find the device associated with the entered device ID
        device = Device.query.filter_by(device_id=form.device_id.data).first()

        # decrement the quantity of the device being borrowed
        if device:
            device.device_quantity -= 1
            new_loan = Loan(device_id=form.device_id.data,
                            student_id=form.student_id.data,
                            borrowdatetime=datetime.now(), duedatetime=datetime.now() + timedelta(seconds=device.loan_period))

            db.session.add(new_loan)

            try:
                db.session.commit()
                flash(f'New Loan added. You must return this device within {device.loan_period} seconds to avoid a fine', 'success')
                return redirect(url_for('index'))
            except:
                db.session.rollback()
                flash('unsuccessful', 'danger')
                return redirect((url_for('index')))

        # if the device ID entered has no associated device in the table give an error message
        if not device:
            flash('this device does not exist', 'danger')
            return redirect(url_for('index'))

    return render_template('borrow.html', title='Borrow', form=form)




@app.route('/deactivate', methods=['GET', 'POST'])
@login_required
def deactivateStudent():
    form = DeactivateStudentForm()
    if form.validate_on_submit():
        student = Student.query.get(form.student_id.data)
        student.active = False
        db.session.add(student)
        try:
            db.session.commit()
            flash(f'student {student.student_id} deactivated', 'success')
            return redirect(url_for('index'))
        except:
            db.session.rollback()
    return render_template('deactivateStudent.html', title='Deactivate Student', form=form)

@app.route('/see_available_devices', methods=['GET', 'POST'])
@login_required
def see_available_devices():
    device_table = Device.query.filter(Device.device_quantity >= 1).all()
    return render_template('see_available_devices.html', device_table=device_table)


@app.route('/add_device', methods=['GET', 'POST'])
@login_required
def add_device():
    form = AddDeviceForm()

    if form.validate_on_submit():

        # see if there is already a device with the entered device name
        existing_device = Device.query.filter_by(device_name=form.device_name.data).first()

        if existing_device:

            # if the device being added already exists increment quantity
            existing_device.device_quantity += 1

            try:
                db.session.commit()
                flash('this device already exists in the devices table.'
                    ' Its quantity has been incremented','success')
                return redirect(url_for('index'))
            except:
                db.session.rollback()
                flash('there was an error adding this device', 'danger')
                return redirect(url_for('index'))

        # if the device does not already exist in the table set the loan_period to whatever is entered in the form
        elif not existing_device:
            device_to_be_added = Device(device_name=form.device_name.data, loan_period=form.loan_period.data)
            db.session.add(device_to_be_added)

        try:
            db.session.commit()
            flash('device successfully added', 'success')
            return redirect(url_for('index'))

        except:
            db.session.rollback()
            flash('unsuccessful', 'danger')
            return redirect(url_for('index'))

    return render_template("add_device.html", form=form)


@app.route('/return_device', methods=['GET', 'POST'])
@login_required
def return_device():
    form = ReturnForm()
    if form.validate_on_submit():

        # find the relevant loan record and device record
        loan_record = Loan.query.filter(
            (Loan.device_id==form.device_id.data)
            &
            (Loan.student_id==form.student_id.data)
            &
            (Loan.returndatetime).is_(None)).first()

        device_record = Device.query.filter_by(device_id=form.device_id.data).first()

        # set the returndatetime of the relevant loan record to the current time
        if loan_record:
            loan_record.returndatetime = datetime.now()

        # increase the quantity of the relevant device by 1
        if device_record:
            device_record.device_quantity += 1

        # if the device is returned late, calculate a fine based on how late the device was returned
        if loan_record.returndatetime > loan_record.duedatetime:
            fine = calculate_fine(loan_record.duedatetime, loan_record.returndatetime)

            # find the relevant student to fine and update their fines attribute
            student_to_fine = Student.query.filter_by(student_id=form.student_id.data).first()
            student_to_fine.fines = str(float(student_to_fine.fines) + float(fine))
            loan_record.fine = str(fine)

            try:
                db.session.commit()
                flash(f'you have returned this device({device_record.device_name}) {(loan_record.returndatetime - loan_record.duedatetime).seconds} seconds late'
                      f' and will be fined £{fine}', 'danger')

                return redirect(url_for('index'))
            except:
                db.session.rollback()
                flash('the student could not be fined', 'danger')
                return redirect(url_for('index'))

        # if the device is returned on time
        else:
            try:
                db.session.commit()
                flash(f'you have successfully returned this device ({device_record.device_name})'
                      f' on time and you will receive no fine', 'success')

                return redirect(url_for('index'))
            except:
                db.session.rollback()
                flash(f'the device could not be returned')
                return redirect(url_for('index'))

    return render_template('return_device.html', form=form)



@app.route('/show_outstanding_fines')
@login_required
def show_outstanding_fines():

    outstanding_fines = Student.query.filter(Student.fines != '0.0').all()

    return render_template('show_outstanding_fines.html', outstanding_fines=outstanding_fines)


@app.route('/pay_fine', methods=['GET', 'POST'])
def pay_fine():

    form = PayFineForm()

    if form.validate_on_submit():

        # find the student associated with the entered student ID
        student = Student.query.filter_by(student_id=form.student_id.data).first()

        # find out how much this student owes
        remaining_fine_to_be_payed = float(student.fines)

        # calculate how much they owe after paying (they don't have to pay their entire fine in one go)
        fine_after_pay = remaining_fine_to_be_payed - float(form.amount.data)

        # update their fine in the table
        student.fines = str(fine_after_pay)

        try:
            db.session.commit()
            flash(f'you have successfully payed £{form.amount.data} out of the £{remaining_fine_to_be_payed}'
                  f' that you owe. You now owe £{fine_after_pay}', 'success')

            return redirect(url_for('index'))

        except Exception as e:
            db.session.rollback()
            flash(f'{e}')
            return redirect(url_for('index'))

    return render_template('pay_fine.html', form=form)


@app.route('/search_students', methods=['GET', 'POST'])
@login_required
def search_students():
    form = SearchStudentForm()

    if form.validate_on_submit():
        # Get the search query from the form
        search_query = form.query.data

        # case-insensitive search for students whose username or name matches the search
        search_results = Student.query.filter(
                (Student.username.ilike(f'%{search_query}%')) |
                (Student.firstname.ilike(f'%{search_query}%')) |
                (Student.lastname.ilike(f'%{search_query}%'))
            ).all()

        return render_template('search_students.html', form=form, search_results=search_results, search_query=search_query)

    # If form is not submitted or validation fails, return an empty list of results
    search_results = []
    return render_template('search_students.html',form=form, search_results=search_results)


@app.route('/delete_student', methods=['GET', 'POST'])
@login_required
def delete_student():

    form = DeleteStudentForm()

    if form.validate_on_submit():
        student_id = form.student_id.data
        student_to_delete = Student.query.filter_by(student_id=student_id).one_or_none()
        if Loan.query.filter_by(student_id=student_id).first():
            flash('This Student could not be deleted because they have active loans.'
                  ' Please clear their loan records and try again', 'danger')
            return redirect(url_for('index'))

        if student_to_delete:
            try:
                db.session.delete(student_to_delete)
                db.session.commit()
                flash('Student successfully deleted', 'success')
            except:
                db.session.rollback()
                flash('student cannot be deleted', 'danger')
        else:
            flash('Student not found', 'error')
            return redirect(url_for('index'))

    return render_template('delete_student.html', form=form)


@app.route('/student_loan_report', methods=['GET', 'POST'])
@login_required
def student_loan_report():
    form = StudentLoanReportForm()

    if form.validate_on_submit():
        student_loans = Loan.query.filter_by(student_id=form.student_id.data)
        student_book_loans = BookLoan.query.filter_by(student_id=form.student_id.data)
        return render_template('student_loan_report.html', form=form,
                               student_loans=student_loans, student_book_loans=student_book_loans)

    return render_template('student_loan_report.html', form=form)


@app.route('/clear tables')
def clear_tables():
    db.drop_all()
    db.create_all()
    try:
        db.session.commit()
        flash('all tables have been cleared', 'success')
        return redirect(url_for('index'))

    except:
        db.session.rollback()
        flash('error clearing tables', 'danger')
        return redirect(url_for('index'))


@app.route('/device_loan_history', methods=['GET', 'POST'])
@login_required
def device_loan_history():
    form = DeviceLoanReportForm()

    if form.validate_on_submit():
        device_loans = Loan.query.filter_by(device_id=form.device_id.data).all()

        return render_template('device_loan_report.html', form=form, device_loans=device_loans)

    return render_template("device_loan_report.html", form=form)


@app.route('/all_loans')
@login_required
def all_loans():
    loans = Loan.query.all()

    return render_template('all_loans.html', loans=loans)


@app.route('/remove_student_loan_records', methods=['GET', 'POST'])
@login_required
def remove_student_loan_records():
    form = RemoveStudentLoansForm()

    if form.validate_on_submit():

        loans_to_be_deleted = Loan.query.filter_by(student_id=form.student_id.data).all()
        BookLoan.query.filter_by(student_id=form.student_id.data).delete()

        for loan in loans_to_be_deleted:
            db.session.delete(loan)

        try:
            db.session.commit()
            flash('Loan records successfully deleted', 'success')
            return redirect(url_for('index'))

        except:
            db.session.rollback()
            flash('there was an error', 'danger')
            return redirect(url_for('index'))

    return render_template('remove_student_loans.html', form=form)

@app.route('/activate_student', methods=['GET', 'POST'])
@login_required
def activate_student():
    form = ActivateStudent()

    if form.validate_on_submit():
        student_to_be_edited = Student.query.get(form.student_id.data)
        print(student_to_be_edited)
        if student_to_be_edited:
            student_to_be_edited.active = True

            try:
                db.session.commit()
                flash(f'successful activation of student {form.student_id.data}', 'success')
                return redirect(url_for('index'))

            except:
                db.session.rollback()
                if Student.query.filter_by(student_id=form.student_id.data).first():
                    form.student_id.errors.append('this student doesnt exist')
                    return redirect(url_for('index'))

                if Student.query.filter((Student.student_id == form.student_id.data) & (Student.active == True)).first():
                    form.student_id.errors.append('this student is already active')
                    return redirect(url_for('index'))

    return render_template('activate_student.html', form=form)


@app.route('/active_loans')
@login_required
def active_loans():

    all_active_loans = Loan.query.filter(Loan.returndatetime.is_(None)).all()

    return render_template('active_loans.html', all_active_loans=all_active_loans)


@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    form = AddBookForm()

    if form.validate_on_submit():

        existing_book = Book.query.filter(
                (Book.book_title == form.book_title.data)
        ).first()

        if existing_book:
            existing_book.quantity += 1
            flash('This book is already in the database. Its quantity has been increased by 1', 'success')
            db.session.commit()
            return redirect(url_for('index'))

        else:

            new_book = Book(
                book_title=form.book_title.data,
                author_firstname=form.author_firstname.data,
                author_lastname=form.author_lastname.data,
                number_of_pages=form.number_of_pages.data,
                quantity=1
            )

            new_author = Author(
                author_firstname=form.author_firstname.data,
                author_lastname=form.author_lastname.data
            )
            db.session.add(new_book)
            db.session.add(new_author)

        try:
            db.session.commit()
            flash('Book successfully added', 'success')
            return redirect(url_for('index'))
        except:
            db.session.rollback()
            flash('There was an error', 'danger')
            return redirect(url_for('index'))

    return render_template('add_book.html', form=form)



@app.route("/available_books")
@login_required
def available_books():

    all_available_books = Book.query.filter(
        (Book.quantity > 0)
    ).all()

    return render_template('available_books.html', all_available_books=all_available_books)

@app.route('/borrow_book', methods=['GET', 'POST'])
@login_required
def borrow_book():
    form = BorrowBookForm()
    if form.validate_on_submit():

        # find the book associated with the entered device ID
        book = Book.query.filter_by(book_id=form.book_id.data).first()

        # decrement the quantity of the book being borrowed
        if book:
            book.quantity -= 1
            new_loan = BookLoan(book_id=form.book_id.data,
                            student_id=form.student_id.data,
                            borrowdatetime=datetime.now(), duedatetime=datetime.now() + timedelta(seconds=book.loan_period))

            db.session.add(new_loan)

            try:
                db.session.commit()
                flash(f'New Loan added', 'success')
                return redirect(url_for('index'))
            except:
                db.session.rollback()
                flash('unsuccessful', 'danger')
                return redirect((url_for('index')))

        # if the book ID entered has no associated book in the table give an error message
        if not Book:
            flash('this book does not exist', 'danger')
            return redirect(url_for('index'))

    return render_template('borrow_book.html', title='BorrowBook', form=form)



@app.route('/populate_books_db')
@login_required
def populate_books_db():

    if len(Book.query.all()) > 5:
        flash("Book table is already populated with data", "danger")
        return redirect(url_for('index'))

    with open('app/data/books.txt', 'r') as file:
        book_info = file.read().split('\n\n')

        for book in book_info:
            lines = book.split('\n')
            title = lines[0].split(': ')[1]
            author_full_name = lines[1].split(': ')[1].strip()
            author_names = author_full_name.split()
            if len(author_names) == 2:
                author_first_name, author_last_name = author_names
            else:
                author_first_name = author_full_name
                author_last_name = ""

            genre = lines[2].split(': ')[1]
            pages = int(lines[3].split(': ')[1])

            new_book = Book(
                book_title=title,
                author_firstname=author_first_name,
                author_lastname=author_last_name,
                number_of_pages=pages,
                genre=genre,
                quantity=1
            )

            existing_author = Author.query.filter_by(author_firstname=author_first_name, author_lastname=author_last_name).first()
            if not existing_author:
                new_author = Author(author_firstname=author_first_name, author_lastname=author_last_name)
                db.session.add(new_author)

            db.session.add(new_book)

        try:
            db.session.commit()
            flash("Database successfully populated with book data", "success")
        except Exception as e:
            db.session.rollback()
            print(f"Error populating database: {e}")

    return redirect(url_for('index'))


@app.route('/return_book', methods=['GET', 'POST'])
@login_required
def return_book():
    form = BookReturnForm()
    if form.validate_on_submit():

        loan_record = BookLoan.query.filter(
            (BookLoan.book_id==form.book_id.data)
            &
            (BookLoan.student_id==form.student_id.data)
            &
            (BookLoan.returndatetime).is_(None)).first()

        book_record = Book.query.filter_by(book_id=form.book_id.data).first()

        # set the returndatetime of the relevant loan record to the current time
        if loan_record:
            loan_record.returndatetime = datetime.now()

        # increase the quantity of the relevant device by 1
        if book_record:
            book_record.quantity += 1

        # if the device is returned late, calculate a fine based on how late the device was returned
        if loan_record.returndatetime > loan_record.duedatetime:
            fine = calculate_fine(loan_record.duedatetime, loan_record.returndatetime)

            # find the relevant student to fine and update their fines attribute
            student_to_fine = Student.query.filter_by(student_id=form.student_id.data).first()
            student_to_fine.fines = str(float(student_to_fine.fines) + float(fine))
            loan_record.fine_amount = str(fine)

            try:
                db.session.commit()
                flash(f'you have returned this book({book_record.book_title}) {(loan_record.returndatetime - loan_record.duedatetime).seconds} seconds late'
                      f' and will be fined £{fine}', 'danger')

                return redirect(url_for('index'))
            except:
                db.session.rollback()
                flash('the student could not be fined', 'danger')
                return redirect(url_for('index'))


        else:
            try:
                db.session.commit()
                flash(f'you have successfully returned {book_record.book_title}'
                      f' on time and you will receive no fine', 'success')

                return redirect(url_for('index'))
            except:
                db.session.rollback()
                flash(f'the book could not be returned')
                return redirect(url_for('index'))

    return render_template('return_book.html', form=form)


@app.route('/search_books', methods=['GET', 'POST'])
@login_required
def search_books():
    form = BookSearchForm()
    books = []

    if form.validate_on_submit():

        title = form.title.data
        author = form.author.data
        genre = form.genre.data

        if title:
            books += Book.query.filter(Book.book_title.ilike(f'%{title}%')).all()
        if author:
            books += Book.query.filter(
                (Book.author_firstname.ilike(f'%{author}%')) | (Book.author_lastname.ilike(f'%{author}%'))
            ).all()
        if genre:
            books += Book.query.filter(Book.genre.ilike(f'%{genre}%')).all()

        books = list(set(books))

    return render_template('search_books.html', form=form, books=books)


@app.route('/remove_book', methods=['GET', 'POST'])
@login_required
def remove_book():
    form = RemoveBookForm()
    if form.validate_on_submit():
        book_to_delete = Book.query.filter_by(book_id=form.book_id.data).first()

        if BookLoan.query.filter_by(book_id=form.book_id.data).first():
            flash('this book cannot be deleted from the database until all of its loan records are removed', 'danger')
            return redirect(url_for('index'))

        else:
            db.session.delete(book_to_delete)

            try:
                db.session.commit()
                flash('book successfully deleted', 'success')
                return redirect(url_for('index'))
            except:
                db.session.rollback()
                flash('there was an error deleting the specified book', 'danger')
                return redirect(url_for('index'))
    return render_template('remove_book.html', form=form)


@app.route('/remove_book_loan_records', methods=['GET', 'POST'])
@login_required
def remove_book_loan_records():
    form = RemoveBookLoanForm()

    if form.validate_on_submit():
        loans_to_remove = BookLoan.query.filter_by(book_id=form.book_id.data).all()

        for loan in loans_to_remove:
            db.session.delete(loan)

        try:
            db.session.commit()
            flash('book records successfully deleted', 'success')
            return redirect(url_for('index'))

        except:
             db.session.rollback()
             flash('there was an error removing the book loan records', 'danger')
             return redirect(url_for('index'))

    return render_template('remove_book_loan_record.html', form=form)



@app.route('/book_loan_records')
@login_required
def all_book_loan_records():
    all_loans = BookLoan.query.all()

    return render_template("book_loan_records.html", all_loans=all_loans)

@app.route('/fine_information')
def fine_information():
    return render_template('fine_information.html')

@app.route('/loan_information')
def loan_information():
    return render_template('loan_information.html')