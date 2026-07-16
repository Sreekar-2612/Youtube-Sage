import React , { useEffect , useState } from "react";
import Sidebar from "./components/Sidebar.jsx";
import EngineConfig from "./components/EngineConfig.jsx";
import ChatPanel from "./components/ChatPanel.jsx";
import { api } from "./api.js";
import "./App.css";

export default function App() {
    const [config, setConfig] = useState(null);
    const [provider,setProvider] = useState("groq");
    const [modelName , setModelName] = useState("");
    const [useAgent, setUseAgent] = useState(false);

    const [videoUrl , setVideoUrl] = useState("");
    const [session, setSession] = useState(null);
    const [loading , setLoading] = useState(false);
    const [error,setError] = useState(null);
    const [messages,setMessages] = useState([]);
    const [sending,setSending] = useState(false);

    // Dynamic metrics trackers
    const [lastLatency, setLastLatency] = useState(0);
    const [totalLatency, setTotalLatency] = useState(0);
    const [lastThroughput, setLastThroughput] = useState(0);
    const [queryCount, setQueryCount] = useState(0);

    // View, Swap & History state
    const [activeView, setActiveView] = useState("source"); // "source" | "history" | "metrics"
    const [isSwapped, setIsSwapped] = useState(false);
    const [history, setHistory] = useState([]);
    const [sessionMessages, setSessionMessages] = useState({});

    // Google Authentication state
    const [user, setUser] = useState(() => {
        const saved = localStorage.getItem("yt_sage_user");
        return saved ? JSON.parse(saved) : null;
    });
    const [googleClientId, setGoogleClientId] = useState("");

    useEffect(() =>{
        api
        .getConfig()
        .then((cfg)=> {
            setConfig(cfg);
            setModelName(Object.values(cfg.groq_models)[0]);
            if (cfg.google_client_id) {
                setGoogleClientId(cfg.google_client_id);
            }
        })
        .catch(() => setError("Couldn't reach the backend. Is it running on :8000?"));
    } , []);

    useEffect(() => {
        if (!user && googleClientId && window.google) {
            window.google.accounts.id.initialize({
                client_id: googleClientId,
                callback: handleCredentialResponse
            });
            window.google.accounts.id.renderButton(
                document.getElementById("google-signin-btn"),
                { theme: "outline", size: "large", width: 280 }
            );
        }
    }, [user, googleClientId]);

    async function handleCredentialResponse(response) {
        setError(null);
        try {
            const result = await api.verifyGoogleToken(response.credential);
            setUser(result);
            localStorage.setItem("yt_sage_user", JSON.stringify(result));
        } catch (e) {
            setError("Google login failed: " + e.message);
        }
    }

    function handleSignOut() {
        setUser(null);
        localStorage.removeItem("yt_sage_user");
        setSession(null);
        setMessages([]);
        setHistory([]);
        setSessionMessages({});
    }

    useEffect(() => {
        if(!config) return;
        const options = provider == "groq"? config.groq_models : config.hf_models;
        setModelName(Object.values(options)[0]);
    },[provider,config]);

    async function handleLoad() {
        setLoading(true);
        setError(null);
        setLastLatency(0);
        setTotalLatency(0);
        setLastThroughput(0);
        setQueryCount(0);
        try {
            const result = await api.loadVideo(videoUrl,provider,modelName);
            setSession(result);
            setMessages([]);

            // Add to stack history (most recent on top)
            const newHistoryItem = {
                session_id: result.session_id,
                video_id: result.video_id,
                title: result.title,
                num_chunks: result.num_chunks,
                date: new Date().toLocaleDateString('en-US', { day: 'numeric', month: 'short', year: 'numeric' }),
                time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false })
            };
            setHistory(prev => [newHistoryItem, ...prev]);
            setSessionMessages(prev => ({
                ...prev,
                [result.session_id]: []
            }));
        } catch(e) {
            setError(e.message);
        } finally{
            setLoading(false);
        }
    }

    async function handleSend(question) {
        const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
        const userMsg = { role: "user", content: question, timestamp };
        setMessages((prev) => {
            const nextMsgs = [...prev, userMsg];
            setSessionMessages(prevMap => ({
                ...prevMap,
                [session.session_id]: nextMsgs
            }));
            return nextMsgs;
        });

        setSending(true);
        setError(null);
        const startTime = Date.now();
        try{
            const result = await api.chat(session.session_id , question, useAgent);
            const endTime = Date.now();
            const elapsed = endTime - startTime;
            
            setLastLatency(elapsed);
            setTotalLatency((prev) => prev + elapsed);
            setQueryCount((prev) => prev + 1);

            // Compute throughput (est. 1.3 tokens per word)
            const words = result.answer.trim().split(/\s+/).length;
            const tokens = Math.max(1, Math.round(words * 1.3));
            const throughput = elapsed > 0 ? Math.round((tokens / (elapsed / 1000)) * 10) / 10 : 0;
            setLastThroughput(throughput);

            const botTimestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
            const botMsg = {
                role:"assistant",
                content : result.answer,
                keyPoints: result.key_points,
                confidence: result.confidence,
                timestamp: botTimestamp,
            };
            setMessages((prev) => {
                const nextMsgs = [...prev, botMsg];
                setSessionMessages(prevMap => ({
                    ...prevMap,
                    [session.session_id]: nextMsgs
                }));
                return nextMsgs;
            });
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
        setLastLatency(0);
        setTotalLatency(0);
        setLastThroughput(0);
        setQueryCount(0);
        setSessionMessages(prevMap => ({
            ...prevMap,
            [session.session_id]: []
        }));
    }

    const [pingStatus, setPingStatus] = useState("Idle"); // "Idle" | "Checking..." | "Online (Xms)" | "Offline"

    function handleSelectSession(histItem) {
        setSession({
            session_id: histItem.session_id,
            video_id: histItem.video_id,
            num_chunks: histItem.num_chunks,
            title: histItem.title
        });
        setVideoUrl(`https://www.youtube.com/watch?v=${histItem.video_id}`);
        setMessages(sessionMessages[histItem.session_id] || []);
        setActiveView("source"); // Swap view back to workspace
    }

    const handleSwapClick = (e) => {
        // Detect triple click
        if (e.detail === 3) {
            setIsSwapped(prev => !prev);
        }
    };

    function handleExportChat() {
        if (messages.length === 0) return;
        const title = session?.title || "yt_sage_chat";
        let content = `YT-Sage Chat Transcript - ${title}\n`;
        content += `Session ID: ${session?.session_id || "N/A"}\n`;
        content += `Generated on: ${new Date().toLocaleString()}\n`;
        content += `========================================================================\n\n`;
        
        messages.forEach(msg => {
            const roleName = msg.role === "user" ? "ROOT_ADMIN" : "SAGE_AI";
            content += `[${roleName}] (${msg.timestamp || ""})\n`;
            content += `------------------------------------------------------------------------\n`;
            content += `${msg.content}\n\n`;
            if (msg.keyPoints && msg.keyPoints.length > 0) {
                content += `Key Highlights:\n`;
                msg.keyPoints.forEach(pt => {
                    content += `- ${pt}\n`;
                });
                content += `\n`;
            }
            if (msg.confidence) {
                content += `Confidence: ${msg.confidence}\n\n`;
            }
            content += `========================================================================\n\n`;
        });
        
        const blob = new Blob([content], { type: "text/plain;charset=utf-8;" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("download", `${title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_transcript.txt`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    async function handleWipeMemoryClick() {
        if (!session) return;
        if (window.confirm("Are you sure you want to wipe this session's memory and chat history?")) {
            await handleClearMemory();
        }
    }

    async function handlePingServer() {
        setPingStatus("Checking...");
        const startTime = Date.now();
        try {
            const response = await fetch("http://127.0.0.1:8000/api/config");
            if (response.ok) {
                const latency = Date.now() - startTime;
                setPingStatus(`Online (${latency}ms)`);
                setTimeout(() => setPingStatus("Idle"), 3000);
            } else {
                setPingStatus("Offline");
                setTimeout(() => setPingStatus("Idle"), 3000);
            }
        } catch {
            setPingStatus("Offline");
            setTimeout(() => setPingStatus("Idle"), 3000);
        }
    }

    // Component Definition for left-column items
    const leftColumn = (
        <div 
            onClick={handleSwapClick}
            className="col-span-12 lg:col-span-4 flex flex-col gap-6 select-none cursor-pointer"
            title="Triple click anywhere here to swap sides"
        >
            {activeView === "source" ? (
                <>
                    <Sidebar
                      videoUrl={videoUrl}
                      setVideoUrl={setVideoUrl}
                      onLoad={handleLoad}
                      loading={loading}
                      session={session}
                      onClearMemory={handleClearMemory}
                    />
                    <EngineConfig
                      config={config}
                      provider={provider}
                      setProvider={setProvider}
                      modelName={modelName}
                      setModelName={setModelName}
                      useAgent={useAgent}
                      setUseAgent={setUseAgent}
                    />
                </>
            ) : activeView === "history" ? (
                <div className="bg-white tech-border p-6 rounded shadow-sm border-l-4 border-l-primary flex-1 flex flex-col min-h-[400px]">
                    <h2 className="font-headline-md text-base mb-4 flex items-center gap-2 text-primary">
                      <span className="material-symbols-outlined">history</span> SESSION HISTORY
                    </h2>
                    
                    {history.length === 0 ? (
                        <div className="flex-1 flex flex-col items-center justify-center text-center p-6 border border-dashed border-outline-variant bg-surface-container-low rounded">
                            <span className="material-symbols-outlined text-outline text-3xl mb-2">history</span>
                            <p className="font-label-technical text-xs text-on-surface-variant uppercase">No history sessions found</p>
                        </div>
                    ) : (
                        <div className="space-y-4 overflow-y-auto max-h-[500px] pr-1">
                            {history.map((item, index) => (
                                <div 
                                    key={item.session_id}
                                    onClick={() => handleSelectSession(item)}
                                    className={`p-4 rounded border cursor-pointer transition-all duration-200 ${
                                        session?.session_id === item.session_id 
                                            ? 'bg-surface-container-low border-primary border-l-4 border-l-primary-container shadow'
                                            : 'bg-white border-outline hover:border-primary-container'
                                    }`}
                                >
                                    <h3 className="font-headline-md text-xs font-bold text-primary line-clamp-1 mb-1">{item.title}</h3>
                                    <div className="flex justify-between items-center text-[9px] text-on-surface-variant opacity-75 font-label-technical">
                                        <span>{item.date} @ {item.time}</span>
                                        <span className="text-secondary font-semibold">ID: {item.session_id.slice(0, 6)}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            ) : (
                /* Metrics View */
                <div className="bg-white tech-border p-6 rounded shadow-sm border-l-4 border-l-primary flex-1 flex flex-col min-h-[400px]">
                    <h2 className="font-headline-md text-base mb-4 flex items-center gap-2 text-primary">
                      <span className="material-symbols-outlined">analytics</span> SESSION METRICS
                    </h2>
                    
                    {!session ? (
                        <div className="flex-1 flex flex-col items-center justify-center text-center p-6 border border-dashed border-outline-variant bg-surface-container-low rounded">
                            <span className="material-symbols-outlined text-outline text-3xl mb-2">analytics</span>
                            <p className="font-label-technical text-xs text-on-surface-variant uppercase">No active session metrics</p>
                        </div>
                    ) : (
                        <div className="space-y-4 font-label-technical text-xs text-on-surface-variant">
                            <div className="p-3 bg-surface-container-low border border-outline rounded">
                                <span className="text-[10px] text-secondary font-black uppercase">Chat Title</span>
                                <p className="font-headline-md text-xs font-bold text-primary mt-1 line-clamp-2">{session.title}</p>
                            </div>
                            
                            <div className="p-3 bg-surface-container-low border border-outline rounded">
                                <span className="text-[10px] text-secondary font-black uppercase">Session ID</span>
                                <p className="text-[10px] font-bold text-primary mt-1">{session.session_id}</p>
                            </div>

                            <div className="grid grid-cols-2 gap-3">
                                <div className="p-3 bg-surface-container-low border border-outline rounded text-center">
                                    <span className="text-[9px] font-bold uppercase text-on-surface-variant">Data Chunks</span>
                                    <span className="block text-xs font-black text-primary mt-1">{session.num_chunks}</span>
                                </div>
                                <div className="p-3 bg-surface-container-low border border-outline rounded text-center">
                                    <span className="text-[9px] font-bold uppercase text-on-surface-variant">Query Count</span>
                                    <span className="block text-xs font-black text-tertiary mt-1">{queryCount}</span>
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-3">
                                <div className="p-3 bg-surface-container-low border border-outline rounded text-center">
                                    <span className="text-[9px] font-bold uppercase text-on-surface-variant">Last Latency</span>
                                    <span className="block text-xs font-black text-secondary mt-1">{lastLatency || 0} ms</span>
                                </div>
                                <div className="p-3 bg-surface-container-low border border-outline rounded text-center">
                                    <span className="text-[9px] font-bold uppercase text-on-surface-variant">Total Time</span>
                                    <span className="block text-xs font-black text-primary mt-1">{totalLatency || 0} ms</span>
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-3">
                                <div className="p-3 bg-surface-container-low border border-outline rounded text-center">
                                    <span className="text-[9px] font-bold uppercase text-on-surface-variant">Avg Response</span>
                                    <span className="block text-xs font-black text-secondary mt-1">
                                        {queryCount > 0 ? Math.round(totalLatency / queryCount) : 0} ms
                                    </span>
                                </div>
                                <div className="p-3 bg-surface-container-low border border-outline rounded text-center">
                                    <span className="text-[9px] font-bold uppercase text-on-surface-variant">Throughput</span>
                                    <span className="block text-xs font-black text-primary mt-1">
                                        {lastThroughput || 0} t/s
                                    </span>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );

    // Component Definition for right-column chat
    const rightColumn = (
        <div 
            onClick={handleSwapClick}
            className="col-span-12 lg:col-span-8 flex flex-col gap-6 h-full select-none cursor-pointer"
            title="Triple click anywhere here to swap sides"
        >
            <ChatPanel
              session={session}
              messages={messages}
              onSend={handleSend}
              sending={sending}
              useAgent={useAgent}
            />
        </div>
    );

    if (!user) {
        return (
            <div className="w-screen h-screen flex items-center justify-center bg-background relative overflow-hidden select-none">
                {/* Background Decorative Tech Lines/Glows */}
                <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-primary/5 rounded-full filter blur-[120px]"></div>
                <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-secondary/5 rounded-full filter blur-[120px]"></div>
                
                <div className="bg-white tech-border border-t-8 border-t-primary p-10 max-w-md w-full shadow-2xl rounded text-center z-10">
                    <h1 className="font-display-lg text-3xl font-black text-primary tracking-wider uppercase mb-2">YouYap</h1>
                    <p className="font-label-technical text-xs text-on-surface-variant uppercase font-semibold mb-6">🔥 WAR-ZONE // SECURE GATEWAY</p>
                    
                    <div className="my-8 flex flex-col items-center justify-center p-6 border border-dashed border-outline-variant bg-surface-container-low rounded min-h-[140px]">
                        <span className="material-symbols-outlined text-4xl text-primary animate-pulse mb-3">lock_open</span>
                        <p className="font-label-technical text-[10px] text-on-surface-variant uppercase tracking-wider mb-6 text-center">
                            Authentication Required for Dashboard Access
                        </p>
                        
                        {googleClientId ? (
                            <div id="google-signin-btn" className="w-[280px] h-[40px] flex justify-center"></div>
                        ) : (
                            <div className="flex flex-col items-center gap-2">
                                <span className="text-[10px] text-secondary font-black uppercase text-xs">Configuration Missing</span>
                                <p className="font-body-md text-[11px] text-on-surface-variant leading-relaxed max-w-[240px]">
                                    Please add <code>GOOGLE_CLIENT_ID</code> to your backend <code>.env</code> file.
                                </p>
                            </div>
                        )}
                    </div>

                    <p className="text-[9px] text-on-surface-variant font-label-technical opacity-60 mt-4 leading-relaxed uppercase">
                        Authorized Personnel Only. Actions Are Logged.
                    </p>
                </div>

                {/* Styled Toast Error inside login */}
                {error && (
                    <div className="fixed bottom-6 right-6 bg-secondary text-on-secondary px-4 py-3 border border-secondary text-xs uppercase font-bold z-50 shadow-2xl">
                        {error}
                    </div>
                )}
            </div>
        );
    }

    return (
        <div className="flex h-screen w-screen overflow-hidden bg-background text-on-background font-body-md text-body-md">
            {/* Sidebar Navigation */}
            <aside className="hidden md:flex flex-col h-full p-4 gap-4 bg-surface border-r border-outline-variant w-64 z-50">
                <div className="px-4 py-6">
                    <h1 className="font-display-lg text-2xl font-black text-primary uppercase tracking-wider">YouYap</h1>
                    <p className="font-label-technical text-xs text-on-surface-variant opacity-70">V3.4 Stable</p>
                </div>
                <nav className="flex-1 flex flex-col gap-2">
                    {/* Navigation Links */}
                    <button 
                        onClick={() => setActiveView("source")}
                        className={`flex items-center gap-3 px-4 py-3 rounded border-2 transition-all w-full text-left outline-none ${
                            activeView === "source"
                                ? "bg-primary text-on-primary border-primary shadow-[4px_0px_0px_0px_rgba(184,19,17,1)]"
                                : "text-on-surface-variant border-transparent hover:bg-surface-variant"
                        }`}
                    >
                        <span className="material-symbols-outlined">video_library</span>
                        <span className="font-label-technical text-xs uppercase font-semibold">Source</span>
                    </button>
                    <button 
                        onClick={() => setActiveView("history")}
                        className={`flex items-center gap-3 px-4 py-3 rounded border-2 transition-all w-full text-left outline-none ${
                            activeView === "history"
                                ? "bg-primary text-on-primary border-primary shadow-[4px_0px_0px_0px_rgba(184,19,17,1)]"
                                : "text-on-surface-variant border-transparent hover:bg-surface-variant"
                        }`}
                    >
                        <span className="material-symbols-outlined">history</span>
                        <span className="font-label-technical text-xs uppercase font-semibold">History</span>
                    </button>
                    <button 
                        onClick={() => setActiveView("metrics")}
                        className={`flex items-center gap-3 px-4 py-3 rounded border-2 transition-all w-full text-left outline-none ${
                            activeView === "metrics"
                                ? "bg-primary text-on-primary border-primary shadow-[4px_0px_0px_0px_rgba(184,19,17,1)]"
                                : "text-on-surface-variant border-transparent hover:bg-surface-variant"
                        }`}
                    >
                        <span className="material-symbols-outlined">analytics</span>
                        <span className="font-label-technical text-xs uppercase font-semibold">Metrics</span>
                    </button>
                    <a className="flex items-center gap-3 px-4 py-3 text-on-surface-variant hover:bg-surface-variant transition-all rounded" href="#">
                        <span className="material-symbols-outlined">settings</span>
                        <span className="font-label-technical text-xs uppercase">Settings</span>
                    </a>
                </nav>
                <div className="mt-auto p-4 flex flex-col gap-4">
                    <button 
                        onClick={handleExportChat}
                        disabled={messages.length === 0}
                        className={`w-full font-button-text text-xs uppercase py-3 rounded border-2 transition-all duration-100 font-bold ${
                            messages.length === 0 
                                ? "bg-outline text-on-surface-variant cursor-not-allowed border-outline opacity-50"
                                : "bg-secondary text-on-secondary border-secondary hover:translate-y-[-2px] hover:shadow-[4px_4px_0px_0px_#00acc1] cursor-pointer"
                        }`}
                    >
                        Export Chat (.txt)
                    </button>
                    <div className="flex flex-col gap-2 border-t border-outline-variant pt-4">
                        <button 
                            onClick={handleWipeMemoryClick}
                            disabled={!session}
                            className={`flex items-center gap-3 px-4 py-2 font-label-technical text-xs transition-colors text-left outline-none ${
                                !session 
                                    ? "text-outline cursor-not-allowed opacity-50"
                                    : "text-on-surface-variant hover:text-secondary cursor-pointer"
                            }`}
                        >
                            <span className="material-symbols-outlined text-[16px]">delete_forever</span> Wipe Memory
                        </button>
                        <button 
                            onClick={handlePingServer}
                            className="flex items-center gap-3 px-4 py-2 text-on-surface-variant font-label-technical text-xs hover:text-primary transition-colors text-left outline-none cursor-pointer"
                        >
                            <span className="material-symbols-outlined text-[16px]">sensors</span> Ping Server
                            {pingStatus !== "Idle" && (
                                <span className={`ml-auto text-[8px] font-bold px-1.5 py-0.5 rounded border uppercase ${
                                    pingStatus.startsWith("Online") 
                                        ? "bg-green-100 border-green-300 text-green-700"
                                        : pingStatus === "Offline"
                                        ? "bg-red-100 border-red-300 text-secondary"
                                        : "bg-gray-100 border-gray-300 text-gray-500 animate-pulse"
                                }`}>
                                    {pingStatus}
                                </span>
                            )}
                        </button>
                    </div>
                </div>
            </aside>

            {/* Main Workspace Container */}
            <main className="flex-1 flex flex-col h-full bg-background overflow-hidden relative">
                {/* Top Navigation Bar */}
                <header className="flex justify-between items-center px-8 w-full h-16 border-b border-outline-variant bg-surface z-40">
                    <div className="flex items-center gap-4">
                        <span className="material-symbols-outlined text-primary">analytics</span>
                        <span className="font-display-lg text-lg font-black tracking-widest text-on-surface">🔥 WAR-ZONE // ACTIVE</span>
                    </div>
                    <div className="flex items-center gap-6">
                        <button className="material-symbols-outlined text-on-surface-variant hover:text-primary transition-colors">notifications</button>
                        <div className="flex items-center gap-3">
                            <img 
                                src={user?.picture} 
                                alt={user?.name} 
                                className="w-8 h-8 rounded-full border border-primary shadow-sm"
                                referrerPolicy="no-referrer"
                            />
                            <div className="hidden lg:flex flex-col text-left">
                                <span className="font-label-technical text-xs font-bold text-on-surface leading-none mb-0.5">{user?.name}</span>
                                <span className="font-label-technical text-[9px] text-on-surface-variant opacity-70 leading-none">{user?.email}</span>
                            </div>
                            <button 
                                onClick={handleSignOut}
                                className="material-symbols-outlined text-on-surface-variant hover:text-secondary transition-colors cursor-pointer ml-1 outline-none"
                                title="Sign Out"
                            >
                                logout
                            </button>
                        </div>
                    </div>
                </header>

                {/* Content Area */}
                <div className="flex-1 overflow-y-auto p-6 grid grid-cols-12 gap-6 transition-all duration-300">
                    {isSwapped ? rightColumn : leftColumn}
                    {isSwapped ? leftColumn : rightColumn}
                </div>

                {/* Styled Toast Error */}
                {error && (
                    <div className="fixed bottom-6 right-6 bg-secondary text-on-secondary px-4 py-3 border border-secondary text-xs uppercase font-bold z-50 shadow-2xl">
                        {error}
                    </div>
                )}
            </main>
        </div>
    );    
}