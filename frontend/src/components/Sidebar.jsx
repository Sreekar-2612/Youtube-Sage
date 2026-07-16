import React from "react";

export default function Sidebar({
  videoUrl,
  setVideoUrl,
  onLoad,
  loading,
  session,
  onClearMemory,
}) {
  return (
    <section className="bg-white tech-border p-6 rounded shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-headline-md text-headline-md flex items-center gap-2 text-primary">
          <span className="material-symbols-outlined text-primary">link</span> SOURCE
        </h2>
        <span className="bg-secondary-fixed text-secondary px-2 py-0.5 font-label-technical text-[10px] rounded border border-secondary uppercase font-semibold">
          Live
        </span>
      </div>

      {/* Input & Action */}
      <div className="space-y-4">
        <div>
          <label className="block font-label-technical text-label-technical mb-2 text-on-surface-variant text-xs uppercase font-semibold">
            Video URL / Stream
          </label>
          <input
            className="w-full bg-surface-container-low border border-outline px-4 py-3 font-label-technical text-xs text-primary focus:border-primary focus:ring-0 outline-none rounded"
            type="text"
            placeholder="PASTE YOUTUBE LINK..."
            value={videoUrl}
            onChange={(e) => setVideoUrl(e.target.value)}
          />
        </div>

        <button
          className="w-full bg-primary text-on-primary font-button-text text-xs uppercase py-3 rounded border-2 border-primary hover:opacity-95 transition-all font-bold disabled:opacity-30 disabled:cursor-not-allowed"
          onClick={onLoad}
          disabled={loading || !videoUrl}
        >
          {loading ? "Indexing Transcript…" : "Load Transcript"}
        </button>

        {/* Session Card Info */}
        {session && (
          <div className="space-y-4 pt-2">
            <div className="aspect-video bg-surface-container relative overflow-hidden rounded tech-border">
              <img
                className="w-full h-full object-cover grayscale-[0.2]"
                src={`https://img.youtube.com/vi/${session.video_id}/mqdefault.jpg`}
                alt="Video thumbnail"
              />
            </div>
            
            <dl className="grid grid-cols-3 gap-2 text-center font-label-technical text-[9px] tracking-tighter">
              <div className="p-2 bg-surface-container-low rounded border border-outline">
                <dt className="text-secondary font-black uppercase mb-1">Video ID</dt>
                <dd className="text-primary font-bold">{session.video_id}</dd>
              </div>
              <div className="p-2 bg-surface-container-low rounded border border-outline">
                <dt className="text-primary font-black uppercase mb-1">Chunks</dt>
                <dd className="text-primary font-bold">{session.num_chunks}</dd>
              </div>
              <div className="p-2 bg-surface-container-low rounded border border-outline">
                <dt className="text-tertiary font-black uppercase mb-1">Session</dt>
                <dd className="text-primary font-bold">{session.session_id.slice(0, 6)}</dd>
              </div>
            </dl>

            <button
              onClick={onClearMemory}
              className="w-full py-2.5 border-2 border-secondary text-secondary font-bold uppercase rounded text-xs hover:bg-secondary hover:text-on-secondary transition-all"
            >
              Clear Memory
            </button>
          </div>
        )}
      </div>
    </section>
  );
}