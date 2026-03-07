import { useState } from "react";
import HexGrid from "./components/HexGrid";
import NodeNetwork from "./components/NodeNetwork";
import ParticleField from "./components/ParticleField";
import Sidebar from "./components/Sidebar";
import AIAssistant from "./modes/AIAssistant";
import KnowledgeBase from "./modes/KnowledgeBase";
import Workbench from "./modes/Workbench";
import "./App.css";

// 标题栏组件
const TitleBar = () => (
  <div
    style={{
      height: 48,
      background: "rgba(13, 17, 23, 0.8)",
      backdropFilter: "blur(10px)",
      WebkitBackdropFilter: "blur(10px)",
      borderBottom: "1px solid rgba(0, 229, 255, 0.15)",
      display: "flex",
      alignItems: "center",
      paddingInline: 20,
      gap: 12,
      flexShrink: 0,
      zIndex: 10,
    }}
  >
    <div
      style={{
        width: 32,
        height: 32,
        borderRadius: 8,
        background: "linear-gradient(135deg, #00b8d4, #0097a7)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <svg viewBox="0 0 24 24" width="18" height="18" fill="white">
        <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
      </svg>
    </div>
    <span style={{ color: "#c8d8e0", fontSize: 16, fontWeight: 600 }}>
      MechForge AI
    </span>
    <span style={{ color: "#3a5068", fontSize: 13 }}>v0.6.0</span>

    <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
      {["−", "□", "×"].map((ch, i) => (
        <div
          key={i}
          style={{
            width: 24,
            height: 24,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "#3a5068",
            cursor: "pointer",
            fontSize: 14,
            borderRadius: 4,
            transition: "all 0.2s",
          }}
          onMouseEnter={(e) => {
            e.target.style.color = "#00e5ff";
            e.target.style.background = "rgba(0,229,255,0.1)";
          }}
          onMouseLeave={(e) => {
            e.target.style.color = "#3a5068";
            e.target.style.background = "transparent";
          }}
        >
          {ch}
        </div>
      ))}
    </div>
  </div>
);

// 状态栏组件
const StatusBar = () => (
  <div
    style={{
      height: 36,
      background: "rgba(13, 17, 23, 0.8)",
      backdropFilter: "blur(10px)",
      WebkitBackdropFilter: "blur(10px)",
      borderTop: "1px solid rgba(0, 229, 255, 0.15)",
      display: "flex",
      alignItems: "center",
      paddingInline: 20,
      fontSize: 12,
      color: "#3a6070",
      flexShrink: 0,
      zIndex: 10,
    }}
  >
    <span style={{ color: "#00b8d4", marginRight: 16, fontWeight: 700 }}>
      ⚡ MechForge
    </span>
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
);

// 占位组件
const Placeholder = () => (
  <div
    style={{
      flex: 1,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      color: "#5a7a8a",
    }}
  >
    <div style={{ textAlign: "center" }}>
      <div style={{ fontSize: 48, marginBottom: 16 }}>🚧</div>
      <div style={{ fontSize: 18, color: "#00e5ff" }}>功能开发中</div>
      <div style={{ fontSize: 14, marginTop: 8 }}>
        该模块即将上线，敬请期待...
      </div>
    </div>
  </div>
);

function App() {
  const [activeIcon, setActiveIcon] = useState("assistant");

  const renderContent = () => {
    switch (activeIcon) {
      case "assistant":
        return <AIAssistant />;
      case "knowledge":
        return <KnowledgeBase />;
      case "workbench":
        return <Workbench />;
      default:
        return <Placeholder />;
    }
  };

  return (
    <div className="app">
      {/* ============ 背景层区域 ============ */}
      {/* 1. 六边形网格背景 */}
      <HexGrid />
      {/* 2. 节点连线网络 */}
      <NodeNetwork />
      {/* 3. 粒子特效场 */}
      <ParticleField />
      {/* =================================== */}

      {/* 主窗口容器 */}
      <div className="window">
        <TitleBar />
        <div className="body">
          <Sidebar activeIcon={activeIcon} onIconClick={setActiveIcon} />
          <main className="main-panel">
            {renderContent()}
          </main>
        </div>
        <StatusBar />
      </div>
    </div>
  );
}

export default App;
