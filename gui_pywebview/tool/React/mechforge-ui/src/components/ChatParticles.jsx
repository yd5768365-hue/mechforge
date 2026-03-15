// 聊天区域粒子特效组件
import { useEffect, useRef } from "react";

const ChatParticles = () => {
  const canvasRef = useRef(null);
  const particlesRef = useRef([]);
  const animationRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    let width = canvas.offsetWidth;
    let height = canvas.offsetHeight;

    // 设置 canvas 尺寸
    const resize = () => {
      width = canvas.offsetWidth;
      height = canvas.offsetHeight;
      canvas.width = width;
      canvas.height = height;
    };
    resize();

    // 粒子配置 - 聊天区域粒子
    const config = {
      particleCount: 100,        // 聊天区域粒子数量 - 增加
      connectionDistance: 100,   // 连线距离
      speed: 0.4,                // 速度
      colors: ["#00e5ff", "#00b8d4", "#4fc3f7", "#81d4fa"],
    };

    // 初始化粒子
    class Particle {
      constructor() {
        this.reset();
      }

      reset() {
        this.x = Math.random() * width;
        this.y = Math.random() * height;
        this.size = Math.random() * 1.5 + 0.5;
        this.speedX = (Math.random() - 0.5) * config.speed;
        this.speedY = (Math.random() - 0.5) * config.speed;
        this.color = config.colors[Math.floor(Math.random() * config.colors.length)];
        this.opacity = Math.random() * 0.3 + 0.1;
        this.pulse = Math.random() * Math.PI * 2;
        this.pulseSpeed = 0.02 + Math.random() * 0.02;
      }

      update() {
        this.x += this.speedX;
        this.y += this.speedY;

        // 脉冲效果
        this.pulse += this.pulseSpeed;
        this.currentOpacity = this.opacity + Math.sin(this.pulse) * 0.05;

        // 边界处理
        if (this.x < 0) this.x = width;
        if (this.x > width) this.x = 0;
        if (this.y < 0) this.y = height;
        if (this.y > height) this.y = 0;
      }

      draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fillStyle = this.color;
        ctx.globalAlpha = Math.max(0.05, Math.min(0.4, this.currentOpacity));
        ctx.fill();
        ctx.globalAlpha = 1;
      }
    }

    // 创建粒子
    particlesRef.current = Array.from(
      { length: config.particleCount },
      () => new Particle()
    );

    // 绘制连线
    const drawConnections = () => {
      const particles = particlesRef.current;

      for (let i = 0; i < particles.length; i++) {
        let connections = 0;

        for (let j = i + 1; j < particles.length; j++) {
          if (connections >= 2) break;

          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const distance = Math.sqrt(dx * dx + dy * dy);

          if (distance < config.connectionDistance) {
            const opacity = (1 - distance / config.connectionDistance) * 0.15;
            ctx.beginPath();
            ctx.strokeStyle = "#00e5ff";
            ctx.globalAlpha = opacity;
            ctx.lineWidth = 0.3;
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.stroke();
            ctx.globalAlpha = 1;
            connections++;
          }
        }
      }
    };

    // 动画循环
    const animate = () => {
      ctx.clearRect(0, 0, width, height);

      // 更新和绘制粒子
      particlesRef.current.forEach((particle) => {
        particle.update();
        particle.draw();
      });

      // 绘制连线
      drawConnections();

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    // 清理
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: "absolute",
        inset: 0,
        width: "100%",
        height: "100%",
        pointerEvents: "none",
        zIndex: 0,
        opacity: 0.8,
      }}
    />
  );
};

export default ChatParticles;
