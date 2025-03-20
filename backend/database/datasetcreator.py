import random
from dotenv import load_dotenv
from sqlalchemy import text
from database import Database
# Data Model Classes
class Museum:
    def __init__(self, museum_name, description, location, available_time, price, total_tickets, recommended_pick_time):
        self.museum_name = museum_name
        self.description = description
        self.location = location
        self.available_time = available_time
        self.price = price
        self.total_tickets = total_tickets
        self.recommended_pick_time = recommended_pick_time

    def to_sql(self):
        # Convert Museum object into an SQL INSERT statement.
        """
        Convert Museum object into an SQL INSERT statement.

        Returns:
            str: SQL INSERT statement
        """
        return (
            "INSERT INTO public.museums "
            "(museum_name, description, location, available_time, price, total_tickets, recommended_pick_time) "
            f"VALUES ('{self.museum_name}', '{self.description}', '{self.location}', "
            f"'{self.available_time}', {self.price}, {self.total_tickets}, '{self.recommended_pick_time}');"
        )


class BankAccount:
    def __init__(self, upi_id, accountholdername, phonenumber, balance, is_admin):
        self.upi_id = upi_id
        self.accountholdername = accountholdername
        self.phonenumber = phonenumber
        self.balance = balance
        self.is_admin = is_admin

    def to_sql(self):
        # Convert BankAccount object into an SQL INSERT statement.
        return (
            "INSERT INTO public.bankaccounts "
            "(upi_id, accountholdername, phonenumber, balance, is_admin) "
            f"VALUES ('{self.upi_id}', '{self.accountholdername}', '{self.phonenumber}', {self.balance}, {str(self.is_admin).lower()});"
        )


# Data Generator Class (SRP: only responsible for data creation)
class DataGenerator:
    def __init__(self):
        self.cities = [
            "Chennai", "Madurai", "Thanjavur", "Coimbatore", 
            "Tiruchirapalli", "Salem", "Tirunelveli", "Erode", 
            "Vellore", "Kanyakumari"
        ]
        self.museum_prefixes = [
            "Heritage", "Cultural", "Historical", "Art", 
            "Science", "Textile", "Fort", "Maritime"
        ]
        self.available_times = [
            "09:00 AM - 05:00 PM", "10:00 AM - 06:00 PM",
            "08:30 AM - 04:30 PM", "09:30 AM - 05:30 PM"
        ]
        self.pick_times = [
            "10:00 AM - 12:00 PM", "11:00 AM - 01:00 PM",
            "09:00 AM - 11:00 AM", "10:30 AM - 12:30 PM"
        ]
        self.first_names = [
            "Arun", "Sathya", "Lakshmi", "Karthik", "Meena", "Vignesh",
            "Revathi", "Suresh", "Anitha", "Prakash", "Rajesh", "Deepa",
            "Manoj", "Geetha", "Ravi", "Suman", "Divya", "Hari", "Nisha", "Vijay"
        ]
        self.last_names = [
            "Kumar", "Raj", "Priya", "S", "R", "P", "G", "Babu",
            "M", "D", "N", "Sharma", "Iyer", "Nair", "Verma"
        ]

    def generate_museums(self, count=100):
        museums = []
        for _ in range(count):
            city = random.choice(self.cities)
            prefix = random.choice(self.museum_prefixes)
            museum_name = f"{city} {prefix} Museum"
            description = f"{museum_name} showcasing the rich heritage and culture of Tamil Nadu."
            available_time = random.choice(self.available_times)
            price = round(random.uniform(50, 200), 2)
            total_tickets = random.randint(100, 500)
            recommended_pick_time = random.choice(self.pick_times)
            museums.append(Museum(museum_name, description, city, available_time, price, total_tickets, recommended_pick_time))
        return museums

    def generate_bankaccounts(self, count=100):
        accounts = []
        for i in range(1, count + 1):
            upi_id = f"user{i:03d}@upi"
            name = f"{random.choice(self.first_names)} {random.choice(self.last_names)}"
            phonenumber = self.random_phone()
            balance = round(random.uniform(1000, 10000), 2)
            # Mark the first account as an admin; others as regular users.
            is_admin = True if i == 1 else False
            accounts.append(BankAccount(upi_id, name, phonenumber, balance, is_admin))
        return accounts

    @staticmethod
    def random_phone():
        # Generate a random 10-digit phone number.
        return str(random.randint(9000000000, 9999999999))


# SQL Generator Class (SRP: converts objects to SQL statements)
class SQLGenerator:
    @staticmethod
    def generate_sql_statements(data_objects):
        return [obj.to_sql() for obj in data_objects]


def main():
    load_dotenv('D:\\mlprojt\\ccp_exps\\CCP_2YEAR_MUSEUM\\backend\\.env')
    # Create an instance of DataGenerator.
    data_gen = DataGenerator()
    
    # Generate data following our defined interfaces.
    museums = data_gen.generate_museums(100)
    bank_accounts = data_gen.generate_bankaccounts(100)

    # Convert data objects to SQL statements.
    museum_sql = SQLGenerator.generate_sql_statements(museums)
    bankaccount_sql = SQLGenerator.generate_sql_statements(bank_accounts)
    session_maker = Database.get_db()
    db = next(session_maker)
    try:    
        # Print SQL for Museums.
        print("-- Museums Inserts")
        for sql in museum_sql:
        
            print(sql)
            db.execute(text(sql))
        
        # Print SQL for Bank Accounts.
        print("\n-- Bank Accounts Inserts")
        for sql in bankaccount_sql:
            print(sql)
            db.execute(text(sql))
        db.commit()
    except Exception as e:
        print("Error generating SQL statements:", str(e))
    finally:
        # Close the database session.
        
        db.close()
        
if __name__ == "__main__":
    main()
