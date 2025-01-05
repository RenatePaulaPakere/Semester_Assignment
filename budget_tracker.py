import configparser
import logging
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configure logging
def setup_logging():
    logging.basicConfig(
        filename='budget_tracker.log',
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(message)s'
    )

# Initialize SQLAlchemy Base
Base = declarative_base()

# Define the Transaction model
class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    category = Column(String)
    description = Column(String)
    amount = Column(Float)
    type = Column(String)
    remaining_budget = Column(Float)  # New column for remaining budget

# Initialize SQLite database and create tables if they don't exist
def initialize_database(db_name):
    engine = create_engine(f'sqlite:///{db_name}')
    Base.metadata.create_all(engine)  # Create tables based on the defined models

class BudgetTracker:
    def __init__(self, user_name):
        self.user_name = user_name  # Store user name as an instance variable
        
        # Read configuration from the config.ini file
        config = configparser.ConfigParser()
        config.read('config.ini')
        
        # Initialize income from the configuration file
        self.income = float(config['budget']['initial_income'])
        self.expenses = []
        
        # Create a user-specific database
        self.db_name = f"{self.user_name}_budget_tracker.db"
        
        # Initialize or connect to the database
        self.engine = create_engine(f'sqlite:///{self.db_name}')
        Base.metadata.create_all(self.engine)  # Create tables if they don't exist
        
        logging.info(f"Initialized BudgetTracker for {self.user_name} with initial income: ${self.income:.2f}")

        # Load existing transactions from the database
        self.load_transactions()

    def load_transactions(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        
        # Load transactions from the database into the expenses list
        transactions = session.query(Transaction).all()
        
        for transaction in transactions:
            if transaction.type == "Income":
                self.income += transaction.amount  # Accumulate income from transactions
            else:
                self.expenses.append({
                    'category': transaction.category,
                    'amount': transaction.amount,
                    'description': transaction.description,
                    'date': transaction.date,
                    'type': transaction.type
                })
        
        session.close()  # Close session after loading transactions

    def add_income(self, amount):
        if amount < 0:
            logging.warning("Attempted to add negative income.")
            print("Income cannot be negative.")
            return
        
        self.income += amount
        
        # Calculate remaining budget after adding income
        remaining_budget = self.income - sum(expense['amount'] for expense in self.expenses)
        
        self.save_transaction(amount, "Income", "Added income", remaining_budget)
        logging.info(f"Added income: ${amount:.2f}. Total income: ${self.income:.2f}. Remaining budget: ${remaining_budget:.2f}")

    def add_expense(self, category, amount, description):
        if amount < 0:
            logging.warning("Attempted to add negative expense.")
            print("Expense cannot be negative.")
            return
        
        expense = {
            'category': category,
            'amount': amount,
            'description': description
        }
        
        self.expenses.append(expense)
        
        # Calculate remaining budget before saving transaction
        remaining_budget = self.income - sum(exp['amount'] for exp in self.expenses)
        
        self.save_transaction(amount, category, description, remaining_budget)
        logging.info(f"Added expense: ${amount:.2f} in category '{category}' with description '{description}'. Remaining budget: ${remaining_budget:.2f}")

    def save_transaction(self, amount, category, description, remaining_budget=None):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        
        # Create a new transaction instance and add it to the session
        transaction = Transaction(date=datetime.now(), category=category,
                                  description=description, amount=amount,
                                  type="Expense" if category != "Income" else "Income",
                                  remaining_budget=remaining_budget)  # Save remaining budget
        
        session.add(transaction)  # Add transaction to the session
        session.commit()  # Commit the session to save changes
        session.close()  # Close the session

    def display_budget(self):
        total_expenses = sum(expense['amount'] for expense in self.expenses)

        print("\n--- Budget Summary ---")
        print(f"Total Income: ${self.income:.2f}")
        
        print("Expenses:")
        
        from collections import defaultdict
        category_summary = defaultdict(float)
        
        for expense in self.expenses:
            category_summary[expense['category']] += expense['amount']

        for category, total in category_summary.items():
            print(f"  {category} - ${total:.2f}")

        print(f"Total Expenses: ${total_expenses:.2f}")
        
        remaining_budget = self.income - total_expenses
        
        print(f"Remaining Budget: ${remaining_budget:.2f}")

def main():
    setup_logging()  # Set up logging configuration
    
    # Ask for user's name to create a personalized database
    user_name = input("Enter your name to access your budget tracker: ")
    
    tracker = BudgetTracker(user_name)  # Create an instance of BudgetTracker
    
    while True:
        print("\nOptions:")
        print("1. Add Income")
        print("2. Add Expense")
        print("3. Display Budget")
        print("4. Exit")
        
        choice = input("Choose an option (1-4): ")
        
        if choice == '1':
            try:
                amount = float(input("Enter income amount: "))
                tracker.add_income(amount)
            except ValueError:
                logging.error("Invalid input for income amount.")
                print("Invalid input! Please enter a numeric value.")
        
        elif choice == '2':
            while True:
                category_choice = input("Choose category (1 - Necessity, 2 - Want): ")
                if category_choice == '1':
                    category = "Necessity"
                    break
                elif category_choice == '2':
                    category = "Want"
                    break
                else:
                    logging.warning("Invalid category choice.")
                    print("Invalid choice. Please choose 1 or 2.")
            
            try:
                amount = float(input("Enter expense amount: "))
                description = input("Enter a brief description of the expense: ")
                tracker.add_expense(category, amount, description)
            except ValueError:
                logging.error("Invalid input for expense amount.")
                print("Invalid input! Please enter a numeric value for the expense amount.")
        
        elif choice == '3':
            tracker.display_budget()
        
        elif choice == '4':
            confirm = input("Are you sure you want to exit? (y/n): ")
            if confirm.lower() == 'y':
                logging.info(f"Exiting the budget tracker for {user_name}.")
                print("Exiting the budget tracker. Goodbye!")
                break
        
        else:
            logging.warning("Invalid option chosen.")
            print("Invalid option. Please choose again.")

if __name__ == "__main__":
    main()  # Run the main function when the script is executed
