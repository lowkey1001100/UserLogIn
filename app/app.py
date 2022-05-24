"""
created: 2022/05/24 13:17:51
@author: lowkey★1001100
contact: lowkey1001100@gmail.com
project: User Login
metadoc: App Functions
license: MIT 
"""

from app_functions import create_login_db, options_menu, add_users, delete_user, view_database, verify_credentials

if __name__ == '__main__':
    create_login_db()
    options_menu()
