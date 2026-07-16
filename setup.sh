#!/bin/bash
set -e

echo "=== AI Video Generator V0.4 - Setup ==="

# Creer la structure
mkdir -p ai-video-generator/backend
mkdir -p ai-video-generator/frontend
cd ai-video-generator

# --- BACKEND ---
cd backend

cat > requirements.txt << 'EOF'
fastapi
uvicorn[standard]
python-dotenv
openai
pydantic
requests
pillow
aiofiles
EOF

cat > .env.example << 'EOF'
OPENAI_API_KEY=sk-your-key-here
PEXELS_API_KEY=your-pexels-key-here
EOF

touch main.py tts.py renderer.py

echo "Backend structure created."
cd ..

# --- FRONTEND ---
cd frontend
npx create-next-app@latest . --ts --tailwind --eslint --no-src-dir --import-alias "@/*" --yes
mkdir -p components
touch components/SceneEditor.tsx
echo "Frontend structure created."
cd ..

echo ""
echo "=== Setup terminé ! ==="
echo "1. cd ai-video-generator/backend && pip install -r requirements.txt"
echo "2. cp .env.example .env && remplir les clés API"
echo "3. uvicorn main:app --reload"
echo "4. cd ../frontend && npm run dev"
