// 启动日志行组件
const BootLine = ({ line, visible }) => {
  if (!visible) return null;
  const parts = line.text.split(": ");
  const isLabeled = parts.length === 2 && line.label;

  return (
    <div
      style={{
        fontFamily: "'Courier New', monospace",
        fontSize: 13,
        lineHeight: 1.6,
        color: "#c8d8e0",
      }}
    >
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

export default BootLine;
