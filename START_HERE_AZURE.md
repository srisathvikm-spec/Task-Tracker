# 🚀 BEGIN HERE: Your Azure Deployment Journey

Welcome! This file will guide you through deploying your Task Tracker application to Azure Cloud.

---

## ⏱️ Time Commitment
- **Automatic Deployment**: 20-30 minutes (using script)
- **Manual Deployment**: 1-2 hours (step-by-step)
- **Your choice**: Use automation or follow detailed guide

---

## 📍 You Are Here: Step 0 - Prerequisites

### ✅ Checklist Before Starting

- [ ] **Azure Account**: Create free account at https://azure.microsoft.com/free
  - Includes 12 months free + $200 credit
  - Free PostgreSQL for first 12 months

- [ ] **Azure CLI**: Install from https://aka.ms/cli
  ```powershell
  # Verify installation
  az --version
  # Should show: azure-cli 2.xx.x
  ```

- [ ] **Git**: Should already be installed
  ```powershell
  git --version
  ```

- [ ] **PowerShell 5.1+**: 
  ```powershell
  $PSVersionTable.PSVersion
  # Should show Version 5.1 or higher
  ```

- [ ] **Node.js 16+**: (for frontend build)
  ```powershell
  node --version
  npm --version
  ```

---

## 🎯 Choose Your Deployment Path

### Path A: ⚡ FAST (Recommended for First Deployment)
**Use automated script for 30-minute deployment**

👉 Go to: `AZURE_QUICK_START.md`

Steps:
1. Login to Azure
2. Run `deploy-to-azure.ps1`
3. Update Azure AD
4. Deploy frontend
5. Test

### Path B: 📚 DETAILED (Recommended for Learning)
**Follow step-by-step guide with explanations**

👉 Go to: `AZURE_DEPLOYMENT_GUIDE.md`

Phases:
1. Prerequisites setup
2. Database creation
3. Backend deployment
4. Frontend deployment
5. Configuration
6. Testing
7. Scaling

### Path C: 🛠️ CUSTOM (Advanced Users)
**Manual CLI commands for custom setup**

👉 Go to: `AZURE_COMMANDS_REFERENCE.md`

Use individual commands to:
- Create resources separately
- Skip automated steps
- Customize configuration

---

## 🚀 START: Path A (Recommended - 30 Minutes)

### Step 1: Login to Azure (2 minutes)
```powershell
# Open PowerShell and run
az login

# A browser window will open
# Sign in with your Azure account
# Return to PowerShell when done
```

### Step 2: Run Deployment Script (15-20 minutes)
```powershell
# Navigate to your project
cd c:\Users\srisa\Downloads\t_tracker

# Run the automated deployment script
.\deploy-to-azure.ps1

# The script will:
# ✓ Create resource group
# ✓ Create PostgreSQL database
# ✓ Create App Service for backend
# ✓ Deploy backend code
# ✓ Create Static Web App for frontend
# ✓ Configure everything automatically
```

### Step 3: Update Azure AD (5 minutes) - Manual Step
The script will **pause and ask you to**:

1. Go to **Azure Portal** at https://portal.azure.com
2. Navigate to: **Azure Active Directory** → **App registrations**
3. Find app with ID: `0842ec45-61b4-405c-8a1f-f5c8d1b2329a`
4. Click: **Authentication** in left menu
5. Click: **Add a platform** → **Web**
6. Paste this URI: `https://<YOUR_FRONTEND_URL>.azurestaticapps.net/`
   - (Script output will show your exact URL)
7. Click **Save**
8. Return to PowerShell and press ENTER

### Step 4: Deploy Frontend (5-10 minutes)
```powershell
# Build frontend
cd frontend
npm install
npm run build

# Deploy to Azure
# Replace <app-name> with name from script output
az staticwebapp upload `
  --name <app-name> `
  --source "./dist" `
  --resource-group task-tracker-rg
```

### Step 5: Test & Celebrate! (2 minutes)
```powershell
# Open your app (URL from script output)
Start-Process "https://<your-frontend-url>.azurestaticapps.net"

# Login with Azure AD credentials
# You should see your dashboard! 🎉
```

---

## 📊 What Gets Created

After deployment, you'll have:

```
Azure Resources Created:
├── Resource Group: task-tracker-rg
├── Database
│   └── PostgreSQL Server (Single Server B1)
│       └── Database: task_tracker
├── Backend
│   └── App Service (B1 Linux)
│       ├── Python 3.11
│       ├── FastAPI + Uvicorn
│       └── 4 Workers
└── Frontend
    └── Static Web App (Free tier)
        ├── React + Vite
        └── Built from dist/
```

---

## 💡 Important Notes

### ⚠️ Password Security
The script generates passwords. **Save them safely**:
- 📝 Database password: `<saved in script output>`
- Database connection string: `postgresql://...`

### ⚠️ Cost Warning
Resources will start incurring costs immediately:
- PostgreSQL B1: ~$30/month
- App Service B1: ~$13/month
- Static Web App: Free
- **Total: ~$43/month**

To save money initially:
- Delete resources after testing: `az group delete -g task-tracker-rg --yes`
- Or stop app: `az webapp stop -g task-tracker-rg -n task-tracker-api-xyz`

### ✅ Success Signs
After deployment, you should see:
- ✅ Backend health check: `https://<backend>.azurewebsites.net/health` → `{"status":"ok"}`
- ✅ Frontend loads: `https://<frontend>.azurestaticapps.net/`
- ✅ Azure AD login works
- ✅ Dashboard displays after login

---

## 🆘 If Something Goes Wrong

### ❌ Script fails
→ Check: Do you have Azure CLI installed? (`az --version`)

### ❌ Frontend won't build
→ Run: 
```powershell
cd frontend
rm -r node_modules package-lock.json
npm install --force
npm run build
```

### ❌ Login not working
→ Check: Did you add redirect URI to Azure AD?
→ View logs: `az webapp log tail -g task-tracker-rg -n task-tracker-api-xyz`

### ❌ Database connection error
→ Check: Is firewall rule allowing Azure services?
→ Run: `az postgres server firewall-rule list -g task-tracker-rg -n <dbserver>`

### 📞 Still stuck?
→ See: `AZURE_DEPLOYMENT_GUIDE.md` → Troubleshooting section
→ Or: `AZURE_COMMANDS_REFERENCE.md` → Debugging

---

## 📋 After Successful Deployment

### Your URLs
- **Frontend**: `https://<your-app-name>.azurestaticapps.net`
- **Backend API**: `https://task-tracker-api-xyz.azurewebsites.net`
- **API Docs**: `https://task-tracker-api-xyz.azurewebsites.net/docs`

### Next Recommended Steps
1. Test all CRUD operations (create/list/update/delete projects & tasks)
2. Verify role-based access control works
3. Create a few sample projects and tasks
4. Test logout/login cycle
5. Check backend logs for any errors

### Optional Future Enhancements
- Add custom domain name
- Configure CI/CD with GitHub Actions
- Enable monitoring and alerts
- Set up auto-scaling policies
- Create staging environment

---

## 📚 Documentation Structure

```
AZURE_README.md                    ← Project overview (you are here)
├── AZURE_QUICK_START.md          ← 5-step quick guide ⭐ RECOMMENDED
├── AZURE_DEPLOYMENT_GUIDE.md     ← Detailed phase-by-phase guide
├── AZURE_COMMANDS_REFERENCE.md   ← CLI commands for management
└── deploy-to-azure.ps1           ← Automated deployment script
```

---

## ✨ TL;DR (Too Long; Didn't Read)

1. Install Azure CLI: https://aka.ms/cli
2. Run: `az login` 
3. Run: `.\deploy-to-azure.ps1`
4. Update Azure AD redirect URI (script will tell you how)
5. Deploy frontend: `az staticwebapp upload ...`
6. Done! 🎉

---

**Ready?** 👉 Open `AZURE_QUICK_START.md` and begin!

---

*Questions? Check the troubleshooting section or review the detailed guide.*
