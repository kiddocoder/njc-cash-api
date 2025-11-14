# NJC Cash Zone API Documentation

## Base URL
\`\`\`
http://localhost:8000/api/
\`\`\`

## Authentication
Currently, the API does not require authentication. In production, add JWT or session-based authentication.

---

## Endpoints Overview

### Dashboard
- `GET /api/dashboard/stats/` - Get overall dashboard statistics
- `GET /api/dashboard/loan_disbursement/` - Get loan disbursement data by month
- `GET /api/dashboard/loan_status_breakdown/` - Get loan status breakdown (pie chart data)
- `GET /api/dashboard/repayments_performance/` - Get repayments performance by month
- `GET /api/dashboard/approval_rate/` - Get today's approval rate by hour
- `GET /api/dashboard/recent_notifications/` - Get recent notifications

### Customers
- `GET /api/customers/` - List all customers (paginated)
- `POST /api/customers/` - Create a new customer
- `GET /api/customers/{id}/` - Get customer details
- `PUT /api/customers/{id}/` - Update customer
- `PATCH /api/customers/{id}/` - Partial update customer
- `DELETE /api/customers/{id}/` - Delete customer
- `GET /api/customers/stats/` - Get customer statistics
- `GET /api/customers/{id}/loans/` - Get all loans for a customer
- `GET /api/customers/{id}/recent_transactions/` - Get recent transactions for a customer

### Loans
- `GET /api/loans/` - List all loans (paginated)
- `POST /api/loans/` - Create a new loan
- `GET /api/loans/{id}/` - Get loan details
- `PUT /api/loans/{id}/` - Update loan
- `DELETE /api/loans/{id}/` - Delete loan
- `GET /api/loans/today_loans/` - Get today's loans
- `POST /api/loans/{id}/approve/` - Approve a loan
- `POST /api/loans/{id}/reject/` - Reject a loan
- `POST /api/loans/{id}/disburse/` - Disburse an approved loan

**Query Parameters for Filtering:**
- `status` - Filter by loan status (PENDING, APPROVED, REJECTED, DISBURSED, CLOSED)
- `loan_type` - Filter by loan type (PERSONAL, MORTGAGE, AUTO, STUDENT, BUSINESS)
- `start_date` - Filter by start date (YYYY-MM-DD)
- `end_date` - Filter by end date (YYYY-MM-DD)
- `min_amount` - Filter by minimum amount
- `max_amount` - Filter by maximum amount
- `search` - Search by customer name or loan ID

### Accounts
- `GET /api/accounts/` - List all accounts (paginated)
- `POST /api/accounts/` - Create a new account
- `GET /api/accounts/{id}/` - Get account details
- `PUT /api/accounts/{id}/` - Update account
- `DELETE /api/accounts/{id}/` - Delete account
- `POST /api/accounts/{id}/verify_kyc/` - Verify KYC for account
- `POST /api/accounts/{id}/reject_kyc/` - Reject KYC for account
- `POST /api/accounts/{id}/suspend/` - Suspend account
- `POST /api/accounts/{id}/activate/` - Activate account

### Transactions
- `GET /api/transactions/` - List all transactions (paginated)
- `POST /api/transactions/` - Create a new transaction
- `GET /api/transactions/{id}/` - Get transaction details
- `GET /api/transactions/recent/` - Get recent transactions (last 20)
- `GET /api/transactions/by_customer/?customer_id={id}` - Get transactions by customer

**Query Parameters:**
- `transaction_type` - Filter by type (LOAN_REQUEST, LOAN_APPROVED, LOAN_DISBURSED, REPAYMENT, REFUND, PENALTY)
- `customer_id` - Filter by customer
- `loan_id` - Filter by loan
- `start_date` - Filter by start date
- `end_date` - Filter by end date

### Repayments
- `GET /api/repayments/` - List all repayments (paginated)
- `POST /api/repayments/` - Create a new repayment
- `GET /api/repayments/{id}/` - Get repayment details
- `PUT /api/repayments/{id}/` - Update repayment
- `GET /api/repayments/upcoming/` - Get upcoming repayments (next 30 days)
- `GET /api/repayments/overdue/` - Get overdue repayments
- `POST /api/repayments/{id}/mark_paid/` - Mark repayment as paid
- `GET /api/repayments/stats/` - Get repayment statistics

### Appointments
- `GET /api/appointments/` - List all appointments (paginated)
- `POST /api/appointments/` - Create a new appointment
- `GET /api/appointments/{id}/` - Get appointment details
- `PUT /api/appointments/{id}/` - Update appointment
- `DELETE /api/appointments/{id}/` - Delete appointment
- `GET /api/appointments/upcoming/` - Get upcoming appointments
- `GET /api/appointments/today/` - Get today's appointments
- `POST /api/appointments/{id}/complete/` - Mark appointment as completed
- `POST /api/appointments/{id}/cancel/` - Cancel appointment

---

## Response Format

### Success Response
\`\`\`json
{
  "id": 1,
  "field1": "value1",
  "field2": "value2"
}
\`\`\`

### Paginated Response
\`\`\`json
{
  "count": 100,
  "next": "http://localhost:8000/api/customers/?page=2",
  "previous": null,
  "results": [
    {...},
    {...}
  ]
}
\`\`\`

### Error Response
\`\`\`json
{
  "error": "Error message here"
}
\`\`\`

---

## Example Requests

### Get Dashboard Stats
\`\`\`bash
curl http://localhost:8000/api/dashboard/stats/
\`\`\`

### Create a Customer
\`\`\`bash
curl -X POST http://localhost:8000/api/customers/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone": "+27 71 423 9581",
    "address": "123 Main St, Johannesburg",
    "city": "Johannesburg",
    "state": "Gauteng",
    "country": "South Africa",
    "postal_code": "2000"
  }'
\`\`\`

### Approve a Loan
\`\`\`bash
curl -X POST http://localhost:8000/api/loans/1/approve/
\`\`\`

### Filter Loans by Status
\`\`\`bash
curl http://localhost:8000/api/loans/?status=PENDING
\`\`\`

---

## Database Migration Commands

After adding new models, run:

\`\`\`bash
cd backend
python manage.py makemigrations
python manage.py migrate
\`\`\`

To create a superuser for admin access:

\`\`\`bash
python manage.py createsuperuser
\`\`\`

---

## Next Steps

1. Add authentication (JWT or Django sessions)
2. Add permission classes for role-based access
3. Implement file upload handling for customer documents
4. Add WebSocket support for real-time notifications
5. Add data validation and business logic
6. Set up automated tests
7. Configure CORS for frontend integration
