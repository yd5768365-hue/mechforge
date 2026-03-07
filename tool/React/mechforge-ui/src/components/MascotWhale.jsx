// 吉祥物鲸鱼组件 - 放在聊天界面右下角
const MascotWhale = () => {
  return (
    <div style={{
      position: "absolute",
      bottom: -50,   // 放在右下角，稍微沉底一点
      right: -20,
      pointerEvents: "none", // 鼠标穿透，不影响点击
      zIndex: 0,             // 放在最底层
      opacity: 0.15,         // 设置极低的透明度，作为背景暗纹，不影响看字
    }}>
      <img 
        src="/dj-whale.png"  // 图片放在 public 文件夹下
        alt="DJ Whale Mascot"
        style={{
          width: "450px", // 调整吉祥物的大小
          // 加上赛博朋克的青色发光阴影，并稍微降低一点饱和度让它融入深色背景
          filter: "drop-shadow(0 0 30px rgba(0, 229, 255, 0.8)) saturate(0.8)",
          // 悬浮打碟动画！
          animation: "floatDJ 6s ease-in-out infinite" 
        }}
      />

      <style>{`
        @keyframes floatDJ {
          0%, 100% { transform: translateY(0px) rotate(-2deg); }
          50% { transform: translateY(-20px) rotate(2deg); filter: drop-shadow(0 0 50px rgba(0, 255, 163, 0.8)) saturate(1); }
        }
      `}</style>
    </div>
  );
};

export default MascotWhale;
