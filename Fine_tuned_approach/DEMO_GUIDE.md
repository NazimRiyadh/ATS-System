# 🚀 ATS System Demo Guide (Localized)

I have generated **50+ Resumes** with **unique Bangladeshi names** (e.g., Rahim Uddin, Tasnim Rahman) and ingested them into the system.

## � API Documentation

Full API details are available in: **[API_DOCUMENTATION.md](file:///d:/KT%20Informatik/ATS%20project/Fine_tuned_approach/API_DOCUMENTATION.md)**

## � Sample Scenarios

### Scenario 1: Find a Backend Developer

**Query:** `"Senior Python Developer with Django and AWS experience"`

**Powershell Command:**

```powershell
$body = @{
    query = "Senior Python Developer with Django and AWS"
    job_id = "bd_job_001"
    top_k = 5
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/analyze_job" -Method Post -Body $body -ContentType "application/json"
```

### Scenario 2: Reasoning about Candidates

**Question:** `"Who matches the best? Compare Rahim and Karim."`

**Powershell Command:**

```powershell
$body = @{
    job_id = "bd_job_001"
    message = "Who matches the best? Compare Rahim and Karim."
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/chat_job" -Method Post -Body $body -ContentType "application/json"
```

## 📂 Data Location

- **Resumes**: `d:\KT Informatik\ATS project\Fine_tuned_approach\resumes`
- **Graph Storage**: `d:\KT Informatik\ATS project\Fine_tuned_approach\rag_storage`
