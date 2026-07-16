'use client';

interface Scene {
  text: string;
  voiceover: string;
  image_prompt: string;
  duration: number;
  transition: string;
}

interface Props {
  scenes: Scene[];
  onChange: (scenes: Scene[]) => void;
}

const TRANSITIONS = ['fade', 'slide', 'zoom'];

export default function SceneEditor({ scenes, onChange }: Props) {

  function updateScene(index: number, field: keyof Scene, value: string | number) {
    const updated = scenes.map((s, i) =>
      i === index ? { ...s, [field]: value } : s
    );
    onChange(updated);
  }

  function moveScene(from: number, to: number) {
    const updated = [...scenes];
    const [moved] = updated.splice(from, 1);
    updated.splice(to, 0, moved);
    onChange(updated);
  }

  function removeScene(index: number) {
    onChange(scenes.filter((_, i) => i !== index));
  }

  function addScene() {
    onChange([
      ...scenes,
      { text: '', voiceover: '', image_prompt: '', duration: 5, transition: 'fade' }
    ]);
  }

  return (
    <div className="space-y-4">
      {scenes.map((scene, i) => (
        <div key={i} className="bg-gray-800 rounded-xl p-4 border border-gray-700">

          {/* Scene header */}
          <div className="flex justify-between items-center mb-3">
            <span className="text-sm font-semibold text-blue-400">
              🎬 Scène {i + 1}
            </span>
            <div className="flex gap-2">
              {i > 0 && (
                <button onClick={() => moveScene(i, i - 1)}
                  className="text-xs bg-gray-700 hover:bg-gray-600 rounded px-2 py-1">
                  ↑
                </button>
              )}
              {i < scenes.length - 1 && (
                <button onClick={() => moveScene(i, i + 1)}
                  className="text-xs bg-gray-700 hover:bg-gray-600 rounded px-2 py-1">
                  ↓
                </button>
              )}
              <button onClick={() => removeScene(i)}
                className="text-xs bg-red-800 hover:bg-red-700 rounded px-2 py-1">
                ✕
              </button>
            </div>
          </div>

          {/* Fields */}
          <div className="space-y-3">
            <div>
              <label className="text-xs text-gray-400 mb-1 block">Texte à l'écran</label>
              <input
                value={scene.text}
                onChange={e => updateScene(i, 'text', e.target.value)}
                className="w-full bg-gray-900 rounded-lg p-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Texte affiché dans la vidéo"
              />
            </div>

            <div>
              <label className="text-xs text-gray-400 mb-1 block">Voix off</label>
              <textarea
                value={scene.voiceover}
                onChange={e => updateScene(i, 'voiceover', e.target.value)}
                className="w-full bg-gray-900 rounded-lg p-2 text-sm h-16 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Texte lu par la voix off IA"
              />
            </div>

            <div>
              <label className="text-xs text-gray-400 mb-1 block">Image (prompt Pexels)</label>
              <input
                value={scene.image_prompt}
                onChange={e => updateScene(i, 'image_prompt', e.target.value)}
                className="w-full bg-gray-900 rounded-lg p-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Ex: modern office team collaboration"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs text-gray-400 mb-1 block">
                  Durée (s) : {scene.duration}s
                </label>
                <input
                  type="range" min={2} max={15} step={1}
                  value={scene.duration}
                  onChange={e => updateScene(i, 'duration', Number(e.target.value))}
                  className="w-full accent-blue-500"
                />
              </div>
              <div>
                <label className="text-xs text-gray-400 mb-1 block">Transition</label>
                <select
                  value={scene.transition}
                  onChange={e => updateScene(i, 'transition', e.target.value)}
                  className="w-full bg-gray-900 rounded-lg p-2 text-sm">
                  {TRANSITIONS.map(t => (
                    <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        </div>
      ))}

      {/* Add scene */}
      <button onClick={addScene}
        className="w-full border-2 border-dashed border-gray-600 hover:border-blue-500 rounded-xl py-3 text-gray-400 hover:text-blue-400 transition text-sm font-semibold">
        + Ajouter une scène
      </button>
    </div>
  );
}
