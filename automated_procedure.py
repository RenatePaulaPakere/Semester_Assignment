import configparser
import logging
from budget_tracker import BudgetTracker

# Configure logging for the automated procedure
def setup_logging():
    logging.basicConfig(
        filename='automated_procedure.log',
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s'
    )

def add_sample_data(tracker):
    # Adding sample income and expenses
    tracker.add_income(1500.00)
    tracker.add_expense("Necessity", 300.00, "Groceries")
    tracker.add_expense("Necessity", 150.00, "Utilities")
    tracker.add_expense("Want", 100.00, "Entertainment")

def display_budget(tracker):
    print("\n--- Automated Budget Summary ---")
    tracker.display_budget()

def main():
    setup_logging()  # Set up logging configuration
    
    # Ask for user's name to create a personalized database
    user_name = input("Enter your name to access your budget tracker: ")
    
    # Create an instance of BudgetTracker with the user's name
    tracker = BudgetTracker(user_name)
    
    # Add sample data to the tracker
    add_sample_data(tracker)
    
    # Display the budget summary
    display_budget(tracker)

if __name__ == "__main__":
    main()  # Run the automated procedure when the script is executed
