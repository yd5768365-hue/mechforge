/**
 * MechForge AI — Experience Library
 * 参考 Knowledge 面板实现
 */
(function() {
  'use strict';

  // 经验数据
  const DATA = [
    { id: 'e001', title: '高周疲劳裂纹起始于表面划伤处', category: '疲劳失效', severity: 'critical', tags: ['疲劳','裂纹','表面处理'], snippet: '零件表面的机械划伤会显著降低疲劳寿命，应力集中系数 Kt 可达 2~4。', condition: '轴类零件在远低于屈服强度的循环载荷下发生断裂，断口呈典型海滩纹特征，裂纹起源于表面划伤或工具痕迹处。', cause: '表面加工缺陷形成应力集中源，局部应力幅超过材料疲劳极限，在循环载荷作用下裂纹萌生并扩展，直至剩余截面不足以承载而断裂。', solution: '1. 提高表面粗糙度要求 Ra ≤ 0.8 μm（关键部位）\n2. 终加工工序改为磨削或抛光，避免车削痕迹\n3. 危险截面处增加圆角 r ≥ 2 mm\n4. 高应力区增加喷丸处理\n5. 检查图纸：危险截面处禁止标注尖角', source: 'GB/T 19624-2019', url: '#' },
    { id: 'e002', title: '过盈配合拆装导致轴承内圈蠕变', category: '配合失效', severity: 'warning', tags: ['轴承','过盈配合','装配'], snippet: '反复拆装破坏配合面氧化膜，配合面微动磨损后内圈发生蠕变旋转。', condition: '轴承内圈相对轴颈产生相对转动，轴颈出现磨损沟槽，轴承发热，振动增大。', cause: '反复拆装破坏配合面微观形貌，氧化膜被磨损导致实际过盈量衰减，在旋转载荷下配合面微动。', solution: '1. 选用合适的过盈量\n2. 拆装时使用专用工具\n3. 频繁拆装改用锁紧套方案\n4. 配合面涂润滑脂', source: 'SKF 轴承手册', url: '#' },
    { id: 'e003', title: '焊接残余应力引发应力腐蚀开裂', category: '腐蚀失效', severity: 'critical', tags: ['焊接','残余应力','应力腐蚀'], snippet: '焊缝热影响区拉伸残余应力与腐蚀性介质协同作用。', condition: '不锈钢或高强钢焊接件在含 Cl⁻ 介质环境中出现延迟裂纹。', cause: '焊接冷却过程在热影响区产生高达 0.8σy 的拉伸残余应力。', solution: '1. 焊后消应力处理\n2. 选用低残余应力焊接工艺\n3. 焊缝区喷丸处理\n4. 必要时更换材料', source: 'ASME PCC-2', url: '#' },
    { id: 'e004', title: '螺栓松动：振动载荷下预紧力衰减', category: '连接失效', severity: 'warning', tags: ['螺栓','预紧力','振动'], snippet: '振动工况下螺纹副微动导致预紧力损失超过 30%。', condition: '设备运行后螺栓出现松动，连接面漏油/漏气。', cause: '横向振动使螺纹面产生微动滑移，摩擦力不足以维持预紧力。', solution: '1. 施加足够预紧力\n2. 采用防松措施\n3. 定期检查\n4. 优化设计', source: 'VDI 2230', url: '#' },
    { id: 'e005', title: '密封圈老化：O 形圈压缩永久变形', category: '密封失效', severity: 'info', tags: ['密封','O形圈','老化'], snippet: '橡胶 O 形圈在高温下压缩永久变形超过 40% 后丧失密封能力。', condition: '液压系统静密封点出现渗漏，O 形圈截面呈扁平状。', cause: '橡胶分子链在温度和介质作用下发生热氧化降解和溶胀。', solution: '1. 根据介质选择材质\n2. 检查槽深\n3. 定期更换\n4. 储存注意', source: 'Parker O-Ring', url: '#' },
    { id: 'e006', title: '齿轮胶合：高速重载下润滑膜破裂', category: '磨损失效', severity: 'critical', tags: ['齿轮','胶合','润滑'], snippet: '节线附近油膜最薄，是胶合失效的高发区域。', condition: '高速齿轮箱齿面出现撕裂划痕，伴随温升异常。', cause: '高速重载下接触区瞬时温升超过润滑油承载极限，油膜破裂。', solution: '1. 润滑油选型\n2. 提高齿面硬度\n3. 跑合处理\n4. 控制油温', source: 'ISO 6336', url: '#' },
    { id: 'e007', title: '铸件气孔：浇注系统设计不当', category: '铸造缺陷', severity: 'info', tags: ['铸造','气孔','工艺'], snippet: '浇注速度过快或排气不畅是气孔的首要原因。', condition: '铸件加工后发现球形或不规则孔洞。', cause: '浇注过程气体不能及时排出，被包裹于金属液中凝固。', solution: '1. 优化浇注系统\n2. 控制浇注速度\n3. 型砂管理\n4. 铸型预热', source: 'AFS 铸造手册', url: '#' },
    { id: 'e008', title: '轴承早期失效：污染颗粒压痕', category: '污染失效', severity: 'warning', tags: ['轴承','污染','维护'], snippet: '固体颗粒污染是轴承过早失效的第一大因素。', condition: '轴承振动和噪声异常，滚道上出现均匀分布的压痕。', cause: '硬质颗粒进入轴承内部，被滚动体碾压形成压痕。', solution: '1. 装配现场管理\n2. 润滑脂选型\n3. 密封系统检查\n4. 润滑油过滤', source: 'NSK 轴承手册', url: '#' },
    { id: 'e009', title: '热处理变形：淬火冷却不均导致翘曲', category: '热处理缺陷', severity: 'info', tags: ['热处理','淬火','变形'], snippet: '薄壁件和细长轴在淬火中最易产生变形。', condition: '零件淬火后尺寸超差，长轴弯曲量超过 0.3 mm/m。', cause: '淬火冷却时零件各截面温度梯度产生不均匀热应力。', solution: '1. 设计上减少截面突变\n2. 正确装挂\n3. 合理选择冷却介质\n4. 工装定型淬火', source: 'ASM Handbook', url: '#' },
    { id: 'e010', title: '管路振动：共振引起疲劳开裂', category: '振动失效', severity: 'critical', tags: ['管路','振动','共振'], snippet: '管路固有频率与激振频率相近时共振幅值可达 20~100 倍。', condition: '流体管路出现周期性振动，最终在焊缝处发生疲劳裂纹。', cause: '流体脉动频率与管路固有频率接近或重合，发生共振。', solution: '1. 频率避开\n2. 增加支撑\n3. 安装减振器\n4. 加装脉动阻尼器', source: 'ASME B31.3', url: '#' },
    { id: 'e011', title: '滑动轴承烧瓦：供油中断或油膜破裂', category: '润滑失效', severity: 'critical', tags: ['滑动轴承','烧瓦','润滑'], snippet: '供油中断 30 秒内巴氏合金即可熔化。', condition: '滑动轴承温度急剧升高，停机后轴瓦巴氏合金熔化剥落。', cause: '润滑油供应中断或轴瓦间隙过大导致油膜破裂。', solution: '1. 设置供油压力保护\n2. 安装备用润滑油泵\n3. 定期检查轴承间隙\n4. 油品管理', source: 'ISO 7902', url: '#' },
    { id: 'e012', title: '压力容器局部过热：热斑检测与处理', category: '热失效', severity: 'warning', tags: ['压力容器','过热','检测'], snippet: '局部过热可导致蠕变和氢损伤。', condition: '高温压力容器外壁出现温度异常偏高区域。', cause: '内壁结垢导致局部传热恶化，使局部金属温度超过蠕变温度。', solution: '1. 红外热像仪扫描\n2. 评估当前状态\n3. 检修清洗\n4. 在线监测', source: 'API 579', url: '#' }
  ];

  // 标签
  const TAGS = [...new Set(DATA.flatMap(d => d.tags))].sort();

  // 严重程度映射
  const SEVERITY = {
    critical: { label: 'CRITICAL', color: '#ff4757' },
    warning:  { label: 'WARNING',  color: '#ffa502' },
    info:     { label: 'INFO',     color: '#00e5ff' }
  };

  // 状态
  let state = { activeTag: null, query: '' };

  // DOM 工具
  const $ = id => document.getElementById(id);

  // 初始化
  function init() {
    console.log('[ExpLib] 初始化...');
    renderTags();
    renderCards();
    bindEvents();
    console.log('[ExpLib] 完成');
  }

  // 渲染标签
  function renderTags() {
    const container = $('exp-tags-container');
    if (!container) return;

    container.innerHTML = '';

    // 全部标签
    const allBtn = document.createElement('span');
    allBtn.className = 'exp-tag-filter' + (state.activeTag === null ? ' active' : '');
    allBtn.textContent = 'ALL';
    allBtn.onclick = () => toggleTag(null, allBtn);
    container.appendChild(allBtn);

    // 分类标签
    TAGS.forEach(tag => {
      const btn = document.createElement('span');
      btn.className = 'exp-tag-filter' + (state.activeTag === tag ? ' active' : '');
      btn.textContent = '#' + tag;
      btn.onclick = () => toggleTag(tag, btn);
      container.appendChild(btn);
    });
  }

  // 切换标签
  function toggleTag(tag, el) {
    state.activeTag = tag;

    // 更新按钮状态
    document.querySelectorAll('.exp-tag-filter').forEach(btn => {
      btn.classList.remove('active');
    });
    if (el) el.classList.add('active');

    renderCards();
  }

  // 渲染卡片
  function renderCards() {
    const container = $('exp-results');
    if (!container) return;

    // 过滤数据
    let data = DATA;
    if (state.activeTag) {
      data = data.filter(d => d.tags.includes(state.activeTag));
    }
    if (state.query) {
      const q = state.query.toLowerCase();
      data = data.filter(d =>
        d.title.toLowerCase().includes(q) ||
        d.snippet.toLowerCase().includes(q) ||
        d.category.toLowerCase().includes(q) ||
        d.tags.some(t => t.toLowerCase().includes(q))
      );
    }

    // 更新计数
    const badge = $('exp-count-badge');
    if (badge) badge.textContent = data.length;

    // 清空并渲染
    container.innerHTML = '';

    if (data.length === 0) {
      container.innerHTML = '<div class="result-placeholder"><p>No records found</p></div>';
      return;
    }

    data.forEach(item => {
      const sev = SEVERITY[item.severity] || SEVERITY.info;

      const card = document.createElement('div');
      card.className = 'exp-card-item';
      card.style.setProperty('--exp-severity-color', sev.color);

      card.innerHTML = `
        <div class="exp-card-severity ${item.severity}">${sev.label}</div>
        <div class="exp-card-title">${escape(item.title)}</div>
        <div class="exp-card-snippet">${escape(item.snippet)}</div>
        <div class="exp-card-footer">
          <span class="exp-card-category">${escape(item.category)}</span>
          <span class="exp-card-arrow">→</span>
        </div>
      `;

      card.onclick = () => openModal(item);
      container.appendChild(card);
    });
  }

  // 打开弹窗
  function openModal(item) {
    const sev = SEVERITY[item.severity] || SEVERITY.info;

    // 标签
    const tagsHtml = `<span class="exp-card-severity ${item.severity}">${sev.label}</span>` +
      item.tags.map(t => `<span class="exp-tag-filter">#${t}</span>`).join('');
    $('exp-modal-tags').innerHTML = tagsHtml;

    // 内容
    $('exp-modal-title').textContent = item.title;
    $('exp-modal-meta').textContent = item.category;
    $('exp-modal-condition').textContent = item.condition;
    $('exp-modal-cause').textContent = item.cause;
    $('exp-modal-solution').textContent = item.solution;
    $('exp-modal-source').textContent = item.source;
    $('exp-modal-link').href = item.url;

    // 显示
    $('exp-modal-overlay').classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  // 关闭弹窗
  function closeModal() {
    $('exp-modal-overlay').classList.remove('active');
    document.body.style.overflow = '';
  }

  // HTML 转义
  function escape(s) {
    const d = document.createElement('div');
    d.textContent = s || '';
    return d.innerHTML;
  }

  // 事件绑定
  function bindEvents() {
    // 搜索
    const searchInput = $('exp-search-input');
    if (searchInput) {
      searchInput.addEventListener('input', e => {
        state.query = e.target.value.trim();
        renderCards();
      });
      searchInput.addEventListener('keydown', e => {
        if (e.key === 'Escape') {
          state.query = '';
          searchInput.value = '';
          renderCards();
        }
      });
    }

    // 弹窗关闭
    $('exp-modal-close').addEventListener('click', closeModal);
    $('exp-modal-overlay').addEventListener('click', e => {
      if (e.target.id === 'exp-modal-overlay') closeModal();
    });
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') closeModal();
    });
  }

  // 启动
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // 暴露 API
  window.ExpLib = {
    resume: () => {},
    pause: () => {},
    isReady: () => true
  };
})();
