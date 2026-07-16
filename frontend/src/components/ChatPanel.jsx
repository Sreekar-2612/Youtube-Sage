import React, { useEffect, useRef, useState } from "react";
import MessageCard from "./MessageCard.jsx";
import TurnDivider from "./TurnDivider.jsx";

export default function ChatPanel({ session, messages, onSend, sending, useAgent }) {
  const [input, setInput] = useState("");
  const scrollRef = useRef(null);
  const dockRef = useRef(null);

  // Position and Drag States
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ offsetX: 0, offsetY: 0 });
  const [hasDragged, setHasDragged] = useState(false);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  // Drag Event Handlers for Mouse
  const handleMouseDown = (e) => {
    if (e.button !== 0) return; // Left click only
    if (!e.target.classList.contains("drag-handle") && !e.target.closest(".drag-handle")) {
      return;
    }
    setIsDragging(true);
    const rect = dockRef.current.getBoundingClientRect();
    setDragStart({
      offsetX: e.clientX - rect.left,
      offsetY: e.clientY - rect.top,
    });
    e.preventDefault();
  };

  // Drag Event Handlers for Touch Devices
  const handleTouchStart = (e) => {
    if (!e.target.classList.contains("drag-handle") && !e.target.closest(".drag-handle")) {
      return;
    }
    const touch = e.touches[0];
    setIsDragging(true);
    const rect = dockRef.current.getBoundingClientRect();
    setDragStart({
      offsetX: touch.clientX - rect.left,
      offsetY: touch.clientY - rect.top,
    });
  };

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isDragging) return;
      const newX = e.clientX - dragStart.offsetX;
      const newY = e.clientY - dragStart.offsetY;
      setPosition({ x: newX, y: newY });
      setHasDragged(true);
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    const handleTouchMove = (e) => {
      if (!isDragging) return;
      const touch = e.touches[0];
      const newX = touch.clientX - dragStart.offsetX;
      const newY = touch.clientY - dragStart.offsetY;
      setPosition({ x: newX, y: newY });
      setHasDragged(true);
    };

    const handleTouchEnd = () => {
      setIsDragging(false);
    };

    if (isDragging) {
      document.addEventListener("mousemove", handleMouseMove);
      document.addEventListener("mouseup", handleMouseUp);
      document.addEventListener("touchmove", handleTouchMove, { passive: false });
      document.addEventListener("touchend", handleTouchEnd);
    }

    return () => {
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
      document.removeEventListener("touchmove", handleTouchMove);
      document.removeEventListener("touchend", handleTouchEnd);
    };
  }, [isDragging, dragStart]);

  function handleSubmit(e) {
    e.preventDefault();
    if (!input.trim() || sending) return;
    onSend(input.trim());
    setInput("");
  }

  if (!session) {
    return (
      <section className="bg-white tech-border rounded shadow-sm flex flex-col items-center justify-center p-8 h-[calc(100vh-140px)] text-center relative overflow-hidden">
        {/* Grid Background Overlay */}
        <div className="absolute inset-0 opacity-[0.03] pointer-events-none" style={{ backgroundImage: "radial-gradient(#000 1px, transparent 1px)", backgroundSize: "40px 40px" }}></div>
        
        <div className="max-w-md w-full p-8 border border-outline rounded bg-surface-container-low text-center space-y-4 relative z-10">
          <div className="w-12 h-12 border border-primary flex items-center justify-center mx-auto bg-white rounded-full">
            <span className="material-symbols-outlined text-primary text-xl">video_library</span>
          </div>
          <h2 className="font-headline-md text-base font-bold uppercase tracking-widest text-primary">No video loaded</h2>
          <p className="font-body-md text-xs text-on-surface-variant leading-relaxed uppercase tracking-wider">
            Paste a YouTube URL in the left card and load its transcript to start chatting.
          </p>
        </div>
      </section>
    );
  }

  let turn = 0;

  // Floating Draggable style properties
  const floatingStyle = hasDragged
    ? {
        position: "fixed",
        left: `${position.x}px`,
        top: `${position.y}px`,
        transform: "none",
        width: "90%",
        maxWidth: "768px",
      }
    : {
        position: "fixed",
        bottom: "32px",
        left: "50%",
        transform: "translateX(-50%)",
        width: "90%",
        maxWidth: "768px",
      };

  return (
    <section className="bg-white tech-border rounded shadow-sm flex flex-col h-[calc(100vh-140px)] relative overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-outline-variant bg-surface-container-low flex justify-between items-center">
        <h3 className="font-headline-md text-xs font-bold uppercase tracking-tight text-on-surface flex items-center gap-2">
          <span className="material-symbols-outlined text-primary text-sm">chat_bubble</span> {session?.title || "Neural Analysis Feed"}
        </h3>
        <div className="flex gap-2">
          <span className="bg-primary-container/10 text-primary px-3 py-1 font-label-technical text-[10px] rounded border border-primary-container/30 uppercase">
            {useAgent ? "Agent Active" : "High Confidence"}
          </span>
        </div>
      </div>

      {/* Main chat body scroll */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 relative z-10" ref={scrollRef}>
        <div className="space-y-6 pb-28">
          {/* Simple Date Header */}
          <div className="flex items-center gap-4 justify-center my-4 opacity-50">
            <div className="w-8 h-px bg-outline"></div>
            <span className="font-label-technical text-[10px] tracking-widest text-on-surface-variant uppercase font-semibold">
              {new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
            </span>
            <div className="w-8 h-px bg-outline"></div>
          </div>

          {/* Messages list */}
          {messages.length === 0 && (
            <div className="text-center p-6 border border-dashed border-outline-variant bg-surface-container-low rounded">
              <p className="text-xs uppercase tracking-widest text-on-surface-variant font-semibold">
                Transcript indexed successfully. Execute analysis commands below.
              </p>
            </div>
          )}

          {messages.map((m, i) => {
            const showDivider = m.role === "user";
            if (showDivider) turn += 1;
            return (
              <React.Fragment key={i}>
                {showDivider && <TurnDivider index={turn} />}
                <MessageCard
                  role={m.role}
                  content={m.content}
                  keyPoints={m.keyPoints}
                  confidence={m.confidence}
                  timestamp={m.timestamp}
                />
              </React.Fragment>
            );
          })}

          {/* Pending Response Indicator */}
          {sending && (
            <div className="flex flex-col gap-2 max-w-[85%] opacity-75 animate-pulse">
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 bg-primary rounded flex items-center justify-center">
                  <span className="material-symbols-outlined text-white text-[14px] animate-spin">sync</span>
                </div>
                <span className="font-label-technical text-[12px] font-bold text-primary">SAGE_AI</span>
              </div>
              <div className="bg-surface-container-low p-4 tech-border border-l-4 border-l-primary rounded-r-xl">
                <p className="font-body-md text-xs text-on-surface uppercase tracking-widest">
                  {useAgent ? "Deciding which tool to use..." : "Searching transcript..."}
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Floating Interaction Dock (Draggable Input Form) */}
      <form 
        onSubmit={handleSubmit} 
        ref={dockRef}
        style={floatingStyle}
        onMouseDown={handleMouseDown}
        onTouchStart={handleTouchStart}
        className="z-30 p-2 bg-white bg-opacity-95 border border-outline rounded-lg shadow-2xl flex items-center gap-2 focus-within:border-primary transition-all select-none"
      >
        {/* Drag Handle */}
        <div className="drag-handle flex items-center justify-center cursor-grab active:cursor-grabbing p-1.5 text-outline-variant hover:text-primary">
          <span className="material-symbols-outlined text-base">drag_indicator</span>
        </div>
        
        {/* Terminal Icon & Input */}
        <span className="material-symbols-outlined text-outline-variant">terminal</span>
        <input 
          className="flex-1 bg-transparent border-none focus:ring-0 font-label-technical text-xs uppercase tracking-widest placeholder:text-outline text-primary outline-none"
          placeholder="EXECUTE ANALYSIS COMMAND..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={sending}
        />
        
        <button 
          type="submit" 
          className="bg-primary text-on-primary px-6 py-2 font-button-text text-xs uppercase rounded flex items-center gap-2 hard-shadow-hover transition-all font-bold disabled:opacity-40"
          disabled={sending || !input.trim()}
        >
          Send <span className="material-symbols-outlined text-sm">send</span>
        </button>
      </form>
    </section>
  );
}