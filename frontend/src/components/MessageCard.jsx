import React from "react";

export default function MessageCard({ role, content, keyPoints, confidence, timestamp }) {
  const isUser = role === "user";

  if (isUser) {
    return (
      <div className="flex flex-col gap-2 max-w-[80%] ml-auto items-end mb-6">
        <div className="flex items-center gap-2 flex-row-reverse">
          <div className="w-6 h-6 bg-secondary rounded flex items-center justify-center">
            <span className="material-symbols-outlined text-white text-[14px]">person</span>
          </div>
          <span className="font-label-technical text-[12px] font-bold text-secondary">ROOT_ADMIN</span>
          {timestamp && (
            <span className="font-label-technical text-[10px] text-on-surface-variant opacity-60">{timestamp}</span>
          )}
        </div>
        <div className="bg-secondary text-on-secondary p-4 rounded-l-xl rounded-b-xl border-b-4 border-r-4 border-primary">
          <p className="font-body-md text-xs italic whitespace-pre-wrap">{content}</p>
        </div>
      </div>
    );
  }

  // AI Response Styling
  return (
    <div className="flex flex-col gap-2 max-w-[85%] mb-6">
      {/* Bot Header */}
      <div className="flex items-center gap-2">
        <div className="w-6 h-6 bg-primary rounded flex items-center justify-center">
          <span className="material-symbols-outlined text-white text-[14px]" style={{ fontVariationSettings: "'FILL' 1" }}>smart_toy</span>
        </div>
        <span className="font-label-technical text-[12px] font-bold text-primary">SAGE_AI</span>
        {timestamp && (
          <span className="font-label-technical text-[10px] text-on-surface-variant opacity-60">{timestamp}</span>
        )}
        {confidence && (
          <span className="bg-primary-container/10 text-primary px-2 py-0.5 font-label-technical text-[8px] rounded border border-primary-container/30 uppercase">
            Confidence: {confidence}
          </span>
        )}
      </div>

      {/* Bot Content Box */}
      <div className="bg-surface-container-low p-5 tech-border border-l-4 border-l-primary rounded-r-xl">
        <p className="font-body-md text-xs text-on-surface whitespace-pre-wrap leading-relaxed">
          {content}
        </p>

        {/* Key Insights Grid */}
        {keyPoints && keyPoints.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-4 pt-4 border-t border-outline-variant">
            {keyPoints.map((point, i) => (
              <div key={i} className="p-3 bg-white border-l-4 border-l-secondary tech-border">
                <h4 className="font-label-technical text-[9px] text-secondary font-black mb-1 uppercase">
                  Insight {i + 1}
                </h4>
                <p className="font-label-technical text-[10px] text-on-surface-variant font-medium">
                  {point}
                </p>
              </div>
            ))}
          </div>
        )}

      </div>
    </div>
  );
}