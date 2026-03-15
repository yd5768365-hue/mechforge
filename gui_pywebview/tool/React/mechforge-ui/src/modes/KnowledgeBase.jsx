import { useState, useEffect } from "react";

const KnowledgeBase = () => {
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
        setProgress((p) => Math.min(100, p + Math.random() * 8));
      }, 1800);
      return () => clearTimeout(timer);
    }
  }, [progress]);

  return (
    <div
      style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        padding: "24px",
        position: "relative",
        zIndex: 1,
        overflow: "hidden",
        background: "rgba(13, 17, 23, 0.3)",
        backdropFilter: "blur(5px)",
        WebkitBackdropFilter: "blur(5px)",
      }}
    >
      {/* 搜索框 */}
      <div style={{ position: "relative", marginBottom: "24px" }}>
        <input
          type="text"
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
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
          onFocus={(e) => {
            e.target.style.boxShadow = "0 0 0 3px rgba(0, 229, 255, 0.25)";
            e.target.style.borderColor = "#00e5ff";
          }}
          onBlur={(e) => {
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
      <div
        style={{
          marginBottom: "20px",
          padding: "12px 16px",
          background: "rgba(17, 24, 32, 0.5)",
          borderRadius: "10px",
          border: "1px solid rgba(0, 229, 255, 0.15)",
          boxShadow: "0 0 20px rgba(0, 229, 255, 0.08)",
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
            正在构建/更新知识库索引...
          </span>
          <span style={{ color: "#00e5ff", fontWeight: 600 }}>
            {Math.round(progress)}%
          </span>
        </div>
        <div
          style={{
            height: "8px",
            background: "#1a2535",
            borderRadius: "4px",
            overflow: "hidden",
            boxShadow: "inset 0 1px 3px rgba(0,0,0,0.4)",
          }}
        >
          <div
            style={{
              height: "100%",
              width: `${progress}%`,
              background: "linear-gradient(90deg, #00b8d4, #00e5ff)",
              borderRadius: "4px",
              boxShadow: "0 0 12px rgba(0, 229, 255, 0.6)",
              transition: "width 1.2s ease-out",
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
          速度: {indexingSpeed} · 已处理 1.8 GB / 预计剩余 2分14秒
        </div>
      </div>

      {/* 文档列表 */}
      <div
        style={{
          flex: 1,
          overflowY: "auto",
          paddingRight: "8px",
          scrollbarWidth: "thin",
          scrollbarColor: "#1a2535 #0d1117",
        }}
      >
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
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = "#00e5ff";
              e.currentTarget.style.boxShadow =
                "0 0 16px rgba(0,229,255,0.25)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = "rgba(0, 229, 255, 0.12)";
              e.currentTarget.style.boxShadow = "none";
            }}
          >
            {/* 文件图标 */}
            <div
              style={{
                width: 40,
                height: 48,
                background:
                  doc.type === "pdf"
                    ? "#ff5252"
                    : doc.type === "xlsx"
                    ? "#4caf50"
                    : "#ffca28",
                borderRadius: "6px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "white",
                fontWeight: 700,
                fontSize: "12px",
                marginRight: "16px",
                flexShrink: 0,
              }}
            >
              {doc.type.toUpperCase()}
            </div>

            {/* 文件信息 */}
            <div style={{ flex: 1 }}>
              <div
                style={{ color: "#e0f0ff", fontSize: "15px", fontWeight: 500 }}
              >
                {doc.name}
              </div>
              <div style={{ color: "#88aaff", fontSize: "12px", marginTop: "4px" }}>
                {doc.size} · {doc.date} · 相关度 {doc.relevance}%
              </div>
            </div>

            {/* 相关度小条 */}
            <div
              style={{
                width: 60,
                height: 6,
                background: "#1a2535",
                borderRadius: "3px",
                overflow: "hidden",
                marginLeft: "16px",
              }}
            >
              <div
                style={{
                  height: "100%",
                  width: `${doc.relevance}%`,
                  background: "linear-gradient(90deg, #00b8d4, #00e5ff)",
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default KnowledgeBase;
