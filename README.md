# Troops Tech – Visual Chat Assistant Prototype

## 💡 Project Overview
This assistant:
- Processes video input
- Recognizes events
- Summarizes content
- Supports multi-turn conversations

✅ Basic prototype 

---

## 🚀 Setup Instructions

### 1. Clone the repo
```bash
git clone https://github.com/charan26006/troops_tech.git
cd troops_tech
```

### 2. Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate   # On Windows
# or
source venv/bin/activate   # On macOS/Linux
```

### 3. Install the dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
python app.py
```

---

## ⚙️ Technologies Used
- Python
- FastAPI
- Git LFS (for large binary files like video/frame data)

---

## 🔐 Environment Variables

Create a `.env` file in the root folder with the following:

```ini
OPENAI_API_KEY=your_api_key
VIDEO_PROCESSOR_KEY=your_processor_key
```

⚠️ This file is not pushed to GitHub — it's safely ignored by `.gitignore`.

✅ Use `.env.example` as a reference for teammates or collaborators.

---

## 📁 Project Structure

```
troops_tech/
├── app.py
├── requirements.txt
├── structure.txt
├── .gitignore
├── .gitattributes
├── .env          # Not pushed to GitHub
├── .env.example  # Template to share
├── README.md
├── [subfolders]/ # Your modules, logic, assets, etc.
```

---

##  Credits

Made by **Team Tech Troops**  
For  Hackathon – August 2025 🔥

