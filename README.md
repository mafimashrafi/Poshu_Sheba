# Internal Collaboration Guide (README.md)

> **দ্রষ্টব্য:** এটি আমাদের অভ্যন্তরীণ কাজের সুবিধার জন্য একটি সাময়িক ডকুমেন্টেশন। এটি চূড়ান্ত বা প্রোডাকশন README নয়।

This project, **Poshu_Sheba_AI**, is an attempt to use Google's latest `gemma4:e4b-it-q4_K_M` model to build an AI assistant that provides primary veterinary support to common people before a doctor arrives or before they can reach a vet medical center.

---

## 🛠️ Backend Implementation & Documentation
The core API routes, controller logic, and model configurations have been successfully implemented. 
* All technical details, request/response body schemas, and backend architecture details have been documented in the `Backend/` directory.
* Necessary dependencies and packages have been added to the configuration files.
* **Important Note:** Due to some initial environment issues, the baseline configuration was pushed directly to the main branch. Please ensure you pull the latest changes before starting your work.

---

## 🎨 Frontend Requirements & Developer Guidelines
Frontend developers must refer to the frontend documentation folder for routing and state management. Additionally, the following strict user experience (UX) guidelines must be implemented:

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
