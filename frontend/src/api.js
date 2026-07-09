const BASE_URL = "https://localhost:8000"

async function handle(res) {
    if(!res.ok) {
        const body = await res.json().catch(()=>({}));
        throw new Error(body.detail || `Request failed: ${res.status}`);
    }
    return res.json();
}

export const api = {
    getConfig: () => fetch(`${BASE_URL}/api/config`).then(handle),

    loadVideo: (video_url,provider,model_name) =>
        fetch(`${BASE_URL}/api/session/load`, {
            method : "POST",
            headers : {"Content-Type": "application/json" },
            body : JSON.stringify({video_url,provider,model_name }),
        }).then(handle),

    chat:(session_id,question,use_agent) => 
        fetch(`{BASE_URL}/api/chat`,{
            method : "POST",
            headers = {"Content-Type":"application/json"},
            body: JSON.stringify({session_id,question,use_agent}),
        }).then(handle),

    clearSession : (session_id) =>
        fetch(`{BASE_URL}/api/session/clear`,{
            method:"POST",
            headers : {"Content-Type":"application/json"},
            body:JSON.stringify({session_id}),
        }).then(handle),

};