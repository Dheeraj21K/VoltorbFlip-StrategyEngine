# Voltorb Flip Solver - Setup Guide

## 🚀 Quick Start

### Backend Setup (Python)

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
```

3. **Activate virtual environment:**

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
.\venv\Scripts\activate.bat
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

4. **Install dependencies:**
```bash
pip install -r requirements.txt
```

5. **Run tests (optional but recommended):**
```bash
pytest
```

6. **Start the backend server:**
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

The backend should now be running at `http://127.0.0.1:8000`

You can test it by visiting: `http://127.0.0.1:8000/health`

---

### Frontend Setup (React + TypeScript)

1. **Navigate to frontend directory:**
```bash
cd frontend/voltorb-ui
```

2. **Install dependencies:**
```bash
npm install
```

3. **Start the development server:**
```bash
npm run dev
```

The frontend should now be running at `http://localhost:5173`

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/
```

Run specific test files:
```bash
pytest tests/test_validation.py
pytest tests/test_constraints.py
pytest tests/test_policies.py
```

Run with verbose output:
```bash
pytest -v
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. "Module not found" errors (Backend)

**Problem:** Python can't find the `src` module.

**Solution:** Make sure you're in the `backend` directory and pytest.ini is configured correctly:
```bash
cd backend
pytest
```

#### 2. CORS errors (Frontend → Backend)

**Problem:** Browser blocks requests from frontend to backend.

**Solution:** The backend is already configured for CORS. Make sure both servers are running:
- Backend: `http://127.0.0.1:8000`
- Frontend: `http://localhost:5173`

#### 3. "Constraint error" when analyzing

**Problem:** Invalid board configuration.

**Solution:** The new validation will show exactly what's wrong:
- Check that row sums = column sums (total)
- Check that row voltorbs = column voltorbs (total)
- Each constraint must be mathematically possible

**Example valid board:**
```
Row 0: sum=6, voltorbs=1
Row 1: sum=7, voltorbs=0
Row 2: sum=5, voltorbs=2
Row 3: sum=8, voltorbs=0
Row 4: sum=4, voltorbs=2

Col 0: sum=6, voltorbs=1
Col 1: sum=5, voltorbs=1
Col 2: sum=7, voltorbs=1
Col 3: sum=6, voltorbs=1
Col 4: sum=6, voltorbs=1

Total row sums: 30 ✓
Total col sums: 30 ✓
Total row voltorbs: 5 ✓
Total col voltorbs: 5 ✓
```

#### 4. Port already in use

**Backend (port 8000):**
```bash
# Find process using port 8000
# Windows:
netstat -ano | findstr :8000

# Mac/Linux:
lsof -i :8000

# Kill the process or use a different port:
uvicorn api.main:app --reload --port 8001
```

**Frontend (port 5173):**
```bash
# Vite will automatically try the next available port
# Or specify a different port in vite.config.ts
```

---

## 📝 Development Workflow

### Making Changes

1. **Backend changes:**
   - Edit files in `backend/src/` or `backend/api/`
   - The server auto-reloads (if using `--reload`)
   - Run tests: `pytest`

2. **Frontend changes:**
   - Edit files in `frontend/voltorb-ui/src/`
   - The browser auto-reloads (Vite HMR)
   - Check console for errors

### Testing Changes

1. **Start with a valid board:**
   - All constraints sum/voltorb counts should be possible
   - Total row sums = total column sums
   - Total row voltorbs = total column voltorbs

2. **Test edge cases:**
   - Empty board (all zeros)
   - Maximum values (sum=15, all 3s)
   - Minimum values (sum=5, all 1s)
   - Mixed revealed tiles

3. **Test error handling:**
   - Impossible constraints (sum=20)
   - Mismatched totals
   - Invalid revealed tiles

---

## 🎯 Next Steps

### Quick Test

1. Start both backend and frontend
2. Enter this valid board:

**Rows:** (sum, voltorbs)
- 6, 1
- 7, 0  
- 5, 2
- 8, 0
- 4, 2

**Columns:** (sum, voltorbs)
- 6, 1
- 5, 1
- 7, 1
- 6, 1
- 6, 1

3. Click "ANALYZE BOARD"
4. You should see probability overlays and recommendations!

### Try Both Modes

- **🛡 Level Mode**: Conservative, survival-focused
- **💰 Profit Mode**: Aggressive, reward-focused

---

## 📚 Additional Resources

- **CSP Theory**: See `docs/csp_model.md`
- **Probability Engine**: See `docs/probability.md`
- **Policy Design**: See `docs/policies.md`
- **Architecture**: See `docs/design.md`

---

## 🆘 Still Having Issues?

If you encounter errors:

1. Check that both servers are running
2. Check browser console (F12) for errors
3. Check backend terminal for error messages
4. Verify Python version (3.8+)
5. Verify Node version (18+)

The new error handling should show clear, actionable error messages!