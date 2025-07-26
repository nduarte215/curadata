from fastapi import FastAPI

app = FastAPI()

@app.get("/test")
def test():
    return {"message": "working"}

@app.get("/test")
async def test_route():
    return {"message": "Test route works!", "status": "success"}

# ===== ADD THIS AFTER YOUR CURRENT LINE 22 =====

# Storage for journal entries and bloodwork
journal_entries = []
bloodwork_submissions = []

# ===== YOUR EXISTING ROUTES STAY THE SAME =====
# (Keep your existing @app.get("/") and @app.post("/upload/") routes)

# ===== ADD THIS NEW JOURNAL ROUTE =====
@app.get("/journal", response_class=HTMLResponse)
async def journal_page():
    """Health Journal Calendar Page"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Health Journal - CuraData</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            .container { max-width: 1000px; margin: 0 auto; padding: 20px; }
            .header { text-align: center; color: white; margin-bottom: 2rem; }
            .header h1 { font-size: 2.5rem; margin-bottom: 0.5rem; }
            .journal-section {
                background: rgba(255, 255, 255, 0.95);
                padding: 2rem;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            }
            .calendar-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 2rem;
            }
            .nav-btn {
                background: #667eea;
                color: white;
                border: none;
                padding: 0.5rem 1rem;
                border-radius: 50%;
                cursor: pointer;
                font-size: 1.2rem;
            }
            .calendar-grid {
                display: grid;
                grid-template-columns: repeat(7, 1fr);
                gap: 1px;
                background: #ddd;
                border-radius: 10px;
                overflow: hidden;
            }
            .calendar-day {
                background: white;
                padding: 1rem;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s ease;
                min-height: 80px;
                display: flex;
                flex-direction: column;
                justify-content: center;
            }
            .calendar-day:hover { background: #f0f8ff; }
            .calendar-day.today { background: #667eea; color: white; }
            .day-headers {
                display: grid;
                grid-template-columns: repeat(7, 1fr);
                gap: 1px;
                margin-bottom: 1rem;
                text-align: center;
                font-weight: bold;
            }
            .modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.5);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 1000;
            }
            .modal-content {
                background: white;
                padding: 2rem;
                border-radius: 15px;
                width: 90%;
                max-width: 500px;
                max-height: 80vh;
                overflow-y: auto;
            }
            .mood-selector {
                display: flex;
                gap: 1rem;
                margin: 1rem 0;
                flex-wrap: wrap;
            }
            .mood-btn {
                padding: 0.5rem 1rem;
                border: 2px solid #ddd;
                border-radius: 25px;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .mood-btn:hover, input[type="radio"]:checked + .mood-btn {
                border-color: #667eea;
                background: #e8f4fd;
            }
            input[type="radio"] { display: none; }
            .supplement-checkboxes, .symptom-checkboxes {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 0.5rem;
                margin: 1rem 0;
            }
            .hidden { display: none; }
            .btn-primary {
                background: #667eea;
                color: white;
                border: none;
                padding: 0.8rem 1.5rem;
                border-radius: 25px;
                cursor: pointer;
                font-weight: 600;
            }
            .btn-secondary {
                background: #ccc;
                color: #333;
                border: none;
                padding: 0.8rem 1.5rem;
                border-radius: 25px;
                cursor: pointer;
                font-weight: 600;
            }
            .form-actions { display: flex; gap: 1rem; justify-content: flex-end; margin-top: 2rem; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📅 Health Journal</h1>
                <p>Track your daily symptoms and supplement effects</p>
            </div>

            <div class="journal-section">
                <div class="calendar-header">
                    <button class="nav-btn" onclick="changeMonth(-1)">‹</button>
                    <h2 id="currentMonth"></h2>
                    <button class="nav-btn" onclick="changeMonth(1)">›</button>
                </div>

                <div class="day-headers">
                    <div>Sun</div><div>Mon</div><div>Tue</div><div>Wed</div><div>Thu</div><div>Fri</div><div>Sat</div>
                </div>
                
                <div class="calendar-grid" id="calendarGrid">
                    <!-- Calendar days will be generated here -->
                </div>

                <div style="text-align: center; margin-top: 2rem;">
                    <a href="/" style="color: #667eea; text-decoration: none;">← Back to Home</a>
                </div>
            </div>
        </div>

        <!-- Modal for adding entries -->
        <div id="entryModal" class="modal hidden">
            <div class="modal-content">
                <h3>📝 Log Entry for <span id="selectedDate"></span></h3>
                <form id="entryForm">
                    <div>
                        <label>How did you feel today?</label>
                        <div class="mood-selector">
                            <input type="radio" id="great" name="mood" value="great">
                            <label for="great" class="mood-btn">😄 Great</label>
                            
                            <input type="radio" id="good" name="mood" value="good">
                            <label for="good" class="mood-btn">😊 Good</label>
                            
                            <input type="radio" id="okay" name="mood" value="okay">
                            <label for="okay" class="mood-btn">😐 Okay</label>
                            
                            <input type="radio" id="poor" name="mood" value="poor">
                            <label for="poor" class="mood-btn">😔 Poor</label>
                        </div>
                    </div>

                    <div>
                        <label>Supplements taken yesterday:</label>
                        <div class="supplement-checkboxes">
                            <label><input type="checkbox" name="supplements" value="vitaminD"> Vitamin D</label>
                            <label><input type="checkbox" name="supplements" value="vitaminC"> Vitamin C</label>
                            <label><input type="checkbox" name="supplements" value="iron"> Iron</label>
                            <label><input type="checkbox" name="supplements" value="omega3"> Omega-3</label>
                        </div>
                    </div>

                    <div>
                        <label>Symptoms experienced:</label>
                        <div class="symptom-checkboxes">
                            <label><input type="checkbox" name="symptoms" value="fatigue"> Fatigue</label>
                            <label><input type="checkbox" name="symptoms" value="headache"> Headache</label>
                            <label><input type="checkbox" name="symptoms" value="nausea"> Nausea</label>
                            <label><input type="checkbox" name="symptoms" value="joint-pain"> Joint Pain</label>
                        </div>
                    </div>

                    <div>
                        <label for="notes">Notes:</label>
                        <textarea id="notes" name="notes" rows="3" style="width: 100%; padding: 0.5rem; border-radius: 8px; border: 1px solid #ddd;"></textarea>
                    </div>

                    <div class="form-actions">
                        <button type="button" class="btn-secondary" onclick="closeModal()">Cancel</button>
                        <button type="submit" class="btn-primary">Save Entry</button>
                    </div>
                </form>
            </div>
        </div>

        <script>
            let currentDate = new Date();
            let selectedDate = null;

            function generateCalendar() {
                const grid = document.getElementById('calendarGrid');
                const monthHeader = document.getElementById('currentMonth');
                
                const year = currentDate.getFullYear();
                const month = currentDate.getMonth();
                
                monthHeader.textContent = new Date(year, month).toLocaleDateString('en-US', { 
                    month: 'long', 
                    year: 'numeric' 
                });
                
                const firstDay = new Date(year, month, 1).getDay();
                const daysInMonth = new Date(year, month + 1, 0).getDate();
                
                grid.innerHTML = '';
                
                for (let i = 0; i < firstDay; i++) {
                    const emptyDay = document.createElement('div');
                    emptyDay.className = 'calendar-day';
                    grid.appendChild(emptyDay);
                }
                
                for (let day = 1; day <= daysInMonth; day++) {
                    const dayElement = document.createElement('div');
                    dayElement.className = 'calendar-day';
                    dayElement.textContent = day;
                    
                    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
                    
                    const today = new Date();
                    if (year === today.getFullYear() && month === today.getMonth() && day === today.getDate()) {
                        dayElement.classList.add('today');
                    }
                    
                    dayElement.onclick = () => openModal(dateStr);
                    grid.appendChild(dayElement);
                }
            }
            
            function changeMonth(direction) {
                currentDate.setMonth(currentDate.getMonth() + direction);
                generateCalendar();
            }
            
            function openModal(date) {
                selectedDate = date;
                document.getElementById('selectedDate').textContent = new Date(date).toLocaleDateString();
                document.getElementById('entryModal').classList.remove('hidden');
            }
            
            function closeModal() {
                document.getElementById('entryModal').classList.add('hidden');
            }
            
            document.getElementById('entryForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = new FormData(e.target);
                const entry = {
                    date: selectedDate,
                    mood: formData.get('mood'),
                    supplements: formData.getAll('supplements'),
                    symptoms: formData.getAll('symptoms'),
                    notes: formData.get('notes')
                };
                
                try {
                    const response = await fetch('/api/journal/entry', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(entry)
                    });
                    
                    if (response.ok) {
                        alert('Entry saved successfully!');
                        closeModal();
                    }
                } catch (error) {
                    alert('Failed to save entry');
                }
            });
            
            generateCalendar();
        </script>
    </body>
    </html>
    """

# Add the API endpoint after the journal route
@app.post("/api/journal/entry")
async def save_journal_entry(entry: JournalEntry):
    try:
        entry_data = {
            **entry.dict(),
            "timestamp": datetime.now().isoformat(),
            "id": len(journal_entries) + 1
        }
        journal_entries.append(entry_data)
        return {"success": True, "message": "Journal entry saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
