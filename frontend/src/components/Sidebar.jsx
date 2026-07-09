import React from "react";

export default function Sidebar({
    config,
    provider,
    setProvider,
    modelName,
    setModelName,
    useAgent,
    setUseAgent,
    videoUrl,
    setVideoUrl,
    onLoad,
    loading,
    session,
    onClearMemory,
}) {
    const modelOptions = provider == "groq" ? config?.groq_models: config?.hf_models;

    return {
        
    }
}