# Internal Collaboration Guide (README.md)

> **দ্রষ্টব্য:** এটি আমাদের অভ্যন্তরীণ কাজের সুবিধার জন্য একটি সাময়িক ডকুমেন্টেশন। এটি চূড়ান্ত বা প্রোডাকশন README নয়।

This project, **Poshu_Sheba_AI**, is an attempt to use Google's latest Gemma models to build an AI assistant that provides primary veterinary support to common people before a doctor arrives or before they can reach a vet medical center.

---

## 🚀 How to Run the Project Locally

Follow these step-by-step instructions to set up and run both the backend and frontend services.

### 📋 Prerequisites
* **Python**: Version 3.8 to 3.13.x.
* **MongoDB**: A local instance or a remote connection string (MongoDB Atlas).
* **Ollama**: Installed locally on your machine (Download from [ollama.com](https://ollama.com)).

---

### Step 1: Clone the Repository
```bash
git clone https://github.com/mafimashrafi/Poshu_Sheba.git
cd Poshu_Sheba
```

### Step 2: Set Up Python Virtual Environment
1. **Create the virtual environment**:
   ```bash
   python -m venv venv
   ```
2. **Activate the environment**:
   * **Windows (PowerShell)**:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   * **Windows (Command Prompt)**:
     ```cmd
     venv\Scripts\activate.bat
     ```
   * **macOS / Linux**:
     ```bash
     source venv/bin/activate
     ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

### Step 3: Configure Environment Variables
Create a file named `.env` in the **root directory** of the repository (at the same level as this `README.md`) and add the following variables:

```env
# MongoDB config
MONGODB_URI=mongodb://localhost:27017/  # Or your MongoDB Atlas connection string
MONGODB_DB=poshu_sheba                  # Database name

# Ollama model configuration
OLLAMA_MODEL=gemma2                     # The model you want to use (e.g., gemma2, gemma:2b, llama3 etc.)
```
*(Note: If `OLLAMA_MODEL` is not specified, it defaults to the custom model `gemma4:e4b-it-q4_K_M`).*

---

### Step 4: Pull the Ollama Model
Ensure the Ollama application is running on your machine, then pull the model you specified in the `.env` file:
```bash
ollama pull gemma2
```

---

### Step 5: Start the Backend (FastAPI)
1. Navigate to the `Backend` directory:
   ```bash
   cd Backend
   ```
2. Start the Uvicorn server:
   ```bash
   uvicorn main:app --reload
   ```
* The API will be available at: `http://127.0.0.1:8000`
* You can view and test the API endpoints interactively at: `http://127.0.0.1:8000/docs`

---

### Step 6: Start the Frontend (Streamlit)
1. Open a **new terminal window** or tab.
2. Activate your virtual environment (refer to Step 2).
3. Navigate to the `Frontend` directory:
   ```bash
   cd Frontend
   ```
4. Start the Streamlit application:
   ```bash
   streamlit run app.py
   ```
* The web app will automatically open in your default browser at: `http://localhost:8501`

---

## 🛠️ Backend Architecture & Documentation
* The backend API routes, controller logic, and database schemas are defined in the `Backend` directory.
* For details on request/response body schemas and specific endpoints, read the [BACKEND_DOCUMENTATION.md](file:///e:/Poshu_Sheva/BACKEND_DOCUMENTATION.md).

---

## 🎨 Frontend Requirements & Developer Guidelines
Frontend developers must refer to the [FRONTEND_DOCUMENTATION.md](file:///e:/Poshu_Sheva/FRONTEND_DOCUMENTATION.md) for UX and design specs. Additionally, the following strict guidelines must be adhered to:

### 1. 🇧🇩 Complete Bangla UI Localization
The entire application interface must be fully localized in Bangla. No English text or transliterated words should be visible to the user. Use the exact phrasing specified below:
* **Project Name:** পশু সেবা AI
* **Authentication:** লগ ইন অথবা নতুন অ্যাকাউন্ট খুলুন
* **History:** পুরনো সংরক্ষিত তথ্য দেখুন
* **Inputs & Controls:**
  * লিখিত তথ্য দিন (Text input field)
  * ছবি দিন (Image upload button)
  * অডিও দিন (Audio recording/upload button)
* **Actions:** সংরক্ষণ করুন (Save button)

### 2. 🗺️ Application Directions & Prompts
All user instructions, form placeholders, error alerts, tooltips, and informational text must be written entirely in clear, simple Bangla. Avoid complex technical jargon so that common people facing an animal emergency can navigate the system easily and without confusion.

---

## 🚀 Git Workflow Reminder
* **Do not push directly to the `main` branch.**
* Always pull the latest changes from upstream.
* Create a dedicated feature branch for your implementation (e.g., `feature/frontend-ui`).
* Open a Pull Request (PR) for review once your components are fully tested.
