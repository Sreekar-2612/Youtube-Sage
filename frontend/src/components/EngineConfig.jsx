import React from "react";

export default function EngineConfig({
  config,
  provider,
  setProvider,
  modelName,
  setModelName,
  useAgent,
  setUseAgent,
  lastLatency = 0,
  lastThroughput = 0,
}) {
  const modelOptions =
    provider === "groq" ? config?.groq_models : config?.hf_models;

  return (
    <section className="bg-white tech-border p-6 rounded shadow-sm border-l-4 border-l-primary">
      <h2 className="font-headline-md text-headline-md mb-4 flex items-center gap-2 text-primary">
        <span className="material-symbols-outlined">memory</span> ENGINE
      </h2>

      <div className="space-y-4">
        {/* Provider Toggle Tabs */}
        <div>
          <label className="block font-label-technical text-label-technical mb-2 text-on-surface-variant uppercase text-xs">
            Model Provider
          </label>
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={() => setProvider("groq")}
              className={`p-3 text-center rounded font-label-technical text-xs uppercase transition-all duration-700 ${
                provider === "groq"
                  ? "bg-primary text-on-primary font-bold border-2 border-primary-container shadow-[2px_2px_0px_0px_rgba(184,19,17,1)]"
                  : "bg-surface-container text-on-surface-variant border border-outline hover:bg-surface-variant"
              }`}
            >
              Groq LPU
            </button>
            <button
              onClick={() => setProvider("huggingface")}
              className={`p-3 text-center rounded font-label-technical text-xs uppercase transition-all duration-700 ${
                provider === "huggingface"
                  ? "bg-primary text-on-primary font-bold border-2 border-primary-container shadow-[2px_2px_0px_0px_rgba(184,19,17,1)]"
                  : "bg-surface-container text-on-surface-variant border border-outline hover:bg-surface-variant"
              }`}
            >
              HuggingFace
            </button>
          </div>
        </div>

        {/* Model Dropdown */}
        <div>
          <label className="block font-label-technical text-label-technical mb-2 text-on-surface-variant uppercase text-xs">
            Model Selection
          </label>
          <select
            className="w-full bg-surface-container-low border border-outline px-4 py-3 font-label-technical text-xs text-primary focus:border-primary focus:ring-0 outline-none rounded"
            value={modelName}
            onChange={(e) => setModelName(e.target.value)}
          >
            {modelOptions &&
              Object.entries(modelOptions).map(([label, value]) => (
                <option key={value} value={value} className="bg-white text-primary">
                  {label}
                </option>
              ))}
          </select>
        </div>

        {/* Agent Toggle Switch */}
        <div className="flex items-center justify-between pt-2">
          <span className="font-label-technical text-xs text-on-surface-variant uppercase font-semibold">
            Agent Mode (Tool Calling)
          </span>
          <div
            className={`w-12 h-6 border-2 relative cursor-pointer bg-surface-container-lowest rounded-full transition-colors duration-300 ${
              useAgent ? "border-primary" : "border-secondary"
            }`}
            onClick={() => setUseAgent(!useAgent)}
          >
            <div
              className={`absolute top-0.5 left-0.5 w-[16px] h-[16px] rounded-full transition-all duration-300 ${
                useAgent ? "translate-x-6 bg-primary" : "translate-x-0 bg-secondary"
              }`}
            ></div>
          </div>
        </div>

        <div className="engine-stats">
          <div>
            <span>Inference Latency</span>
            <strong>{lastLatency || "--"}<small>{lastLatency ? " ms" : ""}</small></strong>
            <em>Optimized TTFT</em>
          </div>
          <div>
            <span>Throughput</span>
            <strong>{lastThroughput || "--"}<small>{lastThroughput ? " tok/s" : ""}</small></strong>
            <em>Live Cluster</em>
          </div>
        </div>
        <div className="engine-footer">
          <span>↻ Flush Memory Cache</span>
          <span>RAM: 1.2 GB</span>
        </div>
      </div>
    </section>
  );
}
