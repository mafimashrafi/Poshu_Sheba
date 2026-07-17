# Poshu Sheba AI — Frontend Documentation

## Overview

The Poshu Sheba AI frontend is a Bengali-first, Streamlit-based interface for seeking preliminary animal-health guidance. It gives livestock owners and pet caregivers a simple way to describe a problem in writing, attach animal images, or record an audio description. The application presents the AI’s Bengali response and allows signed-in users to keep a private history of useful responses.

The experience is designed for everyday users in Bangladesh. It uses plain Bengali labels, visual cues, and a consistent safety reminder that AI guidance is not a replacement for a qualified veterinarian.

## What users can do

- Submit an animal-health question as text, images, audio, or a combination of these inputs.
- Receive a Bengali AI response containing preliminary guidance.
- Create an account or sign in with a Bangladesh mobile number.
- Save an AI response after signing in.
- Read previously saved responses, with the most recent shown first.
- Consult the in-app Bengali usage guide and safety reminder.

## Application experience

```text
Home
  └─ Describe the animal’s condition
       ├─ Write the details
       ├─ Add one or more images
       └─ Record audio in Bengali
             │
             ▼
        Receive AI guidance
             │
             └─ Sign in (optional) → Save guidance → View saved responses
```

The main home screen has three areas:

| Area | Purpose |
| --- | --- |
| Left navigation | Opens a new question, saved responses, or the usage guide; also displays a veterinary-care reminder |
| Main workspace | Collects the question and shows the AI response |
| Saved-response panel | Shows a sign-in prompt for guests or a preview of saved responses for signed-in users |

## User journeys

### Ask a question

On **নতুন প্রশ্ন করুন** (New question), the user may provide any one or more of the following:

| Input | User-facing purpose |
| --- | --- |
| Written description | Explain symptoms, duration, behaviour, or other observations |
| Images | Show visible concerns such as wounds, swelling, rashes, or colour changes |
| Audio recording | Describe the issue in Bengali without typing |

After selecting **জমা দিন** (Submit), the application displays the generated guidance in an AI advice card. A clear reminder below the form notes that AI may be incorrect.

### Create an account and sign in

The account dialog is available from the header and anywhere a saved-response action requires sign-in. A user can create an account with an optional name, Bangladesh mobile number, and password, or sign in to an existing account. The header then shows the user’s name when supplied, otherwise a masked version of the phone number. Logging out returns the user to the home screen.

Account access is optional for asking questions. It is required only for saving and reading response history.

### Save and revisit guidance

After an AI response is shown, a signed-in user can select **সংরক্ষণ করুন** (Save). The saved-response panel shows recent entries on the home screen, while **সেভ করা উত্তরসমূহ** (Saved responses) shows the complete history. Each entry includes a short preview and its saved time.

If an account session has expired, the application removes the local signed-in state and asks the user to sign in again.

## Content and safety principles

The interface is intentionally Bengali-first: labels, actions, feedback, and common error messages are written for Bangla-speaking users. It focuses on animal health and care, including livestock, poultry, and companion animals.

The product presents AI guidance as preliminary information, not a clinical diagnosis. Users are reminded to contact a nearby veterinarian when needed, especially for emergencies or severe symptoms.

## Visual identity

The interface uses a calm navy, teal, and light-gray palette, rounded cards, and simple animal-care imagery. The `vet.ai` brand appears in the header, with a small animated cow mascot and locally stored logo assets that create a friendly, approachable tone without competing with the question-and-answer flow.

## Screen reference

| Screen or component | Description |
| --- | --- |
| Header | Brand, home shortcut, and account controls |
| New question | Text field, image selection, Bengali audio recording, submit action, and AI guidance card |
| Saved responses | Private history for the signed-in user |
| Usage guide | Short Bengali explanation of the core question-to-guidance flow |
| Safety card | Persistent reminder to seek professional veterinary care when appropriate |

## Privacy and session behaviour

The frontend keeps sign-in information only for the active browser session. Saved responses are tied to the signed-in account and are not displayed to other users. The application does not show a password after it has been entered. When the session is unavailable or expired, it returns to a signed-out state before showing protected saved content.

## Service availability

The frontend depends on the Poshu Sheba AI backend for account access, saved responses, and AI-generated advice. Audio transcription and response generation may take longer than a typical page action, particularly when the AI service is busy. The interface gives Bengali feedback if the service is unavailable, a request takes too long, or a response cannot be generated.
