# Error Reference Guide

## Common Errors and Solutions

### 🔴 Constraint Errors

#### Error: "Sum X is too low for Y voltorbs"

**What it means:** The sum you entered is mathematically impossible with that many voltorbs.

**Example:**
```
Row 0: sum=2, voltorbs=4
```

**Problem:** With 4 voltorbs, you have 1 remaining tile. That tile must be at least 1, so minimum sum = 1.

**Solution:** Increase the sum or decrease voltorbs.

**Valid ranges:**
- 0 voltorbs: sum can be 5-15
- 1 voltorb: sum can be 4-12
- 2 voltorbs: sum can be 3-9
- 3 voltorbs: sum can be 2-6
- 4 voltorbs: sum can be 1-3
- 5 voltorbs: sum must be 0

---

#### Error: "Sum X is too high for Y voltorbs"

**What it means:** Even with maximum values (all 3s), you can't reach this sum.

**Example:**
```
Row 0: sum=13, voltorbs=3
```

**Problem:** With 3 voltorbs, you have 2 remaining tiles. Maximum: 2×3 = 6, not 13.

**Solution:** Decrease the sum or decrease voltorbs.

---

#### Error: "Sum of all row sums (X) must equal sum of all column sums (Y)"

**What it means:** The board is inconsistent - rows and columns describe different totals.

**Example:**
```
Rows total: 25
Cols total: 30
```

**Problem:** Both represent the same 5×5 grid, so they must be equal.

**Solution:** Adjust constraints until both totals match:
```
Row totals: 5 + 6 + 7 + 6 + 6 = 30 ✓
Col totals: 6 + 6 + 6 + 6 + 6 = 30 ✓
```

---

#### Error: "Total voltorbs counted by rows (X) must equal total voltorbs counted by columns (Y)"

**What it means:** Rows and columns count different numbers of voltorbs.

**Example:**
```
Row voltorbs: 1 + 0 + 2 + 0 + 2 = 5
Col voltorbs: 1 + 1 + 1 + 1 + 1 = 5 ✓ (correct)

Row voltorbs: 1 + 0 + 2 + 0 + 0 = 3
Col voltorbs: 1 + 1 + 1 + 1 + 1 = 5 ✗ (wrong)
```

**Solution:** Recount voltorbs - they're the same grid!

---

### 🟡 Sampling Errors

#### Error: "Could not find any valid board configurations after 10000 attempts"

**What it means:** The constraints look valid individually but can't be satisfied together.

**Example:**
```
Row 0: sum=10, voltorbs=0  (needs high values)
Row 1: sum=5,  voltorbs=0  (needs low values)
...
Col 0: sum=3,  voltorbs=0  (conflicts with row 0)
```

**Problem:** Row 0, Col 0 intersects. It needs to be high (for row) AND low (for col). Impossible!

**Solution:** 
1. Double-check that constraints are from an actual game
2. Verify no typos in constraint values
3. Try a simpler test board first

---

#### Error: "The given row/column constraints are inconsistent"

**What it means:** After trying many combinations, no valid board exists.

**Common causes:**
1. Typo in constraints
2. Copied constraints from different game states
3. Impossible combination (rare but possible)

**Solution:**
1. Re-enter constraints carefully
2. Use the validation errors to find the issue
3. Start with a known-good board to test

---

### 🟢 Valid Test Boards

Use these to verify your setup:

#### Simple Board (Easy)
```
Rows: (sum, voltorbs)
  0: 5, 0
  1: 5, 0
  2: 5, 0
  3: 5, 0
  4: 5, 0

Cols: (sum, voltorbs)
  0: 5, 0
  1: 5, 0
  2: 5, 0
  3: 5, 0
  4: 5, 0

Notes: All tiles are 1s. Very safe!
```

#### Medium Board
```
Rows: (sum, voltorbs)
  0: 6, 1
  1: 7, 0
  2: 5, 2
  3: 8, 0
  4: 4, 2

Cols: (sum, voltorbs)
  0: 6, 1
  1: 5, 1
  2: 7, 1
  3: 6, 1
  4: 6, 1

Notes: Mixed difficulty, good for testing.
```

#### Hard Board (Dangerous)
```
Rows: (sum, voltorbs)
  0: 3, 4
  1: 3, 4
  2: 3, 4
  3: 3, 4
  4: 3, 4

Cols: (sum, voltorbs)
  0: 3, 4
  1: 3, 4
  2: 3, 4
  3: 3, 4
  4: 3, 4

Notes: 20 voltorbs, 5 tiles with value. High risk!
```

---

### 🔵 API Errors

#### Error: "Failed to connect to solver API"

**What it means:** Frontend can't reach backend.

**Solutions:**
1. Check backend is running: `http://127.0.0.1:8000/health`
2. Check correct ports:
   - Backend: 8000
   - Frontend: 5173
3. Check CORS configuration in `main.py`

---

#### Error: "Internal solver error"

**What it means:** Unexpected error in backend processing.

**Solutions:**
1. Check backend terminal for detailed error
2. Check that all Python dependencies are installed
3. Try a simpler test board
4. Report with error details if persists

---

### 📊 Validation Cheat Sheet

**Per-Row/Column Constraints:**
```python
voltorbs: 0-5
sum: (5 - voltorbs) to (5 - voltorbs) × 3

Examples:
- 0V: sum 5-15
- 1V: sum 4-12
- 2V: sum 3-9
- 3V: sum 2-6
- 4V: sum 1-3
- 5V: sum 0
```

**Global Constraints:**
```python
sum(row_sums) == sum(col_sums)
sum(row_voltorbs) == sum(col_voltorbs)

Both must be between 0 and 75 (25 tiles × 3 max)
Voltorbs must be between 0 and 25 (all tiles)
```

---

### 🛠️ Quick Fixes

**If nothing works:**

1. **Reset everything:**
```bash
# Backend
cd backend
rm -rf __pycache__ .pytest_cache
pip install -r requirements.txt --force-reinstall

# Frontend  
cd frontend/voltorb-ui
rm -rf node_modules
npm install
```

2. **Use validated test board above**

3. **Check both servers are running:**
```bash
# Terminal 1
cd backend
uvicorn api.main:app --reload

# Terminal 2
cd frontend/voltorb-ui
npm run dev
```

4. **Clear browser cache:** Ctrl+Shift+R (hard refresh)

---

### 📞 Still Stuck?

The new error messages should tell you exactly what's wrong!

Look for:
- ⚠️ symbols
- "Row X" or "Column X" references
- "Min: X" or "Max: X" hints
- "Total" mentions (global issues)

Every error message now includes:
- What's wrong
- Why it's wrong
- What values are valid