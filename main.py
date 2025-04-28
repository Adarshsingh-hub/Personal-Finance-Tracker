import os
import json
import datetime
from functools import wraps

# Decorators
def validate_amount(func):
    """Decorator to validate if the transaction amount is a positive number."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        amount = kwargs.get('amount') or args[1]  # Assuming amount is the second argument
        try:
            amount = float(amount)
            if amount <= 0:
                print("\nError: Amount must be a positive number.")
                return None
        except ValueError:
            print("\nError: Please enter a valid number for the amount.")
            return None
        return func(*args, **kwargs)
    return wrapper

def log_transaction(func):
    """Decorator to log all transactions."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if result is not None:
            with open("transaction_log.txt", "a") as f:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"{timestamp} - {func.__name__}: {args[1]} ${args[2]} - {args[3]}\n")
        return result
    return wrapper

# Classes
class Transaction:
    def __init__(self, transaction_id, date, amount, category, transaction_type, description=""):
        self.transaction_id = transaction_id
        self.date = date
        self.amount = float(amount)
        self.category = category
        self.type = transaction_type  # 'income' or 'expense'
        self.description = description
    
    def to_dict(self):
        """Convert transaction object to dictionary for JSON serialization."""
        return {
            'id': self.transaction_id,
            'date': self.date,
            'amount': self.amount,
            'category': self.category,
            'type': self.type,
            'description': self.description
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a Transaction object from a dictionary."""
        return cls(
            data['id'],
            data['date'],
            data['amount'],
            data['category'],
            data['type'],
            data.get('description', '')
        )

class SavingsGoal:
    def __init__(self, goal_id, name, target_amount, current_amount=0.0):
        self.goal_id = goal_id
        self.name = name
        self.target_amount = float(target_amount)
        self.current_amount = float(current_amount)
    
    def add_funds(self, amount):
        """Add funds to the savings goal."""
        self.current_amount += float(amount)
    
    def get_progress_percentage(self):
        """Calculate the percentage of completion for the goal."""
        return (self.current_amount / self.target_amount) * 100 if self.target_amount > 0 else 0
    
    def to_dict(self):
        """Convert savings goal object to dictionary for JSON serialization."""
        return {
            'id': self.goal_id,
            'name': self.name,
            'target_amount': self.target_amount,
            'current_amount': self.current_amount
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a SavingsGoal object from a dictionary."""
        return cls(
            data['id'],
            data['name'],
            data['target_amount'],
            data.get('current_amount', 0.0)
        )

class Budget:
    def __init__(self, budget_id, category, limit, period="monthly"):
        self.budget_id = budget_id
        self.category = category
        self.limit = float(limit)
        self.period = period  # monthly, weekly, etc.
    
    def to_dict(self):
        """Convert budget object to dictionary for JSON serialization."""
        return {
            'id': self.budget_id,
            'category': self.category,
            'limit': self.limit,
            'period': self.period
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a Budget object from a dictionary."""
        return cls(
            data['id'],
            data['category'],
            data['limit'],
            data.get('period', 'monthly')
        )

class User:
    def __init__(self, username, password, transactions=None, savings_goals=None, budgets=None):
        self.username = username
        self.password = password  # In a real app, this should be hashed
        self.transactions = transactions or []
        self.savings_goals = savings_goals or []
        self.budgets = budgets or []
        self.categories = ["Groceries", "Bills", "Entertainment", "Transportation", "Housing", "Other"]
    
    def authenticate(self, password):
        """Check if the provided password matches the user's password."""
        return self.password == password
    
    def get_balance(self):
        """Calculate the current balance."""
        total_income = sum(t.amount for t in self.transactions if t.type == 'income')
        total_expenses = sum(t.amount for t in self.transactions if t.type == 'expense')
        return total_income - total_expenses
    
    def get_total_income(self):
        """Calculate the total income."""
        return sum(t.amount for t in self.transactions if t.type == 'income')
    
    def get_total_expenses(self):
        """Calculate the total expenses."""
        return sum(t.amount for t in self.transactions if t.type == 'expense')
    
    def get_expenses_by_category(self):
        """Get expenses grouped by category."""
        expenses_by_category = {}
        for transaction in self.transactions:
            if transaction.type == 'expense':
                if transaction.category not in expenses_by_category:
                    expenses_by_category[transaction.category] = 0
                expenses_by_category[transaction.category] += transaction.amount
        return expenses_by_category
    
    def check_budget_notifications(self):
        """Check if any budget limits have been reached."""
        notifications = []
        expenses_by_category = self.get_expenses_by_category()
        
        for budget in self.budgets:
            if budget.category in expenses_by_category:
                current_spending = expenses_by_category[budget.category]
                if current_spending >= budget.limit:
                    notifications.append(f"Budget Alert: You've exceeded your {budget.category} budget of ${budget.limit:.2f}. Current spending: ${current_spending:.2f}")
                elif current_spending >= budget.limit * 0.8:
                    notifications.append(f"Budget Warning: You're approaching your {budget.category} budget of ${budget.limit:.2f}. Current spending: ${current_spending:.2f}")
        
        return notifications
    
    @log_transaction
    @validate_amount
    def add_transaction(self, date, amount, category, transaction_type, description=""):
        """Add a new transaction."""
        transaction_id = len(self.transactions) + 1
        transaction = Transaction(transaction_id, date, amount, category, transaction_type, description)
        self.transactions.append(transaction)
        return transaction
    
    def add_savings_goal(self, name, target_amount):
        """Add a new savings goal."""
        goal_id = len(self.savings_goals) + 1
        savings_goal = SavingsGoal(goal_id, name, target_amount)
        self.savings_goals.append(savings_goal)
        return savings_goal
    
    def add_budget(self, category, limit, period="monthly"):
        """Add a new budget for a specific category."""
        budget_id = len(self.budgets) + 1
        budget = Budget(budget_id, category, limit, period)
        self.budgets.append(budget)
        return budget
    
    def to_dict(self):
        """Convert user object to dictionary for JSON serialization."""
        return {
            'username': self.username,
            'password': self.password,
            'transactions': [t.to_dict() for t in self.transactions],
            'savings_goals': [g.to_dict() for g in self.savings_goals],
            'budgets': [b.to_dict() for b in self.budgets],
            'categories': self.categories
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a User object from a dictionary."""
        transactions = [Transaction.from_dict(t) for t in data.get('transactions', [])]
        savings_goals = [SavingsGoal.from_dict(g) for g in data.get('savings_goals', [])]
        budgets = [Budget.from_dict(b) for b in data.get('budgets', [])]
        user = cls(
            data['username'],
            data['password'],
            transactions,
            savings_goals,
            budgets
        )
        if 'categories' in data:
            user.categories = data['categories']
        return user

class FinanceTracker:
    def __init__(self):
        self.users = {}
        self.current_user = None
        self.data_file = "finance_data.json"
        self.load_data()
    
    def load_data(self):
        """Load user data from the JSON file."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    for username, user_data in data.items():
                        self.users[username] = User.from_dict(user_data)
                print("Data loaded successfully.")
            except Exception as e:
                print(f"Error loading data: {e}")
        else:
            print("No existing data found. Starting fresh.")
    
    def save_data(self):
        """Save user data to the JSON file."""
        try:
            data = {username: user.to_dict() for username, user in self.users.items()}
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            print("Data saved successfully.")
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def register_user(self, username, password):
        """Register a new user."""
        if username in self.users:
            print(f"User '{username}' already exists.")
            return False
        
        self.users[username] = User(username, password)
        self.save_data()
        print(f"User '{username}' registered successfully.")
        return True
    
    def login(self, username, password):
        """Log in a user."""
        if username not in self.users:
            print(f"User '{username}' does not exist.")
            return False
        
        user = self.users[username]
        if user.authenticate(password):
            self.current_user = user
            print(f"Welcome, {username}!")
            return True
        else:
            print("Incorrect password.")
            return False
    
    def logout(self):
        """Log out the current user."""
        if self.current_user:
            print(f"Goodbye, {self.current_user.username}!")
            self.current_user = None
            return True
        return False
    
    def is_logged_in(self):
        """Check if a user is currently logged in."""
        return self.current_user is not None

# Main CLI Application
def main():
    finance_tracker = FinanceTracker()
    
    while True:
        if not finance_tracker.is_logged_in():
            print("\n--- Personal Finance Tracker ---")
            print("1. Register")
            print("2. Login")
            print("3. Exit")
            choice = input("Enter your choice (1-3): ")
            
            if choice == "1":
                username = input("Enter a username: ")
                password = input("Enter a password: ")
                finance_tracker.register_user(username, password)
            
            elif choice == "2":
                username = input("Enter your username: ")
                password = input("Enter your password: ")
                finance_tracker.login(username, password)
            
            elif choice == "3":
                print("Thank you for using Personal Finance Tracker!")
                break
            
            else:
                print("Invalid choice. Please try again.")
        
        else:  # User is logged in
            # Check for budget notifications
            notifications = finance_tracker.current_user.check_budget_notifications()
            if notifications:
                print("\n--- Budget Notifications ---")
                for notification in notifications:
                    print(notification)
            
            print("\n--- Personal Finance Tracker ---")
            print(f"Current Balance: ${finance_tracker.current_user.get_balance():.2f}")
            print("1. Add Transaction")
            print("2. View Transactions")
            print("3. View Summary")
            print("4. Manage Savings Goals")
            print("5. Manage Budgets")
            print("6. Manage Categories")
            print("7. Logout")
            print("8. Exit")
            choice = input("Enter your choice (1-8): ")
            
            if choice == "1":
                handle_add_transaction(finance_tracker)
            
            elif choice == "2":
                handle_view_transactions(finance_tracker)
            
            elif choice == "3":
                handle_view_summary(finance_tracker)
            
            elif choice == "4":
                handle_savings_goals(finance_tracker)
            
            elif choice == "5":
                handle_budgets(finance_tracker)
            
            elif choice == "6":
                handle_categories(finance_tracker)
            
            elif choice == "7":
                finance_tracker.logout()
            
            elif choice == "8":
                finance_tracker.save_data()
                print("Thank you for using Personal Finance Tracker!")
                break
            
            else:
                print("Invalid choice. Please try again.")

def handle_add_transaction(finance_tracker):
    """Handle adding a new transaction."""
    user = finance_tracker.current_user
    
    print("\n--- Add Transaction ---")
    print("1. Add Income")
    print("2. Add Expense")
    print("3. Back")
    choice = input("Enter your choice (1-3): ")
    
    if choice in ["1", "2"]:
        transaction_type = "income" if choice == "1" else "expense"
        date = input("Enter date (YYYY-MM-DD) or leave blank for today: ")
        if not date:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        amount = input(f"Enter {transaction_type} amount: $")
        
        # Show available categories
        print("\nAvailable Categories:")
        for i, category in enumerate(user.categories, 1):
            print(f"{i}. {category}")
        
        category_choice = input("Enter category number or name: ")
        try:
            category_idx = int(category_choice) - 1
            if 0 <= category_idx < len(user.categories):
                category = user.categories[category_idx]
            else:
                category = category_choice
        except ValueError:
            category = category_choice
        
        if category not in user.categories:
            add_to_categories = input(f"Category '{category}' doesn't exist. Add it to your categories? (y/n): ")
            if add_to_categories.lower() == 'y':
                user.categories.append(category)
                print(f"Category '{category}' added!")
            else:
                category = "Other"
        
        description = input("Enter description (optional): ")
        
        # Add the transaction
        transaction = user.add_transaction(date, amount, category, transaction_type, description)
        
        if transaction:
            print(f"{transaction_type.capitalize()} added successfully!")
            finance_tracker.save_data()
    
    elif choice == "3":
        return
    
    else:
        print("Invalid choice. Please try again.")

def handle_view_transactions(finance_tracker):
    """Handle viewing transactions."""
    user = finance_tracker.current_user
    
    if not user.transactions:
        print("\nNo transactions found.")
        return
    
    print("\n--- Transactions ---")
    print("ID | Date | Type | Amount | Category | Description")
    print("-" * 60)
    
    for transaction in user.transactions:
        print(f"{transaction.transaction_id} | {transaction.date} | {transaction.type.capitalize()} | ${transaction.amount:.2f} | {transaction.category} | {transaction.description}")
    
    while True:
        print("\n1. Filter Transactions")
        print("2. Delete Transaction")
        print("3. Back")
        choice = input("Enter your choice (1-3): ")
        
        if choice == "1":
            handle_filter_transactions(user)
        
        elif choice == "2":
            transaction_id = input("Enter ID of transaction to delete: ")
            try:
                transaction_id = int(transaction_id)
                found = False
                for i, transaction in enumerate(user.transactions):
                    if transaction.transaction_id == transaction_id:
                        del user.transactions[i]
                        print("Transaction deleted.")
                        finance_tracker.save_data()
                        found = True
                        break
                if not found:
                    print("Transaction not found.")
            except ValueError:
                print("Please enter a valid ID.")
        
        elif choice == "3":
            break
        
        else:
            print("Invalid choice. Please try again.")

def handle_filter_transactions(user):
    """Handle filtering transactions by various criteria."""
    print("\n--- Filter Transactions ---")
    print("1. By Date Range")
    print("2. By Category")
    print("3. By Type (Income/Expense)")
    print("4. Back")
    choice = input("Enter your choice (1-4): ")
    
    filtered_transactions = []
    
    if choice == "1":
        start_date = input("Enter start date (YYYY-MM-DD): ")
        end_date = input("Enter end date (YYYY-MM-DD): ")
        filtered_transactions = [t for t in user.transactions if start_date <= t.date <= end_date]
    
    elif choice == "2":
        print("\nAvailable Categories:")
        for i, category in enumerate(user.categories, 1):
            print(f"{i}. {category}")
        
        category_choice = input("Enter category number or name: ")
        try:
            category_idx = int(category_choice) - 1
            if 0 <= category_idx < len(user.categories):
                selected_category = user.categories[category_idx]
            else:
                selected_category = category_choice
        except ValueError:
            selected_category = category_choice
        
        filtered_transactions = [t for t in user.transactions if t.category == selected_category]
    
    elif choice == "3":
        transaction_type = input("Enter type (income/expense): ").lower()
        if transaction_type in ['income', 'expense']:
            filtered_transactions = [t for t in user.transactions if t.type == transaction_type]
        else:
            print("Invalid type. Please enter 'income' or 'expense'.")
            return
    
    elif choice == "4":
        return
    
    else:
        print("Invalid choice. Please try again.")
        return
    
    if not filtered_transactions:
        print("\nNo matching transactions found.")
        return
    
    print("\n--- Filtered Transactions ---")
    print("ID | Date | Type | Amount | Category | Description")
    print("-" * 60)
    
    for transaction in filtered_transactions:
        print(f"{transaction.transaction_id} | {transaction.date} | {transaction.type.capitalize()} | ${transaction.amount:.2f} | {transaction.category} | {transaction.description}")

def handle_view_summary(finance_tracker):
    """Handle viewing financial summary."""
    user = finance_tracker.current_user
    
    print("\n--- Financial Summary ---")
    print(f"Total Income: ${user.get_total_income():.2f}")
    print(f"Total Expenses: ${user.get_total_expenses():.2f}")
    print(f"Current Balance: ${user.get_balance():.2f}")
    
    # Expenses by category
    expenses_by_category = user.get_expenses_by_category()
    if expenses_by_category:
        print("\n--- Expenses by Category ---")
        for category, amount in expenses_by_category.items():
            print(f"{category}: ${amount:.2f}")
    else:
        print("\nNo expenses recorded yet.")

def handle_savings_goals(finance_tracker):
    """Handle savings goals operations."""
    user = finance_tracker.current_user
    
    while True:
        print("\n--- Savings Goals ---")
        print("1. View Savings Goals")
        print("2. Add New Savings Goal")
        print("3. Add Funds to a Goal")
        print("4. Back")
        choice = input("Enter your choice (1-4): ")
        
        if choice == "1":
            if not user.savings_goals:
                print("\nNo savings goals found.")
            else:
                print("\nID | Name | Target Amount | Current Amount | Progress")
                print("-" * 60)
                for goal in user.savings_goals:
                    progress = goal.get_progress_percentage()
                    print(f"{goal.goal_id} | {goal.name} | ${goal.target_amount:.2f} | ${goal.current_amount:.2f} | {progress:.2f}%")
        
        elif choice == "2":
            name = input("Enter goal name: ")
            target_amount = input("Enter target amount: $")
            try:
                target_amount = float(target_amount)
                if target_amount <= 0:
                    print("Target amount must be positive.")
                    continue
                
                goal = user.add_savings_goal(name, target_amount)
                print(f"Savings goal '{name}' added successfully!")
                finance_tracker.save_data()
            except ValueError:
                print("Please enter a valid amount.")
        
        elif choice == "3":
            if not user.savings_goals:
                print("\nNo savings goals found.")
                continue
            
            print("\nID | Name | Target Amount | Current Amount | Progress")
            print("-" * 60)
            for goal in user.savings_goals:
                progress = goal.get_progress_percentage()
                print(f"{goal.goal_id} | {goal.name} | ${goal.target_amount:.2f} | ${goal.current_amount:.2f} | {progress:.2f}%")
            
            goal_id = input("\nEnter goal ID to add funds: ")
            try:
                goal_id = int(goal_id)
                found = False
                for goal in user.savings_goals:
                    if goal.goal_id == goal_id:
                        amount = input("Enter amount to add: $")
                        try:
                            amount = float(amount)
                            if amount <= 0:
                                print("Amount must be positive.")
                                continue
                            
                            goal.add_funds(amount)
                            print(f"${amount:.2f} added to '{goal.name}'.")
                            finance_tracker.save_data()
                        except ValueError:
                            print("Please enter a valid amount.")
                        found = True
                        break
                if not found:
                    print("Goal not found.")
            except ValueError:
                print("Please enter a valid ID.")
        
        elif choice == "4":
            break
        
        else:
            print("Invalid choice. Please try again.")

def handle_budgets(finance_tracker):
    """Handle budget operations."""
    user = finance_tracker.current_user
    
    while True:
        print("\n--- Budgets ---")
        print("1. View Budgets")
        print("2. Add New Budget")
        print("3. Delete Budget")
        print("4. Back")
        choice = input("Enter your choice (1-4): ")
        
        if choice == "1":
            if not user.budgets:
                print("\nNo budgets found.")
            else:
                expenses_by_category = user.get_expenses_by_category()
                print("\nID | Category | Limit | Current Spending | Status")
                print("-" * 70)
                for budget in user.budgets:
                    current_spending = expenses_by_category.get(budget.category, 0)
                    status = "OK"
                    if current_spending >= budget.limit:
                        status = "EXCEEDED"
                    elif current_spending >= budget.limit * 0.8:
                        status = "WARNING"
                    
                    print(f"{budget.budget_id} | {budget.category} | ${budget.limit:.2f} | ${current_spending:.2f} | {status}")
        
        elif choice == "2":
            print("\nAvailable Categories:")
            for i, category in enumerate(user.categories, 1):
                print(f"{i}. {category}")
            
            category_choice = input("Enter category number or name: ")
            try:
                category_idx = int(category_choice) - 1
                if 0 <= category_idx < len(user.categories):
                    selected_category = user.categories[category_idx]
                else:
                    selected_category = category_choice
            except ValueError:
                selected_category = category_choice
            
            if selected_category not in user.categories:
                add_to_categories = input(f"Category '{selected_category}' doesn't exist. Add it to your categories? (y/n): ")
                if add_to_categories.lower() == 'y':
                    user.categories.append(selected_category)
                    print(f"Category '{selected_category}' added!")
                else:
                    continue
            
            limit = input("Enter budget limit: $")
            try:
                limit = float(limit)
                if limit <= 0:
                    print("Budget limit must be positive.")
                    continue
                
                # Check if a budget already exists for this category
                exists = False
                for budget in user.budgets:
                    if budget.category == selected_category:
                        exists = True
                        update = input(f"A budget for '{selected_category}' already exists. Update it? (y/n): ")
                        if update.lower() == 'y':
                            budget.limit = limit
                            print(f"Budget for '{selected_category}' updated to ${limit:.2f}")
                            finance_tracker.save_data()
                        break
                
                if not exists:
                    period = input("Enter budget period (monthly/weekly/yearly) [default: monthly]: ").lower()
                    if period not in ['monthly', 'weekly', 'yearly']:
                        period = 'monthly'
                    
                    budget = user.add_budget(selected_category, limit, period)
                    print(f"Budget for '{selected_category}' added successfully!")
                    finance_tracker.save_data()
            except ValueError:
                print("Please enter a valid amount.")
        
        elif choice == "3":
            if not user.budgets:
                print("\nNo budgets found.")
                continue
            
            print("\nID | Category | Limit | Period")
            print("-" * 40)
            for budget in user.budgets:
                print(f"{budget.budget_id} | {budget.category} | ${budget.limit:.2f} | {budget.period}")
            
            budget_id = input("\nEnter budget ID to delete: ")
            try:
                budget_id = int(budget_id)
                found = False
                for i, budget in enumerate(user.budgets):
                    if budget.budget_id == budget_id:
                        del user.budgets[i]
                        print("Budget deleted.")
                        finance_tracker.save_data()
                        found = True
                        break
                if not found:
                    print("Budget not found.")
            except ValueError:
                print("Please enter a valid ID.")
        
        elif choice == "4":
            break
        
        else:
            print("Invalid choice. Please try again.")

def handle_categories(finance_tracker):
    """Handle category management."""
    user = finance_tracker.current_user
    
    while True:
        print("\n--- Manage Categories ---")
        print("Current Categories:")
        for i, category in enumerate(user.categories, 1):
            print(f"{i}. {category}")
        
        print("\n1. Add Category")
        print("2. Rename Category")
        print("3. Delete Category")
        print("4. Back")
        choice = input("Enter your choice (1-4): ")
        
        if choice == "1":
            category = input("Enter new category name: ")
            if category in user.categories:
                print(f"Category '{category}' already exists.")
            else:
                user.categories.append(category)
                print(f"Category '{category}' added successfully!")
                finance_tracker.save_data()
        
        elif choice == "2":
            old_category = input("Enter category to rename: ")
            if old_category not in user.categories:
                print(f"Category '{old_category}' not found.")
                continue
            
            new_category = input("Enter new name: ")
            if new_category in user.categories:
                print(f"Category '{new_category}' already exists.")
                continue
            
            # Update category in transactions
            for transaction in user.transactions:
                if transaction.category == old_category:
                    transaction.category = new_category
            
            # Update category in budgets
            for budget in user.budgets:
                if budget.category == old_category:
                    budget.category = new_category
            
            # Update category list
            index = user.categories.index(old_category)
            user.categories[index] = new_category
            
            print(f"Category renamed from '{old_category}' to '{new_category}'.")
            finance_tracker.save_data()
        
        elif choice == "3":
            category = input("Enter category to delete: ")
            if category not in user.categories:
                print(f"Category '{category}' not found.")
                continue
            
            confirm = input(f"Are you sure you want to delete the category '{category}'? This will set all related transactions to 'Other'. (y/n): ")
            if confirm.lower() != 'y':
                continue
            
            # Update transactions with this category
            for transaction in user.transactions:
                if transaction.category == category:
                    transaction.category = "Other"
            
            # Remove budgets with this category
            user.budgets = [b for b in user.budgets if b.category != category]
            
            # Remove category from list
            user.categories.remove(category)
            
            print(f"Category '{category}' deleted.")
            finance_tracker.save_data()
        
        elif choice == "4":
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()