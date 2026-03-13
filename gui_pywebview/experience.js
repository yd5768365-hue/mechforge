/**
 * MechForge AI — Experience Library
 * 工业风故障案例知识库
 */
(function() {
  'use strict';

  var DATA = [
    { id: 'EXP-001', title: '高周疲劳裂纹起始于表面划伤处', category: '疲劳失效', severity: 'critical', tags: ['疲劳','裂纹','表面处理'], snippet: '零件表面的机械划伤会显著降低疲劳寿命，应力集中系数 Kt 可达 2~4。', condition: '轴类零件在远低于屈服强度的循环载荷下发生断裂，断口呈典型海滩纹特征，裂纹起源于表面划伤或工具痕迹处。', cause: '表面加工缺陷形成应力集中源，局部应力幅超过材料疲劳极限，在循环载荷作用下裂纹萌生并扩展，直至剩余截面不足以承载而断裂。', solution: '1. 提高表面粗糙度要求 Ra ≤ 0.8 μm（关键部位）\n2. 终加工工序改为磨削或抛光，避免车削痕迹\n3. 危险截面处增加圆角 r ≥ 2 mm\n4. 高应力区增加喷丸处理\n5. 检查图纸：危险截面处禁止标注尖角', source: 'GB/T 19624-2019', url: '#' },
    { id: 'EXP-002', title: '过盈配合拆装导致轴承内圈蠕变', category: '配合失效', severity: 'warning', tags: ['轴承','过盈配合','装配'], snippet: '反复拆装破坏配合面氧化膜，配合面微动磨损后内圈发生蠕变旋转。', condition: '轴承内圈相对轴颈产生相对转动，轴颈出现磨损沟槽，轴承发热，振动增大。', cause: '反复拆装破坏配合面微观形貌，氧化膜被磨损导致实际过盈量衰减，在旋转载荷下配合面微动。', solution: '1. 选用合适的过盈量（根据 ISO 286 选择配合等级）\n2. 拆装时使用专用感应加热或液压工具\n3. 频繁拆装改用锁紧套方案\n4. 配合面涂专用装配胶', source: 'SKF 轴承手册', url: '#' },
    { id: 'EXP-003', title: '焊接残余应力引发应力腐蚀开裂', category: '腐蚀失效', severity: 'critical', tags: ['焊接','残余应力','应力腐蚀'], snippet: '焊缝热影响区拉伸残余应力与腐蚀性介质协同作用，导致延迟开裂。', condition: '不锈钢或高强钢焊接件在含 Cl⁻ 介质环境中出现延迟裂纹。', cause: '焊接冷却过程在热影响区产生高达 0.8σy 的拉伸残余应力，与腐蚀介质协同作用导致 SCC。', solution: '1. 焊后消应力处理（SR 退火或振动消应力）\n2. 选用低残余应力焊接工艺（小线能量多道焊）\n3. 焊缝区喷丸处理引入压应力\n4. 必要时更换双相不锈钢或含钼材料', source: 'ASME PCC-2', url: '#' },
    { id: 'EXP-004', title: '螺栓松动：振动载荷下预紧力衰减', category: '连接失效', severity: 'warning', tags: ['螺栓','预紧力','振动'], snippet: '振动工况下螺纹副微动导致预紧力损失超过 30%。', condition: '设备运行后螺栓出现松动，连接面漏油/漏气。', cause: '横向振动使螺纹面产生微动滑移，摩擦力不足以维持预紧力。', solution: '1. 施加足够预紧力（按 VDI 2230 计算）\n2. 采用防松措施（Nord-Lock 锁紧垫圈、自锁螺母）\n3. 关键连接定期检查扭矩\n4. 优化法兰刚度减少横向位移', source: 'VDI 2230', url: '#' },
    { id: 'EXP-005', title: '密封圈老化：O 形圈压缩永久变形', category: '密封失效', severity: 'info', tags: ['密封','O形圈','老化'], snippet: '橡胶 O 形圈在高温下压缩永久变形超过 40% 后丧失密封能力。', condition: '液压系统静密封点出现渗漏，O 形圈截面呈扁平状。', cause: '橡胶分子链在温度和介质作用下发生热氧化降解和溶胀，弹性回复力下降。', solution: '1. 根据介质和温度选择材质（FKM 耐高温、EPDM 耐蒸汽）\n2. 检查槽深确保压缩率 15~25%\n3. 定期更换（按预防性维护周期）\n4. 储存避免阳光直射和臭氧', source: 'Parker O-Ring Handbook', url: '#' },
    { id: 'EXP-006', title: '齿轮胶合：高速重载下润滑膜破裂', category: '磨损失效', severity: 'critical', tags: ['齿轮','胶合','润滑'], snippet: '节线附近油膜最薄，PV 值最大，是胶合失效的高发区域。', condition: '高速齿轮箱齿面出现撕裂划痕，伴随温升异常和金属颗粒。', cause: '高速重载下接触区瞬时温升（闪温）超过润滑油承载极限，油膜破裂导致金属直接接触。', solution: '1. 润滑油选型：使用 EP 极压添加剂\n2. 提高齿面硬度至 HRC 58~62\n3. 新齿轮进行跑合处理（50% 载荷运行 24h）\n4. 控制油温 < 80°C，设置油温报警', source: 'ISO 6336', url: '#' },
    { id: 'EXP-007', title: '铸件气孔：浇注系统设计不当', category: '铸造缺陷', severity: 'info', tags: ['铸造','气孔','工艺'], snippet: '浇注速度过快或排气不畅是气孔的首要原因。', condition: '铸件加工后发现球形或不规则孔洞，降低力学性能和气密性。', cause: '浇注过程气体（型芯产气、卷入空气）不能及时排出，被包裹于金属液中凝固。', solution: '1. 优化浇注系统设计（设置排气冒口和排气通道）\n2. 控制浇注速度和温度\n3. 型砂水分控制 < 4%\n4. 铸型预热至 150~200°C 减少气体生成', source: 'AFS 铸造手册', url: '#' },
    { id: 'EXP-008', title: '轴承早期失效：污染颗粒压痕', category: '污染失效', severity: 'warning', tags: ['轴承','污染','维护'], snippet: '固体颗粒污染是轴承过早失效的第一大因素（占比超过 50%）。', condition: '轴承振动和噪声异常，滚道上出现均匀分布的压痕。', cause: '硬质颗粒（金属碎屑、砂粒）进入轴承内部，被滚动体碾压形成压痕，引起应力集中。', solution: '1. 装配现场保持清洁（ISO 7级以上）\n2. 润滑脂选型注意清洁度等级\n3. 密封系统检查（接触式 + 迷宫式双重密封）\n4. 润滑油过滤精度 ≤ 25 μm', source: 'NSK 轴承手册', url: '#' },
    { id: 'EXP-009', title: '热处理变形：淬火冷却不均导致翘曲', category: '热处理缺陷', severity: 'info', tags: ['热处理','淬火','变形'], snippet: '薄壁件和细长轴在淬火中最易产生变形，翘曲量可达 mm 级。', condition: '零件淬火后尺寸超差，长轴弯曲量超过 0.3 mm/m。', cause: '淬火冷却时零件各截面温度梯度产生不均匀热应力和相变应力。', solution: '1. 设计上减少截面突变和壁厚不均\n2. 正确装挂（细长轴竖直入液）\n3. 合理选择冷却介质（等温淬火减少变形）\n4. 重要零件使用工装定型淬火', source: 'ASM Handbook Vol.4', url: '#' },
    { id: 'EXP-010', title: '管路振动：共振引起疲劳开裂', category: '振动失效', severity: 'critical', tags: ['管路','振动','共振'], snippet: '管路固有频率与激振频率相近时共振幅值可达 20~100 倍。', condition: '流体管路出现周期性振动，最终在焊缝处发生疲劳裂纹。', cause: '流体脉动频率（泵频率 × 叶片数）与管路固有频率接近或重合，发生共振。', solution: '1. 频率避开：固有频率避开激振频率 ±20%\n2. 增加支撑：减小跨距提高固有频率\n3. 安装减振器（调谐质量阻尼器）\n4. 加装脉动阻尼器（蓄能器）', source: 'ASME B31.3', url: '#' },
    { id: 'EXP-011', title: '滑动轴承烧瓦：供油中断或油膜破裂', category: '润滑失效', severity: 'critical', tags: ['滑动轴承','烧瓦','润滑'], snippet: '供油中断 30 秒内巴氏合金即可熔化，造成严重停机事故。', condition: '滑动轴承温度急剧升高，停机后轴瓦巴氏合金熔化剥落。', cause: '润滑油供应中断或轴瓦间隙过大导致油膜破裂，金属直接接触产生大量摩擦热。', solution: '1. 设置供油压力低报警和联锁停机\n2. 安装备用润滑油泵（自动切换）\n3. 定期检查轴承间隙（千分之一~千分之二轴径）\n4. 油品管理：定期检测粘度和水分', source: 'ISO 7902', url: '#' },
    { id: 'EXP-012', title: '压力容器局部过热：热斑检测与处理', category: '热失效', severity: 'warning', tags: ['压力容器','过热','检测'], snippet: '局部过热可导致蠕变加速和氢损伤，严重时引发泄漏。', condition: '高温压力容器外壁出现温度异常偏高区域（热斑）。', cause: '内壁结垢或催化剂偏流导致局部传热恶化，使局部金属温度超过蠕变温度门槛。', solution: '1. 定期红外热像仪全面扫描\n2. 评估当前蠕变损伤和剩余寿命\n3. 停机时化学清洗去除结垢\n4. 安装在线壁温监测系统', source: 'API 579-1/ASME FFS-1', url: '#' }
  ];

  var TAGS = [];
  var tagSet = {};
  DATA.forEach(function(d) {
    d.tags.forEach(function(t) { tagSet[t] = true; });
  });
  TAGS = Object.keys(tagSet).sort();

  var SEVERITY = {
    critical: { label: 'CRITICAL', color: '#ff4757', icon: '⚠' },
    warning:  { label: 'WARNING',  color: '#ffa502', icon: '◈' },
    info:     { label: 'INFO',     color: '#00e5ff', icon: '◉' }
  };

  var state = { activeTag: null, query: '' };
  var $ = function(id) { return document.getElementById(id); };

  function init() {
    renderTags();
    renderCards();
    bindEvents();
  }

  function renderTags() {
    var container = $('exp-tags-container');
    if (!container) return;
    container.innerHTML = '';

    var allBtn = document.createElement('span');
    allBtn.className = 'exp-tag-filter' + (state.activeTag === null ? ' active' : '');
    allBtn.textContent = 'ALL';
    allBtn.onclick = function() { toggleTag(null, allBtn); };
    container.appendChild(allBtn);

    TAGS.forEach(function(tag) {
      var btn = document.createElement('span');
      btn.className = 'exp-tag-filter' + (state.activeTag === tag ? ' active' : '');
      btn.textContent = '#' + tag;
      btn.onclick = function() { toggleTag(tag, btn); };
      container.appendChild(btn);
    });
  }

  function toggleTag(tag, el) {
    state.activeTag = tag;
    document.querySelectorAll('.exp-tag-filter').forEach(function(btn) {
      btn.classList.remove('active');
    });
    if (el) el.classList.add('active');
    renderCards();
  }

  function renderCards() {
    var container = $('exp-results');
    if (!container) return;

    var data = DATA;
    if (state.activeTag) {
      data = data.filter(function(d) { return d.tags.indexOf(state.activeTag) !== -1; });
    }
    if (state.query) {
      var q = state.query.toLowerCase();
      data = data.filter(function(d) {
        return d.title.toLowerCase().indexOf(q) !== -1 ||
               d.snippet.toLowerCase().indexOf(q) !== -1 ||
               d.category.toLowerCase().indexOf(q) !== -1 ||
               d.id.toLowerCase().indexOf(q) !== -1 ||
               d.tags.some(function(t) { return t.toLowerCase().indexOf(q) !== -1; });
      });
    }

    var badge = $('exp-count-badge');
    if (badge) badge.textContent = data.length;

    container.innerHTML = '';

    if (data.length === 0) {
      container.innerHTML = '<div class="result-placeholder"><p>未找到匹配的案例</p></div>';
      return;
    }

    data.forEach(function(item, index) {
      var sev = SEVERITY[item.severity] || SEVERITY.info;

      var card = document.createElement('div');
      card.className = 'exp-card-item';
      card.style.setProperty('--exp-severity-color', sev.color);
      card.style.animationDelay = (index * 0.04) + 's';

      var tagsHtml = item.tags.map(function(t) {
        return '<span class="exp-card-tag">' + esc(t) + '</span>';
      }).join('');

      card.innerHTML =
        '<div class="exp-card-inner">' +
          '<div class="exp-card-header">' +
            '<span class="exp-card-severity ' + item.severity + '">' + sev.icon + ' ' + sev.label + '</span>' +
            '<span class="exp-card-id">' + esc(item.id) + '</span>' +
          '</div>' +
          '<div class="exp-card-title">' + esc(item.title) + '</div>' +
          '<div class="exp-card-snippet">' + esc(item.snippet) + '</div>' +
          '<div class="exp-card-tags">' + tagsHtml + '</div>' +
          '<div class="exp-card-footer">' +
            '<span class="exp-card-category">' + esc(item.category) + '</span>' +
            '<span class="exp-card-arrow">→</span>' +
          '</div>' +
        '</div>';

      card.onclick = function() { openModal(item); };
      container.appendChild(card);
    });
  }

  function openModal(item) {
    var sev = SEVERITY[item.severity] || SEVERITY.info;

    var tagsHtml = '<span class="exp-card-severity ' + item.severity + '">' + sev.icon + ' ' + sev.label + '</span>' +
      item.tags.map(function(t) { return '<span class="exp-tag-filter">#' + esc(t) + '</span>'; }).join('');
    $('exp-modal-tags').innerHTML = tagsHtml;

    $('exp-modal-title').textContent = item.title;
    $('exp-modal-meta').textContent = item.id + ' · ' + item.category;
    $('exp-modal-condition').textContent = item.condition;
    $('exp-modal-cause').textContent = item.cause;
    $('exp-modal-solution').textContent = item.solution;
    $('exp-modal-source').textContent = item.source;
    $('exp-modal-link').href = item.url;

    $('exp-modal-overlay').classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function closeModal() {
    $('exp-modal-overlay').classList.remove('active');
    document.body.style.overflow = '';
  }

  function esc(s) {
    var d = document.createElement('div');
    d.textContent = s || '';
    return d.innerHTML;
  }

  function bindEvents() {
    var searchInput = $('exp-search-input');
    if (searchInput) {
      searchInput.addEventListener('input', function(e) {
        state.query = e.target.value.trim();
        renderCards();
      });
      searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
          state.query = '';
          searchInput.value = '';
          renderCards();
        }
      });
    }

    var closeBtn = $('exp-modal-close');
    if (closeBtn) closeBtn.addEventListener('click', closeModal);

    var overlay = $('exp-modal-overlay');
    if (overlay) {
      overlay.addEventListener('click', function(e) {
        if (e.target.id === 'exp-modal-overlay') closeModal();
      });
    }

    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') closeModal();
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  window.ExpLib = {
    resume: function() {},
    pause: function() {},
    isReady: function() { return true; }
  };
})();
