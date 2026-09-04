export const BASE_URL = (import.meta.env.VITE_API_URL || "https://youtube-sage-backend.onrender.com").replace(/\/+$/, "");

// Default timeout: 120s for video loading (Render cold start + transcript + vectorstore), 60s for chat
const DEFAULT_TIMEOUT = 120_000;
const CHAT_TIMEOUT = 60_000;

async function fetchWithTimeout(url, options = {}, timeoutMs = DEFAULT_TIMEOUT) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    try {
        const res = await fetch(url, { ...options, signal: controller.signal });
        return res;
    } catch (err) {
        if (err.name === "AbortError") {
            throw new Error(
                `Request timed out after ${Math.round(timeoutMs / 1000)}s. The server may be cold-starting — try again in 30s.`
            );
        }
        throw err;
    } finally {
        clearTimeout(timer);
    }
}

async function handle(res) {
    if(!res.ok) {
        const body = await res.json().catch(()=>({}));
        throw new Error(body.detail || `Request failed: ${res.status}`);
    }
    return res.json();
}

export const api = {
    getConfig: () => fetchWithTimeout(`${BASE_URL}/api/config`).then(handle),

    loadVideo: (video_url,provider,model_name) =>
        fetchWithTimeout(`${BASE_URL}/api/session/load`, {
            method : "POST",
            headers : {"Content-Type": "application/json" },
            body : JSON.stringify({video_url,provider,model_name }),
        }).then(handle),

    chat:(session_id,question,use_agent) => 
        fetchWithTimeout(`${BASE_URL}/api/chat`, {
            method : "POST",
            headers : {"Content-Type":"application/json"},
            body: JSON.stringify({session_id,question,use_agent}),
        }, CHAT_TIMEOUT).then(handle),

    clearSession : (session_id) =>
        fetchWithTimeout(`${BASE_URL}/api/session/clear`,{
            method:"POST",
            headers : {"Content-Type":"application/json"},
            body:JSON.stringify({session_id}),
        }).then(handle),

    verifyGoogleToken: (id_token) =>
        fetchWithTimeout(`${BASE_URL}/api/auth/google`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id_token }),
        }).then(handle),

};