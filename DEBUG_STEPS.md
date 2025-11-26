# Debugging Chat Issues After Login

## Quick Checklist

### 1. **Ensure Backend is Running**
```powershell
# Check if server is running on port 8000
Invoke-RestMethod http://127.0.0.1:8000/api/health -ErrorAction SilentlyContinue
# Should return: @{status=ok}
```

### 2. **Verify MongoDB is Running**
```powershell
# Test MongoDB connection
python -c "from pymongo import MongoClient; client = MongoClient('mongodb://localhost:27017'); print('Connected:', client.server_info())"
```
If this fails:
- Install MongoDB Community from https://www.mongodb.com/try/download/community
- Or use MongoDB Atlas cloud: update MONGO_URI in `backend/.env` to your cloud connection string

### 3. **Verify .env is Complete**
```powershell
# Check backend/.env has these keys:
# - GROQ_API_KEY (you have this)
# - LLM_MODEL (you have this)
# - SECRET_KEY (you have this)
# - MONGO_URI (newly added)
# - LOG_LEVEL (optional, defaults to INFO)
```

### 4. **Check Browser Console for Errors**
1. Open browser → Right-click → Inspect → Console tab
2. Attempt signup/login/chat
3. Look for red error messages showing API response details
4. Screenshot and share error messages

### 5. **Test API Endpoints Manually**

#### Signup
```powershell
$body = @{
    name = "Test User"
    email = "test@example.com"
    password = "password123"
} | ConvertTo-Json

$response = Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/api/signup" `
    -Method POST `
    -Headers @{"Content-Type"="application/json"} `
    -Body $body

$response
```
Expected: `{user_id: "...", token: "..."}`

#### Login
```powershell
$body = @{
    email = "test@example.com"
    password = "password123"
} | ConvertTo-Json

$response = Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/api/login" `
    -Method POST `
    -Headers @{"Content-Type"="application/json"} `
    -Body $body

$token = $response.token
$token
```

#### Create Chat (use token from above)
```powershell
$headers = @{
    "Content-Type" = "application/json"
    "Authorization" = "Bearer $token"
}

$response = Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/api/new_chat" `
    -Method POST `
    -Headers $headers

$chatId = $response.chat_id
$chatId
```

#### Send Message (use token & chatId from above)
```powershell
$body = @{
    conversation_id = $chatId
    message = "What is diabetes?"
} | ConvertTo-Json

$headers = @{
    "Content-Type" = "application/json"
    "Authorization" = "Bearer $token"
}

$response = Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/api/chat" `
    -Method POST `
    -Headers $headers `
    -Body $body

$response
```
Expected: `{response: "Bot response here..."}`

## If You See These Errors

### "Connection refused" on health check
→ Backend is not running. Restart it:
```powershell
.\my_env\Scripts\Activate.ps1
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

### "401 Unauthorized" on chat endpoints
→ Token is missing or invalid. Try logging in again in the browser.

### "500 Internal Server Error"
→ Check backend logs in `logs/medibot.log` for the actual error.

### "MONGO_URI not set" or MongoDB connection error
→ Add/update MONGO_URI in `backend/.env`:
```dotenv
MONGO_URI=mongodb://localhost:27017
```
Then restart the backend.

### "ModuleNotFoundError" for embeddings/FAISS/langchain
→ Install missing packages:
```powershell
pip install -r backend/requirements.txt
```

## What Should Happen

1. User visits `http://localhost:8000/` → sees login page
2. Clicks "Signup" → sees signup form
3. Enters name, email, password → clicks "Create Account"
4. Backend: Creates user in MongoDB, generates JWT token
5. Frontend: Stores token in localStorage, redirects to `/chat`
6. Chat page: Loads previous chats from MongoDB
7. User clicks "+ New Chat" → new conversation created
8. User sends message → backend calls GROQ LLM with retrieved context
9. Response appears in chat

## Still Not Working?

1. Share the browser console errors (screenshot)
2. Share the backend logs from `logs/medibot.log`
3. Run the manual API tests above and share the results
