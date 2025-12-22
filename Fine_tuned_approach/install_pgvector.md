# Installing pgvector Extension for PostgreSQL 16

## Problem

LightRAG requires the `pgvector` extension for PostgreSQL, but it's not installed.

Error: `extension "vector" is not available`

## Solution: Install pgvector

### Method 1: Download Pre-built Binary (Recommended for Windows)

1. **Download pgvector for PostgreSQL 16**:

   - Go to: https://github.com/pgvector/pgvector/releases
   - Download the latest Windows release (e.g., `pgvector-v0.7.4-windows-x64-pg16.zip`)

2. **Extract and Install**:

   ```powershell
   # Extract the zip file
   # Copy the files to PostgreSQL directories:
   # - vector.dll → C:\Program Files\PostgreSQL\16\lib\
   # - vector.control and vector--*.sql → C:\Program Files\PostgreSQL\16\share\extension\
   ```

3. **Restart PostgreSQL**:

   ```powershell
   Restart-Service postgresql-x64-16
   ```

4. **Enable the extension**:

   ```powershell
   cd "C:\Program Files\PostgreSQL\16\bin"
   .\psql -U postgres
   ```

   In PostgreSQL:

   ```sql
   CREATE EXTENSION vector;
   \q
   ```

### Method 2: Install via Stack Builder (Easier)

1. **Open Stack Builder** (installed with PostgreSQL)

   - Location: Start Menu → PostgreSQL 16 → Application Stack Builder

2. **Select pgvector** from available extensions

3. **Install and restart** PostgreSQL

### Method 3: Build from Source (Advanced)

If you have Visual Studio installed:

```powershell
git clone https://github.com/pgvector/pgvector.git
cd pgvector
# Follow build instructions for Windows
```

## After Installation

Test that pgvector is installed:

```powershell
cd "C:\Program Files\PostgreSQL\16\bin"
.\psql -U postgres -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

Then retry ingestion:

```powershell
cd "d:\KT Informatik\ATS project\Fine_tuned_approach"
python batch_ingest.py --dir ./resumes --batch 10
```

## Quick Test Command

```powershell
cd "C:\Program Files\PostgreSQL\16\bin"
.\psql -U postgres -c "SELECT * FROM pg_available_extensions WHERE name = 'vector';"
```

If it shows the extension, you're good to go!
