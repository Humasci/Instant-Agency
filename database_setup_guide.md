# PostgreSQL Database Setup Guide

## 🎯 Recommended: Neon (Always Free)

### Why Neon:
- ✅ **Always free** (not just trial)
- ✅ **Serverless** - auto-scales to zero
- ✅ **0.5GB storage** free forever
- ✅ **Built-in connection pooling**
- ✅ **Automatic backups**
- ✅ **No credit card required**

### Setup Steps (5 minutes):

1. **Sign up at [neon.tech](https://neon.tech)**
   - Use GitHub/Google login (instant setup)

2. **Create Database**
   - Click "Create Project"
   - Choose region closest to your users
   - Database name: `six3_agency`

3. **Get Connection String**
   ```
   postgresql://username:password@ep-example.us-east-1.aws.neon.tech/six3_agency?sslmode=require
   ```

4. **Update .env file**
   ```bash
   # Replace this line in your .env:
   DATABASE_URL=postgresql://username:password@ep-example.us-east-1.aws.neon.tech/six3_agency?sslmode=require
   ```

5. **Run Database Schema**
   ```bash
   # Install psql if needed
   sudo apt install postgresql-client

   # Apply schema
   psql $DATABASE_URL -f database_schema.sql
   ```

## 🏃‍♂️ Quick Alternative: Supabase

### Setup (3 minutes):
1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Copy connection string from Settings → Database
4. Update your .env file

## 💾 Local Development Option

### If you want local PostgreSQL:
```bash
# Install PostgreSQL
sudo apt update && sudo apt install postgresql postgresql-contrib

# Create user and database
sudo -u postgres createuser --interactive six3_agency
sudo -u postgres createdb six3_agency

# Set password
sudo -u postgres psql -c "ALTER USER six3_agency PASSWORD 'your_password';"

# Update .env for local
DATABASE_URL=postgresql://six3_agency:your_password@localhost/six3_agency
```

## 🔗 Connection String Format

```
postgresql://[user]:[password]@[host]:[port]/[database]?[options]

Example:
postgresql://six3user:mypassword@ep-cool-mountain-123456.us-east-1.aws.neon.tech/six3_agency?sslmode=require
```

## ✅ Test Connection

```bash
# Test with psql
psql "postgresql://username:password@host/database" -c "SELECT version();"

# Test with Python
python3 -c "
import psycopg2
conn = psycopg2.connect('your_connection_string_here')
print('✅ Database connection successful!')
conn.close()
"
```

## 📊 Recommended Choice

**For your SIX3 Agency setup: Use Neon**
- Zero cost
- Zero maintenance  
- Perfect for MVP and beyond
- Scales automatically
- Professional features included