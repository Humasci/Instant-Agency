# Neon Database Setup Instructions

Since `npx neonctl@latest init` requires interactive cursor support, here's the manual setup:

## 🚀 Manual Neon Database Setup (5 minutes)

### Step 1: Sign Up
1. Go to [console.neon.tech](https://console.neon.tech)
2. Sign up with GitHub/Google (instant)
3. No credit card required

### Step 2: Create Project
1. Click "Create Project"
2. **Project Name**: `six3-agency`
3. **Database Name**: `six3_agency`
4. **Region**: Choose closest to your users (e.g., US East, EU West)
5. Click "Create Project"

### Step 3: Get Connection String
After project creation, you'll see a connection string like:
```
postgresql://username:password@ep-example-123456.us-east-1.aws.neon.tech/six3_agency?sslmode=require
```

### Step 4: Update Your .env File
Replace the database configuration in your `.env` file:

```bash
# OLD (in your current .env)
POSTGRES_DB=six3_agency
POSTGRES_USER=six3_agency
POSTGRES_PASSWORD=CHANGE_ME_TO_SECURE_PASSWORD

# NEW (add this line)
DATABASE_URL=postgresql://username:password@ep-example-123456.us-east-1.aws.neon.tech/six3_agency?sslmode=require
```

### Step 5: Test Connection
```bash
# Install PostgreSQL client if needed
sudo apt install postgresql-client -y

# Test connection (replace with your actual connection string)
psql "postgresql://username:password@ep-example-123456.us-east-1.aws.neon.tech/six3_agency?sslmode=require" -c "SELECT version();"
```

### Step 6: Apply Database Schema
```bash
# Apply your database schema
psql "$DATABASE_URL" -f database_schema.sql
```

## ✅ Alternative: Quick Railway Database

If you prefer even simpler setup:

1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Provision PostgreSQL"
3. Copy the `DATABASE_URL` from Variables tab
4. Add to your `.env` file

Railway provides instant PostgreSQL with no signup friction.

## 🔧 Example .env Update

Add this line to your existing `.env` file:
```bash
# Neon Database (replace with your actual connection string)
DATABASE_URL=postgresql://neondb_owner:your_password@ep-cool-mountain-123456.us-east-1.aws.neon.tech/six3_agency?sslmode=require

# Keep your existing settings
POSTGRES_DB=six3_agency
POSTGRES_USER=six3_agency
POSTGRES_PASSWORD=CHANGE_ME_TO_SECURE_PASSWORD
```

The `DATABASE_URL` will take precedence in your application code.