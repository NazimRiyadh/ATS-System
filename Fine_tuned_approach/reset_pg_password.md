# Reset PostgreSQL Password on Windows

## Method 1: Using pgAdmin (Easiest)

1. Open **pgAdmin 4** (should be installed with PostgreSQL)
2. Connect to your local server (you'll need the current password, or it might auto-connect)
3. Right-click on **Login/Group Roles** → **postgres**
4. Go to **Definition** tab
5. Enter new password
6. Click **Save**

## Method 2: Command Line with Trust Authentication

### Step 1: Modify pg_hba.conf

1. **Find pg_hba.conf file** (typically at):

   ```
   C:\Program Files\PostgreSQL\16\data\pg_hba.conf
   ```

2. **Open as Administrator** in Notepad

3. **Find these lines** (near the bottom):

   ```
   # IPv4 local connections:
   host    all             all             127.0.0.1/32            scram-sha-256
   ```

4. **Change to**:

   ```
   # IPv4 local connections:
   host    all             all             127.0.0.1/32            trust
   ```

5. **Save the file**

### Step 2: Restart PostgreSQL

Open PowerShell as Administrator:

```powershell
Restart-Service postgresql-x64-16
```

### Step 3: Reset Password

```powershell
cd "C:\Program Files\PostgreSQL\16\bin"
.\psql -U postgres
```

In the PostgreSQL prompt:

```sql
ALTER USER postgres PASSWORD 'your_new_password_here';
\q
```

### Step 4: Revert pg_hba.conf

1. Change `trust` back to `scram-sha-256`
2. Save
3. Restart service again:
   ```powershell
   Restart-Service postgresql-x64-16
   ```

## Method 3: Try Common Default Passwords

Sometimes the password is one of these:

- `postgres`
- `admin`
- `root`
- (blank/empty)

Try these in psql:

```powershell
cd "C:\Program Files\PostgreSQL\16\bin"
.\psql -U postgres
# When prompted, try each password above
```

## After Resetting

Update your `.env` file:

```
POSTGRES_URI=postgresql+asyncpg://postgres:YOUR_NEW_PASSWORD@127.0.0.1:5432/postgres
```

Then test:

```powershell
python check_pg_tables.py
```
