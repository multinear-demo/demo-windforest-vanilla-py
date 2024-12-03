import logging
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Date,
    ForeignKey,
    or_,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, backref
from faker import Faker
import random
from datetime import datetime, timedelta
import numpy as np
import time
import functools

# Initialize Faker
fake = Faker()

# Set up logging
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s'
)

# Database setup
Base = declarative_base()
engine = create_engine('sqlite:///data/windforest.db')


# Define models
class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    address = Column(String)
    segment = Column(String)
    region = Column(String)
    age = Column(Integer)
    gender = Column(String)
    income_level = Column(Float)
    clv = Column(Float)
    account_creation_date = Column(Date)
    preferred_contact_method = Column(String)
    purchase_frequency = Column(String)
    seasonal_preference = Column(String)
    last_purchase_date = Column(Date)
    avg_order_value = Column(Float)
    orders = relationship("Order", back_populates="customer")
    interactions = relationship("CustomerServiceInteraction", back_populates="customer")


class Employee(Base):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    title = Column(String)
    department = Column(String)
    manager_id = Column(Integer, ForeignKey('employees.id'))
    hire_date = Column(Date)
    termination_date = Column(Date, nullable=True)
    salary = Column(Float)
    bonus = Column(Float)
    commission = Column(Float)
    kpi_score = Column(Float)
    shift = Column(String)
    level = Column(Integer)
    direct_reports = relationship(
        "Employee", backref=backref('manager', remote_side=[id])
    )
    orders = relationship("Order", back_populates="employee")


class Supplier(Base):
    __tablename__ = 'suppliers'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    contact_name = Column(String)
    address = Column(String)
    rating = Column(Float)
    location = Column(String)
    contract_terms = Column(String)
    relationship_length = Column(Integer)
    books = relationship("Book", back_populates="supplier")


class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    popularity = Column(Float)
    books = relationship(
        "Book", secondary='book_categories', back_populates="categories"
    )
    subcategories = relationship(
        "Category", backref=backref('parent', remote_side=[id])
    )


class Author(Base):
    __tablename__ = 'authors'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    books = relationship("Book", secondary='book_authors', back_populates="authors")


class BookAuthor(Base):
    __tablename__ = 'book_authors'
    book_id = Column(Integer, ForeignKey('books.id'), primary_key=True)
    author_id = Column(Integer, ForeignKey('authors.id'), primary_key=True)


class CustomerServiceInteraction(Base):
    __tablename__ = 'customer_service_interactions'
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=True)
    interaction_date = Column(Date)
    interaction_type = Column(String)
    channel = Column(String)
    priority = Column(String)
    status = Column(String)
    resolution_date = Column(Date, nullable=True)
    satisfaction_score = Column(Integer, nullable=True)
    notes = Column(String)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    customer = relationship("Customer", back_populates="interactions")
    order = relationship("Order", back_populates="interactions")
    employee = relationship("Employee")


class BookCategory(Base):
    __tablename__ = 'book_categories'
    book_id = Column(Integer, ForeignKey('books.id'), primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.id'), primary_key=True)


class BookPriceHistory(Base):
    __tablename__ = 'book_price_history'
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id'))
    price = Column(Float)
    effective_date = Column(Date)
    end_date = Column(Date, nullable=True)
    change_reason = Column(String)
    book = relationship("Book", back_populates="price_history")


class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    isbn = Column(String)
    format = Column(String)
    language = Column(String)
    price = Column(Float)
    stock_level = Column(Integer)
    safety_stock = Column(Integer)
    reorder_point = Column(Integer)
    publication_date = Column(Date)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    supplier = relationship("Supplier", back_populates="books")
    categories = relationship(
        "Category", secondary='book_categories', back_populates="books"
    )
    order_items = relationship("OrderItem", back_populates="book")
    authors = relationship("Author", secondary='book_authors', back_populates="books")
    price_history = relationship("BookPriceHistory", back_populates="book")

    def get_price_at_date(self, session, date=None):
        """Get the effective price at a specific date, or current price
        if date is None"""
        if date is None:
            date = datetime.now().date()

        historical_price = (
            session.query(BookPriceHistory)
            .filter(
                BookPriceHistory.book_id == self.id,
                BookPriceHistory.effective_date <= date,
                or_(
                    BookPriceHistory.end_date > date,
                    BookPriceHistory.end_date.is_(None),
                ),
            )
            .first()
        )
        return historical_price.price if historical_price else self.price


class Shipper(Base):
    __tablename__ = 'shippers'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    phone = Column(String)
    service_area = Column(String)
    base_cost = Column(Float)
    performance_rating = Column(Float)
    orders = relationship("Order", back_populates="shipper")


class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    order_date = Column(Date)
    status = Column(String)
    shipping_method = Column(String)
    payment_method = Column(String)
    discount = Column(Float)
    tax = Column(Float)
    notes = Column(String, nullable=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    employee_id = Column(Integer, ForeignKey('employees.id'))
    shipper_id = Column(Integer, ForeignKey('shippers.id'))
    customer = relationship("Customer", back_populates="orders")
    employee = relationship("Employee", back_populates="orders")
    shipper = relationship("Shipper", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order")
    interactions = relationship("CustomerServiceInteraction", back_populates="order")


class OrderItem(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    book_id = Column(Integer, ForeignKey('books.id'))
    quantity = Column(Integer)
    unit_price = Column(Float)
    order = relationship("Order", back_populates="order_items")
    book = relationship("Book", back_populates="order_items")


# Create tables
Base.metadata.create_all(engine)


# Data generation functions
def generate_seasonal_date(start_date, end_date):
    """Generate dates with higher probability during peak seasons."""
    # Convert to datetime objects if strings
    start = (
        datetime.strptime(start_date, '%Y-%m-%d')
        if isinstance(start_date, str)
        else start_date
    )
    end = (
        datetime.strptime(end_date, '%Y-%m-%d')
        if isinstance(end_date, str)
        else end_date
    )

    # Generate random date
    days_between = (end - start).days
    random_days = random.randint(0, days_between)
    date = start + timedelta(days=random_days)

    # Adjust probability based on month (higher weights for Nov-Dec)
    month_weights = {
        11: 1.5,  # November
        12: 1.8,  # December
        1: 0.7,  # January (post-holiday slump)
        7: 1.2,  # July (summer reading)
        8: 1.2,  # August (back to school)
    }

    # If random number is greater than weight, try again
    if random.random() > month_weights.get(date.month, 1.0):
        return generate_seasonal_date(start_date, end_date)

    return date


def measure_duration(func):
    """Decorator to measure and log function duration."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        # Format duration with appropriate unit (ms if < 1s, s otherwise)
        if duration < 1:
            duration_str = "<1s"
        else:
            duration_str = f"{int(duration)}s"
        logging.info(f" ↳ Completed in {duration_str}")
        return result

    return wrapper


def measure_step(description):
    """Decorator to measure and log duration of a simulation step."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logging.info(f"→ {description}")
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            if duration < 1:
                duration_str = "<1s"
            else:
                duration_str = f"{int(duration)}s"
            logging.info(f"   ↳ Completed in {duration_str}")
            return result

        return wrapper

    return decorator


# Add decorator to all generation functions
@measure_duration
def generate_customers(session, n=1000):
    logging.info(f"Generating {n} customers...")

    # Existing distributions
    segments = ['Retail', 'Wholesale', 'VIP']
    segment_weights = [0.7, 0.2, 0.1]  # 70% retail, 20% wholesale, 10% VIP

    regions = ['North America', 'Europe', 'Asia', 'South America', 'Africa']
    region_weights = [0.4, 0.3, 0.2, 0.07, 0.03]  # Weighted by market size

    genders = ['Male', 'Female', 'Non-binary']
    gender_weights = [0.48, 0.48, 0.04]

    contact_methods = ['Email', 'Phone', 'SMS']
    contact_weights = [0.6, 0.25, 0.15]  # Email most preferred

    # New purchase behavior distributions
    purchase_frequencies = {
        'frequent': 0.15,  # Orders multiple times per month
        'regular': 0.35,  # Orders monthly
        'occasional': 0.30,  # Orders every few months
        'rare': 0.20,  # Orders few times per year
    }

    seasonal_preferences = {
        'holiday': 0.25,  # Primarily shops during holidays
        'summer': 0.15,  # Summer reading preference
        'back-to-school': 0.20,  # Academic season preference
        'year-round': 0.40,  # No strong seasonal preference
    }

    # Define typical order values by segment and frequency
    avg_order_values = {
        'Retail': {
            'frequent': (50, 100),
            'regular': (30, 80),
            'occasional': (20, 60),
            'rare': (15, 40),
        },
        'Wholesale': {
            'frequent': (200, 500),
            'regular': (150, 400),
            'occasional': (100, 300),
            'rare': (80, 200),
        },
        'VIP': {
            'frequent': (150, 300),
            'regular': (100, 250),
            'occasional': (80, 200),
            'rare': (50, 150),
        },
    }

    current_date = datetime.now().date()

    for _ in range(n):
        # Generate age using normal distribution (mean=35, std=12)
        age = int(np.clip(np.random.normal(35, 12), 18, 80))

        # Select segment
        segment = random.choices(segments, weights=segment_weights)[0]

        # Determine purchase frequency based on segment
        segment_frequency_weights = {
            'Retail': [0.1, 0.3, 0.4, 0.2],  # Retail customers tend to be occasional
            'Wholesale': [
                0.3,
                0.4,
                0.2,
                0.1,
            ],  # Wholesale customers tend to be regular/frequent
            'VIP': [0.4, 0.3, 0.2, 0.1],  # VIP customers tend to be frequent
        }

        purchase_frequency = random.choices(
            list(purchase_frequencies.keys()),
            weights=segment_frequency_weights[segment],
        )[0]

        # Determine seasonal preference
        seasonal_weights = list(seasonal_preferences.values())
        if segment == 'Wholesale':
            # Wholesale customers are more likely to be year-round
            seasonal_weights = [0.15, 0.15, 0.2, 0.5]
        elif segment == 'VIP':
            # VIP customers have stronger holiday preference
            seasonal_weights = [0.35, 0.15, 0.1, 0.4]

        seasonal_preference = random.choices(
            list(seasonal_preferences.keys()), weights=seasonal_weights
        )[0]

        # Calculate last purchase date based on frequency
        days_since_purchase = {
            'frequent': random.randint(1, 15),
            'regular': random.randint(15, 45),
            'occasional': random.randint(45, 120),
            'rare': random.randint(120, 365),
        }
        last_purchase_date = current_date - timedelta(
            days=days_since_purchase[purchase_frequency]
        )

        # Calculate average order value
        min_value, max_value = avg_order_values[segment][purchase_frequency]
        avg_order_value = round(random.uniform(min_value, max_value), 2)

        # Income level based on age and segment
        base_income = np.random.normal(50000, 20000)
        income_multipliers = {'Retail': 1, 'Wholesale': 1.5, 'VIP': 2.5}
        age_factor = (
            1 + 0.02 * (age - 25)
            if age < 55
            else 1 + 0.02 * (55 - 25) - 0.01 * (age - 55)
        )
        income_level = base_income * income_multipliers[segment] * age_factor

        # Calculate CLV based on frequency and average order value
        frequency_multiplier = {
            'frequent': 24,  # ~24 orders per year
            'regular': 12,  # ~12 orders per year
            'occasional': 4,  # ~4 orders per year
            'rare': 2,  # ~2 orders per year
        }

        # Project CLV over 3 years with segment-specific retention rates
        retention_rates = {'Retail': 0.6, 'Wholesale': 0.8, 'VIP': 0.9}
        yearly_value = avg_order_value * frequency_multiplier[purchase_frequency]
        clv = 0
        for year in range(3):
            clv += yearly_value * (retention_rates[segment] ** year)
        clv = round(clv, 2)

        # Account creation date with more recent bias
        days_ago = int(
            np.random.exponential(365 * 2)
        )  # Most accounts within last 2 years
        account_date = datetime.now() - timedelta(days=days_ago)

        customer = Customer(
            name=fake.name(),
            email=fake.email(),
            phone=fake.phone_number(),
            address=fake.address(),
            segment=segment,
            region=random.choices(regions, weights=region_weights)[0],
            age=age,
            gender=random.choices(genders, weights=gender_weights)[0],
            income_level=round(income_level, 2),
            clv=clv,
            account_creation_date=account_date,
            preferred_contact_method=random.choices(
                contact_methods, weights=contact_weights
            )[0],
            purchase_frequency=purchase_frequency,
            seasonal_preference=seasonal_preference,
            last_purchase_date=last_purchase_date,
            avg_order_value=avg_order_value,
        )
        session.add(customer)
    session.commit()


@measure_duration
def generate_employees(session, n=50):
    logging.info(f"Generating {n} employees...")

    # Define organizational structure
    org_levels = {
        1: {'titles': ['CEO', 'President'], 'ratio': 0.02},  # Top level
        2: {'titles': ['VP', 'Director'], 'ratio': 0.08},  # Senior management
        3: {
            'titles': ['Senior Manager', 'Regional Manager'],
            'ratio': 0.15,
        },  # Middle management
        4: {'titles': ['Manager', 'Team Lead'], 'ratio': 0.25},  # Junior management
        5: {
            'titles': ['Senior Associate', 'Specialist'],
            'ratio': 0.25,
        },  # Senior individual contributors
        6: {
            'titles': ['Associate', 'Representative'],
            'ratio': 0.25,
        },  # Junior individual contributors
    }

    departments = {
        'Sales': 0.3,
        'Operations': 0.2,
        'Customer Service': 0.2,
        'IT': 0.15,
        'HR': 0.1,
        'Finance': 0.05,
    }

    shifts = ['Morning', 'Afternoon', 'Night']

    # Calculate number of employees per level
    level_counts = {
        level: max(1, int(n * ratio['ratio'])) for level, ratio in org_levels.items()
    }

    # Adjust to ensure we hit our target number
    total = sum(level_counts.values())
    if total < n:
        level_counts[6] += n - total  # Add remaining to entry level

    employees_by_level = {level: [] for level in org_levels.keys()}
    all_employees = []

    # Generate employees level by level
    for level in sorted(org_levels.keys()):
        count = level_counts[level]

        # Base salary ranges by level
        base_salary_range = {
            1: (300000, 500000),
            2: (200000, 300000),
            3: (150000, 200000),
            4: (100000, 150000),
            5: (70000, 100000),
            6: (50000, 70000),
        }

        # Bonus percentages by level
        bonus_percentages = {
            1: (0.50, 1.00),  # 50-100% bonus potential
            2: (0.30, 0.50),  # 30-50% bonus potential
            3: (0.20, 0.30),  # 20-30% bonus potential
            4: (0.15, 0.20),  # 15-20% bonus potential
            5: (0.10, 0.15),  # 10-15% bonus potential
            6: (0.05, 0.10),  # 5-10% bonus potential
        }

        for _ in range(count):
            # Generate hire date with more senior levels having earlier dates
            max_years_ago = 20 - (level * 2)  # More senior levels hired longer ago
            min_years_ago = max(1, max_years_ago - 5)
            hire_date = fake.date_between(
                start_date=f'-{max_years_ago}y', end_date=f'-{min_years_ago}y'
            )

            # 10% chance of terminated employment for non-management levels
            termination_date = None
            if level > 3 and random.random() < 0.1:
                termination_date = fake.date_between(
                    start_date=hire_date, end_date='today'
                )

            # KPI scores tend to be higher for more senior levels
            base_kpi = 3.5 + (6 - level) * 0.2  # Higher levels have higher base KPI
            kpi_score = round(np.clip(np.random.normal(base_kpi, 0.3), 1, 5), 2)

            # Calculate salary with experience factor
            min_salary, max_salary = base_salary_range[level]
            experience_factor = (datetime.now().date() - hire_date).days / 365
            salary = min_salary + (max_salary - min_salary) * (experience_factor / 20)
            salary = round(np.clip(salary, min_salary, max_salary), 2)

            # Calculate bonus based on KPI score and level
            min_bonus_pct, max_bonus_pct = bonus_percentages[level]
            bonus_pct = min_bonus_pct + (max_bonus_pct - min_bonus_pct) * (
                kpi_score / 5
            )
            bonus = round(salary * bonus_pct, 2)

            # Determine department based on level and weights
            if level <= 2:  # Top levels can be in any department
                department = random.choices(
                    list(departments.keys()), weights=list(departments.values())
                )[0]
            else:
                # Adjust weights based on level
                dept_weights = departments.copy()
                if level >= 5:  # Entry levels more likely in Sales and Customer Service
                    dept_weights['Sales'] *= 1.5
                    dept_weights['Customer Service'] *= 1.5
                department = random.choices(
                    list(dept_weights.keys()), weights=list(dept_weights.values())
                )[0]

            # Commission only for sales department
            commission = (
                round(random.uniform(500, 5000), 2) if department == 'Sales' else 0
            )

            # Create employee
            employee = Employee(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                title=random.choice(org_levels[level]['titles']),
                department=department,
                hire_date=hire_date,
                termination_date=termination_date,
                salary=salary,
                bonus=bonus,
                commission=commission,
                kpi_score=kpi_score,
                shift=random.choice(shifts),
                level=level,
            )

            session.add(employee)
            employees_by_level[level].append(employee)
            all_employees.append(employee)

    session.commit()  # Commit to get IDs assigned

    # Assign managers
    for level in range(6, 1, -1):  # Start from bottom, excluding top level
        for employee in employees_by_level[level]:
            # Find potential managers (from level above)
            potential_managers = [
                m
                for m in employees_by_level[level - 1]
                if m.hire_date < employee.hire_date
                and m.department == employee.department  # Same department
                and len(m.direct_reports) < 8  # Limit direct reports
            ]

            if potential_managers:
                # Prefer managers in same department with fewer direct reports
                weighted_managers = [
                    (m, 1 / (len(m.direct_reports) + 1)) for m in potential_managers
                ]
                manager = random.choices(
                    [m[0] for m in weighted_managers],
                    weights=[m[1] for m in weighted_managers],
                )[0]
                employee.manager = manager

    session.commit()


@measure_duration
def generate_suppliers(session, n=100):
    logging.info(f"Generating {n} suppliers...")

    # More realistic location distribution
    locations = ['Domestic', 'International']
    location_weights = [0.7, 0.3]  # 70% domestic, 30% international

    # Contract terms with realistic distribution
    contract_terms = {
        'Net 30': 0.4,
        'Net 60': 0.3,
        'Net 90': 0.1,
        'Prepaid': 0.1,
        'Consignment': 0.1,
    }

    for _ in range(n):
        # Rating follows normal distribution centered at 3.5
        rating = round(np.clip(np.random.normal(3.5, 0.8), 1, 5), 2)

        # Relationship length follows exponential distribution
        relationship_length = int(np.random.exponential(5)) + 1  # Minimum 1 year

        supplier = Supplier(
            name=fake.company(),
            contact_name=fake.name(),
            address=fake.address(),
            rating=rating,
            location=random.choices(locations, weights=location_weights)[0],
            contract_terms=random.choices(
                list(contract_terms.keys()), weights=list(contract_terms.values())
            )[0],
            relationship_length=relationship_length,
        )
        session.add(supplier)
    session.commit()


@measure_duration
def generate_categories(session, n=20):
    logging.info(f"Generating {n} categories...")

    # Define main categories with subcategories
    category_structure = {
        'Fiction': [
            'Mystery',
            'Science Fiction',
            'Romance',
            'Fantasy',
            'Literary Fiction',
        ],
        'Non-Fiction': ['Biography', 'History', 'Science', 'Self-Help', 'Business'],
        'Children': ['Picture Books', 'Middle Grade', 'Young Adult'],
        'Academic': ['Textbooks', 'Research Papers', 'Reference'],
        'Special Interest': ['Cooking', 'Travel', 'Art', 'Religion'],
    }

    categories = []

    # Create main categories first
    for main_category in category_structure.keys():
        # Popularity follows beta distribution (most categories moderately popular)
        popularity = round(np.random.beta(2, 2) * 5, 2)

        category = Category(name=main_category, parent_id=None, popularity=popularity)
        session.add(category)
        categories.append(category)

    session.commit()  # Commit to get IDs for main categories

    # Create subcategories
    for main_category in categories:
        subcategories = category_structure[main_category.name]
        for subcategory in subcategories:
            # Subcategories tend to have lower popularity than main categories
            sub_popularity = round(np.random.beta(2, 3) * main_category.popularity, 2)

            category = Category(
                name=subcategory, parent_id=main_category.id, popularity=sub_popularity
            )
            session.add(category)

    session.commit()


@measure_duration
def generate_authors(session, n=500):
    logging.info(f"Generating {n} authors...")

    # Generate birth dates for realistic age distribution
    current_year = datetime.now().year

    for _ in range(n):
        # Authors age distribution: mostly 30-70 years old
        birth_year = int(np.random.normal((current_year - 50), 12))
        birth_year = min(
            max(birth_year, current_year - 90), current_year - 25
        )  # Clip to reasonable range

        # Some authors use pen names
        uses_pen_name = random.random() < 0.15  # 15% chance of pen name

        name = fake.name()
        if uses_pen_name:
            # Create a more artistic/memorable pen name
            if random.random() < 0.5:
                name = f"{fake.first_name()} {fake.word().title()}"
            else:
                name = f"{fake.word().title()} {fake.word().title()}"

        author = Author(name=name)
        session.add(author)

        # Add batched commits
        if _ % 100 == 0:
            session.commit()

    session.commit()


@measure_duration
def generate_books(session, n=5000):
    logging.info(f"Generating {n} books...")
    suppliers = session.query(Supplier).all()
    categories = session.query(Category).all()
    authors = session.query(Author).all()

    # Format distribution
    formats = {'Hardcover': 0.3, 'Paperback': 0.5, 'E-book': 0.15, 'Audiobook': 0.05}

    # Language distribution based on market size
    languages = {
        'English': 0.6,
        'Spanish': 0.15,
        'French': 0.1,
        'German': 0.08,
        'Chinese': 0.07,
    }

    # Price ranges by format
    price_ranges = {
        'Hardcover': (20, 45),
        'Paperback': (10, 25),
        'E-book': (5, 15),
        'Audiobook': (15, 35),
    }

    # Price change reasons with weights
    price_change_reasons = {
        'Initial Price': 1.0,  # Always for first price
        'Seasonal Adjustment': 0.3,
        'Demand-Based': 0.25,
        'Competitive Response': 0.2,
        'Promotion': 0.15,
        'Cost Change': 0.1,
    }

    for _ in range(n):
        # Select format based on weights
        book_format = random.choices(
            list(formats.keys()), weights=list(formats.values())
        )[0]

        # Generate price based on format
        min_price, max_price = price_ranges[book_format]
        base_price = round(np.random.uniform(min_price, max_price), 2)

        # Adjust price based on publication date
        publication_date = fake.date_between(start_date='-10y', end_date='today')
        days_old = (datetime.now().date() - publication_date).days
        age_discount = max(0, (days_old / 365) * 0.1)  # 10% discount per year
        price = round(base_price * (1 - age_discount), 2)

        # Generate realistic stock levels
        mean_stock = 100 if book_format != 'E-book' else 999999
        stock_level = int(np.clip(np.random.normal(mean_stock, 30), 0, mean_stock * 2))

        # Safety stock and reorder points based on format
        if book_format != 'E-book':
            safety_stock = int(mean_stock * 0.2)  # 20% of mean stock
            reorder_point = int(mean_stock * 0.4)  # 40% of mean stock
        else:
            safety_stock = 999999
            reorder_point = 999999

        # Create and add book to session first
        book = Book(
            title=fake.catch_phrase(),
            isbn=fake.isbn13(),
            format=book_format,
            language=random.choices(
                list(languages.keys()), weights=list(languages.values())
            )[0],
            price=price,
            stock_level=stock_level,
            safety_stock=safety_stock,
            reorder_point=reorder_point,
            publication_date=publication_date,
            supplier=random.choice(suppliers),
        )
        session.add(book)
        session.flush()  # This ensures the book gets an ID

        # Create initial price history entry
        initial_price = BookPriceHistory(
            book=book,
            price=price,
            effective_date=publication_date,
            change_reason='Initial Price',
        )
        session.add(initial_price)

        # Generate historical price changes
        current_price = price

        # Number of price changes depends on book age
        days_since_publication = (datetime.now().date() - publication_date).days
        num_price_changes = int(
            days_since_publication / 180
        )  # Average one change every 6 months

        if num_price_changes > 0:
            # Generate price change dates
            change_dates = sorted(
                fake.date_between(start_date=publication_date, end_date='today')
                for _ in range(num_price_changes)
            )

            for change_date in change_dates:
                # Close previous price period
                current_price_record = (
                    session.query(BookPriceHistory)
                    .filter(
                        BookPriceHistory.book_id == book.id,
                        BookPriceHistory.end_date.is_(None),
                    )
                    .first()
                )
                if current_price_record:
                    current_price_record.end_date = change_date

                # Calculate new price based on reason
                reason = random.choices(
                    list(price_change_reasons.keys())[1:],  # Exclude 'Initial Price'
                    weights=list(price_change_reasons.values())[1:],
                )[0]

                # Price adjustment based on reason
                if reason == 'Seasonal Adjustment':
                    # Higher prices during peak seasons (e.g., back to school)
                    month = change_date.month
                    if month in [8, 9]:  # Back to school
                        adjustment = random.uniform(1.1, 1.2)
                    elif month in [11, 12]:  # Holiday season
                        adjustment = random.uniform(0.8, 0.9)  # Holiday discounts
                    else:
                        adjustment = random.uniform(0.95, 1.05)

                elif reason == 'Demand-Based':
                    # Simulate price changes based on popularity
                    adjustment = random.uniform(0.9, 1.3)

                elif reason == 'Competitive Response':
                    # Usually results in price decrease
                    adjustment = random.uniform(0.8, 0.95)

                elif reason == 'Promotion':
                    # Temporary discounts
                    adjustment = random.uniform(0.7, 0.85)

                elif reason == 'Cost Change':
                    # Small adjustments up or down
                    adjustment = random.uniform(0.95, 1.05)

                new_price = round(current_price * adjustment, 2)

                # Ensure price doesn't go below minimum or above maximum
                min_price, max_price = price_ranges[book_format]
                new_price = max(min_price * 0.7, min(max_price * 1.3, new_price))

                # Create new price history entry
                price_history = BookPriceHistory(
                    book=book,
                    price=new_price,
                    effective_date=change_date,
                    change_reason=reason,
                )
                session.add(price_history)
                current_price = new_price

        # Assign 1-3 categories to each book based on logical relationships
        num_categories = random.randint(1, 3)
        # Get main category first
        main_category = random.choice(categories)
        selected_categories = [main_category]

        # Add related categories based on the main category
        if main_category.parent_id is None:  # If it's a main category
            # Add some of its subcategories
            subcategories = [
                cat for cat in categories if cat.parent_id == main_category.id
            ]
            if subcategories:
                additional_categories = random.sample(
                    subcategories, min(len(subcategories), num_categories - 1)
                )
                selected_categories.extend(additional_categories)
        else:  # If it's a subcategory
            # Maybe add its parent category
            parent = [cat for cat in categories if cat.id == main_category.parent_id][0]
            if random.random() < 0.7:  # 70% chance to include parent
                selected_categories.append(parent)
                # Maybe add a sibling category
                siblings = [
                    cat
                    for cat in categories
                    if cat.parent_id == parent.id and cat != main_category
                ]
                if siblings and random.random() < 0.3:  # 30% chance to include sibling
                    selected_categories.append(random.choice(siblings))

        book.categories = selected_categories

        # Assign authors
        book.authors = random.sample(authors, random.randint(1, 3))

        # Commit every 1000 books to avoid memory issues
        if _ % 1000 == 0:
            session.commit()

    session.commit()


@measure_duration
def generate_shippers(session, n=10):
    logging.info(f"Generating {n} shippers...")

    # Define service areas with market share weights
    service_areas = {
        'North America': 0.4,
        'Europe': 0.3,
        'Asia': 0.2,
        'South America': 0.07,
        'Africa': 0.03,
    }

    # Shipping cost models
    cost_models = {'Weight-based': 0.5, 'Distance-based': 0.3, 'Flat-rate': 0.2}

    for _ in range(n):
        # Generate realistic performance metrics
        delivery_speed = round(
            np.random.normal(4.2, 0.5), 2
        )  # Most are good performers
        reliability = round(
            np.random.normal(0.95, 0.03), 3
        )  # 95% reliable with small variance

        # Calculate overall performance rating
        performance_rating = round((delivery_speed + reliability * 5) / 2, 2)
        performance_rating = min(max(performance_rating, 1), 5)  # Clip to 1-5 range

        # Base cost varies by service area and cost model
        base_cost = np.random.normal(15, 3)  # Mean $15, std dev $3
        cost_model = random.choices(
            list(cost_models.keys()), weights=list(cost_models.values())
        )[0]

        # Adjust base cost by cost model
        if cost_model == 'Weight-based':
            base_cost *= 1.2
        elif cost_model == 'Distance-based':
            base_cost *= 1.1

        shipper = Shipper(
            name=fake.company(),
            phone=fake.phone_number(),
            service_area=random.choices(
                list(service_areas.keys()), weights=list(service_areas.values())
            )[0],
            base_cost=round(base_cost, 2),
            performance_rating=performance_rating,
        )
        session.add(shipper)
    session.commit()


@measure_duration
def generate_orders(session, n=10000):
    logging.info(f"Generating {n} orders...")
    customers = session.query(Customer).all()
    employees = session.query(Employee).all()
    shippers = session.query(Shipper).all()

    # Status distribution reflecting real-world scenarios
    statuses = ['Pending', 'Shipped', 'Delivered', 'Canceled', 'Returned']
    status_weights = [0.1, 0.2, 0.6, 0.07, 0.03]

    shipping_methods = ['Standard', 'Expedited', 'International']
    shipping_weights = [0.7, 0.2, 0.1]

    payment_methods = ['Credit Card', 'PayPal', 'Gift Card']
    payment_weights = [0.65, 0.3, 0.05]

    # Generate orders with seasonal patterns
    start_date = datetime.now() - timedelta(days=365 * 5)  # 5 years ago
    end_date = datetime.now()

    for _ in range(n):
        # Generate seasonal order date
        order_date = generate_seasonal_date(start_date, end_date)

        # Simulate seasonal discounts
        base_discount = np.random.exponential(5)  # Most discounts are small

        # Increase discounts during holiday seasons
        if order_date.month in [11, 12]:  # Holiday season
            discount = base_discount * 2
        elif order_date.month in [7, 8]:  # Back to school
            discount = base_discount * 1.5
        else:
            discount = base_discount

        # Simulate fraud patterns
        is_suspicious = random.random() < 0.01  # 1% chance of suspicious order

        if is_suspicious:
            status = 'Pending'
            payment_method = 'Gift Card'
            shipping_method = random.choice(['Expedited', 'International'])
        else:
            status = random.choices(statuses, weights=status_weights)[0]
            payment_method = random.choices(payment_methods, weights=payment_weights)[0]
            shipping_method = random.choices(
                shipping_methods, weights=shipping_weights
            )[0]

        # Calculate tax based on order value and region
        base_tax_rate = 0.08  # 8% base tax rate
        customer = random.choice(customers)
        # Adjust tax rate based on region
        tax_multipliers = {
            'North America': 1,
            'Europe': 1.2,
            'Asia': 0.9,
            'South America': 0.85,
            'Africa': 0.8,
        }
        tax_rate = base_tax_rate * tax_multipliers[customer.region]
        tax = round(random.uniform(5, 50) * tax_rate, 2)  # Simplified calculation

        order = Order(
            order_date=order_date,
            status=status,
            shipping_method=shipping_method,
            payment_method=payment_method,
            discount=round(discount, 2),
            tax=tax,
            customer=customer,
            employee=random.choice(employees),
            shipper=random.choice(shippers),
        )
        session.add(order)
    session.commit()


@measure_duration
def generate_order_items(session, n=30000):
    logging.info(f"Generating {n} order items...")

    # Fetch all required data upfront
    orders = session.query(Order).all()
    books = session.query(Book).all()

    # Pre-calculate book categories for faster lookup
    book_categories = {book.id: [cat.name for cat in book.categories] for book in books}

    # Bundle patterns for quick reference
    bundle_patterns = {
        'Series Collection': ['Science Fiction', 'Fantasy'],
        'Educational Pack': ['Textbooks', 'Reference'],
        'Starter Kit': ['Self-Help', 'Business'],
        'Children Set': ['Picture Books', 'Middle Grade'],
    }

    # Track books per order for realistic distribution
    books_per_order = {}
    order_items = []
    batch_size = 1000

    for i in range(n):
        order = random.choice(orders)

        # Initialize books count for this order if not exists
        if order.id not in books_per_order:
            books_per_order[order.id] = 0

        # Check if this should be part of a bundle
        create_bundle = (
            books_per_order[order.id] == 0 and random.random() < 0.15
        )  # 15% chance of bundle for new orders

        if create_bundle:
            # Select bundle type based on category
            bundle_type = random.choice(list(bundle_patterns.keys()))
            relevant_categories = bundle_patterns[bundle_type]

            # Get books from relevant categories using pre-calculated categories
            bundle_books = [
                b
                for b in books
                if any(cat in relevant_categories for cat in book_categories[b.id])
            ]

            # Select 3-5 books for the bundle
            bundle_size = random.randint(3, 5)
            if len(bundle_books) >= bundle_size:
                bundle_items = random.sample(bundle_books, bundle_size)
                bundle_discount = 0.2  # 20% discount for bundles

                for book in bundle_items:
                    # Use the get_price_at_date method
                    base_price = book.get_price_at_date(session, order.order_date)
                    discounted_price = base_price * (1 - bundle_discount)

                    order_items.append(
                        {
                            'order_id': order.id,
                            'book_id': book.id,
                            'quantity': 1,
                            'unit_price': round(discounted_price, 2),
                        }
                    )
                    books_per_order[order.id] += 1

        else:
            # Regular order item
            book = random.choice(books)

            # Use pre-calculated categories for quantity determination
            book_cats = book_categories[book.id]
            if any(cat in ['Textbooks', 'Reference'] for cat in book_cats):
                quantity = int(np.random.exponential(2)) + 1
            else:
                quantity = 1 if random.random() < 0.8 else random.randint(2, 3)

            # Get historical price
            unit_price = book.get_price_at_date(session, order.order_date)

            # Apply discounts
            if quantity > 2:
                unit_price *= 0.9  # 10% bulk discount
            if book.stock_level > book.safety_stock * 2:
                unit_price *= 0.95  # 5% discount for overstocked items

            order_items.append(
                {
                    'order_id': order.id,
                    'book_id': book.id,
                    'quantity': quantity,
                    'unit_price': round(unit_price, 2),
                }
            )
            books_per_order[order.id] += 1

        # Batch insert when we reach batch_size
        if len(order_items) >= batch_size:
            session.execute(OrderItem.__table__.insert(), order_items)
            session.commit()
            order_items = []

    # Insert any remaining items
    if order_items:
        session.execute(OrderItem.__table__.insert(), order_items)
        session.commit()


@measure_duration
def generate_customer_service_interactions(session, n=2000):
    logging.info(f"Generating {n} customer service interactions...")
    customers = session.query(Customer).all()
    cs_employees = (
        session.query(Employee)
        .filter(
            Employee.department == 'Customer Service',
            Employee.termination_date.is_(None),
        )
        .all()
    )

    # Define interaction types with realistic weights and order relevance
    interaction_types = {
        'Order Status Inquiry': {
            'weight': 0.25,
            'needs_order': True,
            'typical_priority': 'Normal',
            'satisfaction_range': (3, 5),  # Usually satisfactory
            'resolution_days': (0, 2),  # Quick resolution
        },
        'Return Request': {
            'weight': 0.15,
            'needs_order': True,
            'typical_priority': 'High',
            'satisfaction_range': (2, 4),  # Mixed satisfaction
            'resolution_days': (1, 5),
        },
        'Product Information': {
            'weight': 0.15,
            'needs_order': False,
            'typical_priority': 'Low',
            'satisfaction_range': (3, 5),
            'resolution_days': (0, 1),
        },
        'Technical Support': {
            'weight': 0.10,
            'needs_order': False,
            'typical_priority': 'Normal',
            'satisfaction_range': (2, 5),
            'resolution_days': (1, 3),
        },
        'Complaint': {
            'weight': 0.10,
            'needs_order': True,
            'typical_priority': 'High',
            'satisfaction_range': (1, 3),  # Usually unsatisfactory
            'resolution_days': (2, 7),  # Takes longer to resolve
        },
        'Billing Issue': {
            'weight': 0.10,
            'needs_order': True,
            'typical_priority': 'High',
            'satisfaction_range': (2, 4),
            'resolution_days': (1, 4),
        },
        'Account Management': {
            'weight': 0.08,
            'needs_order': False,
            'typical_priority': 'Normal',
            'satisfaction_range': (3, 5),
            'resolution_days': (0, 2),
        },
        'Shipping Delay': {
            'weight': 0.07,
            'needs_order': True,
            'typical_priority': 'High',
            'satisfaction_range': (2, 4),
            'resolution_days': (1, 5),
        },
    }

    channels = {'Phone': 0.4, 'Email': 0.3, 'Chat': 0.2, 'Social Media': 0.1}

    status_progression = {
        'Open': 0.1,
        'In Progress': 0.15,
        'Pending Customer': 0.05,
        'Escalated': 0.05,
        'Resolved': 0.15,
        'Closed': 0.5,
    }

    # Templates for realistic notes
    note_templates = {
        'Order Status Inquiry': [
            "Customer inquired about delivery timeline for order #{order_id}",
            "Provided tracking information for order #{order_id}",
            "Updated customer on shipping status of order #{order_id}",
        ],
        'Return Request': [
            "Customer requesting return for order #{order_id}. Reason: {reason}",
            "Processed return authorization for order #{order_id}",
            "Explained return policy for items in order #{order_id}",
        ],
        'Complaint': [
            "Customer expressed dissatisfaction with {issue} in order #{order_id}",
            "Addressing customer concerns regarding order #{order_id}",
            "Escalated complaint about order #{order_id} to supervisor",
        ],
        'Shipping Delay': [
            "Customer inquired about delayed delivery for order #{order_id}",
            "Investigating shipping delay for order #{order_id}",
            "Provided compensation for delayed order #{order_id}",
        ],
    }

    return_reasons = [
        "Wrong size/fit",
        "Damaged in shipping",
        "Not as described",
        "Changed mind",
        "Defective product",
    ]

    complaint_issues = [
        "delivery time",
        "product quality",
        "customer service",
        "billing",
        "website functionality",
    ]

    for _ in range(n):
        # Select interaction type based on weights
        interaction_type = random.choices(
            list(interaction_types.keys()),
            weights=[t['weight'] for t in interaction_types.values()],
        )[0]
        type_info = interaction_types[interaction_type]

        # Select customer and potentially related order
        customer = random.choice(customers)
        order = None
        if type_info['needs_order'] and customer.orders:
            order = random.choice(customer.orders)
            # Ensure interaction date is after order date
            min_date = order.order_date
            max_date = min_date + timedelta(days=30)
        else:
            # For non-order interactions, use customer's account creation date
            min_date = customer.account_creation_date
            max_date = datetime.now().date()

        interaction_date = fake.date_between(start_date=min_date, end_date=max_date)

        # Calculate resolution date based on type
        min_days, max_days = type_info['resolution_days']
        resolution_date = None
        status = random.choices(
            list(status_progression.keys()), weights=list(status_progression.values())
        )[0]

        if status in ['Resolved', 'Closed']:
            resolution_date = interaction_date + timedelta(
                days=random.randint(min_days, max_days)
            )

        # Generate satisfaction score if resolved
        satisfaction_score = None
        if resolution_date:
            min_score, max_score = type_info['satisfaction_range']
            satisfaction_score = random.randint(min_score, max_score)

        # Generate realistic notes
        if interaction_type in note_templates:
            note_template = random.choice(note_templates[interaction_type])
            if interaction_type == 'Return Request':
                notes = note_template.format(
                    order_id=order.id if order else 'N/A',
                    reason=random.choice(return_reasons),
                )
            elif interaction_type == 'Complaint':
                notes = note_template.format(
                    order_id=order.id if order else 'N/A',
                    issue=random.choice(complaint_issues),
                )
            else:
                notes = note_template.format(order_id=order.id if order else 'N/A')
        else:
            notes = fake.sentence()

        interaction = CustomerServiceInteraction(
            customer=customer,
            order=order,
            interaction_date=interaction_date,
            interaction_type=interaction_type,
            channel=random.choices(
                list(channels.keys()), weights=list(channels.values())
            )[0],
            priority=type_info['typical_priority'],
            status=status,
            resolution_date=resolution_date,
            satisfaction_score=satisfaction_score,
            notes=notes,
            employee=random.choice(cs_employees) if cs_employees else None,
        )
        session.add(interaction)

        # Batch commits
        if _ % 100 == 0:
            session.commit()

    session.commit()


@measure_duration
def generate_cross_functional_data(session):
    """Generate additional cross-functional relationships and data points."""
    logging.info("Generating cross-functional data relationships...")

    # Get existing data
    orders = session.query(Order).all()
    customers = session.query(Customer).all()
    books = session.query(Book).all()

    # Update category popularity based on book sales
    category_popularity = {}
    for book in books:
        sales = sum(
            item.quantity
            for order in orders
            for item in order.order_items
            if item.book_id == book.id
        )
        # Update popularity for all categories of the book
        for category in book.categories:
            category_popularity[category.id] = (
                category_popularity.get(category.id, 0) + sales
            )

    # Normalize and update category popularity
    if category_popularity:
        max_sales = max(category_popularity.values())
        for category_id, sales in category_popularity.items():
            category = session.get(Category, category_id)
            if category:
                category.popularity = round((sales / max_sales) * 5, 2)  # Scale to 0-5

    # Update customer CLV based on actual order history
    for customer in customers:
        total_spent = sum(
            item.quantity * item.unit_price
            for order in customer.orders
            for item in order.order_items
        )
        # Adjust CLV based on actual spending
        customer.clv = round(
            total_spent * 1.2, 2
        )  # Expected future value 20% higher than historical

    # Create supplier performance metrics based on order history
    supplier_metrics = {}
    for book in books:
        supplier_id = book.supplier_id
        if supplier_id not in supplier_metrics:
            supplier_metrics[supplier_id] = {
                'total_sales': 0,
                'stock_outs': 0,
                'total_revenue': 0,
            }

        # Calculate metrics
        sales = sum(
            item.quantity
            for order in orders
            for item in order.order_items
            if item.book_id == book.id
        )
        supplier_metrics[supplier_id]['total_sales'] += sales
        supplier_metrics[supplier_id]['total_revenue'] += sales * book.price
        if book.stock_level < book.safety_stock:
            supplier_metrics[supplier_id]['stock_outs'] += 1

    # Update supplier ratings based on metrics
    for supplier_id, metrics in supplier_metrics.items():
        supplier = session.get(Supplier, supplier_id)
        if supplier:
            # Calculate rating based on sales performance and stock management
            sales_score = min(
                5, metrics['total_sales'] / 100
            )  # Scale based on sales volume
            stock_score = 5 - min(
                5, metrics['stock_outs']
            )  # Lower score for stock outs
            supplier.rating = round((sales_score + stock_score) / 2, 2)

    session.commit()


@measure_step("Simulating customer churn patterns")
def simulate_customer_churn(session):
    """Simulate customer churn patterns to create realistic patterns in the data."""

    # Get existing data
    customers = session.query(Customer).all()

    current_date = datetime.now().date()

    for customer in customers:
        if customer.orders:
            last_order = max(customer.orders, key=lambda x: x.order_date)
            days_since_last_order = (current_date - last_order.order_date).days

            # Mark customers as likely to churn if inactive for long periods
            if days_since_last_order > 365:  # Inactive for 1 year
                customer.clv *= 0.5  # Reduce CLV for churning customers

                # Create retention attempt interaction
                if random.random() < 0.7:  # 70% chance of retention attempt
                    interaction = CustomerServiceInteraction(
                        customer=customer,
                        order=last_order,
                        interaction_date=current_date
                        - timedelta(days=random.randint(1, 30)),
                        interaction_type='Retention',
                        notes="Customer identified as at-risk for churn. "
                        "Retention offer made.",
                    )
                    session.add(interaction)


@measure_step("Simulating inventory management scenarios")
def simulate_inventory(session):
    """Simulate inventory management scenarios to create realistic patterns
    in the data."""

    # Get existing data
    books = session.query(Book).all()
    orders = session.query(Order).all()

    # Pre-calculate order counts for each book
    order_counts = {book.id: 0 for book in books}
    for order in orders:
        for item in order.order_items:
            order_counts[item.book_id] += item.quantity

    for book in books:
        # Simulate stockouts for popular items
        if book.format != 'E-book':
            order_count = order_counts[book.id]
            if order_count > 50:  # Popular book
                if random.random() < 0.2:  # 20% chance of stockout
                    book.stock_level = 0
                    book.reorder_point *= (
                        1.2  # Increase reorder point for frequently stocked-out items
                    )

    session.commit()


@measure_step("Simulating promotional impacts")
def simulate_promotions(session):
    """Simulate promotional impacts to create realistic patterns in the data."""

    # Get existing data
    orders = session.query(Order).all()

    current_date = datetime.now().date()

    # 1. Promotional Impact Simulation
    promotion_periods = [
        (
            current_date - timedelta(days=60),
            current_date - timedelta(days=45),
            'Holiday Sale',
        ),
        (
            current_date - timedelta(days=120),
            current_date - timedelta(days=105),
            'Back to School',
        ),
        (
            current_date - timedelta(days=180),
            current_date - timedelta(days=165),
            'Summer Reading',
        ),
    ]

    for order in orders:
        # Check if order falls within promotion periods
        for start_date, end_date, promo_name in promotion_periods:
            # Convert order_date to date if it's datetime
            order_date = (
                order.order_date.date()
                if isinstance(order.order_date, datetime)
                else order.order_date
            )

            if start_date <= order_date <= end_date:
                # Increase discount for promotional periods
                order.discount = max(order.discount, random.uniform(0.15, 0.30))
                # Add promotion name to notes
                if not order.notes:
                    order.notes = f"Part of {promo_name} promotion"


@measure_step("Simulating fraud patterns")
def simulate_fraud(session):
    """Simulate fraud patterns to create realistic patterns in the data."""

    # Get existing data
    orders = session.query(Order).all()

    # Pre-calculate order values and counts for each customer
    customer_order_data = {}
    for order in orders:
        if order.customer_id not in customer_order_data:
            customer_order_data[order.customer_id] = {
                'order_count': 0,
                'total_value': 0,
                'orders': [],
            }
        order_value = sum(item.quantity * item.unit_price for item in order.order_items)
        customer_order_data[order.customer_id]['order_count'] += 1
        customer_order_data[order.customer_id]['total_value'] += order_value
        customer_order_data[order.customer_id]['orders'].append(order)

    # Detect suspicious patterns
    for customer_id, data in customer_order_data.items():
        # Pattern 1: Multiple orders in short timeframe
        for order in data['orders']:
            same_day_orders = [
                o
                for o in data['orders']
                if abs((o.order_date - order.order_date).days) < 1
            ]
            if len(same_day_orders) > 3:
                for o in same_day_orders:
                    o.status = 'Pending Review'
                    o.notes = (
                        o.notes or ''
                    ) + ' [Flagged for review - multiple orders]'

        # Pattern 2: Unusually high value orders
        for order in data['orders']:
            order_value = sum(
                item.quantity * item.unit_price for item in order.order_items
            )
            if order_value > 1000:  # High value threshold
                order.status = 'Pending Review'
                order.notes = (order.notes or '') + ' [Flagged for review - high value]'

        # Pattern 3: Unusual shipping patterns
        for order in data['orders']:
            order_value = sum(
                item.quantity * item.unit_price for item in order.order_items
            )
            if (
                order.shipping_method == 'Expedited'
                and order.payment_method == 'Gift Card'
                and order_value > 500
            ):
                order.status = 'Pending Review'
                order.notes = (
                    order.notes or ''
                ) + ' [Flagged for review - unusual shipping]'

    session.commit()


@measure_step("Simulating dynamic pricing")
def simulate_pricing(session):
    """Simulate dynamic pricing to create realistic patterns in the data."""

    # Get existing data
    books = session.query(Book).all()
    orders = session.query(Order).all()

    # Pre-calculate order counts for each book
    order_counts = {book.id: 0 for book in books}
    for order in orders:
        for item in order.order_items:
            order_counts[item.book_id] += item.quantity

    for book in books:
        # Adjust prices based on demand (order frequency)
        order_count = order_counts[book.id]
        if order_count > 100:  # High demand
            book.price *= 1.1  # 10% price increase
        elif order_count < 10:  # Low demand
            book.price *= 0.9  # 10% price decrease

        # Adjust prices based on competition (simulated)
        if random.random() < 0.1:  # 10% chance of competitive pressure
            book.price *= random.uniform(0.85, 0.95)

    session.commit()


@measure_duration
def simulate_business_scenarios(session):
    """Simulate various business scenarios to create realistic patterns in the data."""
    logging.info("Simulating business scenarios...")

    simulate_customer_churn(session)
    simulate_inventory(session)
    simulate_promotions(session)
    simulate_fraud(session)
    simulate_pricing(session)

    session.commit()


@measure_duration
def introduce_data_anomalies(session):
    """Introduce realistic data anomalies and exceptions into the dataset."""
    logging.info("Introducing data anomalies and exceptions...")

    customers = session.query(Customer).all()
    orders = session.query(Order).all()
    books = session.query(Book).all()

    # 1. Incomplete Customer Data (5% of customers)
    logging.info("Adding incomplete customer records...")
    for customer in random.sample(customers, int(len(customers) * 0.05)):
        field_to_nullify = random.choice(['email', 'phone', 'address'])
        setattr(customer, field_to_nullify, None)

        # Add note about incomplete data
        customer_interaction = CustomerServiceInteraction(
            customer=customer,
            interaction_date=datetime.now().date(),
            interaction_type='Data Quality Issue',
            notes=f"Missing {field_to_nullify} information",
        )
        session.add(customer_interaction)

    # 2. Duplicate Customer Records (1% of customers)
    logging.info("Creating duplicate customer records...")
    for customer in random.sample(customers, int(len(customers) * 0.01)):
        duplicate = Customer(
            name=customer.name,
            email=customer.email,
            phone=customer.phone,
            address=customer.address,
            segment=customer.segment,
            region=customer.region,
            age=customer.age,
            gender=customer.gender,
            income_level=customer.income_level,
            clv=customer.clv,
            account_creation_date=customer.account_creation_date,
            preferred_contact_method=customer.preferred_contact_method,
        )
        session.add(duplicate)

    # 3. Typos in customer names (2% of customers)
    logging.info("Introducing typos in customer names...")
    typo_patterns = {
        'replace_vowel': lambda s: s.replace('a', '@', 1).replace('i', '1', 1),
        'add_numbers': lambda s: s + '123',
        'add_special': lambda s: s + '!!',
        'uppercase': lambda s: s.upper(),
        'lowercase': lambda s: s.lower(),
    }

    for customer in random.sample(customers, int(len(customers) * 0.02)):
        pattern_name = random.choice(list(typo_patterns.keys()))
        customer.name = typo_patterns[pattern_name](customer.name)

    # 4. Inconsistent phone number formats (3% of customers)
    logging.info("Creating inconsistent phone formats...")

    def generate_phone(pattern):
        return ''.join(str(random.randint(0, 9)) if c == 'X' else c for c in pattern)

    phone_formats = [
        '(XXX) XXX-XXXX',
        'XXX.XXX.XXXX',
        'XXX-XXX-XXXX',
        'XXXXXXXXXX',
        '+1XXXXXXXXXX',
    ]

    for customer in random.sample(customers, int(len(customers) * 0.03)):
        pattern = random.choice(phone_formats)
        customer.phone = generate_phone(pattern)

    # 5. Outlier Values
    logging.info("Introducing outlier values...")

    # Extreme prices (0.5% of books)
    for book in random.sample(books, int(len(books) * 0.005)):
        if random.random() < 0.5:
            # Extremely high price
            book.price *= 100
        else:
            # Extremely low price (pricing error)
            book.price = 0.01

    # Unusual order quantities (0.5% of orders)
    for order in random.sample(orders, int(len(orders) * 0.005)):
        if order.order_items:
            item = random.choice(order.order_items)
            item.quantity = random.randint(1000, 5000)

    # 6. Inconsistent Dates
    logging.info("Introducing date inconsistencies...")

    # Future dates (0.1% of orders)
    future_dates = [
        datetime.now().date() + timedelta(days=random.randint(1, 365))
        for _ in range(int(len(orders) * 0.001))
    ]

    for order, future_date in zip(
        random.sample(orders, len(future_dates)), future_dates
    ):
        order.order_date = future_date

    session.commit()
    logging.info("Data anomalies introduction complete.")


@measure_duration
def generate_data():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s │ %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    logging.info("Starting data generation...")
    logging.info("═" * 40)

    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        generate_customers(session, n=1000)
        generate_employees(session, n=50)
        generate_suppliers(session, n=100)
        generate_categories(session, n=20)
        generate_authors(session, n=500)
        generate_books(session, n=5000)
        generate_shippers(session, n=10)
        generate_orders(session, n=10000)
        generate_order_items(session, n=30000)
        generate_customer_service_interactions(session, n=2000)
        generate_cross_functional_data(session)
        simulate_business_scenarios(session)
        introduce_data_anomalies(session)

        logging.info("Data generation completed successfully")
        logging.info("═" * 40)
    finally:
        session.close()


if __name__ == "__main__":
    generate_data()
