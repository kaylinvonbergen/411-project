from dataclasses import dataclass
import logging
import os
from passlib.hash import pbkdf2_sha256
import sqlite3
from typing import Any


from typing import List

from utils.logger import *
from utils.sql_utils import *

logger = logging.getLogger(__name__)
configure_logger(logger)


@dataclass
class User:
    username: str
    password_hash: str


def create_user(username: str, password: str) -> None :
    hashed_password = pbkdf2_sha256.hash(password)

    try: 
       with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, hashed_password)
                VALUES (?, ?)
            """, (username, hashed_password))
           
            conn.commit()
            logger.info("User successfully added to the database: %s", username)
    
    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e


def check_credentials(username, password):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user_row = cursor.fetchone()

            conn.close()

            if user_row is None:
                raise ValueError("User not found")
            
            stored_hash = user_row[2]

            if pbkdf2_sha256.verify(password, stored_hash):
                logger.info("Login successful :)")
            else:
                raise ValueError("Invalid credentials")
            
    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e
    

def update_password(username, old_password, new_password):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user_row = cursor.fetchone()

            if user_row is None:
                raise ValueError("User not found")
            

            stored_hash = user_row[2]


            if pbkdf2_sha256.verify(old_password, stored_hash):
                new_hashed_password = pbkdf2_sha256.hash(new_password)
            
                cursor.execute("""
                    UPDATE users
                    SET hashed_password = ?
                    WHERE username = ?
                """, (new_hashed_password, username))

                conn.commit()
                conn.close()

                logger.info("Password update successful :)")
        
            else:
                conn.close()
                raise ValueError("Current password is incorrect")
            
    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e
    
    






