'use client';

import { useState, useEffect, useRef } from 'react';
import SceneEditor from '../components/SceneEditor';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Scene {
  text: string;
  voiceover: string;
  image_prompt: string;
  duration: number;
  transition: string;
}

interface JobStatus {
  status: string;
  progress: number;
  video_url: string | null;
  storyboard: Scene[] | null;
  error: string | null;
}

export default function Home() {
  const [prompt, setPrompt] = useState('');
  const [format, setFormat] = useState('16:9');
  const [style, setStyle] = useState('corporate');
  const [music, setMusic] = useState('corporate');
  const [brandText, setBrandText] = useState('');
  const [jobId, setJobId] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null);
  const [scenes, setScenes] = useState<Scene[] | null>(null);
  const [editingScenes, setEditingScenes] = useState(false);
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const pollRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    fetchHistory();
    return () => { if (pollRef.current) clearInterval(pollRef.current); };
  }, []);

  async function fetchHistory() {
    try {
      const res = await fetch(`${API_URL}/api/videos/history`);
      if (res.ok) setHistory(await res.json());
    } catch {}
  }

  async function generateStoryboard() {
    if (!prompt.trim()) return;
    setLoading(true);
    setJobStatus(null);
    setScenes(null);
    setEditingScenes(false);

    const res = await fetch(`${API_URL}/api/videos/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, format, style, music, brand_text: brandText || null }),
    });
    const data = await res.json();
    setJobId(data.job_id);
    pollStatus(data.job_id);
    setLoading(false);
  }

  function pollStatus(id: string) {
    pollRef.current = setInterval(async () => {
      try {
        const res = await fetch(`${API_URL}/api/videos/status/${id}`);
        const data: JobStatus = await res.json();
        setJobStatus(data);

        if (data.storyboard && !scenes) {
          setScenes(data.storyboard);
          setEditingScenes(true);
        }

        if (data.status === 'completed' || data.status === 'error') {
          clearInterval(pollRef.current!);
          fetchHistory();
        }
      } catch {}
    }, 2000);
  }

  async function renderFinal() {
    if (!prompt.trim() || !scenes) return;
    setEditingScenes(false);
    setLoading(true);

    const res = await fetch(`${API_URL}/api/videos/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt, format, style, music,
        brand_text: brandText || null,
        scenes,
      }),
    });
    const data = await res.json();
    setJobId(data.job_id);
    pollStatus(data.job_id);
    setLoading(false);
  }

  const statusColor: Record<string, string> = {
    queued: 'text-yellow-400',
    completed: 'text-green-400',
    error: 'text-red-400',
  };

  return (
    <main className="min-h-screen bg-gray-950 text-white p-6">
      <div className="max-w-4xl mx-auto">

        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-2">🎬 AI Video Generator</h1>
          <p className="text-gray-400">Transforme ton prompt en vidéo montaé automatiquement</p>
        </div>

        {/* Form */}
        <div className="bg-gray-900 rounded-2xl p-6 mb-6 space-y-4">
          <textarea
            value={prompt}
            onChange={e => setPrompt(e.target.value)}
            placeholder="Décris ta vidéo... Ex: Présentation produit pour une startup tech"
            className="w-full bg-gray-800 rounded-xl p-4 h-28 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
          />

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div>
              <label className="text-xs text-gray-400 mb-1 block">Format</label>
              <select value={format} onChange={e => setFormat(e.target.value)}
                className="w-full bg-gray-800 rounded-lg p-2 text-sm">
                <option value="16:9">16:9 YouTube</option>
                <option value="9:16">9:16 TikTok</option>
                <option value="1:1">1:1 Instagram</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-gray-400 mb-1 block">Style</label>
              <select value={style} onChange={e => setStyle(e.target.value)}
                className="w-full bg-gray-800 rounded-lg p-2 text-sm">
                <option value="corporate">Corporate</option>
                <option value="cinematic">Cinématique</option>
                <option value="educational">Pédagogique</option>
                <option value="viral">Viral</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-gray-400 mb-1 block">Musique</label>
              <select value={music} onChange={e => setMusic(e.target.value)}
                className="w-full bg-gray-800 rounded-lg p-2 text-sm">
                <option value="corporate">Corporate</option>
                <option value="cinematic">Cinématique</option>
                <option value="upbeat">Upbeat</option>
                <option value="none">Aucune</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-gray-400 mb-1 block">Watermark</label>
              <input value={brandText} onChange={e => setBrandText(e.target.value)}
                placeholder="Mon Brand"
                className="w-full bg-gray-800 rounded-lg p-2 text-sm"
              />
            </div>
          </div>

          <button onClick={generateStoryboard} disabled={loading || !prompt.trim()}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 rounded-xl py-3 font-semibold transition">
            {loading ? 'Génération...' : '✨ Générer la vidéo'}
          </button>
        </div>

        {/* Job Status */}
        {jobStatus && (
          <div className="bg-gray-900 rounded-2xl p-6 mb-6">
            <div className="flex justify-between items-center mb-3">
              <span className={`font-semibold ${statusColor[jobStatus.status] || 'text-blue-400'}`}>
                {jobStatus.status.replace(/_/g, ' ').toUpperCase()}
              </span>
              <span className="text-gray-400 text-sm">{jobStatus.progress}%</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2 mb-4">
              <div className="bg-blue-500 h-2 rounded-full transition-all"
                style={{ width: `${jobStatus.progress}%` }} />
            </div>
            {jobStatus.status === 'completed' && jobStatus.video_url && (
              <div className="space-y-3">
                <video controls className="w-full rounded-xl">
                  <source src={`${API_URL}${jobStatus.video_url}`} type="video/mp4" />
                </video>
                <a href={`${API_URL}${jobStatus.video_url}`} download
                  className="block text-center bg-green-600 hover:bg-green-700 rounded-xl py-2 font-semibold">
                  ⬇️ Télécharger MP4
                </a>
              </div>
            )}
            {jobStatus.status === 'error' && (
              <p className="text-red-400">⚠️ {jobStatus.error}</p>
            )}
          </div>
        )}

        {/* Scene Editor */}
        {editingScenes && scenes && (
          <div className="bg-gray-900 rounded-2xl p-6 mb-6">
            <h2 className="text-xl font-bold mb-4">✒️ Éditeur de scènes</h2>
            <SceneEditor scenes={scenes} onChange={setScenes} />
            <button onClick={renderFinal}
              className="mt-4 w-full bg-purple-600 hover:bg-purple-700 rounded-xl py-3 font-semibold transition">
              🎬 Lancer le rendu final
            </button>
          </div>
        )}

        {/* History */}
        {history.length > 0 && (
          <div className="bg-gray-900 rounded-2xl p-6">
            <h2 className="text-xl font-bold mb-4">📌 Historique</h2>
            <div className="space-y-2">
              {history.map((h: any) => (
                <div key={h.job_id} className="flex justify-between items-center bg-gray-800 rounded-xl p-3">
                  <span className="text-sm text-gray-400 font-mono">{h.job_id.slice(0, 8)}...</span>
                  <a href={`${API_URL}/api/videos/download/${h.job_id}`} download
                    className="bg-blue-600 hover:bg-blue-700 rounded-lg px-3 py-1 text-sm">
                    Télécharger
                  </a>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
