import { useState, useEffect, useRef } from "react";

const HexGrid = () => (
  <svg
    style={{
      position: "absolute", inset: 0, width: "100%", height: "100%",
      opacity: 0.07, pointerEvents: "none"
    }}
    xmlns="http://www.w3.org/2000/svg"
  >
    <defs>
      <pattern id="hex" x="0" y="0" width="56" height="48" patternUnits="userSpaceOnUse">
        <polygon
          points="14,2 42,2 56,24 42,46 14,46 0,24"
          fill="none" stroke="#00e5ff" strokeWidth="0.8"
        />
      </pattern>
    </defs>
    <rect width="100%" height="100%" fill="url(#hex)" />
  </svg>
);

const NodeNetwork = () => {
  const nodes = [
    { x: 75, y: 30 }, { x: 85, y: 55 }, { x: 90, y: 20 },
    { x: 70, y: 70 }, { x: 95, y: 40 }, { x: 80, y: 80 },
  ];
  const edges = [[0,1],[1,3],[0,4],[4,1],[2,4],[3,5],[1,5]];
  return (
    <svg style={{ position:"absolute", inset:0, width:"100%", height:"100%", opacity:0.15, pointerEvents:"none" }}>
      {edges.map(([a,b],i) => (
        <line key={i}
          x1={`${nodes[a].x}%`} y1={`${nodes[a].y}%`}
          x2={`${nodes[b].x}%`} y2={`${nodes[b].y}%`}
          stroke="#00e5ff" strokeWidth="0.5"
        />
      ))}
      {nodes.map((n,i) => (
        <circle key={i} cx={`${n.x}%`} cy={`${n.y}%`} r="2.5" fill="#00e5ff" />
      ))}
    </svg>
  );
};

const BOOT_LINES = [
  { text: "[21:04] SYSTEM: Initializing MechForge AI...", color: "#c8d8e0", delay: 0 },
  { text: "> AI Assistant Ready", color: "#00e5ff", delay: 600 },
  { text: "Model: qwen2.5:3b", color: "#00e5ff", label: "Model", delay: 1000 },
  { text: "RAG Status: Active", color: "#00e5ff", label: "RAG Status", delay: 1200 },
  { text: "API: Ollama", color: "#00e5ff", label: "API", delay: 1400 },
  { text: "Memory: 42 KB", color: "#00e5ff", label: "Memory", delay: 1600 },
  { text: "Awaiting input...", color: "#c8d8e0", delay: 2000 },
];

const BootLine = ({ line, visible }) => {
  if (!visible) return null;
  const parts = line.text.split(": ");
  const isLabeled = parts.length === 2 && line.label;
  return (
    <div style={{ fontFamily: "'Courier New', monospace", fontSize: 14, lineHeight: "1.8", color: "#c8d8e0" }}>
      {isLabeled ? (
        <>
          <span style={{ color: "#c8d8e0" }}>{parts[0]}: </span>
          <span style={{ color: "#00e5ff" }}>{parts[1]}</span>
        </>
      ) : (
        <span style={{ color: line.color }}>{line.text}</span>
      )}
    </div>
  );
};

const icons = [
  {
    id: "assistant", label: "AI\nAssistant", active: true,
    svg: <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><circle cx="9" cy="10" r="1.5" fill="currentColor"/><circle cx="15" cy="10" r="1.5" fill="currentColor"/></svg>
  },
  {
    id: "shield", label: "",
    svg: <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M12 2L4 6v6c0 5.25 3.75 10.15 8 11 4.25-.85 8-5.75 8-11V6l-8-4z"/></svg>
  },
  {
    id: "doc", label: "",
    svg: <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="1.5"><rect x="4" y="3" width="12" height="16" rx="1"/><path d="M8 7h8M8 11h6M8 15h4"/><path d="M14 3v4h4"/></svg>
  },
  {
    id: "scan", label: "",
    svg: <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M4 6V4h4M20 6V4h-4M4 18v2h4M20 18v2h-4M3 12h18"/></svg>
  },
  {
    id: "plugin", label: "",
    svg: <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="1.5"><rect x="3" y="3" width="8" height="8" rx="1"/><rect x="13" y="3" width="8" height="8" rx="1"/><rect x="3" y="13" width="8" height="8" rx="1"/><rect x="13" y="13" width="8" height="8" rx="1"/></svg>
  },
  {
    id: "db", label: "",
    svg: <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="1.5"><ellipse cx="12" cy="6" rx="8" ry="3"/><path d="M4 6v6c0 1.66 3.58 3 8 3s8-1.34 8-3V6"/><path d="M4 12v6c0 1.66 3.58 3 8 3s8-1.34 8-3v-6"/></svg>
  },
];

export default function MechForgeUI() {
  const [visibleLines, setVisibleLines] = useState([]);
  const [activeIcon, setActiveIcon] = useState("assistant");
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [blinkOn, setBlinkOn] = useState(true);
  const [booted, setBooted] = useState(false);
  const outputRef = useRef(null);

  useEffect(() => {
    BOOT_LINES.forEach((line, i) => {
      setTimeout(() => {
        setVisibleLines(prev => [...prev, i]);
        if (i === BOOT_LINES.length - 1) setBooted(true);
      }, line.delay);
    });
  }, []);

  useEffect(() => {
    const t = setInterval(() => setBlinkOn(b => !b), 530);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    if (outputRef.current) outputRef.current.scrollTop = outputRef.current.scrollHeight;
  }, [messages, visibleLines]);

  const handleSend = () => {
    if (!input.trim()) return;
    const now = new Date();
    const time = `[${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}]`;
    setMessages(prev => [...prev, { type: "user", text: input, time }]);
    const query = input;
    setInput("");
    setTimeout(() => {
      setMessages(prev => [...prev, {
        type: "ai", time,
        text: `Processing query: "${query}"\n> Analysis complete. RAG retrieval active.\nResponse generated by qwen2.5:3b.`
      }]);
    }, 800);
  };

  return (
    <div style={{
      width: "100vw", height: "100vh", background: "#0a0e14",
      display: "flex", alignItems: "center", justifyContent: "center",
      fontFamily: "'Courier New', monospace",
    }}>
      {/* Window */}
      <div style={{
        width: 900, height: 620, borderRadius: 8,
        background: "#0d1117", border: "1px solid #1e2d3d",
        boxShadow: "0 0 60px rgba(0,229,255,0.08), 0 20px 60px rgba(0,0,0,0.6)",
        display: "flex", flexDirection: "column", overflow: "hidden",
        position: "relative",
      }}>
        {/* Title Bar */}
        <div style={{
          height: 44, background: "#0d1117", borderBottom: "1px solid #1a2535",
          display: "flex", alignItems: "center", paddingInline: 16, gap: 10,
          flexShrink: 0,
        }}>
          <div style={{
            width: 28, height: 28, borderRadius: 6,
            background: "linear-gradient(135deg, #00b8d4, #0097a7)",
            display: "flex", alignItems: "center", justifyContent: "center",
          }}>
            <svg viewBox="0 0 20 20" width="16" height="16" fill="white">
              <path d="M10 2a8 8 0 100 16A8 8 0 0010 2zm0 3l2 4h4l-3 3 1 4-4-2-4 2 1-4-3-3h4z"/>
            </svg>
          </div>
          <span style={{ color: "#c8d8e0", fontSize: 14, fontWeight: 600, letterSpacing: 1 }}>MechForge AI</span>
          <span style={{ color: "#3a5068", fontSize: 12 }}>v0.5.0</span>
          <div style={{ marginLeft: "auto", display: "flex", gap: 12 }}>
            {["−","□","×"].map((ch,i) => (
              <div key={i} style={{
                width: 20, height: 20, display:"flex", alignItems:"center", justifyContent:"center",
                color: "#3a5068", cursor: "pointer", fontSize: 14,
                transition: "color 0.2s",
              }}
              onMouseEnter={e => e.target.style.color = "#00e5ff"}
              onMouseLeave={e => e.target.style.color = "#3a5068"}
              >{ch}</div>
            ))}
          </div>
        </div>

        {/* Body */}
        <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
          {/* Sidebar */}
          <div style={{
            width: 68, background: "#0a0e14", borderRight: "1px solid #1a2535",
            display: "flex", flexDirection: "column", alignItems: "center",
            paddingTop: 12, gap: 4, flexShrink: 0,
          }}>
            {icons.map(icon => (
              <div key={icon.id}
                onClick={() => setActiveIcon(icon.id)}
                style={{
                  width: 52, minHeight: 52, borderRadius: 8,
                  display: "flex", flexDirection: "column", alignItems: "center",
                  justifyContent: "center", cursor: "pointer",
                  background: activeIcon === icon.id
                    ? "linear-gradient(135deg, #00b8d4 0%, #0097a7 100%)"
                    : "transparent",
                  color: activeIcon === icon.id ? "#fff" : "#3a6070",
                  transition: "all 0.2s",
                  fontSize: 9, fontFamily: "sans-serif", textAlign: "center",
                  whiteSpace: "pre", lineHeight: 1.2, paddingBlock: 6,
                  boxShadow: activeIcon === icon.id ? "0 0 16px rgba(0,229,255,0.3)" : "none",
                }}
                onMouseEnter={e => { if (activeIcon !== icon.id) e.currentTarget.style.color = "#00e5ff"; }}
                onMouseLeave={e => { if (activeIcon !== icon.id) e.currentTarget.style.color = "#3a6070"; }}
              >
                {icon.svg}
                {icon.label && <span style={{ marginTop: 3 }}>{icon.label}</span>}
              </div>
            ))}
          </div>

          {/* Main panel */}
          <div style={{
            flex: 1, display: "flex", flexDirection: "column",
            position: "relative", background: "#0d1117",
          }}>
            <HexGrid />
            <NodeNetwork />

            {/* Output area */}
            <div ref={outputRef} style={{
              flex: 1, padding: "20px 24px", overflowY: "auto",
              position: "relative", zIndex: 1,
              scrollbarWidth: "thin", scrollbarColor: "#1a2535 transparent",
            }}>
              {BOOT_LINES.map((line, i) => (
                <BootLine key={i} line={line} visible={visibleLines.includes(i)} />
              ))}

              {/* Separator */}
              {booted && (
                <div style={{ height: 1, background: "linear-gradient(90deg, #00e5ff33, transparent)", marginBlock: 12 }} />
              )}

              {/* Chat messages */}
              {messages.map((msg, i) => (
                <div key={i} style={{ marginBottom: 8 }}>
                  {msg.type === "user" ? (
                    <div style={{ color: "#c8d8e0", fontSize: 14 }}>
                      <span style={{ color: "#3a6070" }}>{msg.time} </span>
                      <span style={{ color: "#00e5ff" }}>&gt; </span>
                      {msg.text}
                    </div>
                  ) : (
                    <div style={{ color: "#8ab4c8", fontSize: 14, paddingLeft: 16, borderLeft: "2px solid #00e5ff33" }}>
                      {msg.text.split("\n").map((l, j) => (
                        <div key={j} style={{ lineHeight: 1.7 }}>
                          {l.startsWith(">") ? <span style={{ color: "#00e5ff" }}>{l}</span> : l}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}

              {/* Blinking cursor */}
              {booted && (
                <div style={{
                  display: "inline-block", width: 8, height: 14,
                  background: blinkOn ? "#00e5ff" : "transparent",
                  marginTop: 4, verticalAlign: "middle",
                  transition: "background 0.1s",
                }} />
              )}
            </div>

            {/* Input */}
            <div style={{
              padding: "10px 16px", borderTop: "1px solid #1a2535",
              position: "relative", zIndex: 1,
            }}>
              <div style={{
                display: "flex", gap: 10, alignItems: "center",
                background: "#111820", borderRadius: 24,
                border: "1px solid #1e2d3d", padding: "6px 6px 6px 16px",
              }}>
                <input
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={e => e.key === "Enter" && handleSend()}
                  placeholder="Type your query here..."
                  style={{
                    flex: 1, background: "transparent", border: "none", outline: "none",
                    color: "#c8d8e0", fontFamily: "'Courier New', monospace", fontSize: 13,
                    caretColor: "#00e5ff",
                  }}
                />
                <button
                  onClick={handleSend}
                  style={{
                    padding: "8px 20px", borderRadius: 20, border: "none", cursor: "pointer",
                    background: "linear-gradient(135deg, #00b8d4, #0097a7)",
                    color: "#fff", fontFamily: "sans-serif", fontSize: 13, fontWeight: 600,
                    display: "flex", alignItems: "center", gap: 6,
                    boxShadow: "0 0 12px rgba(0,183,212,0.4)",
                    transition: "all 0.2s",
                  }}
                  onMouseEnter={e => e.currentTarget.style.boxShadow = "0 0 20px rgba(0,229,255,0.6)"}
                  onMouseLeave={e => e.currentTarget.style.boxShadow = "0 0 12px rgba(0,183,212,0.4)"}
                >
                  <svg viewBox="0 0 24 24" width="14" height="14" fill="white"><path d="M2 21l21-9L2 3v7l15 2-15 2z"/></svg>
                  Send
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Status Bar */}
        <div style={{
          height: 32, background: "#080c10", borderTop: "1px solid #1a2535",
          display: "flex", alignItems: "center", paddingInline: 16, gap: 0,
          fontSize: 11, color: "#3a6070", flexShrink: 0,
        }}>
          <span style={{ color: "#00b8d4", marginRight: 12, fontWeight: 700 }}>? MechForge</span>
          {[
            ["API", "Ollama"],
            ["Model", "qwen2.5:3b"],
            ["RAG", "ON", "#00e5ff"],
            ["Memory", "42 KB"],
          ].map(([k, v, vc], i) => (
            <span key={i} style={{ marginRight: 12 }}>
              | <span style={{ color: "#3a6070" }}>{k}: </span>
              <span style={{ color: vc || "#3a6070" }}>{v}</span>
            </span>
          ))}
          <div style={{ marginLeft: "auto", display: "flex", gap: 10, color: "#3a5068" }}>
            {["◇","≡","+","○"].map((s,i) => <span key={i} style={{ cursor:"pointer" }}>{s}</span>)}
          </div>
        </div>
      </div>
    </div>
  );
}
