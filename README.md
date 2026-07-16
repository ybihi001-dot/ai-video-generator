# 🎬 AI Video Generator SaaS

> Transforme un simple prompt en une vidéo montée automatiquement avec voix off IA, sous-titres, musique de fond et effets de transition.

![Version](https://img.shields.io/badge/version-0.4-blue)
![Stack](https://img.shields.io/badge/stack-FastAPI%20%2B%20Next.js-green)
![License](https://img.shields.io/badge/license-MIT-orange)

---

## ✨ Fonctionnalités

| Version | Fonctionnalités |
|---|---|
| **V0.1** | Prompt → Script → Images Pexels → Rendu FFmpeg |
| **V0.2** | Jobs asynchrones, statut temps réel, voix off OpenAI TTS, sous-titres |
| **V0.3** | Éditeur de scènes (SceneEditor), prévisualisation par scène |
| **V0.4** | Musique de fond, transitions (fade/slide/zoom), branding watermark, export MP4 |

---

## 🏗️ Architecture

```
ai-video-generator/
├── backend/              # FastAPI (Python)
│   ├── main.py          # API principale + jobs asynchrones
│   ├── tts.py           # Voix off via OpenAI TTS
│   ├── renderer.py      # Montage vidéo avec FFmpeg
│   └── requirements.txt
├── frontend/             # Next.js + Tailwind CSS
│   ├── app/
│   │   └── page.tsx     # Interface principale
│   └── components/
│       └── SceneEditor.tsx  # Éditeur de scènes
├── render.yaml           # Déploiement Render (backend)
├── setup.sh              # Script d'initialisation
└── README.md
```

---

## 🚀 Démarrage rapide

### Prérequis
- Python 3.10+
- Node.js 18+
- FFmpeg installé ([télécharger](https://ffmpeg.org/download.html))
- Clés API : OpenAI + Pexels

### Installation

```bash
# 1. Cloner le repo
git clone https://github.com/ybihi001-dot/ai-video-generator.git
cd ai-video-generator

# 2. Backend
cd backend
pip install -r requirements.txt
cp .env.example .env
# Remplir OPENAI_API_KEY et PEXELS_API_KEY dans .env
uvicorn main:app --reload

# 3. Frontend (nouvel onglet terminal)
cd frontend
npm install
npm run dev
```

Ouvrir http://localhost:3000

---

## 🌐 Déploiement

### Backend → Render
1. Connecter ce repo GitHub à [Render](https://render.com)
2. Le fichier `render.yaml` configure automatiquement le service
3. Ajouter les variables d'environnement dans le dashboard Render :
   - `OPENAI_API_KEY`
   - `PEXELS_API_KEY`

### Frontend → Netlify
1. Connecter ce repo à [Netlify](https://app.netlify.com)
2. Build command : `npm run build`
3. Publish directory : `.next`
4. Variable d'environnement : `NEXT_PUBLIC_API_URL=https://your-backend.onrender.com`

---

## 🔗 API Endpoints

| Méthode | Endpoint | Description |
|---|---|---|
| `POST` | `/api/videos/create` | Créer une vidéo (retourne job_id) |
| `GET` | `/api/videos/status/{job_id}` | Statut du job en temps réel |
| `GET` | `/api/videos/history` | Historique des vidéos |
| `POST` | `/api/videos/preview-scene` | Prévisualiser une scène |
| `GET` | `/api/videos/download/{job_id}` | Télécharger la vidéo MP4 |

---

## 🛠️ Tech Stack

- **Backend** : FastAPI + Python + FFmpeg
- **Frontend** : Next.js 14 + Tailwind CSS + TypeScript
- **IA** : OpenAI GPT-4o (script) + OpenAI TTS (voix off)
- **Médias** : Pexels API (images/vidéos stock)
- **Déploiement** : Render (backend) + Netlify (frontend)

---

## 📄 License

MIT — © 2026 [ybihi001-dot](https://github.com/ybihi001-dot)
