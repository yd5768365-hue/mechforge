import { useState, useEffect, useRef } from "react";

// ==========================================
// 背景装饰组件
// ==========================================
const HexGrid = () => (
  <svg
    style={{
      position: "absolute", inset: 0, width: "100%", height: "100%",
      opacity: 0.05, pointerEvents: "none"
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
    <svg style={{ position:"absolute", inset:0, width:"100%", height:"100%", opacity:0.12, pointerEvents:"none" }}>
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

// ==========================================
// 启动日志组件
// ==========================================
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

// ==========================================
// 知识库面板组件 (v3新增)
// ==========================================
const KnowledgeBasePanel = () => {
  const [searchText, setSearchText] = useState("");
  const [progress, setProgress] = useState(68);
  const [indexingSpeed, setIndexingSpeed] = useState("12.4 MB/s");

  const documents = [
    { name: "机械设计基础.pdf", type: "pdf", size: "8.2 MB", relevance: 98, date: "2025-12-18" },
    { name: "材料力学性能表.xlsx", type: "xlsx", size: "3.1 MB", relevance: 92, date: "2026-01-05" },
    { name: "齿轮设计手册 v2.3.docx", type: "docx", size: "14.7 MB", relevance: 85, date: "2025-11-30" },
    { name: "有限元分析案例集.pdf", type: "pdf", size: "21.4 MB", relevance: 79, date: "2026-02-14" },
    { name: "螺栓强度校核规范.pdf", type: "pdf", size: "5.6 MB", relevance: 71, date: "2025-10-22" },
  ];

  useEffect(() => {
    if (progress < 100) {
      const timer = setTimeout(() => {
        setProgress(p => Math.min(100, p + Math.random() * 8));
      }, 1800);
      return () => clearTimeout(timer);
    }
  }, [progress]);

  return (
    <div style={{
      flex: 1,
      display: "flex",
      flexDirection: "column",
      padding: "24px",
      position: "relative",
      zIndex: 1,
      overflow: "hidden",
    }}>
      {/* 搜索框 */}
      <div style={{ position: "relative", marginBottom: "24px" }}>
        <input
          type="text"
          value={searchText}
          onChange={e => setSearchText(e.target.value)}
          placeholder="搜索知识库中的文档、材料、标准、公式..."
          style={{
            width: "100%",
            padding: "14px 20px 14px 48px",
            background: "rgba(17, 24, 32, 0.7)",
            border: "1px solid rgba(0, 229, 255, 0.25)",
            borderRadius: "12px",
            color: "#e0f0ff",
            fontSize: "15px",
            outline: "none",
            transition: "all 0.25s",
            boxShadow: "0 0 0 0 rgba(0, 229, 255, 0.0)",
          }}
          onFocus={e => {
            e.target.style.boxShadow = "0 0 0 3px rgba(0, 229, 255, 0.25)";
            e.target.style.borderColor = "#00e5ff";
          }}
          onBlur={e => {
            e.target.style.boxShadow = "0 0 0 0 rgba(0, 229, 255, 0.0)";
            e.target.style.borderColor = "rgba(0, 229, 255, 0.25)";
          }}
        />
        <svg
          viewBox="0 0 24 24"
          width="20"
          height="20"
          fill="none"
          stroke="#00e5ff"
          strokeWidth="2"
          style={{
            position: "absolute",
            left: "16px",
            top: "50%",
            transform: "translateY(-50%)",
            opacity: 0.7,
          }}
        >
          <circle cx="11" cy="11" r="8" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
        {searchText && (
          <button
            onClick={() => setSearchText("")}
            style={{
              position: "absolute",
              right: "12px",
              top: "50%",
              transform: "translateY(-50%)",
              background: "none",
              border: "none",
              color: "#ff6b6b",
              cursor: "pointer",
              fontSize: "16px",
            }}
          >
            ×
          </button>
        )}
      </div>

      {/* 索引进度条 */}
      <div style={{
        marginBottom: "20px",
        padding: "12px 16px",
        background: "rgba(17, 24, 32, 0.5)",
        borderRadius: "10px",
        border: "1px solid rgba(0, 229, 255, 0.15)",
        boxShadow: "0 0 20px rgba(0, 229, 255, 0.08)",
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
          <span style={{ color: "#a0d0ff", fontSize: "14px" }}>正在构建/更新知识库索引...</span>
          <span style={{ color: "#00e5ff", fontWeight: 600 }}>{Math.round(progress)}%</span>
        </div>
        <div style={{
          height: "8px",
          background: "#1a2535",
          borderRadius: "4px",
          overflow: "hidden",
          boxShadow: "inset 0 1px 3px rgba(0,0,0,0.4)",
        }}>
          <div style={{
            height: "100%",
            width: `${progress}%`,
            background: "linear-gradient(90deg, #00b8d4, #00e5ff)",
            borderRadius: "4px",
            boxShadow: "0 0 12px rgba(0, 229, 255, 0.6)",
            transition: "width 1.2s ease-out",
          }} />
        </div>
        <div style={{
          marginTop: "6px",
          fontSize: "12px",
          color: "#88aaff",
          textAlign: "right",
        }}>
          速度: {indexingSpeed} · 已处理 1.8 GB / 预计剩余 2分14秒
        </div>
      </div>

      {/* 文档列表 */}
      <div style={{
        flex: 1,
        overflowY: "auto",
        paddingRight: "8px",
        scrollbarWidth: "thin",
        scrollbarColor: "#1a2535 #0d1117",
      }}>
        {documents.map((doc, i) => (
          <div
            key={i}
            style={{
              display: "flex",
              alignItems: "center",
              padding: "12px 16px",
              marginBottom: "8px",
              background: "rgba(20, 30, 40, 0.5)",
              borderRadius: "8px",
              border: "1px solid rgba(0, 229, 255, 0.12)",
              transition: "all 0.2s",
              cursor: "pointer",
            }}
            onMouseEnter={e => {
              e.currentTarget.style.borderColor = "#00e5ff";
              e.currentTarget.style.boxShadow = "0 0 16px rgba(0,229,255,0.25)";
            }}
            onMouseLeave={e => {
              e.currentTarget.style.borderColor = "rgba(0, 229, 255, 0.12)";
              e.currentTarget.style.boxShadow = "none";
            }}
          >
            {/* 文件图标 */}
            <div style={{
              width: 40,
              height: 48,
              background: doc.type === "pdf" ? "#ff5252" : doc.type === "xlsx" ? "#4caf50" : "#ffca28",
              borderRadius: "6px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "white",
              fontWeight: 700,
              fontSize: "12px",
              marginRight: "16px",
              flexShrink: 0,
            }}>
              {doc.type.toUpperCase()}
            </div>

            {/* 文件信息 */}
            <div style={{ flex: 1 }}>
              <div style={{ color: "#e0f0ff", fontSize: "15px", fontWeight: 500 }}>
                {doc.name}
              </div>
              <div style={{ color: "#88aaff", fontSize: "12px", marginTop: "4px" }}>
                {doc.size} · {doc.date} · 相关度 {doc.relevance}%
              </div>
            </div>

            {/* 相关度小条 */}
            <div style={{
              width: 60,
              height: 6,
              background: "#1a2535",
              borderRadius: "3px",
              overflow: "hidden",
              marginLeft: "16px",
            }}>
              <div style={{
                height: "100%",
                width: `${doc.relevance}%`,
                background: "linear-gradient(90deg, #00b8d4, #00e5ff)",
              }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// ==========================================
// 工具台面板组件 (v3新增)
// ==========================================
const WorkbenchPanel = () => {
  const [calcProgress, setCalcProgress] = useState(67);
  const [logs, setLogs] = useState([
    { level: "INFO", msg: "Reading STEP file: bracket_v2.step", time: "14:32:01" },
    { level: "INFO", msg: "Initializing Gmsh API...", time: "14:32:03" },
    { level: "INFO", msg: "Surface meshing completed", time: "14:32:15" },
    { level: "WARN", msg: "High aspect ratio detected at surface ID: 42", time: "14:32:28" },
    { level: "INFO", msg: "Volume meshing: 67%", time: "14:32:45" },
    { level: "INFO", msg: "Optimizing mesh quality...", time: "14:33:02" },
  ]);

  useEffect(() => {
    const timer = setInterval(() => {
      setCalcProgress(p => {
        if (p >= 100) return 0;
        return p + Math.random() * 2;
      });
    }, 2000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div style={{
      flex: 1,
      display: "flex",
      flexDirection: "column",
      padding: "24px",
      position: "relative",
      zIndex: 1,
    }}>
      {/* 工具栏 */}
      <div style={{ display: "flex", gap: "12px", marginBottom: "20px" }}>
        {["➕ 新建计算", "📂 导入几何", "🔲 网格划分", "▶ 求解分析"].map((label, i) => (
          <button
            key={i}
            style={{
              padding: "10px 20px",
              background: i === 0 ? "linear-gradient(135deg, #00b8d4, #0097a7)" : "rgba(0, 229, 255, 0.1)",
              border: "1px solid rgba(0, 229, 255, 0.3)",
              borderRadius: "8px",
              color: i === 0 ? "#fff" : "#00e5ff",
              fontSize: "13px",
              cursor: "pointer",
              transition: "all 0.2s",
            }}
            onMouseEnter={e => {
              e.target.style.boxShadow = "0 0 16px rgba(0,229,255,0.3)";
            }}
            onMouseLeave={e => {
              e.target.style.boxShadow = "none";
            }}
          >
            {label}
          </button>
        ))}
      </div>

      {/* 进度条 */}
      <div style={{
        marginBottom: "20px",
        padding: "12px 16px",
        background: "rgba(17, 24, 32, 0.5)",
        borderRadius: "10px",
        border: "1px solid rgba(0, 229, 255, 0.15)",
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
          <span style={{ color: "#a0d0ff", fontSize: "14px" }}>Gmsh 网格生成中...</span>
          <span style={{ color: "#00e5ff", fontWeight: 600 }}>{Math.round(calcProgress)}%</span>
        </div>
        <div style={{
          height: "8px",
          background: "#1a2535",
          borderRadius: "4px",
          overflow: "hidden",
        }}>
          <div style={{
            height: "100%",
            width: `${calcProgress}%`,
            background: "linear-gradient(90deg, #00b8d4, #00e5ff)",
            borderRadius: "4px",
            boxShadow: "0 0 12px rgba(0, 229, 255, 0.6)",
            transition: "width 0.5s ease-out",
          }} />
        </div>
        <div style={{ marginTop: "6px", fontSize: "12px", color: "#88aaff", textAlign: "right" }}>
          预计剩余 {Math.max(0, Math.round((100 - calcProgress) / 10))} 秒
        </div>
      </div>

      {/* 左右分栏 */}
      <div style={{ display: "flex", gap: "16px", flex: 1 }}>
        {/* 控制台日志 */}
        <div style={{
          width: "45%",
          background: "rgba(17, 24, 32, 0.5)",
          borderRadius: "10px",
          border: "1px solid rgba(0, 229, 255, 0.15)",
          padding: "16px",
          overflowY: "auto",
        }}>
          <div style={{ color: "#00e5ff", fontSize: "14px", fontWeight: 600, marginBottom: "12px" }}>
            📋 系统日志
          </div>
          {logs.map((log, i) => (
            <div key={i} style={{ marginBottom: "8px", fontSize: "12px" }}>
              <span style={{ color: "#5a7a8a" }}>[{log.time}]</span>
              <span style={{
                color: log.level === "WARN" ? "#ffca28" : log.level === "ERROR" ? "#ff5252" : "#00e5ff",
                marginLeft: "8px",
              }}>
                {log.level}
              </span>
              <span style={{ color: "#a0c0d0", marginLeft: "8px" }}>{log.msg}</span>
            </div>
          ))}
        </div>

        {/* 3D预览区 */}
        <div style={{
          flex: 1,
          background: "rgba(17, 24, 32, 0.5)",
          borderRadius: "10px",
          border: "1px solid rgba(0, 229, 255, 0.15)",
          padding: "16px",
          display: "flex",
          flexDirection: "column",
        }}>
          <div style={{ color: "#00e5ff", fontSize: "14px", fontWeight: 600, marginBottom: "12px" }}>
            🔮 3D 预览
          </div>
          <div style={{ flex: 1, position: "relative" }}>
            <svg width="100%" height="100%" style={{ position: "absolute", inset: 0 }}>
              {/* 网格背景 */}
              <defs>
                <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                  <path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(0,229,255,0.1)" strokeWidth="0.5"/>
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#grid)" />
              
              {/* 3D立方体线框 */}
              <g transform="translate(150, 100)">
                {/* 前面 */}
                <rect x="-40" y="-40" width="80" height="80" fill="none" stroke="#00e5ff" strokeWidth="2" />
                {/* 后面 */}
                <rect x="-20" y="-60" width="80" height="80" fill="none" stroke="#00b8d4" strokeWidth="1.5" opacity="0.6" />
                {/* 连接线 */}
                <line x1="-40" y1="-40" x2="-20" y2="-60" stroke="#00e5ff" strokeWidth="1" opacity="0.5" />
                <line x1="40" y1="-40" x2="60" y2="-60" stroke="#00e5ff" strokeWidth="1" opacity="0.5" />
                <line x1="-40" y1="40" x2="-20" y2="20" stroke="#00e5ff" strokeWidth="1" opacity="0.5" />
                <line x1="40" y1="40" x2="60" y2="20" stroke="#00e5ff" strokeWidth="1" opacity="0.5" />
              </g>
              
              {/* 统计信息 */}
              <text x="10" y="20" fill="#88aaff" fontSize="12">节点: 45,230</text>
              <text x="10" y="40" fill="#88aaff" fontSize="12">单元: 182,456</text>
              <text x="10" y="60" fill="#4caf50" fontSize="12">质量: 8.4/10</text>
            </svg>
          </div>
        </div>
      </div>
    </div>
  );
};

// ==========================================
// 侧边栏图标配置
// ==========================================
const icons = [
  {
    id: "assistant",
    label: "AI\n助手",
    svg: <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><circle cx="9" cy="10" r="1.5" fill="currentColor"/><circle cx="15" cy="10" r="1.5" fill="currentColor"/></svg>
  },
  {
    id: "knowledge",
    label: "知识库\nKB",
    svg: <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M4 19.5v-15A2.5 2.5 0 016.5 2H20v20H6.5A2.5 2.5 0 014 19.5z"/><path d="M8 7h8M8 11h6M8 15h4"/></svg>
  },
  {
    id: "workbench",
    label: "工具台\nCAE",
    svg: <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="1.5"><rect x="2" y="3" width="20" height="6" rx="1"/><rect x="2" y="15" width="20" height="6" rx="1"/><line x1="6" y1="9" x2="6" y2="15"/><line x1="10" y1="9" x2="10" y2="15"/><line x1="14" y1="9" x2="14" y2="15"/><line x1="18" y1="9" x2="18" y2="15"/></svg>
  },
  {
    id: "shield",
    label: "安全",
    svg: <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M12 2L4 6v6c0 5.25 3.75 10.15 8 11 4.25-.85 8-5.75 8-11V6l-8-4z"/></svg>
  },
  {
    id: "db",
    label: "数据库",
    svg: <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="1.5"><ellipse cx="12" cy="6" rx="8" ry="3"/><path d="M4 6v6c0 1.66 3.58 3 8 3s8-1.34 8-3V6"/><path d="M4 12v6c0 1.66 3.58 3 8 3s8-1.34 8-3v-6"/></svg>
  },
  {
    id: "settings",
    label: "设置",
    svg: <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="1.5"><circle cx="12" cy="12" r="3"/><path d="M12 1v6m0 6v6m4.22-10.22l4.24-4.24M6.34 6.34L2.1 2.1m17.8 17.8l-4.24-4.24M6.34 17.66l-4.24 4.24M23 12h-6m-6 0H1m20.24-4.24l-4.24 4.24M6.34 6.34l-4.24-4.24"/></svg>
  },
];

// ==========================================
// 主组件
// ==========================================
export default function MechForgeUI() {
  const [visibleLines, setVisibleLines] = useState([]);
  const [activeIcon, setActiveIcon] = useState("assistant");
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [blinkOn, setBlinkOn] = useState(true);
  const [booted, setBooted] = useState(false);
  const outputRef = useRef(null);

  // 启动动画
  useEffect(() => {
    BOOT_LINES.forEach((line, i) => {
      setTimeout(() => {
        setVisibleLines(prev => [...prev, i]);
        if (i === BOOT_LINES.length - 1) setBooted(true);
      }, line.delay);
    });
  }, []);

  // 光标闪烁
  useEffect(() => {
    const t = setInterval(() => setBlinkOn(b => !b), 530);
    return () => clearInterval(t);
  }, []);

  // 自动滚动
  useEffect(() => {
    if (outputRef.current) outputRef.current.scrollTop = outputRef.current.scrollHeight;
  }, [messages, visibleLines]);

  // 发送消息
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
      {/* 主窗口 */}
      <div style={{
        width: 1000, height: 700, borderRadius: 12,
        background: "#0d1117", border: "1px solid #1e2d3d",
        boxShadow: "0 0 60px rgba(0,229,255,0.08), 0 20px 60px rgba(0,0,0,0.6)",
        display: "flex", flexDirection: "column", overflow: "hidden",
        position: "relative",
      }}>
        {/* 标题栏 */}
        <div style={{
          height: 48, background: "#0d1117", borderBottom: "1px solid #1a2535",
          display: "flex", alignItems: "center", paddingInline: 20, gap: 12,
          flexShrink: 0,
        }}>
          <div style={{
            width: 32, height: 32, borderRadius: 8,
            background: "linear-gradient(135deg, #00b8d4, #0097a7)",
            display: "flex", alignItems: "center", justifyContent: "center",
          }}>
            <svg viewBox="0 0 24 24" width="18" height="18" fill="white">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
            </svg>
          </div>
          <span style={{ color: "#c8d8e0", fontSize: 16, fontWeight: 600 }}>MechForge AI</span>
          <span style={{ color: "#3a5068", fontSize: 13 }}>v0.6.0</span>
          
          <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
            {["−","□","×"].map((ch,i) => (
              <div key={i} style={{
                width: 24, height: 24, display:"flex", alignItems:"center", justifyContent:"center",
                color: "#3a5068", cursor: "pointer", fontSize: 14,
                borderRadius: 4,
                transition: "all 0.2s",
              }}
              onMouseEnter={e => { e.target.style.color = "#00e5ff"; e.target.style.background = "rgba(0,229,255,0.1)"; }}
              onMouseLeave={e => { e.target.style.color = "#3a5068"; e.target.style.background = "transparent"; }}
              >{ch}</div>
            ))}
          </div>
        </div>

        {/* 主体 */}
        <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
          {/* 侧边栏 */}
          <div style={{
            width: 72, background: "#0a0e14", borderRight: "1px solid #1a2535",
            display: "flex", flexDirection: "column", alignItems: "center",
            paddingTop: 16, gap: 6, flexShrink: 0,
          }}>
            {icons.map(icon => (
              <div key={icon.id}
                onClick={() => setActiveIcon(icon.id)}
                style={{
                  width: 56, minHeight: 56, borderRadius: 10,
                  display: "flex", flexDirection: "column", alignItems: "center",
                  justifyContent: "center", cursor: "pointer",
                  background: activeIcon === icon.id
                    ? "linear-gradient(135deg, #00b8d4 0%, #0097a7 100%)"
                    : "transparent",
                  color: activeIcon === icon.id ? "#fff" : "#3a6070",
                  transition: "all 0.2s",
                  fontSize: 10, fontFamily: "sans-serif", textAlign: "center",
                  whiteSpace: "pre", lineHeight: 1.3, paddingBlock: 6,
                  boxShadow: activeIcon === icon.id ? "0 0 20px rgba(0,229,255,0.4)" : "none",
                }}
                onMouseEnter={e => { if (activeIcon !== icon.id) e.currentTarget.style.color = "#00e5ff"; }}
                onMouseLeave={e => { if (activeIcon !== icon.id) e.currentTarget.style.color = "#3a6070"; }}
              >
                {icon.svg}
                {icon.label && <span style={{ marginTop: 4 }}>{icon.label}</span>}
              </div>
            ))}
          </div>

          {/* 主面板 */}
          <div style={{
            flex: 1, display: "flex", flexDirection: "column",
            position: "relative", background: "#0d1117",
          }}>
            <HexGrid />
            <NodeNetwork />

            {/* 模式切换内容 */}
            {activeIcon === "assistant" ? (
              // AI助手模式
              <>
                <div ref={outputRef} style={{
                  flex: 1, padding: "20px 24px", overflowY: "auto",
                  position: "relative", zIndex: 1,
                }}>
                  {BOOT_LINES.map((line, i) => (
                    <BootLine key={i} line={line} visible={visibleLines.includes(i)} />
                  ))}
                  {booted && (
                    <div style={{ height: 1, background: "linear-gradient(90deg, #00e5ff33, transparent)", marginBlock: 12 }} />
                  )}
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
                  {booted && (
                    <div style={{
                      display: "inline-block", width: 8, height: 14,
                      background: blinkOn ? "#00e5ff" : "transparent",
                      marginTop: 4, verticalAlign: "middle",
                    }} />
                  )}
                </div>

                {/* 输入框 */}
                <div style={{
                  padding: "12px 20px", borderTop: "1px solid #1a2535",
                  position: "relative", zIndex: 1,
                }}>
                  <div style={{
                    display: "flex", gap: 12, alignItems: "center",
                    background: "#111820", borderRadius: 24,
                    border: "1px solid #1e2d3d", padding: "6px 6px 6px 20px",
                  }}>
                    <input
                      value={input}
                      onChange={e => setInput(e.target.value)}
                      onKeyDown={e => e.key === "Enter" && handleSend()}
                      placeholder="输入工程问题，例如：计算M12螺栓的预紧力..."
                      style={{
                        flex: 1, background: "transparent", border: "none", outline: "none",
                        color: "#c8d8e0", fontSize: 14, caretColor: "#00e5ff",
                      }}
                    />
                    <button
                      onClick={handleSend}
                      style={{
                        padding: "10px 24px", borderRadius: 20, border: "none", cursor: "pointer",
                        background: "linear-gradient(135deg, #00b8d4, #0097a7)",
                        color: "#fff", fontSize: 13, fontWeight: 600,
                        display: "flex", alignItems: "center", gap: 6,
                        boxShadow: "0 0 16px rgba(0,183,212,0.4)",
                        transition: "all 0.2s",
                      }}
                      onMouseEnter={e => e.currentTarget.style.boxShadow = "0 0 24px rgba(0,229,255,0.6)"}
                      onMouseLeave={e => e.currentTarget.style.boxShadow = "0 0 16px rgba(0,183,212,0.4)"}
                    >
                      <svg viewBox="0 0 24 24" width="14" height="14" fill="white"><path d="M2 21l21-9L2 3v7l15 2-15 2z"/></svg>
                      发送
                    </button>
                  </div>
                </div>
              </>
            ) : activeIcon === "knowledge" ? (
              // 知识库模式
              <KnowledgeBasePanel />
            ) : activeIcon === "workbench" ? (
              // 工具台模式
              <WorkbenchPanel />
            ) : (
              // 其他模式占位
              <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", color: "#5a7a8a" }}>
                <div style={{ textAlign: "center" }}>
                  <div style={{ fontSize: 48, marginBottom: 16 }}>🚧</div>
                  <div style={{ fontSize: 18, color: "#00e5ff" }}>功能开发中</div>
                  <div style={{ fontSize: 14, marginTop: 8 }}>该模块即将上线，敬请期待...</div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* 状态栏 */}
        <div style={{
          height: 36, background: "#080c10", borderTop: "1px solid #1a2535",
          display: "flex", alignItems: "center", paddingInline: 20,
          fontSize: 12, color: "#3a6070", flexShrink: 0,
        }}>
          <span style={{ color: "#00b8d4", marginRight: 16, fontWeight: 700 }}>⚡ MechForge</span>
          {[
            ["API", "Ollama"],
            ["Model", "qwen2.5:3b"],
            ["RAG", "ON", "#00e5ff"],
            ["Memory", "42 MB"],
          ].map(([k, v, vc], i) => (
            <span key={i} style={{ marginRight: 16 }}>
              | <span style={{ color: "#3a6070" }}>{k}: </span>
              <span style={{ color: vc || "#88aaff" }}>{v}</span>
            </span>
          ))}
          <div style={{ marginLeft: "auto", display: "flex", gap: 12 }}>
            <span style={{ color: "#00e5ff" }}>●</span>
            <span>就绪</span>
          </div>
        </div>
      </div>
    </div>
  );
}
