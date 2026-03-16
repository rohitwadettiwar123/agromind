# 🌾 AgroMind — AI Smart Farming Assistant

An intelligent farming chatbot powered by **llama-3.3-70b-versatile** + **Python rule engine**.

---

## ⚡ Quick Start (3 Steps)

### 1. Get a Free Groq API Key
1. Go to **https://console.groq.com**
2. Sign up (free) → Create API Key
3. Copy your key

### 2. Setup Backend
```bash
cd backend

# Create .env file
cp .env.example .env
# Edit .env → paste your GROQ_API_KEY

# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```
Server starts at → **http://localhost:5000**

### 3. Open Frontend
- Open `frontend/index.html` directly in your browser
- OR use Live Server in VS Code

---

## 💬 Example Conversations

| You Say | AgroMind Does |
|---------|---------------|
| "What crops should I grow in Kharif season?" | Lists Paddy, Maize, Cotton, Soybean + explains |
| "Calculate fertilizer for wheat on 2 hectares" | NPK dosage, Urea/DAP/MOP quantities, split schedule |
| "My paddy leaves have brown spots" | Identifies Brown Spot Disease + prevention |
| "How often should I irrigate potato?" | Every 5 days, Sprinkler/Drip, critical stages |
| "Best crops for black soil?" | Cotton, Soybean, Jowar, Sunflower + reasoning |

---

## 🛠 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat` | POST | Main chatbot (conversational) |
| `/crop-advice` | POST | Structured crop recommendations |
| `/fertilizer-calculator` | POST | NPK dosage calculator |
| `/weather-tips` | POST | Weather & irrigation advice |
| `/health` | GET | Server health check |

---

## 📁 Project Structure
```
FAI-AGENT/
├── Backend/                 # The "Brain": Server-side logic and API
│   ├── logic/               # Specific calculation modules (Crop, Weather, etc.)
│   │   ├── crop_logic.py
│   │   ├── fertilizer_logic.py
│   │   └── weather_logic.py
│   ├── app.py               # API entry point (Connects Frontend to Backend)
│   └── groq_agent.py        # AI Agent implementation using Groq LLM
├── Frontend/                # The "Face": User interface for the farmer
│   ├── index.html           # Structure of the dashboard
│   ├── style.css            # Visual styling and layout
│   └── script.js            # Frontend logic (Sends data to app.py)

---

## 🔐 Security Notes
- API key stays server-side only
- Frontend never sees the Groq key
- Input validation on all endpoints
