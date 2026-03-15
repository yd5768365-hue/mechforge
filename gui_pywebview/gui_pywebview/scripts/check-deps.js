/**
 * 依赖检查脚本
 * 检查项目依赖是否最新
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

// 颜色
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  cyan: '\x1b[36m'
};

// 检查 Python 依赖
async function checkPythonDeps() {
  console.log('\n🐍 Checking Python dependencies...\n');

  const requirementsPath = path.join(__dirname, '..', 'requirements.txt');
  if (!fs.existsSync(requirementsPath)) {
    console.log('❌ requirements.txt not found');
    return;
  }

  const content = fs.readFileSync(requirementsPath, 'utf8');
  const deps = content
    .split('\n')
    .filter(line => line.trim() && !line.startsWith('#'))
    .map(line => {
      const match = line.match(/^([a-zA-Z0-9_-]+)([<>=!~].*)?$/);
      return match ? { name: match[1], version: match[2] || '' } : null;
    })
    .filter(Boolean);

  for (const dep of deps) {
    process.stdout.write(`  ${dep.name}... `);
    try {
      const latest = await getLatestPythonVersion(dep.name);
      const current = dep.version.replace(/[<>=!~]/g, '');

      if (!current || current === latest) {
        console.log(`${colors.green}✓${colors.reset} ${latest}`);
      } else {
        console.log(`${colors.yellow}⬆${colors.reset} ${current} → ${latest}`);
      }
    } catch (e) {
      console.log(`${colors.red}✗${colors.reset} ${e.message}`);
    }
  }
}

// 获取最新 Python 包版本
function getLatestPythonVersion(packageName) {
  return new Promise((resolve, reject) => {
    const url = `https://pypi.org/pypi/${packageName}/json`;
    https.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          resolve(json.info.version);
        } catch (e) {
          reject(new Error('Failed to parse'));
        }
      });
    }).on('error', reject);
  });
}

// 检查 Node.js 依赖
async function checkNodeDeps() {
  console.log('\n📦 Checking Node.js dependencies...\n');

  const packagePath = path.join(__dirname, '..', 'package.json');
  if (!fs.existsSync(packagePath)) {
    console.log('❌ package.json not found');
    return;
  }

  const pkg = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
  const deps = {
    ...pkg.dependencies,
    ...pkg.devDependencies
  };

  for (const [name, version] of Object.entries(deps)) {
    process.stdout.write(`  ${name}... `);
    try {
      const latest = await getLatestNodeVersion(name);
      const current = version.replace(/[^\d.]/g, '');

      if (current === latest) {
        console.log(`${colors.green}✓${colors.reset} ${latest}`);
      } else {
        console.log(`${colors.yellow}⬆${colors.reset} ${current} → ${latest}`);
      }
    } catch (e) {
      console.log(`${colors.red}✗${colors.reset} ${e.message}`);
    }
  }
}

// 获取最新 Node.js 包版本
function getLatestNodeVersion(packageName) {
  return new Promise((resolve, reject) => {
    const url = `https://registry.npmjs.org/${packageName}`;
    https.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          resolve(json['dist-tags'].latest);
        } catch (e) {
          reject(new Error('Failed to parse'));
        }
      });
    }).on('error', reject);
  });
}

// 主函数
async function main() {
  console.log(`${colors.cyan}🔍 Dependency Checker${colors.reset}`);
  console.log('═'.repeat(50));

  await checkPythonDeps();
  await checkNodeDeps();

  console.log('\n✅ Check complete!\n');
}

main().catch(console.error);
