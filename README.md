# ClarityDx - AI-Powered Multi-Disease Diagnosis System

<div align="center">

![ClarityDx Banner](https://img.shields.io/badge/ClarityDx-AI%20Health%20Assistant-teal?style=for-the-badge)
[![License](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)](LICENSE)

**AI-powered diagnostic assistant for Heart Disease, Chronic Kidney Disease, Hepatitis C, Malaria, and Symptom-based diagnosis**

[Live Demo](https://claritydx.netlify.app) • [Documentation](#documentation) • [Report Bug](https://github.com/your-username/ClarityDx/issues)

</div>

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Getting Started](#-getting-started)
- [Deployment](#-deployment)
  - [Option 1: Netlify (Serverless)](#option-1-netlify-serverless)
  - [Option 2: Render (Traditional Backend)](#option-2-render-traditional-backend)
- [Environment Variables](#-environment-variables)
- [API Endpoints](#-api-endpoints)
- [ML Models](#-ml-models)
- [Contributing](#-contributing)
- [License](#-license)
- [Disclaimer](#-medical-disclaimer)

---

## ✨ Features

### 🏥 Diagnostic Tools

- **Heart Disease Prediction** - 13-parameter cardiovascular risk assessment
- **Chronic Kidney Disease (CKD)** - 24-parameter kidney function analysis
- **Hepatitis C Diagnosis** - Liver enzyme and biomarker evaluation
- **Malaria Detection** - blood smear image analysis
- **SymScan** - Symptom-based disease prediction with precautions

### 🔐 Patient Management

- Complete patient records system
- Encounter tracking and medical history
- Secure authentication with Firebase
- CRUD operations for patients, encounters, and records

### 🚀 Performance

- Serverless architecture for scalability
- Model caching for faster predictions
- PostgreSQL database for reliable data storage
- Real-time AI predictions

---

## 🛠️ Tech Stack

### Frontend

- **React 19.0** - UI framework
- **Vite 6.1** - Build tool & dev server
- **TailwindCSS 3.4** - Styling
- **shadcn/ui** - UI components
- **Firebase** - Authentication
- **Axios** - HTTP client

### Backend (Serverless)

- **Netlify Functions** - Python serverless endpoints
- **TensorFlow 2.14** - Deep learning models
- **scikit-learn 1.6** - Machine learning algorithms
- **OpenCV 4.11** - Image processing
- **PostgreSQL** - Database

### ML Models

- **Heart Disease**: Advanced neural network with PCA
- **CKD**: Random Forest Classifier
- **Hepatitis C**: Random Forest model
- **Malaria**: Multi-class CNN (Uninfected/Parasitized/Non-Blood Smear)
- **SymScan**: Symptom-to-disease classifier with NLTK

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                     │
│                  Hosted on Netlify                      │
└────────────┬────────────────────────────────────────────┘
             │ API Calls (/api/*)
             ↓
┌─────────────────────────────────────────────────────────┐
│          Netlify Functions (Python)                     │
│  ┌─────────────────────────────────────────────┐       │
│  │  Prediction Functions                       │       │
│  │  - predict-heart-disease.py                 │       │
│  │  - predict-ckd.py                           │       │
│  │  - predict-hepatitis-c.py                   │       │
│  │  - predict-symscan.py                       │       │
│  │  - process-malaria-image.py                 │       │
│  └─────────────────────────────────────────────┘       │
│  ┌─────────────────────────────────────────────┐       │
│  │  Patient Management Functions               │       │
│  │  - patients.py                              │       │
│  │  - encounters.py                            │       │
│  │  - records.py                               │       │
│  └─────────────────────────────────────────────┘       │
└────────────┬────────────────────────────────────────────┘
             │
        ┌────┴─────┬───────────────┐
        │          │               │
        ↓          ↓               ↓
   ┌────────┐ ┌─────────┐   ┌──────────┐
   │  AWS   │ │PostgreSQL│   │ Firebase │
   │  S3    │ │ Database │   │   Auth   │
   │ Models │ │          │   │          │
   └────────┘ └─────────┘   └──────────┘
```

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+ (for local backend)
- **PostgreSQL** 14+ (for production)
- **Git**
- **Netlify CLI** (optional, for local testing)

### Local Development

#### 1. Clone the Repository

```bash
git clone https://github.com/your-username/ClarityDx.git
cd ClarityDx
```

#### 2. Install Frontend Dependencies

```bash
cd frontend
npm install
```

#### 3. Set Up Environment Variables

Create `frontend/.env.local`:

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8888/api

# Firebase Configuration (get from Firebase Console)
VITE_FIREBASE_API_KEY=your_firebase_api_key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.firebasestorage.app
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id
```

See [`ENV_VARIABLES.md`](ENV_VARIABLES.md) for complete list.

#### 4. Run with Netlify Dev (Recommended)

```bash
# Install Netlify CLI globally
npm install -g netlify-cli

# From project root
netlify dev
```

This runs both frontend and serverless functions locally at `http://localhost:8888`

#### 5. Alternative: Run Frontend Only

```bash
cd frontend
npm run dev
```

Frontend will be at `http://localhost:5173` (functions won't work without backend)

---

## 🌐 Deployment

### Option 1: Netlify (Serverless)

**Best for:** Scalable, serverless deployment with automatic scaling

#### Step 1: Prepare Database

1. Create a PostgreSQL database:

   - **Recommended**: [Supabase](https://supabase.com) (free tier) or [Neon](https://neon.tech)
   - Get your connection string

2. Run the database schema (see [`NETLIFY_DEPLOYMENT.md`](NETLIFY_DEPLOYMENT.md) for complete schema):

```sql
CREATE TABLE patients (
    patient_id SERIAL PRIMARY KEY,
    unique_patient_code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    age INTEGER,
    gender VARCHAR(50),
    contact_info TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- ... (see NETLIFY_DEPLOYMENT.md for complete schema)
```

#### Step 2: Deploy to Netlify

**Via Dashboard:**

1. Go to [app.netlify.com](https://app.netlify.com)
2. Click **"Add new site"** → **"Import an existing project"**
3. Connect to your GitHub repository
4. Configure build settings:
   - **Base directory**: `frontend/`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/dist`
   - **Functions directory**: `netlify/functions`
5. Click **"Deploy site"**

**Via CLI:**

```bash
netlify init
netlify deploy --prod
```

#### Step 3: Configure Environment Variables

In Netlify Dashboard → **Site settings** → **Environment variables**, add:

```
# Database
DATABASE_URL=postgresql://user:password@host:5432/database

# Frontend (IMPORTANT: Use /api not full URL!)
VITE_API_BASE_URL=/api

# Firebase
VITE_FIREBASE_API_KEY=your_key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.firebasestorage.app
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id
```

**⚠️ Important:** Use `/api` for `VITE_API_BASE_URL` (relative path), not the full Netlify URL.

#### Step 4: Redeploy

Trigger a new deployment to apply environment variables:

- Dashboard → **Deploys** → **Trigger deploy** → **Clear cache and deploy site**

---

### Option 2: Render (Traditional Backend)

**Best for:** Traditional deployment, easier Python setup, more control

#### Step 1: Deploy Backend to Render

1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:

   - **Name**: `claritydx-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: Free (or paid for better performance)

5. Add environment variables in Render:

```
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=5432
DATABASE_URL=postgresql://user:password@host:5432/database
```

6. Click **"Create Web Service"**
7. Copy your Render backend URL (e.g., `https://claritydx-backend.onrender.com`)

#### Step 2: Create PostgreSQL Database on Render

1. In Render dashboard, click **"New +"** → **"PostgreSQL"**
2. Name: `claritydx-database`
3. Click **"Create Database"**
4. Copy the **Internal Database URL**
5. Add to backend environment variables as `DATABASE_URL`

#### Step 3: Deploy Frontend to Netlify

1. In Netlify dashboard, import your repository
2. Configure build settings:

   - **Base directory**: `frontend/`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/dist`
   - **Functions directory**: Leave empty (not using Netlify functions)

3. Set environment variables:

```
# Point to your Render backend
VITE_API_BASE_URL=https://claritydx-backend.onrender.com/api

# Firebase config
VITE_FIREBASE_API_KEY=your_key
# ... other Firebase variables
```

4. Deploy the frontend

#### Step 4: Test the Deployment

Visit your Netlify URL and test:

- Frontend loads ✅
- Login works (Firebase) ✅
- Predictions work (calls Render backend) ✅

---

## 🔐 Environment Variables

### Required Variables

| Variable                            | Description                  | Example                                                         |
| ----------------------------------- | ---------------------------- | --------------------------------------------------------------- |
| `DATABASE_URL`                      | PostgreSQL connection string | `postgresql://user:pass@host:5432/db`                           |
| `VITE_API_BASE_URL`                 | API base URL                 | `/api` (Netlify) or `https://backend.onrender.com/api` (Render) |
| `VITE_FIREBASE_API_KEY`             | Firebase API key             | `AIza...`                                                       |
| `VITE_FIREBASE_AUTH_DOMAIN`         | Firebase auth domain         | `project.firebaseapp.com`                                       |
| `VITE_FIREBASE_PROJECT_ID`          | Firebase project ID          | `project-id`                                                    |
| `VITE_FIREBASE_STORAGE_BUCKET`      | Firebase storage bucket      | `project.firebasestorage.app`                                   |
| `VITE_FIREBASE_MESSAGING_SENDER_ID` | Firebase sender ID           | `1234567890`                                                    |
| `VITE_FIREBASE_APP_ID`              | Firebase app ID              | `1:123:web:abc`                                                 |

See [`ENV_VARIABLES.md`](ENV_VARIABLES.md) for detailed setup instructions.

---

## 📡 API Endpoints

### Prediction Endpoints

| Endpoint                              | Method | Description                        |
| ------------------------------------- | ------ | ---------------------------------- |
| `/api/predict/heart_disease`          | POST   | Heart disease prediction           |
| `/api/predict/ckd`                    | POST   | Chronic kidney disease prediction  |
| `/api/predict/hepatitis_c`            | POST   | Hepatitis C prediction             |
| `/api/predict/symscan`                | POST   | Symptom-based disease prediction   |
| `/api/image-processing/process-image` | POST   | Malaria blood smear image analysis |

### Patient Management

| Endpoint                       | Method           | Description               |
| ------------------------------ | ---------------- | ------------------------- |
| `/api/patients`                | GET, POST        | List/Create patients      |
| `/api/patients/:id`            | GET, PUT, DELETE | Manage specific patient   |
| `/api/patients/:id/encounters` | GET, POST        | Manage encounters         |
| `/api/encounters/:id`          | GET, PUT, DELETE | Manage specific encounter |
| `/api/encounters/:id/records`  | GET, POST        | Manage medical records    |
| `/api/records/:id`             | GET, PUT, DELETE | Manage specific record    |

### Example Request

```bash
curl -X POST https://claritydx.netlify.app/api/predict/heart_disease \
  -H "Content-Type: application/json" \
  -d '{
    "age": 55,
    "sex": 1,
    "cp": 1,
    "trestbps": 140,
    "chol": 250,
    "fbs": 0,
    "restecg": 0,
    "thalach": 150,
    "exang": 0,
    "oldpeak": 1.5,
    "slope": 1,
    "ca": 0,
    "thal": 2
  }'
```

---

## 🤖 ML Models

All models are hosted on AWS S3 and loaded on-demand with caching.

### Model Details

| Disease       | Model Type           | Features                       | Framework        |
| ------------- | -------------------- | ------------------------------ | ---------------- |
| Heart Disease | Neural Network + PCA | 13 cardiovascular parameters   | TensorFlow/Keras |
| CKD           | Random Forest        | 24 kidney function indicators  | scikit-learn     |
| Hepatitis C   | Random Forest        | Liver enzyme biomarkers        | scikit-learn     |
| Malaria       | CNN (Multi-class)    | Blood smear image analysis     | TensorFlow/Keras |
| SymScan       | Symptom Classifier   | 100+ symptoms, NLTK processing | scikit-learn     |

Models are cached in `/tmp` (serverless) and in-memory for faster subsequent predictions.

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Medical Disclaimer

**IMPORTANT:** ClarityDx is an educational and informational tool only. It is **NOT** a substitute for professional medical advice, diagnosis, or treatment.

- **Do not** use this system for making medical decisions
- **Always** consult qualified healthcare professionals
- **Never** delay seeking medical advice based on predictions from this system
- **Understand** that AI predictions may be inaccurate

This system should only be used:

- For educational purposes
- As a preliminary screening tool
- To facilitate discussions with healthcare providers

---

## 📚 Documentation

- **[`docs/ NETLIFY_DEPLOYMENT.md`](NETLIFY_DEPLOYMENT.md)** - Comprehensive Netlify deployment guide
- **[`docs/ ENV_VARIABLES.md`](ENV_VARIABLES.md)** - Environment variables configuration

---

## 🙏 Acknowledgments

- TensorFlow and scikit-learn communities
- Firebase for authentication services
- Netlify for serverless hosting
- Render for backend hosting option
- shadcn/ui for beautiful components

---

<div align="center">

**Made with ❤️ for better healthcare accessibility**

[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start/deploy?repository=https://github.com/your-username/ClarityDx)

</div>
