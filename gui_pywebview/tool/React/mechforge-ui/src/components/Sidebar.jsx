// 侧边栏组件
const icons = [
  {
    id: "assistant",
    label: "AI\n助手",
    svg: (
      <svg
        viewBox="0 0 24 24"
        width="22"
        height="22"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
      >
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z" />
        <path d="M8 14s1.5 2 4 2 4-2 4-2" />
        <circle cx="9" cy="10" r="1.5" fill="currentColor" />
        <circle cx="15" cy="10" r="1.5" fill="currentColor" />
      </svg>
    ),
  },
  {
    id: "knowledge",
    label: "知识库\nKB",
    svg: (
      <svg
        viewBox="0 0 24 24"
        width="22"
        height="22"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
      >
        <path d="M4 19.5v-15A2.5 2.5 0 016.5 2H20v20H6.5A2.5 2.5 0 014 19.5z" />
        <path d="M8 7h8M8 11h6M8 15h4" />
      </svg>
    ),
  },
  {
    id: "workbench",
    label: "工具台\nCAE",
    svg: (
      <svg
        viewBox="0 0 24 24"
        width="22"
        height="22"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
      >
        <rect x="2" y="3" width="20" height="6" rx="1" />
        <rect x="2" y="15" width="20" height="6" rx="1" />
        <line x1="6" y1="9" x2="6" y2="15" />
        <line x1="10" y1="9" x2="10" y2="15" />
        <line x1="14" y1="9" x2="14" y2="15" />
        <line x1="18" y1="9" x2="18" y2="15" />
      </svg>
    ),
  },
  {
    id: "shield",
    label: "安全",
    svg: (
      <svg
        viewBox="0 0 24 24"
        width="22"
        height="22"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
      >
        <path d="M12 2L4 6v6c0 5.25 3.75 10.15 8 11 4.25-.85 8-5.75 8-11V6l-8-4z" />
      </svg>
    ),
  },
  {
    id: "db",
    label: "数据库",
    svg: (
      <svg
        viewBox="0 0 24 24"
        width="22"
        height="22"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
      >
        <ellipse cx="12" cy="6" rx="8" ry="3" />
        <path d="M4 6v6c0 1.66 3.58 3 8 3s8-1.34 8-3V6" />
        <path d="M4 12v6c0 1.66 3.58 3 8 3s8-1.34 8-3v-6" />
      </svg>
    ),
  },
  {
    id: "settings",
    label: "设置",
    svg: (
      <svg
        viewBox="0 0 24 24"
        width="22"
        height="22"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
      >
        <circle cx="12" cy="12" r="3" />
        <path d="M12 1v6m0 6v6m4.22-10.22l4.24-4.24M6.34 6.34L2.1 2.1m17.8 17.8l-4.24-4.24M6.34 17.66l-4.24 4.24M23 12h-6m-6 0H1m20.24-4.24l-4.24 4.24M6.34 6.34l-4.24-4.24" />
      </svg>
    ),
  },
];

const Sidebar = ({ activeIcon, onIconClick }) => {
  return (
    <div
      style={{
        width: 72,
        background: "rgba(13, 17, 23, 0.7)",
        backdropFilter: "blur(10px)",
        WebkitBackdropFilter: "blur(10px)",
        borderRight: "1px solid rgba(0, 229, 255, 0.15)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        paddingTop: 16,
        gap: 6,
        flexShrink: 0,
        zIndex: 10,
      }}
    >
      {icons.map((icon) => (
        <div
          key={icon.id}
          onClick={() => onIconClick(icon.id)}
          style={{
            width: 56,
            minHeight: 56,
            borderRadius: 10,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            cursor: "pointer",
            background:
              activeIcon === icon.id
                ? "linear-gradient(135deg, #00b8d4 0%, #0097a7 100%)"
                : "transparent",
            color: activeIcon === icon.id ? "#fff" : "#3a6070",
            transition: "all 0.2s",
            fontSize: 10,
            fontFamily: "sans-serif",
            textAlign: "center",
            whiteSpace: "pre",
            lineHeight: 1.3,
            paddingBlock: 6,
            boxShadow:
              activeIcon === icon.id
                ? "0 0 20px rgba(0,229,255,0.4)"
                : "none",
          }}
          onMouseEnter={(e) => {
            if (activeIcon !== icon.id)
              e.currentTarget.style.color = "#00e5ff";
          }}
          onMouseLeave={(e) => {
            if (activeIcon !== icon.id)
              e.currentTarget.style.color = "#3a6070";
          }}
        >
          {icon.svg}
          {icon.label && <span style={{ marginTop: 4 }}>{icon.label}</span>}
        </div>
      ))}
    </div>
  );
};

export default Sidebar;
