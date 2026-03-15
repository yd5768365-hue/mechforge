// 六边形网格背景组件
const HexGrid = () => (
  <svg
    style={{
      position: "absolute",
      inset: 0,
      width: "100%",
      height: "100%",
      opacity: 0.07,
      pointerEvents: "none",
      zIndex: 0,
    }}
    xmlns="http://www.w3.org/2000/svg"
  >
    <defs>
      <pattern
        id="hex"
        x="0"
        y="0"
        width="56"
        height="48"
        patternUnits="userSpaceOnUse"
      >
        <polygon
          points="14,2 42,2 56,24 42,46 14,46 0,24"
          fill="none"
          stroke="#00e5ff"
          strokeWidth="0.8"
        />
      </pattern>
    </defs>
    <rect width="100%" height="100%" fill="url(#hex)" />
  </svg>
);

export default HexGrid;
