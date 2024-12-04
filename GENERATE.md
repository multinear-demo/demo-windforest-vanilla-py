# Generating a Complex Mock Database for AI Text-to-SQL Testing

## Introduction

In the realm of database-driven applications, the **Northwind** database has long been a staple for learning and testing. It provides a complex yet understandable environment that mirrors real-world business operations. However, we sought to create our own version — a database that emulates the complexities of Northwind without directly copying it. This document outlines the rationale, design, and implementation details of our custom database, which serves as an excellent testing ground for AI-powered text-to-SQL solutions.

## Rationale Behind the Custom Database

The primary goal was to build a comprehensive database that:

- **Reflects Real-World Business Complexities**: Mimicking an actual business environment with relevant entities and relationships.
- **Avoids Legal Issues**: By creating our own data generation logic and structure, we steer clear of any legal concerns associated with using the Northwind database.
- **Facilitates AI Text-to-SQL Testing**: Providing a robust dataset that challenges AI models to generate accurate SQL queries from natural language.

## Overview of the Database Structure

Our database models a fictional company involved in selling books and includes entities like customers, employees, suppliers, products (books), categories, orders, and more. The SQLite database is populated using Python and SQLAlchemy, ensuring ease of use and adaptability.

### Core Entities and Relationships

- **Customers**: Individuals who purchase books.
- **Employees**: Staff members handling various operational roles.
- **Suppliers**: Entities supplying books.
- **Categories**: Classification of books into genres and types.
- **Authors**: Writers of books.
- **Books**: Products sold by the company.
- **Shippers**: Companies responsible for delivering orders.
- **Orders**: Purchases made by customers.
- **Order Items**: Line items within an order, detailing the books purchased.
- **Customer Service Interactions**: Records of customer support engagements.

### Complex Relationships

- **One-to-Many Relationships**:
  - **Customers to Orders**: One customer can have multiple orders.
  - **Employees to Orders**: One employee can handle multiple orders.
  - **Suppliers to Books**: One supplier can supply multiple books.
- **Many-to-Many Relationships**:
  - **Books to Categories**: A book can belong to multiple categories, and each category can have multiple books.
  - **Books to Authors**: A book can have multiple authors, and an author can write multiple books.
- **Hierarchical Relationships**:
  - **Employees to Employees**: Employees can manage other employees.
  - **Categories to Subcategories**: Categories can have parent categories, forming a hierarchy.

## Data Generation Logic and Complexities

To create a realistic and complex dataset, we implemented detailed data generation functions for each entity, incorporating statistical distributions, real-world patterns, and business logic.

### 1. Customers

**Objective**: Simulate realistic customer behaviors and demographics.

**Data Generation Details**:

- **Segments**: Customers are divided into *Retail*, *Wholesale*, and *VIP* segments with weighted probabilities.
- **Regions**: Customers come from different regions with market-size-based weighting.
- **Purchase Behavior**:
  - **Purchase Frequencies**: Customers are categorized as *frequent*, *regular*, *occasional*, or *rare* buyers.
  - **Seasonal Preferences**: Preferences like *holiday*, *summer*, *back-to-school*, or *year-round* shopping habits are assigned.
  - **Last Purchase Date**: Calculated based on purchase frequency to simulate recency.
  - **Average Order Value**: Determined by segment and purchase frequency, introducing variability in spending habits.
- **Income Level and CLV**:
  - **Income Level**: Calculated using age and segment multipliers to reflect realistic earnings.
  - **Customer Lifetime Value (CLV)**: Projected over three years considering retention rates and spending patterns.
- **Account Details**:
  - **Account Creation Date**: More recent dates are favored to simulate new customer acquisition.
  - **Preferred Contact Method**: Assigned based on common preferences.

**Complexities Introduced**:

- **Statistical Distributions**: Used normal, exponential, and beta distributions to mimic real-world demographic spreads.
- **Behavioral Patterns**: Modeled seasonal shopping habits and purchase frequencies.
- **Lifecycle Simulation**: Calculated CLV and last purchase dates to reflect customer engagement over time.

### 2. Employees

**Objective**: Create a realistic organizational structure with hierarchical relationships.

**Data Generation Details**:

- **Organizational Levels**: Six levels from top management (CEO) to entry-level positions.
- **Titles and Departments**: Assigned based on organizational level and department distribution.
- **Managerial Relationships**:
  - **Managers**: Employees at higher levels manage those at lower levels.
  - **Direct Reports**: Limited to maintain realistic team sizes.
- **Compensation**:
  - **Salary**: Based on level, experience, and performance.
  - **Bonus and Commission**: Calculated using KPI scores and applicable to certain departments.
- **Performance Metrics**:
  - **KPI Scores**: Higher levels tend to have higher base KPI scores.
  - **Termination Dates**: Some employees may have left the company.

**Complexities Introduced**:

- **Hierarchical Modeling**: Employees managing other employees with recursive relationships.
- **Compensation Structures**: Variable salary, bonus, and commission based on multiple factors.
- **Departmental Distribution**: Weighted probabilities to reflect company structure.

### 3. Suppliers

**Objective**: Represent suppliers with realistic profiles and relationships to books.

**Data Generation Details**:

- **Locations**: Classified as *Domestic* or *International* with weighted probabilities.
- **Contract Terms**: Varied terms like *Net 30*, *Net 60*, *Prepaid*, etc., with assigned probabilities.
- **Rating and Relationships**:
  - **Ratings**: Generated using a normal distribution centered around a satisfactory level.
  - **Relationship Length**: Simulated using an exponential distribution to represent years of partnership.

**Complexities Introduced**:

- **Distribution Modeling**: Used statistical methods to represent supplier ratings and relationship lengths.
- **Contract Variation**: Introduced diverse contract terms to affect business dynamics.

### 4. Categories

**Objective**: Create a hierarchical category system for books.

**Data Generation Details**:

- **Main Categories and Subcategories**: Defined primary categories with associated subcategories.
- **Popularity Metrics**: Assigned using beta distributions to reflect varying levels of interest.
- **Hierarchical Links**: Subcategories reference their parent categories to form a tree structure.

**Complexities Introduced**:

- **Hierarchical Relationships**: Modeled parent-child relationships among categories.
- **Popularity Variance**: Used statistical distributions to vary the popularity of categories realistically.

### 5. Authors

**Objective**: Populate the database with authors, some using pen names.

**Data Generation Details**:

- **Age Distribution**: Birth years generated to ensure authors are within a realistic age range.
- **Pen Names**: A percentage of authors are assigned pen names, adding diversity to the data.

**Complexities Introduced**:

- **Demographic Variation**: Ensured authors' ages reflect real-world industry demographics.
- **Pen Name Usage**: Added layers of complexity to author identification.

### 6. Books

**Objective**: Generate books with diverse attributes and relationships.

**Data Generation Details**:

- **Formats and Languages**: Assigned based on market trends and probabilities.
- **Pricing and Price History**:
  - **Base Price**: Determined by format and adjusted for publication date (age discount).
  - **Price Changes**: Historical price changes simulated based on reasons like demand, seasonal adjustments, and promotions.
- **Stock Levels**: Calculated mean stock levels, safety stock, and reorder points.
- **Categories and Authors**: Books are linked to multiple categories and authors to reflect real-world associations.

**Complexities Introduced**:

- **Dynamic Pricing**: Simulated price changes over time with reasons and effective dates.
- **Inventory Management**: Included stock levels, safety stock, and reorder points.
- **Many-to-Many Relationships**: Linked books to multiple categories and authors.

### 7. Shippers

**Objective**: Represent shipping companies with performance metrics.

**Data Generation Details**:

- **Service Areas**: Assigned based on market share.
- **Performance Ratings**: Calculated using delivery speed and reliability.
- **Cost Models**: Varied cost models like *Weight-based*, *Distance-based*, and *Flat-rate*.

**Complexities Introduced**:

- **Performance Calculations**: Used statistical distributions for delivery speed and reliability.
- **Cost Model Variations**: Affected base costs and shipping charges.

### 8. Orders

**Objective**: Simulate customer orders with complexities like seasonal patterns and fraud detection.

**Data Generation Details**:

- **Order Dates**: Generated with higher probabilities during peak seasons.
- **Discounts and Taxes**:
  - **Seasonal Discounts**: Increased during holidays and special events.
  - **Tax Calculations**: Adjusted based on customer's region.
- **Fraud Patterns**:
  - **Suspicious Orders**: Introduced anomalies like high-value orders, multiple orders in a short time, and unusual shipping methods.
- **Statuses and Methods**:
  - **Order Statuses**: Assigned with weighted probabilities, including *Pending*, *Shipped*, *Delivered*, etc.
  - **Shipping and Payment Methods**: Varied to reflect customer preferences.

**Complexities Introduced**:

- **Seasonal Effects**: Simulated demand fluctuations and discount strategies.
- **Fraud Simulation**: Introduced patterns to test data integrity and fraud detection mechanisms.

### 9. Order Items

**Objective**: Populate orders with line items, considering bundling and bulk purchases.

**Data Generation Details**:

- **Bundles**: Created bundles based on patterns (e.g., *Series Collection*, *Educational Pack*) with discounts.
- **Quantities**: Adjusted quantities based on product types (e.g., textbooks often purchased in bulk).
- **Pricing**:
  - **Bulk Discounts**: Applied for larger quantities.
  - **Overstock Discounts**: Applied if stock levels were significantly above safety stock.

**Complexities Introduced**:

- **Bundle Logic**: Introduced complex purchasing patterns.
- **Dynamic Pricing**: Adjusted unit prices based on various factors.

### 10. Customer Service Interactions

**Objective**: Record customer interactions with support, adding depth to customer profiles.

**Data Generation Details**:

- **Interaction Types**: Varied types like *Order Status Inquiry*, *Return Request*, *Complaint*, etc., with associated probabilities.
- **Channels and Priorities**: Determined how customers reached out and the urgency of their issues.
- **Resolutions**:
  - **Satisfaction Scores**: Assigned based on interaction type and resolution.
  - **Resolution Dates**: Calculated to reflect processing times.
- **Notes**: Generated realistic notes, sometimes using templates for consistency.

**Complexities Introduced**:

- **Behavioral Simulation**: Modeled realistic customer service scenarios.
- **Data Richness**: Added depth to customer profiles and potential insights into customer satisfaction.

## Simulating Business Scenarios and Data Anomalies

To further increase the complexity and realism of the dataset, we simulated several business scenarios and introduced data anomalies.

### Simulated Scenarios

1. **Customer Churn Patterns**:
   - Identified inactive customers and adjusted their CLV.
   - Created retention interaction records.

2. **Inventory Management**:
   - Simulated stockouts for popular books.
   - Adjusted reorder points based on demand.

3. **Promotional Impacts**:
   - Increased discounts during promotions (e.g., *Holiday Sale*, *Back to School*).
   - Annotated orders with promotion names.

4. **Fraud Patterns**:
   - Flagged orders with suspicious patterns for review.
   - Annotated orders with notes indicating potential fraud.

5. **Dynamic Pricing**:
   - Adjusted book prices based on demand and competition.
   - Implemented price increases for high-demand books and decreases for low-demand ones.

### Data Anomalies Introduced

1. **Incomplete Customer Data**:
   - Nullified certain fields (e.g., email, phone) for some customers.
   - Recorded interactions about data quality issues.

2. **Duplicate Customer Records**:
   - Created exact copies of some customer records to simulate duplicates.

3. **Typos in Customer Names**:
   - Altered names using various patterns to introduce inconsistencies.

4. **Inconsistent Phone Number Formats**:
   - Generated phone numbers in different formats.

5. **Outlier Values**:
   - Assigned extreme prices to some books.
   - Set unusually high quantities in some order items.

6. **Inconsistent Dates**:
   - Assigned future dates to some orders to simulate data entry errors.

## Sample SQL Queries

To test the AI's ability to generate SQL queries, here are some sample queries ranging from simple to complex.

### Simple Queries

1. **List All Customers in North America**

   ```sql
   SELECT id, name, region
   FROM customers
   WHERE region = 'North America';
   ```

2. **Find Books Priced Above $30**

   ```sql
   SELECT id, title, price
   FROM books
   WHERE price > 30;
   ```

3. **Get Total Number of Orders Placed**

   ```sql
   SELECT COUNT(*) AS total_orders
   FROM orders;
   ```

### Intermediate Queries

4. **Find Employees Who Have Managed More Than 50 Orders**

   ```sql
   SELECT e.id, e.first_name, e.last_name, COUNT(o.id) AS order_count
   FROM employees e
   INNER JOIN orders o ON e.id = o.employee_id
   GROUP BY e.id
   HAVING COUNT(o.id) > 50;
   ```

5. **List Top 5 Most Popular Book Categories**

   ```sql
   SELECT c.name, SUM(oi.quantity) AS total_sold
   FROM order_items oi
   INNER JOIN books b ON oi.book_id = b.id
   INNER JOIN book_categories bc ON b.id = bc.book_id
   INNER JOIN categories c ON bc.category_id = c.id
   GROUP BY c.name
   ORDER BY total_sold DESC
   LIMIT 5;
   ```

6. **Get Customers with No Orders in the Last Year**

   ```sql
   SELECT c.id, c.name
   FROM customers c
   WHERE c.id NOT IN (
       SELECT DISTINCT customer_id
       FROM orders
       WHERE order_date >= DATE('now', '-1 year')
   );
   ```

### Complex Queries

7. **Calculate Customer Lifetime Value (CLV) for Each Customer**

   ```sql
   SELECT c.id, c.name, SUM(oi.quantity * oi.unit_price) AS total_spent, c.clv
   FROM customers c
   LEFT JOIN orders o ON c.id = o.customer_id
   LEFT JOIN order_items oi ON o.id = oi.order_id
   GROUP BY c.id
   ORDER BY total_spent DESC;
   ```

8. **Identify Potential Fraudulent Orders**

   ```sql
   SELECT o.id, o.order_date, o.status, o.total_value, o.notes
   FROM (
       SELECT o.id, o.order_date, o.status,
              SUM(oi.quantity * oi.unit_price) AS total_value, o.notes
       FROM orders o
       INNER JOIN order_items oi ON o.id = oi.order_id
       GROUP BY o.id
   ) o
   WHERE o.status = 'Pending Review' OR o.notes LIKE '%Flagged for review%';
   ```

9. **Find Books That Need Reordering**

   ```sql
   SELECT b.id, b.title, b.stock_level, b.reorder_point
   FROM books b
   WHERE b.stock_level <= b.reorder_point
     AND b.format != 'E-book';
   ```

10. **Get Average Satisfaction Score by Interaction Type**

    ```sql
    SELECT interaction_type, AVG(satisfaction_score) AS average_satisfaction
    FROM customer_service_interactions
    WHERE satisfaction_score IS NOT NULL
    GROUP BY interaction_type
    ORDER BY average_satisfaction DESC;
    ```

11. **List Suppliers with the Highest Book Sales Revenue**

    ```sql
    SELECT s.id, s.name, SUM(oi.quantity * oi.unit_price) AS total_revenue
    FROM suppliers s
    INNER JOIN books b ON s.id = b.supplier_id
    INNER JOIN order_items oi ON b.id = oi.book_id
    GROUP BY s.id
    ORDER BY total_revenue DESC;
    ```

12. **Find Employees Who Manage More Than 5 Direct Reports**

    ```sql
    SELECT e.id, e.first_name, e.last_name, COUNT(dr.id) AS direct_reports
    FROM employees e
    LEFT JOIN employees dr ON dr.manager_id = e.id
    GROUP BY e.id
    HAVING COUNT(dr.id) > 5;
    ```

13. **Determine the Effectiveness of Promotions on Sales**

    ```sql
    SELECT strftime('%Y-%m', o.order_date) AS month, COUNT(o.id) AS orders_count,
           SUM(oi.quantity * oi.unit_price) AS total_sales
    FROM orders o
    INNER JOIN order_items oi ON o.id = oi.order_id
    WHERE o.notes LIKE '%promotion%'
    GROUP BY month
    ORDER BY month;
    ```

14. **Calculate the Reorder Frequency for Books**

    ```sql
    SELECT b.id, b.title,
           COUNT(*) AS reorder_count,
           AVG(DATEDIFF(day, ph.effective_date, ph.end_date)) AS average_duration
    FROM books b
    INNER JOIN book_price_history ph ON b.id = ph.book_id
    WHERE ph.change_reason = 'Reorder'
    GROUP BY b.id
    ORDER BY reorder_count DESC;
    ```

15. **Get the Most Common Reasons for Customer Returns**

    ```sql
    SELECT SUBSTR(cci.notes, INSTR(cci.notes, 'Reason: ') + 8) AS return_reason,
           COUNT(*) AS occurrences
    FROM customer_service_interactions cci
    WHERE cci.interaction_type = 'Return Request'
    GROUP BY return_reason
    ORDER BY occurrences DESC;
    ```

## Conclusion

By meticulously designing and populating this custom database, we've created a rich and complex dataset that mirrors the intricacies of real-world business operations. This database serves as an effective platform for testing AI text-to-SQL models, challenging them to interpret natural language queries and generate accurate SQL commands across a variety of scenarios.

This approach not only provides a robust testing ground but also ensures that we avoid any legal issues associated with using proprietary databases like Northwind. Developers can leverage this dataset to enhance AI models, improve query interpretation, and ultimately, build more intelligent database interaction systems.
