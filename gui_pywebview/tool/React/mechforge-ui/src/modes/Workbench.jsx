import { useState, useEffect } from "react";

const Workbench = () => {
  const [calcProgress, setCalcProgress] = useState(67);
  const [logs] = useState([
    { level: "INFO", msg: "Reading STEP file: bracket_v2.step", time: "14:32:01" },
    { level: "INFO", msg: "Initializing Gmsh API...", time: "14:32:03" },
    { level: "INFO", msg: "Surface meshing completed", time: "14:32:15" },
    { level: "WARN", msg: "High aspect ratio detected at surface ID: 42", time: "14:32:28" },
    { level: "INFO", msg: "Volume meshing: 67%", time: "14:32:45" },
    { level: "INFO", msg: "Optimizing mesh quality...", time: "14:33:02" },
  ]);

  useEffect(() => {
    const timer = setInterval(() => {
      setCalcProgress((p) => {
        if (p >= 100) return 0;
        return p + Math.random() * 2;
      });
    }, 2000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div
      style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        padding: "24px",
        position: "relative",
        zIndex: 1,
        background: "rgba(13, 17, 23, 0.3)",
        backdropFilter: "blur(5px)",
        WebkitBackdropFilter: "blur(5px)",
      }}
    >
      {/* 工具栏 */}
      <div style={{ display: "flex", gap: "12px", marginBottom: "20px" }}>
        {["➕ 新建计算", "📂 导入几何", "🔲 网格划分", "▶ 求解分析"].map(
          (label, i) => (
            <button
              key={i}
              style={{
                padding: "10px 20px",
                background:
                  i === 0
                    ? "linear-gradient(135deg, #00b8d4, #0097a7)"
                    : "rgba(0, 229, 255, 0.1)",
                border: "1px solid rgba(0, 229, 255, 0.3)",
                borderRadius: "8px",
                color: i === 0 ? "#fff" : "#00e5ff",
                fontSize: "13px",
                cursor: "pointer",
                transition: "all 0.2s",
              }}
              onMouseEnter={(e) => {
                e.target.style.boxShadow = "0 0 16px rgba(0,229,255,0.3)";
              }}
              onMouseLeave={(e) => {
                e.target.style.boxShadow = "none";
              }}
            >
              {label}
            </button>
          )
        )}
      </div>

      {/* 进度条 */}
      <div
        style={{
          marginBottom: "20px",
          padding: "12px 16px",
          background: "rgba(17, 24, 32, 0.5)",
          borderRadius: "10px",
          border: "1px solid rgba(0, 229, 255, 0.15)",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            marginBottom: "8px",
          }}
        >
          <span style={{ color: "#a0d0ff", fontSize: "14px" }}>
            Gmsh 网格生成中...
          </span>
          <span style={{ color: "#00e5ff", fontWeight: 600 }}>
            {Math.round(calcProgress)}%
          </span>
        </div>
        <div
          style={{
            height: "8px",
            background: "#1a2535",
            borderRadius: "4px",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              height: "100%",
              width: `${calcProgress}%`,
              background: "linear-gradient(90deg, #00b8d4, #00e5ff)",
              borderRadius: "4px",
              boxShadow: "0 0 12px rgba(0, 229, 255, 0.6)",
              transition: "width 0.5s ease-out",
            }}
          />
        </div>
        <div
          style={{
            marginTop: "6px",
            fontSize: "12px",
            color: "#88aaff",
            textAlign: "right",
          }}
        >
          预计剩余 {Math.max(0, Math.round((100 - calcProgress) / 10))} 秒
        </div>
      </div>

      {/* 左右分栏 */}
      <div style={{ display: "flex", gap: "16px", flex: 1 }}>
        {/* 控制台日志 */}
        <div
          style={{
            width: "45%",
            background: "rgba(17, 24, 32, 0.5)",
            borderRadius: "10px",
            border: "1px solid rgba(0, 229, 255, 0.15)",
            padding: "16px",
            overflowY: "auto",
          }}
        >
          <div
            style={{
              color: "#00e5ff",
              fontSize: "14px",
              fontWeight: 600,
              marginBottom: "12px",
            }}
          >
            📋 系统日志
          </div>
          {logs.map((log, i) => (
            <div key={i} style={{ marginBottom: "8px", fontSize: "12px" }}>
              <span style={{ color: "#5a7a8a" }}>[{log.time}]</span>
              <span
                style={{
                  color:
                    log.level === "WARN"
                      ? "#ffca28"
                      : log.level === "ERROR"
                      ? "#ff5252"
                      : "#00e5ff",
                  marginLeft: "8px",
                }}
              >
                {log.level}
              </span>
              <span style={{ color: "#a0c0d0", marginLeft: "8px" }}>
                {log.msg}
              </span>
            </div>
          ))}
        </div>

        {/* 3D预览区 */}
        <div
          style={{
            flex: 1,
            background: "rgba(17, 24, 32, 0.5)",
            borderRadius: "10px",
            border: "1px solid rgba(0, 229, 255, 0.15)",
            padding: "16px",
            display: "flex",
            flexDirection: "column",
          }}
        >
          <div
            style={{
              color: "#00e5ff",
              fontSize: "14px",
              fontWeight: 600,
              marginBottom: "12px",
            }}
          >
            🔮 3D 预览
          </div>
          <div style={{ flex: 1, position: "relative" }}>
            <svg width="100%" height="100%" style={{ position: "absolute", inset: 0 }}>
              <defs>
                <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                  <path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(0,229,255,0.1)" strokeWidth="0.5"/>
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#grid)" />
              
              <g transform="translate(150, 100)">
                <rect x="-40" y="-40" width="80" height="80" fill="none" stroke="#00e5ff" strokeWidth="2" />
                <rect x="-20" y="-60" width="80" height="80" fill="none" stroke="#00b8d4" strokeWidth="1.5" opacity="0.6" />
                <line x1="-40" y1="-40" x2="-20" y2="-60" stroke="#00e5ff" strokeWidth="1" opacity="0.5" />
                <line x1="40" y1="-40" x2="60" y2="-60" stroke="#00e5ff" strokeWidth="1" opacity="0.5" />
                <line x1="-40" y1="40" x2="-20" y2="20" stroke="#00e5ff" strokeWidth="1" opacity="0.5" />
                <line x1="40" y1="40" x2="60" y2="20" stroke="#00e5ff" strokeWidth="1" opacity="0.5" />
              </g>
              
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

export default Workbench;
