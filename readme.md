**Overview**

The Library Management System is a web application built using Flask and SQLAlchemy to manage the borrowing and returning of devices and books by students. The system includes user authentication, student management, device management, and fine calculation for overdue items.

**Features**

* User Authentication: Users can register, log in, and log out.
* Student Management: Admins can add, deactivate, and delete student accounts.
* Device Management: Admins can add new devices, check available devices, and manage existing device records.
* Borrowing and Returning: Students can borrow and return devices and books, with validations in place.
* Fine Calculation: Automatic calculation of fines for late returns.
* Reporting: Admins can generate loan reports for individual students.
* Search Functionality: Users can search for books by title, author, or genre.

**Technologies Used**

* Backend: Python, Flask, Flask-WTF, SQLAlchemy
* Frontend: HTML, CSS (for rendering templates)
* Database: SQLite (for local development)
* Validation: WTForms for form handling and validation

**Form Definitions**

* Login Form - The LoginForm allows users to log in with their username and password, with an option to remember their session.
* Registration Form - The RegistrationForm enables new users to create an account, requiring username, email, password, and password confirmation.
* Add Student Form - For adding new students to the system with validations to prevent duplicate usernames and emails.
* Deactivate Student Form - To deactivate existing student accounts.
* Remove Student Loans Form - To delete all loan records associated with a student.
* Activate Student Form - To activate a previously deactivated student account.
* AddDeviceForm: For adding new devices or updating existing device quantities.
* Borrow Form - For students to borrow devices, with validations to ensure students are eligible to borrow and devices are available.
* Return Form - To return borrowed devices, ensuring proper validations are in place.
* AddBook Form - For adding new books to the system with author information.
* Remove Book Form - To delete a book from the database if it has no associated loan records.
* Remove Book Loan Form - To remove all loan records associated with a specific book.
* Book Return Form - To return a borrowed book and calculate any applicable fines.
* Pay Fine Form - To update a student's fine amount based on a particular value.
