# STT Mountain

A full-stack web application for organizing and managing mountain hiking trips within a club.

> In this project, a **trip** refers to a mountain hiking activity initiated by a leader.
> The leader plans a destination or route, recruits members, manages participants, and publishes trip-related posts.

---

## Why This Project Exists

Organizing mountain trips often involves scattered tools: spreadsheets for participants, chat apps for coordination, and documents for official forms.
This project centralizes the **entire trip workflow** into a single system, covering planning, publishing, participation tracking, and personal history management.

---

## Technical Highlights (For Interviewers)

### System Design & Architecture

- **Full-stack architecture**
  - Backend: Flask (REST-style design)
  - Frontend: Server-rendered templates + dynamic interactions
  - Database: MongoDB
  - Cache / Queue-ready: Redis
  - Infrastructure: Docker & Docker Compose

- **Clear separation of concerns**
  - User accounts vs. trip-specific member data are intentionally separated
  - Supports real-world cases where a participant may not have a site account

### Domain Modeling (Non-trivial)

- Designed **two parallel identity systems**:
  - `User` (authentication, login, personal site data)
  - `TripMember` (real-world participant info used for official documents)
- Implemented a **data-linking mechanism** that allows:
  - Linking trip records to user accounts later
  - Importing historical trip data into a user profile

### Trip Workflow State Management

- A trip follows a strict lifecycle:
  - Proposal → Published → Completed / Cancelled
- Editing permissions and available actions depend on trip state
- Prevents inconsistent states (e.g., editing plans after completion)

### Data Consistency & Automation

- When a trip is marked as **Completed**:
  - Participant trip history is automatically written into each user’s profile
  - Historical records remain immutable even if the original trip post changes later
- This models real-world audit and traceability requirements

### Email & Invitation System

- Invitation-only registration flow
- Email-based onboarding using SMTP (Mailtrap / SendGrid)
- Environment-based mail configuration (dev vs. production)

### Developer Experience

- Fully containerized development environment
- One-command startup using Docker Compose
- Supports:
  - Mock data initialization
  - Manual bootstrap for first admin user
- Clear environment variable management via `.env`

---

## What This Project Demonstrates

- Designing systems around **real-world constraints**, not just CRUD
- Translating ambiguous domain concepts into clean data models
- Thinking about **state, ownership, and permissions**
- Writing maintainable systems that future engineers can extend
- Balancing product needs with engineering discipline

---

## Installation Guide

## Download

- Clone the repository using HTTPS
```
git clone [https://github.com/CTingy/sttmountain.git](https://github.com/CTingy/sttmountain.git) --recurse-submodules
```

- If the submodule static files were not downloaded during the initial clone, run:
```
git submodule update --init
```

- Install Docker & Docker Compose

## Configuration

### Environment Variables

- Rename `ex.env` to `.env` and fill in the required fields

# environment variables for sttmt

SECRET_KEY=
FLASK_APP=sttapp/app.py
FLASK_ENV=development

# DB config

DB_NAME=
DB_USERNAME=
DB_PASSWORD=
DB_PORT=27017
DB_HOST=127.0.0.1

# Redis config

REDIS_HOST=127.0.0.1
REDIS_PORT=6379

# Google services (optional)

GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# Google Drive API (optional)

GOOGLE_DRIVE_FOLDER_ID=
GOOGLE_DRIVE_API_CERD_PATH=

# Mail sender and admin email

MAIL_DEFAULT_SENDER=
ADMIN_EMAIL=

# Development mail server

DEV_MAIL_USERNAME=
DEV_MAIL_PASSWORD=

# Production mail server (optional in dev)

SENDGRID_API_KEY=

## Run

```sh
cd <project_root>/
docker-compose rm -fs
docker-compose -f docker-compose-dev.yml build
docker-compose -f docker-compose-dev.yml up
```

---

## Features Overview

### Registration & Login

- Invitation-only registration
- Email / Google OAuth login
- Controlled onboarding flow

### Features Without Login

- Search trip titles and content
- View all published trip posts

### Features After Login

#### Trip Member Management

- Create / edit / delete trip-specific participant data
- Search by national ID + name
- View historical participation records

#### Trip Proposal

- Create a proposal using **“Organize a Trip”**
- Dynamic member search and planning
- Controlled edit and publish permissions

#### Trip Posts

- Published with meeting time and location
- Immutable after completion or cancellation
- Completion automatically syncs participant history

#### User Pages

- Public profile
- Personal trip history
- Editable private records
- Imported system trip data + manual records

---

## To-Dos (Planned Enhancements)

- View-layer unit tests
- CI pipeline integration
- Rich text editor
- Comment system
- Permission control refinement
- Full-text search
- Tagging and categorization
