import React , { useEffect , useState } from "react";
import Sidebar from "./components/Sidebar.jsx";
import ChatPanel from "./components/ChatPanel.jsx";
import { api } from "./api.js";
import "./App.css";

export default function App() {
    const [config, setConfig] = useState(null);
    const [provider,setProvider] = useState("groq");
    const [modelName , setModelName] = useState("");
    const [useAgent, setUseAgent] = useState(false);

    const [VideoUrl , setVideoUrl] = useState("");
    const [session, setSession] = useState(null);
    const [loading , setLoading] = useState(false);
    const [error,setError] = useState(null);
    const [messages,setMessages] = useState([]);
    const [sending,setSending] = useState(false);

    useEffect(() =>{
        api
        .getConfig()
        .then((cfg)=> {
            setConfig(cfg);
            setModelName(Object.values(cfg.groq_models)[0]);
        })
        .catch(() => setError("Couldn't reach the backend. Is it running on :8000?"));
    } , []);

    useEffect(() => {
        if(!config) return;
        const options = provider == "groq"? config.groq_models : config.hf_models;
        setModelName(Object.values(options)[0]);
    },[provider,config]);

    async function handleLoad() {
        setLoading(true);
        setError(null);
        try {
            const result = api.loadVideo(videoUrl,provider,model_name);
            setSession(result);
            setMessages([]);
        } catch(e) {
            setError(e.message);
        } finally{
            setLoading(false);
        }
    }

    async function handleSend(question) {
        setMessages((prev) => [...prev,{ role: "user", content: question }]);
        setSending(true);
        setError(null);
        try{
            const result = await api.chat(session.session_id , question, useAgent);
            setMessages((prev) => [
                ...prev,
                {
                    role:"assistant",
                    content : result.answer,
                    keyPoints: result.key_points,
                    confidence: result.confidence,
                },
            ]);
        } catch(e) {
            setError(e.message);
        } finally {
            setSending(false);
        }
    }

    async function handleClearMemory() {
        if(!session) return;
        await api.clearSession(session.session_id);
        setMessages([]);
    }

    return (
        <div className="app-shell">
            <Sidebar
             config={config}
             provider={provider}
             setProvider={setProvider}
             modelName={modelName}
             setModelName={setModelName}
             useAgent={useAgent}
             setUseAgent={setUseAgent}
             videoUrl={videoUrl}
             setVideoUrl={setVideoUrl}
             onLoad={handleLoad}
             loading={loading}
             session={session}
             onClearMemory={handleClearMemory}

            />
            <ChatPanel
             session={session}
             messages={messages}
             onSend={handleSend}
             sending={sending}
             useAgent={useAgent}
            />
            {error && <div className="toast-error">{error}</div>}
        </div>
    );    
}