// 节点网络动画组件
const NodeNetwork = () => {
  const nodes = [
    { x: 75, y: 30 },
    { x: 85, y: 55 },
    { x: 90, y: 20 },
    { x: 70, y: 70 },
    { x: 95, y: 40 },
    { x: 80, y: 80 },
  ];
  const edges = [
    [0, 1],
    [1, 3],
    [0, 4],
    [4, 1],
    [2, 4],
    [3, 5],
    [1, 5],
  ];

  return (
    <svg
      style={{
        position: "absolute",
        inset: 0,
        width: "100%",
        height: "100%",
        opacity: 0.15,
        pointerEvents: "none",
        zIndex: 0,
      }}
    >
      {edges.map(([a, b], i) => (
        <line
          key={i}
          x1={`${nodes[a].x}%`}
          y1={`${nodes[a].y}%`}
          x2={`${nodes[b].x}%`}
          y2={`${nodes[b].y}%`}
          stroke="#00e5ff"
          strokeWidth="0.5"
        />
      ))}
      {nodes.map((n, i) => (
        <circle
          key={i}
          cx={`${n.x}%`}
          cy={`${n.y}%`}
          r="2.5"
          fill="#00e5ff"
        />
      ))}
    </svg>
  );
};

export default NodeNetwork;
