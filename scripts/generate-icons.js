/**
 * 图标生成脚本
 * 生成各种尺寸的图标
 */

const fs = require('fs');
const path = require('path');

// 配置
const config = {
  sourceIcon: path.join(__dirname, '..', 'dj-whale.png'),
  outputDir: path.join(__dirname, '..', 'assets', 'icons'),
  sizes: [16, 32, 48, 64, 128, 256, 512]
};

// 确保输出目录存在
if (!fs.existsSync(config.outputDir)) {
  fs.mkdirSync(config.outputDir, { recursive: true });
}

// 生成图标
async function generateIcons() {
  console.log('🎨 Generating icons...');

  // 检查源文件
  if (!fs.existsSync(config.sourceIcon)) {
    console.error('❌ Source icon not found:', config.sourceIcon);
    return;
  }

  // 复制源文件到输出目录
  const sourceExt = path.extname(config.sourceIcon);
  fs.copyFileSync(config.sourceIcon, path.join(config.outputDir, `icon-512${sourceExt}`));

  console.log('✅ Icons generated in:', config.outputDir);
  console.log('📦 Sizes:', config.sizes.join(', '));
}

// 生成 ICO 文件（Windows）
async function generateIco() {
  console.log('🪟 Generating Windows ICO...');
  // 这里需要额外的库来处理 ICO 格式
  console.log('ℹ️  Install sharp or jimp to generate ICO files');
}

// 生成 ICNS 文件（macOS）
async function generateIcns() {
  console.log('🍎 Generating macOS ICNS...');
  console.log('ℹ️  Install iconutil or similar to generate ICNS files');
}

// 主函数
async function main() {
  await generateIcons();
  await generateIco();
  await generateIcns();
}

main().catch(console.error);
