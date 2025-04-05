import mysql.connector

class Database:
    def __init__(self):
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="yans",
            database="SpotSearcher"
        )

        # self.mycursor.execute("CREATE DATABASE SpotSearcher")
        self.Q1 = """
            CREATE TABLE Users (
                id INT PRIMARY KEY AUTO_INCREMENT,
                email VARCHAR(50) NOT NULL,
                password VARCHAR(50) NOT NULL,
                name VARCHAR(50) NOT NULL, 
                gender ENUM('M', 'F', 'O'), 
                dob DATE NOT NULL
            )
        """
        # self.mycursor.execute(Q1)

    def add_user(self, email, passw, name, gender, dob):
        Q = "INSERT INTO Users (email, password, name, gender, dob) VALUES (%s, %s, %s, %s, %s)"
        mycursor = self.db.cursor()
        mycursor.execute(Q, (email, passw, name, gender, dob))
        self.db.commit()
        mycursor.close()
        return 

    def call_data(self, table_name, wanted_entry, entry, user_entry):
        try:
            Q = f"SELECT {wanted_entry} FROM {table_name} WHERE {entry} = %s"
            mycursor = self.db.cursor()
            mycursor.execute(Q, (user_entry,))
            result = mycursor.fetchone()

            while mycursor.nextset():
                pass
            
            mycursor.close()
            return result
        except:
            mycursor.close()
            return None
    
    def delete_user(self, wanted_category, category, table_name):
        Q = f"DELETE FROM {table_name} WHERE {wanted_category} = %s"
        mycursor = self.db.cursor()
        mycursor.execute(Q, (category,))
        self.db.commit()
        mycursor.close()
        return
