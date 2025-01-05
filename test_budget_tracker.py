import unittest
import os
from budget_tracker import BudgetTracker, Transaction
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class TestBudgetTracker(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.user_name = "test_user"  # Use a fixed user name for testing
        cls.db_name = f"{cls.user_name}_test_budget_tracker.db"
        cls.engine = create_engine(f'sqlite:///{cls.db_name}')
        
        # Create tables in the test database if they do not exist
        Transaction.__table__.create(cls.engine, checkfirst=True)

    @classmethod
    def tearDownClass(cls):
        # Clean up by deleting the test database file if needed
        if os.path.exists(cls.db_name):
            os.remove(cls.db_name)

    def setUp(self):
        # Create a new instance of BudgetTracker for each test with the test user name
        self.tracker = BudgetTracker(self.user_name)

    def test_add_income(self):
        initial_income = self.tracker.income
        amount_to_add = 500.00
        
        self.tracker.add_income(amount_to_add)
        
        self.assertEqual(self.tracker.income, initial_income + amount_to_add)

        session_maker = sessionmaker(bind=self.engine)
        session = session_maker()
        
        # Query for the transaction after adding income
        transaction = session.query(Transaction).filter_by(amount=amount_to_add, type="Income").first()
        
        self.assertIsNotNone(transaction)
        
        session.close()  # Close session after use

    def test_add_expense(self):
        expense_amount = 200.00
        
        self.tracker.add_expense("Necessity", expense_amount, "Groceries")
        
        self.assertEqual(len(self.tracker.expenses), 1)
        self.assertEqual(self.tracker.expenses[0]['amount'], expense_amount)

        session_maker = sessionmaker(bind=self.engine)
        session = session_maker()
        
        # Query for the transaction after adding expense
        transaction = session.query(Transaction).filter_by(amount=expense_amount, type="Expense").first()
        
        self.assertIsNotNone(transaction)
        
        session.close()  # Close session after use

    def test_display_budget(self):
        income_amount = 1000.00
        expense_amount = 200.00
        
        self.tracker.add_income(income_amount)
        self.tracker.add_expense("Necessity", expense_amount, "Utilities")
        
        total_expenses = sum(expense['amount'] for expense in self.tracker.expenses)
        
        remaining_budget = self.tracker.income - total_expenses
        
        self.assertEqual(remaining_budget, income_amount - expense_amount)

if __name__ == '__main__':
    unittest.main()
