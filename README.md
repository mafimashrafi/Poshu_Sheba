# 🩺 পশু সেবা AI (Poshu Sheba AI)
> **কৃষক ও সাধারণ খামারিদের জন্য একটি নির্ভরযোগ্য প্রাথমিক পশু স্বাস্থ্যসেবা AI সহকারী।**

<p align="center">
  <img src="Frontend/assets/logo_icon.png" alt="Poshu Sheba AI Logo" width="120px" style="border-radius: 50%; box-shadow: 0 4px 15px rgba(0,0,0,0.15); animation: pulse 2s infinite ease-in-out;" />
</p>

<p align="center">
  <a href="#-features">ফিচারসমূহ</a> •
  <a href="#-quick-start">নির্দেশিকা</a> •
  <a href="#-api-documentation">এপিআই ডকুমেন্টেশন</a> •
  <a href="#-collaboration-guide">workflow</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python Version" />
  <img src="https://img.shields.io/badge/FastAPI-0.139%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Streamlit-1.59%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit" />
  <img src="https://img.shields.io/badge/MongoDB-Atlas-47A248?style=for-the-badge&logo=mongodb&logoColor=white" alt="MongoDB" />
</p>

---

## 🔗 Live Application Link
> [!TIP]
> **লাইভ ওয়েবসাইট লিংক:** [পশু সেবা AI লাইভ ডেমো](https://your-live-link-here.com) *(শীঘ্রই আসছে)*

---

## 🌟 Features

* **গবাদি ও হাঁস-মুরগি কভারেজ**: গরু (Cow), ছাগল (Goat), মুরগি (Chicken), এবং হাঁস (Duck)-এর রোগের সঠিক লক্ষণ ও প্রাথমিক যত্ন।
* **স্মার্ট সিম্পটম ম্যাচিং (সিম্পটম ট্র্যাকার)**: ব্যবহারকারীর লিখিত বা কণ্ঠস্বরের (অডিও) বর্ণনা বিশ্লেষণ করে স্বয়ংক্রিয়ভাবে ডাটাবেজ থেকে রোগ শনাক্তকরণ।
* **গ্রাউন্ডেড জেনারেটিভ এআই (Gemma 4 integration)**: স্বয়ংক্রিয়ভাবে ডাটাবেজের সঠিক তথ্যসূত্রের উপর ভিত্তি করে নির্ভুল পরামর্শ তৈরি।
* **অডিও ও ইমেজ আপলোড**: পশুর ছবি এবং বাংলায় বলা অডিওর মাধ্যমে রোগের বর্ণনা সরাসরি আদান-প্রদানের সুবিধা।
* **বাংলা ভাষায় সম্পূর্ণ ইউজার ইন্টারফেস**: প্রান্তিক খামারি ও সাধারণ কৃষকদের ব্যবহারের সুবিধার্থে সম্পূর্ণ সহজ বাংলা ইন্টারফেস।

---

## 🚀 Quick Start (Local Setup)

### 📋 Prerequisites
* **Python**: ৩.৮ থেকে ৩.১৩.x সংস্করণ।
* **MongoDB**: লোকাল মঙ্গোডিবি অথবা মঙ্গোডিবি অ্যাটলাস ক্লাউড সংযোগ।
* **Gemini API Key**: গুগল ক্লাউড বা মেকারসুইট থেকে তৈরি করা এপিআই কি।

### Step 1: ক্লোন করুন এবং পরিবেশ তৈরি করুন
```bash
# ক্লোন করুন
git clone https://github.com/mafimashrafi/Poshu_Sheba.git
cd Poshu_Sheba

# ভার্চুয়াল এনভায়রনমেন্ট তৈরি
python -m venv venv

# অ্যাক্টিভেট করুন (Windows - PowerShell)
.\venv\Scripts\Activate.ps1

# অ্যাক্টিভেট করুন (macOS / Linux)
source venv/bin/activate

# লাইব্রেরি ইনস্টল করুন
pip install -r requirements.txt
```

### Step 2: এনভায়রনমেন্ট ফাইল সেটআপ
রুট ফোল্ডারে একটি `.env` ফাইল তৈরি করুন (অথবা `.env.example` কপি করে এডিট করুন):
```bash
cp .env.example .env
```
তারপর `.env` ফাইলটিতে আপনার ভ্যালুগুলো যোগ করুন:
```env
MONGODB_URI=mongodb+srv://your_username:your_password@cluster.mongodb.net/
MONGODB_DB=poshu_sheba
GEMINI_API_KEY=your_gemini_api_key_here
```

### Step 3: ব্যাকএন্ড এবং ফ্রন্টএন্ড রান করা

#### ১. ব্যাকএন্ড সার্ভার (FastAPI) চালু করুন:
```bash
cd Backend
uvicorn main:app --reload
```
* **এপিআই লিংক:** `http://127.0.0.1:8000`
* **ডকুমেন্টেশন (Swagger UI):** `http://127.0.0.1:8000/docs`

#### ২. ফ্রন্টএন্ড ওয়েব অ্যাপ (Streamlit) চালু করুন:
*একটি নতুন টার্মিনাল উইন্ডো খুলুন এবং ভার্চুয়াল এনভায়রনমেন্ট অ্যাক্টিভেট করুন:*
```bash
cd Frontend
streamlit run app.py
```
* **লোকাল ওয়েবসাইট লিংক:** `http://localhost:8501`

---

## 🧪 Isolated Verification Tests
আমাদের তৈরি করা সুনির্দিষ্ট সিম্পটম ম্যাচিং অ্যালগরিদম পরীক্ষা করার জন্য লোকাল টেস্ট স্ক্রিপ্ট রান করুন:
```bash
$env:PYTHONIOENCODING="utf-8"; .\venv\Scripts\python Backend/Test/test_matching.py
```

---

## 🛠️ Developer Documentation
* **ব্যাকএন্ড সার্ভিস ও এপিআই এন্ডপয়েন্ট**: বিস্তারিত দেখতে পড়ুন [BACKEND_DOCUMENTATION.md](file:///e:/Poshu_Sheva/BACKEND_DOCUMENTATION.md)।
* **ফ্রন্টএন্ড ডিজাইন ও থিম গাইডলাইনস**: বিস্তারিত দেখতে পড়ুন [FRONTEND_DOCUMENTATION.md](file:///e:/Poshu_Sheva/FRONTEND_DOCUMENTATION.md)।

---

## 🎨 UI Guidelines (Bangla UI)
খামারি ও সাধারণ মানুষের সুবিধার্থে পুরো সিস্টেমে নিম্নলিখিত শব্দগুলো ব্যবহার করতে হবে:
* **প্রজেক্টের নাম:** পশু সেবা AI
* **লগইন:** লগ ইন অথবা নতুন অ্যাকাউন্ট খুলুন
* **সংরক্ষণ করুন:** সংরক্ষণ করুন
* **অডিও দিন:** অডিও দিন

---

## 🚀 Collaboration Guide & Git Workflow
1. সরাসরি `main` ব্রাঞ্চে কোনো কোড পুশ করবেন না।
2. নতুন ফিচার বা বাগ-ফিক্স নিয়ে কাজ করার জন্য সবসময় নতুন ব্রাঞ্চ তৈরি করবেন:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. পুল রিকোয়েস্ট (PR) খোলার আগে লোকাল টেস্ট চালিয়ে কোড কোয়ালিটি নিশ্চিত করবেন।

---
<p align="center">
  <i>Made with ❤️ for the Farmers of Bangladesh</i>
</p>
