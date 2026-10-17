import React from "react";
import ReactMarkdown from "react-markdown";

function CodeBlock({ children, className }) {
  const [copied, setCopied] = React.useState(false);
  const match = /language-(\w+)/.exec(className || "");
  const language = match ? match[1] : "code";
  const codeText = String(children).replace(/\n$/, "");

  const handleCopy = () => {
    if (navigator?.clipboard?.writeText) {
      navigator.clipboard.writeText(codeText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="my-3 rounded overflow-hidden tech-border bg-[#101719] text-[#e0e8e8] shadow-sm">
      <div className="flex items-center justify-between px-3 py-1.5 bg-[#1b2326] border-b border-[#2d3a3d] text-[10px] font-label-technical">
        <span className="uppercase tracking-wider text-primary font-bold">{language}</span>
        <button
          type="button"
          onClick={handleCopy}
          className="flex items-center gap-1 text-[10px] text-[#93a2a5] hover:text-white transition-colors cursor-pointer"
          title="Copy code to clipboard"
        >
          <span className="material-symbols-outlined text-[13px]">{copied ? "check" : "content_copy"}</span>
          <span>{copied ? "Copied!" : "Copy"}</span>
        </button>
      </div>
      <pre className="p-3 overflow-x-auto font-label-technical text-xs leading-relaxed m-0 bg-transparent text-[#e0e8e8]">
        <code>{codeText}</code>
      </pre>
    </div>
  );
}

export default function MessageCard({ role, content, keyPoints, confidence, timestamp, onSeek }) {
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

  // Pre-process markdown to convert timestamp citations like [02:15] to markdown links
  const processedContent = (content || "").replace(/\[(\d{1,2}):(\d{2})(?::(\d{2}))?\]/g, (match, p1, p2, p3) => {
    let totalSec = 0;
    if (p3 !== undefined) {
      totalSec = parseInt(p1, 10) * 3600 + parseInt(p2, 10) * 60 + parseInt(p3, 10);
    } else {
      totalSec = parseInt(p1, 10) * 60 + parseInt(p2, 10);
    }
    return `[${match}](#seek=${totalSec})`;
  });

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
        <div className="font-body-md text-xs text-on-surface leading-relaxed space-y-2 prose prose-sm max-w-none">
          <ReactMarkdown
            components={{
              a: ({ href, children, ...props }) => {
                if (href && href.startsWith("#seek=")) {
                  const seconds = parseInt(href.replace("#seek=", ""), 10);
                  return (
                    <button
                      type="button"
                      onClick={(e) => {
                        e.preventDefault();
                        if (onSeek) onSeek(seconds);
                      }}
                      className="inline-flex items-center gap-1 mx-1 px-1.5 py-0.5 rounded bg-primary/10 text-primary border border-primary/30 font-label-technical text-[10px] font-bold hover:bg-primary hover:text-white transition-all cursor-pointer"
                      title={`Jump to ${children} in video`}
                    >
                      <span className="material-symbols-outlined text-[11px]">play_circle</span>
                      {children}
                    </button>
                  );
                }
                return <a href={href} target="_blank" rel="noopener noreferrer" className="text-primary underline font-semibold" {...props}>{children}</a>;
              },
              code: ({ node, inline, className, children, ...props }) => {
                const isBlock = Boolean(className) || String(children).includes("\n");
                if (isBlock) {
                  return <CodeBlock className={className}>{children}</CodeBlock>;
                }
                return (
                  <code className="bg-surface-container-high px-1.5 py-0.5 rounded font-label-technical text-[11px] text-secondary font-semibold" {...props}>
                    {children}
                  </code>
                );
              }
            }}
          >
            {processedContent}
          </ReactMarkdown>
        </div>

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