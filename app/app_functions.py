"""
created: 2022/05/24 13:17:38
@author: lowkey★1001100
contact: lowkey1001100@gmail.com
project: User Login
metadoc: App Functions
license: MIT 
"""


import sys
import os.path
import sqlite3
import binascii
import time
import hashlib
from hashlib import pbkdf2_hmac


def hash_password(password):
    """Hash a password for storing."""
    hash_algo = 'sha512'
    password = password.encode('utf-8')
    salt = hashlib.sha512(os.urandom(256)).hexdigest().encode('ascii')
    iterations = 100_000
    password_hash = hashlib.pbkdf2_hmac(hash_algo, password, salt, iterations)
    password_hash = binascii.hexlify(password_hash)
    final_result = (password_hash + salt).decode('ascii')
    return final_result


def create_login_db():
    if not os.path.isfile('login.db'):
        print('Creating login database...', file=sys.stderr)
        time.sleep(.05)
        conn = sqlite3.connect('login.db')
        c = conn.cursor()
        sql = """CREATE TABLE login (
                    username text,
                    password text
                    )"""
        c.execute(sql)
        print('Creating "Login" table...', file=sys.stderr)
        conn.commit()
        time.sleep(.05)

        sample_username = 'sample_user'
        sample_password = hash_password('test')

        sql = 'INSERT INTO login (username, password) VALUES (?, ?)'
        c.execute(sql, (sample_username, sample_password))
        conn.commit()
        sql = "SELECT * FROM login"
        c.execute(sql)
        print('Inserting sample data...\n', file=sys.stderr)
        time.sleep(.05)
        conn.commit()
    else:
        print('Database already created.', file=sys.stderr)
        time.sleep(1)


def get_username_password():
    username = input('Enter username:\n> ')
    password = input('Enter password:\n> ')
    password = password
    return username, password


def verify_password_string(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    hash_algo = 'sha512'
    stored_hash = stored_password[:128]
    stored_salt = stored_password[128:]
    iteration = 100_000
    password_hash = hashlib.pbkdf2_hmac(hash_algo,
                                        provided_password.encode('utf-8'),
                                        stored_salt.encode('ascii'),
                                        iteration)
    password_hash = binascii.hexlify(password_hash).decode('ascii')
    return password_hash == stored_hash


def verify_credentials() -> bool:
    provided_username, provided_password = get_username_password()
    conn = sqlite3.connect('login.db')
    c = conn.cursor()
    sql = "SELECT * FROM login WHERE username='{}'".format(provided_username)
    c.execute(sql)
    match = c.fetchone()
    if match:
        stored_username, stored_password = match[0], match[1]
        if provided_username == stored_username and verify_password_string(stored_password, provided_password):
            print('Credentials were verified!')
            return True
    print(f'Credentials could not be verified for username "{provided_username}"')
    return False


def add_users():
    conn = sqlite3.connect('login.db')
    c = conn.cursor()
    while True:
        username, password = get_username_password()
        sql = "SELECT * FROM login WHERE username='{}'".format(username)
        c.execute(sql)
        if c.fetchone():
            print('Username already exists, please enter a different username', file=sys.stderr)
            continue
        else:
            sql = "INSERT INTO login (username, password) VALUES (?, ?);"
            hashed_password = hash_password(password)
            c.execute(sql, (username, hashed_password))
            conn.commit()
            print(f'Username "{username}" has been added to the database.')
            print(f'Password hash: {hashed_password}')
            print()
        add_another = input('Would you like to add another user (yes or no)?\n>')
        if add_another == 'yes' or add_another.startswith('y'):
            continue
        elif add_another == 'no' or add_another.startswith('n'):
            break
    conn.close()
    options_menu()


def delete_user():
    conn = sqlite3.connect('login.db')
    c = conn.cursor()

    # Display users
    sql = 'SELECT * FROM login'
    c.execute(sql)
    result = c.fetchall()
    for user, hash_ in result:
        print(f'\t• {user}:\t{hash_}')

    while True:
        username = input('Which username do you want to delete?\n> ')
        # First check if username is in database
        sql = "SELECT * FROM login WHERE username='{}'".format(username)
        c.execute(sql)
        result = c.fetchone()
        if not result:
            print(f'"{username}" does not exit in database.')
        else:
            # TODO: Verify Credentials before deleting
            sql = "DELETE FROM login WHERE username='{}';".format(username)
            c.execute(sql)
            conn.commit()
            print(f'"{username}" has been deleted!')
            sql = 'SELECT * FROM login'
            c.execute(sql)
            result = c.fetchall()
            for user, hash_ in result:
                print(f'\t• {user}:\t{hash_}')
            choice = input('Would you like to delete another user (yes or no)?\n> ')
            if choice == 'yes' or choice.startswith('y'):
                continue
            else:
                break
    conn.close()
    options_menu()


def view_database():
    conn = sqlite3.connect('login.db')
    c = conn.cursor()
    sql = 'SELECT * FROM login'
    c.execute(sql)
    result = c.fetchall()
    for user, hash_ in result:
        print(f'\t• {user}:\t{hash_}')
    input('\nPress "Enter" to go back to main menu:\n> ')
    options_menu()


def options_menu():
    available_options = {1: 'Add User', 2: 'View Database', 3: 'Delete User', 4: 'Verify Password', 5: 'Exit Program'}
    print(f'{"-" * 30}')
    print('■ DATABASE OPTIONS MENU ■'.center(30))
    print(f'{"-" * 30}')
    for key, option in available_options.items():
        print(f'({key})-{option.upper()}')
    user_input = int(input(f'\nSelect an option (1-{len(available_options)}):\n> '))
    users_choice = available_options.get(user_input)
    match users_choice:
        case 'Add User':
            print(f'{"-" * 30}')
            print('■ ADD NEW USER TO DATABASE'.center(30))
            print(f'{"-" * 30}')
            add_users()
        case 'View Database':
            print(f'{"-" * 30}')
            print('■ VIEW DATABASE MODE')
            print(f'{"-" * 30}')
            view_database()
        case 'Delete User':
            print(f'{"-" * 30}')
            print('■ DELETE USER MODE')
            print(f'{"-" * 30}')
            delete_user()
        case 'Verify Password':
            print(f'{"-" * 30}')
            print('■ VERIFY CREDENTIALS')
            print(f'{"-" * 30}')
            verify_credentials()
        case 'Exit Program':
            print('Exiting program... \nGoodbye.')
            sys.exit()
        case _:
            print('INVALID INPUT!')


create_login_db()
options_menu()