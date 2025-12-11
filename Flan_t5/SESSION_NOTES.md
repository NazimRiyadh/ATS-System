# Session Notes - Database & LLM Configuration (Dec 11, 2024)

## What We Tried

- **Database Connectivity**: Attempted to connect to local PostgreSQL on port 5432
- **Password Authentication**: Tested multiple passwords for local PostgreSQL
- **Manual pgvector Installation**: Considered installing pgvector extension on Windows PostgreSQL

## What We Accomplished

### 1. Database Configuration ✅

- **Switched to Dockerized PostgreSQL**: Migrated from local Windows PostgreSQL to Docker container `ats-db`
- **Port Alignment**: Reconfigured Docker container to use standard port 5432 (was 5433)
- **Verified pgvector**: Confirmed `pgvector` extension (v0.8.1) is installed and enabled
- **Connection String**: `postgresql+asyncpg://postgres:password@127.0.0.1:5432/postgres`

### 2. LLM Model Upgrade ✅

- **Identified Issue**: `flan-t5-small` has only 512 token context limit
- **Solution**: Upgraded to `flan-t5-large` for better context handling
- **Configuration**: Added `LLM_MODEL=google/flan-t5-large` to `.env`

### 3. Chat Response Fix ✅

**Problem**: `/chat_job` endpoint was returning empty responses ("---")

**Root Cause**: Context overflow - injecting 20 full resumes exceeded model capacity

**Fixes Applied**:

- Limited chat context to Top 5 candidates (from 20)
- Reduced character limit per candidate from 2000 to 1000 chars
- **Critical**: Moved Question to START of prompt (prevents truncation cutting off the query)
- File Modified: `src/job_manager.py`

### 4. Infrastructure Documentation ✅

Created comprehensive guides:

- `database_guide.md` - PostgreSQL + Neo4j architecture
- `deployment_guide.md` - Docker deployment strategy
- `usage_guide.md` - Best practices for queries
- `walkthrough.md` - Database debugging walkthrough

## What Needs to Be Done

### Immediate

- [ ] Test `/chat_job` endpoint with real queries after server restart
- [ ] Monitor memory usage (saw page file warnings during testing)
- [ ] Start Neo4j service for graph database functionality

### Future Enhancements

- [ ] Consider using `flan-t5-xl` if you have 16GB+ RAM for even better accuracy
- [ ] Implement caching for LLM responses to reduce latency
- [ ] Add pagination for large candidate pools (>20)
- [ ] Set up docker-compose.yml for easier deployment
- [ ] Add database backup/restore scripts

## Files Modified (This Session)

- `src/job_manager.py` - Fixed context overflow and prompt ordering
- `.env` - Added LLM_MODEL configuration (not committed - gitignored)

## Technical Decisions

1. **Docker over Local**: Chose Docker for pgvector to avoid complex Windows installation
2. **Port 5432**: Standardized on PostgreSQL default port for simplicity
3. **Question First**: Placing question at prompt start ensures it's never truncated
4. **Top 5 Limit**: Balance between context richness and token budget
