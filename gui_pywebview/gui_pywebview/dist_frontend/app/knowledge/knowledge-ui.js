/**
 * KnowledgeUI - 知识库模块
 * 冷锻工业全息风格 - 处理知识库搜索、结果展示等功能
 */

(function () {
  'use strict';

  const { $, escapeHtml } = Utils;

  // ==================== DOM 元素 ====================
  let searchInput = null;
  let searchBtn = null;
  let searchResults = null;
  let knowledgeTags = null;
  let detailOverlay = null;
  let detailDrawer = null;
  let drawerClose = null;
  let drawerTitle = null;
  let drawerBadges = null;
  let drawerMeta = null;
  let drawerBody = null;
  let drawerSource = null;

  // ==================== 状态 ====================
  let aiService = null;
  let currentFilter = 'all';
  const searchHistory = [];
  let currentResults = [];

  // ==================== 模拟数据 - 工业档案 ====================
  const mockResults = [
    {
      title: '液压系统严重故障',
      type: 'critical',
      content: '主液压泵组件因严重污染导致严重故障。油样分析发现金属颗粒。需立即停机并更换完整泵组件，以防止灾难性系统故障和潜在安全隐患。',
      score: 0.98,
      source: '维护日志 #2847',
      date: '2024-03-08',
      tags: ['液压', '紧急', '泵', '安全']
    },
    {
      title: 'CNC主轴振动警告',
      type: 'warning',
      content: 'CNC加工中心主轴检测到过度振动。振动水平超过4.5 mm/s RMS阈值。建议立即检查轴承和刀具平衡，以防止精度损失。',
      score: 0.92,
      source: '状态监测 #4521',
      date: '2024-03-10',
      tags: ['数控', '振动', '主轴', '警告']
    },
    {
      title: '五轴CNC校准程序',
      type: 'manual',
      content: '五轴CNC加工中心完整校准程序。包括旋转轴对准、主轴跳动验证和使用激光干涉仪的刀具长度偏移测量。',
      score: 0.89,
      source: '技术手册 v3.2',
      date: '2024-02-15',
      tags: ['数控', '校准', '程序', '五轴']
    },
    {
      title: '轴承温度监测',
      type: 'info',
      content: '主驱动轴承标准工作温度范围：40-65°C。警告阈值设定为75°C。临界停机温度为85°C。润滑系统压力必须保持在2.5-3.0 bar。',
      score: 0.85,
      source: '设备规格 #1204',
      date: '2024-01-28',
      tags: ['轴承', '温度', '监测', '信息']
    },
    {
      title: 'IG-4500减速机技术规格',
      type: 'spec',
      content: '工业减速机IG-4500规格：最大扭矩4500 Nm，减速比15.5:1，效率96%。最大输入转速1800 RPM。维护间隔：8000运行小时。油品类型：ISO VG 320。',
      score: 0.83,
      source: '规格表 IG-4500',
      date: '2024-01-20',
      tags: ['减速机', '规格', '扭矩', 'ig-4500']
    },
    {
      title: '焊接机器人路径优化',
      type: 'case',
      content: '案例研究：使用遗传算法优化汽车底盘装配焊接机器人路径。周期时间减少15%，焊接质量一致性提高。功耗降低8%。',
      score: 0.81,
      source: '案例研究 #89',
      date: '2024-02-28',
      tags: ['焊接', '机器人', '优化', '案例']
    },
    {
      title: '急停电路故障',
      type: 'critical',
      content: '严重安全问题：检测到急停电路间歇性故障。急停按钮响应时间超过500ms限制。恢复生产前需立即维修。已启动安全锁定程序。',
      score: 0.97,
      source: '安全报告 #S-2024-15',
      date: '2024-03-09',
      tags: ['安全', '紧急', '急停', '电路']
    },
    {
      title: '锻压机预防性维护计划',
      type: 'manual',
      content: '2500吨锻压机季度预防性维护计划。包括液压系统检查、模具对准检查和润滑系统保养。预计停机时间：16小时。',
      score: 0.78,
      source: '维护计划 2024年Q1',
      date: '2024-01-05',
      tags: ['维护', '计划', '锻造', '压机']
    },
    {
      title: '伺服电机过流警告',
      type: 'warning',
      content: 'X轴伺服电机在快速定位时电流超过额定值15%。检查机械卡滞并验证负载惯量计算。编码器反馈信号正常。',
      score: 0.88,
      source: '驱动诊断 #3382',
      date: '2024-03-07',
      tags: ['伺服', '电机', '过流', '警告']
    },
    {
      title: '激光切割参数指南',
      type: 'info',
      content: '6mm不锈钢最佳切割参数：功率3000W，速度1.2 m/min，压力12 bar，焦点-1.5mm。切缝宽度0.15mm。辅助气体：氮气纯度99.99%。',
      score: 0.86,
      source: '工艺指南 L-2024',
      date: '2024-02-20',
      tags: ['激光', '切割', '参数', '信息']
    },
    {
      title: '刀具寿命管理系统',
      type: 'spec',
      content: '自动化刀具寿命监测系统规格。跟踪刀具磨损，预测剩余寿命，并触发自动换刀。与ERP集成进行库存管理。',
      score: 0.80,
      source: '系统规格 TLMS-2.0',
      date: '2024-01-15',
      tags: ['刀具', '寿命', '管理', '规格']
    },
    {
      title: '热处理工艺偏差',
      type: 'case',
      content: '根本原因分析：淬火槽温度超过35°C限制，导致硬度不足。实施二次冷却系统和连续温度监测。',
      score: 0.84,
      source: '质量报告 #Q-89',
      date: '2024-02-10',
      tags: ['热处理', '工艺', '质量', '案例']
    },
    {
      title: '气动系统压力下降',
      type: 'warning',
      content: '主气动管路在高峰生产时段压力从6.0 bar降至4.8 bar。发现分配歧管多处漏气。生产效率降低12%。',
      score: 0.87,
      source: '设施报告 #F-2024-23',
      date: '2024-03-11',
      tags: ['气动', '压力', '泄漏', '警告']
    },
    {
      title: '机器人手臂防碰撞设置',
      type: 'manual',
      content: 'FANUC机器人手臂防碰撞系统配置指南。包括安全区域设置、干涉区域编程和急停集成程序。',
      score: 0.91,
      source: '机器人编程指南 v4.1',
      date: '2024-02-05',
      tags: ['机器人', '安全', '碰撞', '发那科']
    },
    {
      title: '钛合金加工参数',
      type: 'spec',
      content: 'Ti-6Al-4V钛合金加工参数。切削速度30-50 m/min，进给率0.1-0.15 mm/rev，切削深度2-5mm。需要高压冷却系统。',
      score: 0.82,
      source: '加工手册 Ti-2024',
      date: '2024-01-25',
      tags: ['钛合金', '加工', '参数', '规格']
    },
    {
      title: '输送带跑偏检测',
      type: 'info',
      content: '输送带跑偏自动视觉检测系统。使用激光线投影和摄像头分析。检测精度±2mm，响应时间<100ms。',
      score: 0.79,
      source: '自动化规格 AS-2024-07',
      date: '2024-02-18',
      tags: ['输送带', '视觉', '自动化', '检测']
    },
    {
      title: '注塑成型缺陷分析',
      type: 'case',
      content: 'ABS塑料件缩痕和翘曲系统分析。根本原因：冷却时间不足和壁厚不均匀。优化浇口位置和冷却通道设计。',
      score: 0.86,
      source: '成型案例研究 #45',
      date: '2024-03-01',
      tags: ['注塑', '成型', '缺陷', '塑料']
    },
    {
      title: '变压器漏油严重',
      type: 'critical',
      content: '主电源变压器T-301检测到严重漏油。24小时内油位下降15cm。存在过热和潜在火灾危险。需立即停机和控制。',
      score: 0.96,
      source: '电气安全报告 #E-112',
      date: '2024-03-12',
      tags: ['变压器', '漏油', '电气', '紧急']
    },
    {
      title: '增材制造后处理',
      type: 'manual',
      content: 'SLM金属件后处理标准操作程序。包括支撑去除、热处理、表面精整和质量检验规程。',
      score: 0.88,
      source: '增材制造工艺手册 v2.0',
      date: '2024-01-30',
      tags: ['增材制造', '后处理', '金属', '工艺']
    },
    {
      title: '暖通空调过滤器更换计划',
      type: 'info',
      content: '洁净室暖通空调过滤器维护计划。预过滤器每3个月，HEPA过滤器每年。需要压差监测。过滤器压差保持<15 Pa。',
      score: 0.75,
      source: '设施维护 FM-2024',
      date: '2024-02-12',
      tags: ['暖通', '过滤器', '洁净室', '维护']
    },
    {
      title: '三坐标测量机校准',
      type: 'spec',
      content: '使用认证量块和球体标准器进行三坐标测量机校准程序。需要20±1°C温度控制。1000mm范围测量不确定度±1.5μm。',
      score: 0.90,
      source: '计量规格 MS-2024-03',
      date: '2024-01-18',
      tags: ['三坐标', '校准', '计量', '测量']
    },
    {
      title: '装配线扭矩监测',
      type: 'warning',
      content: '3号线检测到扭矩扳手校准漂移。多个紧固件显示与规格偏差8-12%。需立即重新校准和零件检查。',
      score: 0.89,
      source: '质量警报 #QA-2024-08',
      date: '2024-03-06',
      tags: ['扭矩', '装配', '校准', '质量']
    },
    {
      title: '工业以太网网络安全',
      type: 'info',
      content: 'OT/IT集成的网络分段指南。为PLC网络实施VLAN，启用端口安全，部署工业防火墙。需要定期漏洞评估。',
      score: 0.77,
      source: '网络安全指南 CS-2024',
      date: '2024-02-25',
      tags: ['网络', '安全', '以太网', 'PLC']
    },
    {
      title: '压铸模具寿命预测',
      type: 'case',
      content: '使用热疲劳分析开发铝合金压铸模具寿命预测模型。通过优化冷却设计将模具寿命从8万次延长至12万次。',
      score: 0.85,
      source: '压铸研究 #DC-12',
      date: '2024-02-08',
      tags: ['压铸', '模具', '预测', '铝合金']
    },
    {
      title: '桥式起重机检查规程',
      type: 'manual',
      content: '10吨桥式起重机月度检查清单。包括钢丝绳检查、制动测试、限位开关验证和负载测试程序。',
      score: 0.83,
      source: '起重设备手册',
      date: '2024-01-12',
      tags: ['起重机', '检查', '安全', '起重']
    },
    {
      title: '超声波焊接质量评估',
      type: 'spec',
      content: '锂电池极耳超声波焊接质量标准。焊接强度>50N，拉拔测试验证，X射线检测空隙。频率20kHz，振幅50μm。',
      score: 0.81,
      source: '电池制造规格',
      date: '2024-03-03',
      tags: ['超声波', '焊接', '电池', '质量']
    },
    {
      title: '冷却液系统细菌污染',
      type: 'warning',
      content: '加工冷却液系统检测到高细菌数(>10^6 CFU/ml)。产生异味和潜在皮肤刺激。需要系统冲洗和杀菌处理。',
      score: 0.84,
      source: '环境报告 #ENV-45',
      date: '2024-03-05',
      tags: ['冷却液', '细菌', '污染', '加工']
    },
    {
      title: 'AGV路径规划优化',
      type: 'case',
      content: '使用A*算法和拥塞避免为仓库AGV车队实施动态路径规划。运输时间减少22%，消除交通堵塞。',
      score: 0.87,
      source: '物流优化 #LOG-09',
      date: '2024-02-22',
      tags: ['AGV', '路径规划', '仓库', '优化']
    },
    {
      title: '等离子切割喷嘴磨损分析',
      type: 'info',
      content: '等离子切割喷嘴磨损模式研究。200A时电极寿命平均2小时。1.5小时后孔口侵蚀影响切割质量。建议预测性更换。',
      score: 0.78,
      source: '切割技术报告',
      date: '2024-01-22',
      tags: ['等离子', '切割', '喷嘴', '磨损']
    },
    {
      title: 'SCADA系统备份程序',
      type: 'manual',
      content: 'SCADA历史数据库每日自动备份配置。包括标签数据库、报警日志和趋势数据。保留策略：合规要求7年。',
      score: 0.80,
      source: 'IT运维手册 v3.5',
      date: '2024-02-14',
      tags: ['SCADA', '备份', '数据库', '合规']
    },
    {
      title: '齿轮齿面疲劳失效',
      type: 'critical',
      content: '主驱动减速机发生灾难性齿轮齿失效。多个齿面观察到点蚀和剥落。根本原因：高负载下润滑膜厚度不足。',
      score: 0.95,
      source: '失效分析 #FA-2024-03',
      date: '2024-03-13',
      tags: ['齿轮', '疲劳', '失效', '润滑']
    },
    {
      title: '视觉系统照明指南',
      type: 'spec',
      content: '机器视觉照明设置规格。表面检查用LED环形灯，反光零件用漫射穹顶照明，高速应用用频闪。色温6500K。',
      score: 0.76,
      source: '视觉系统设计指南',
      date: '2024-01-28',
      tags: ['视觉', '照明', '检查', 'LED']
    },
    {
      title: '隔振垫选型',
      type: 'info',
      content: '精密设备隔振垫选型指南。CNC机床要求自然频率<10Hz。考虑负载能力和环境抗性。',
      score: 0.74,
      source: '设施工程 FE-2024',
      date: '2024-02-06',
      tags: ['振动', '隔振', '数控', '精密']
    },
    {
      title: '电阻点焊电极修整',
      type: 'manual',
      content: '点焊电极修整计划和程序。每500个焊点或尖端直径增加20%时修整。保持适当端面几何形状以确保焊接质量一致。',
      score: 0.85,
      source: '焊接程序 WP-2024-11',
      date: '2024-03-02',
      tags: ['点焊', '电极', '修整', '维护']
    },
    {
      title: '压缩空气干燥机维护',
      type: 'warning',
      content: '冷冻式空气干燥机性能下降。露点从3°C升至8°C。冷凝器盘管需要清洁和制冷剂液位检查。气动系统存在湿气风险。',
      score: 0.82,
      source: '公用事业报告 #U-2024-19',
      date: '2024-03-08',
      tags: ['压缩空气', '干燥机', '维护', '露点']
    },
    {
      title: '有限元分析最佳实践',
      type: 'case',
      content: '建立焊接接头结构验证的FEA工作流程。网格收敛研究、材料属性校准和与物理测试的相关性。原型迭代减少40%。',
      score: 0.88,
      source: '仿真案例研究 #SIM-05',
      date: '2024-02-16',
      tags: ['FEA', '仿真', '焊接', '验证']
    },
    {
      title: '喷漆房过滤器堵塞警报',
      type: 'warning',
      content: '喷漆房过滤器压差超过250Pa限制。气流减少影响喷漆质量。下一批生产前需要更换过滤器。',
      score: 0.81,
      source: '喷漆车间报告 #PS-33',
      date: '2024-03-04',
      tags: ['喷漆', '过滤器', '气流', '警告']
    },
    {
      title: '滚珠丝杠预紧调整',
      type: 'manual',
      content: '机床轴滚珠丝杠预紧调整程序。用千分表测量轴向间隙，调整垫片厚度以达到动态负载额定值2-3%的预紧力。',
      score: 0.87,
      source: '机床维修手册',
      date: '2024-01-20',
      tags: ['滚珠丝杠', '预紧', '调整', '机床']
    },
    {
      title: '热成像检查计划',
      type: 'info',
      content: '电气柜和旋转设备季度热成像检查计划。建立基线热特征。温度升高超过基线10°C触发调查。',
      score: 0.79,
      source: '预测性维护指南',
      date: '2024-02-28',
      tags: ['热成像', '检查', '预测', '维护']
    },
    {
      title: '液压蓄能器预充检查',
      type: 'spec',
      content: '液压蓄能器预充压力检查和调整程序。与系统隔离，排空液体，测量氮气压力。预充应为最小系统压力的80-90%。',
      score: 0.84,
      source: '液压系统手册 v2.8',
      date: '2024-01-15',
      tags: ['液压', '蓄能器', '预充', '氮气']
    },
    {
      title: '协作机器人安全区配置',
      type: 'manual',
      content: '协作机器人安全区设置指南。配置速度和分离监测、手动引导模式和功率/力限制。需要风险评估文件。',
      score: 0.89,
      source: '协作机器人集成指南',
      date: '2024-02-09',
      tags: ['协作机器人', '安全', '协作', '机器人']
    },
    {
      title: '表面粗糙度测量规程',
      type: 'spec',
      content: '使用轮廓仪进行表面粗糙度测量标准规程。截止长度0.8mm，评定长度4mm。报告Ra、Rz、Rmax参数。用认证粗糙度标准器校准。',
      score: 0.83,
      source: '质量程序 QP-2024-17',
      date: '2024-03-07',
      tags: ['表面', '粗糙度', '测量', '质量']
    },
    {
      title: '感应淬火工艺控制',
      type: 'case',
      content: '优化齿轮齿感应淬火工艺。功率85kW，频率10kHz，停留时间2.5s。达到58-62 HRC表面硬度，有效硬化层深度2mm。',
      score: 0.86,
      source: '热处理案例 #HT-23',
      date: '2024-02-01',
      tags: ['感应', '淬火', '齿轮', '热处理']
    },
    {
      title: '机床基础振动分析',
      type: 'warning',
      content: '通过共享基础传递到相邻机床的过度振动。附近精密磨床测量到6.2 mm/s RMS。建议基础隔振或独立垫块。',
      score: 0.85,
      source: '振动研究 #VS-2024-04',
      date: '2024-03-09',
      tags: ['振动', '基础', '隔振', '精密']
    },
    {
      title: '静电放电防护',
      type: 'info',
      content: '电子装配区ESD防护要求。保持40-60%湿度，接地工作站，腕带<1MΩ电阻。EPA标识和培训是强制性的。',
      score: 0.77,
      source: 'ESD控制程序手册',
      date: '2024-02-19',
      tags: ['ESD', '电子', '防护', '装配']
    },
    {
      title: '喷丸覆盖率检查',
      type: 'manual',
      content: '喷丸工艺控制的阿尔门试片测试程序。强度0.4-0.5mmA，覆盖率200%。按SAE J442标准计算试片放置和暴露时间。',
      score: 0.82,
      source: '表面强化手册',
      date: '2024-01-24',
      tags: ['喷丸', '阿尔门', '覆盖', '检查']
    }
  ];

  // 关键词列表用于高亮
  const keywordsToHighlight = [
    'critical', 'failure', 'warning', 'emergency', 'safety', 'hydraulic',
    'CNC', 'spindle', 'bearing', 'gearbox', 'torque', 'welding', 'robot',
    'temperature', 'pressure', 'vibration', 'calibration', 'maintenance',
    'servo', 'motor', 'laser', 'cutting', 'heat', 'treatment', 'quench',
    'pneumatic', 'compressor', 'air', 'leak', 'filter', 'oil', 'contamination',
    'inspection', 'quality', 'defect', 'analysis', 'optimization', 'efficiency',
    'production', 'schedule', 'planning', 'inventory', 'supply-chain',
    'automation', 'vision', 'sensor', 'PLC', 'SCADA', 'IoT', 'digital',
    'simulation', 'FEA', 'CAD', 'CAM', 'programming', 'g-code', 'macro',
    'grinding', 'milling', 'turning', 'drilling', 'tapping', 'boring',
    'casting', 'forging', 'stamping', 'forming', 'bending', 'rolling',
    'assembly', 'fabrication', 'machining', 'manufacturing', 'processing',
    'measurement', 'metrology', 'CMM', 'gauge', 'calibration', 'tolerance',
    'surface', 'roughness', 'hardness', 'strength', 'fatigue', 'stress',
    'corrosion', 'coating', 'plating', 'anodizing', 'painting', 'finishing',
    'cleaning', 'degreasing', 'blasting', 'peening', 'treatment',
    'preventive', 'predictive', 'reliability', 'MTBF', 'MTTR', 'OEE',
    'lean', 'six-sigma', 'kaizen', 'TPM', '5S', 'continuous-improvement',
    'energy', 'power', 'consumption', 'savings', 'efficiency', 'sustainability',
    'safety', 'hazard', 'risk', 'PPE', 'LOTO', 'ergonomics', 'compliance',
    'ISO', 'ASME', 'ASTM', 'SAE', 'DIN', 'JIS', 'GB', 'standards',
    'training', 'certification', 'documentation', 'procedure', 'protocol',
    'troubleshooting', 'diagnostic', 'repair', 'replacement', 'overhaul',
    'commissioning', 'installation', 'setup', 'configuration', 'validation'
  ];

  // ==================== 动态效果 ====================
  let dustInterval = null;
  let pulseInterval = null;
  let isPanelVisible = false;

  /**
   * 初始化知识库模块
   * @param {Object} service - AIService 实例
   */
  function init(service) {
    aiService = service;

    searchInput = $('knowledge-search');
    searchBtn = $('search-btn');
    searchResults = $('search-results');
    knowledgeTags = $('knowledge-tags');

    // 详情抽屉元素
    detailOverlay = $('detail-overlay');
    detailDrawer = $('detail-drawer');
    drawerClose = $('drawer-close');
    drawerTitle = $('drawer-title');
    drawerBadges = $('drawer-badges');
    drawerMeta = $('drawer-meta');
    drawerBody = $('drawer-body');
    drawerSource = $('drawer-source');

    setupEventListeners();
    setupTagFilters();
    setupIndustrialEffects();
    setupDrawerListeners();

    // 初始显示一些结果
    displayResults(mockResults.slice(0, 6));
  }

  /**
   * 设置工业风动态效果
   */
  function setupIndustrialEffects() {
    // 监听面板可见性变化
    const knowledgePanel = $('knowledge-panel');
    if (!knowledgePanel) return;

    // 使用 MutationObserver 监听面板显示状态
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
          const isActive = knowledgePanel.classList.contains('active');
          if (isActive && !isPanelVisible) {
            isPanelVisible = true;
            startIndustrialEffects();
          } else if (!isActive && isPanelVisible) {
            isPanelVisible = false;
            stopIndustrialEffects();
          }
        }
      });
    });

    observer.observe(knowledgePanel, { attributes: true });

    // 初始检查
    if (knowledgePanel.classList.contains('active')) {
      isPanelVisible = true;
      startIndustrialEffects();
    }
  }

  /**
   * 启动工业风效果
   */
  function startIndustrialEffects() {
    createMetalDust();
    startHeatPulse();
  }

  /**
   * 停止工业风效果
   */
  function stopIndustrialEffects() {
    if (dustInterval) {
      clearInterval(dustInterval);
      dustInterval = null;
    }
    if (pulseInterval) {
      clearInterval(pulseInterval);
      pulseInterval = null;
    }
    // 清理现有粒子
    const dustContainer = $('metal-dust-container');
    if (dustContainer) {
      dustContainer.innerHTML = '';
    }
  }

  /**
   * 创建金属尘埃粒子 - 冷却金属粉尘沉降效果
   */
  function createMetalDust() {
    const dustContainer = $('metal-dust-container');
    if (!dustContainer) return;

    // 初始创建 6-8 个粒子
    const particleCount = 6 + Math.floor(Math.random() * 3);
    for (let i = 0; i < particleCount; i++) {
      setTimeout(() => spawnMetalParticle(dustContainer), i * 800);
    }

    // 持续生成新粒子（间隔较长，保持稀疏感）
    dustInterval = setInterval(() => {
      if (dustContainer.childElementCount < 8) {
        spawnMetalParticle(dustContainer);
      }
    }, 3000 + Math.random() * 2000);
  }

  /**
   * 生成单个金属尘埃粒子
   */
  function spawnMetalParticle(container) {
    const particle = document.createElement('div');
    particle.className = 'metal-particle';
    
    // 随机选择粒子类型（暗青色为主，少量暗橙色）
    const rand = Math.random();
    if (rand > 0.92) {
      particle.classList.add('orange-dust');
    } else if (rand > 0.65) {
      particle.classList.add('iron-dust');
    } else {
      particle.classList.add('cyan-dust');
    }

    // 随机大小（2-5px，极细小）
    const size = 2 + Math.random() * 3;
    particle.style.width = `${size}px`;
    particle.style.height = `${size}px`;

    // 随机水平位置
    particle.style.left = `${Math.random() * 100}%`;
    particle.style.top = '-10px';

    // 极慢的下沉速度（15-25秒）
    const duration = 15 + Math.random() * 10;
    particle.style.animationDuration = `${duration}s`;

    // 随机水平漂移
    const drift = (Math.random() - 0.5) * 60;
    particle.style.setProperty('--drift', `${drift}px`);

    container.appendChild(particle);

    // 动画结束后移除
    setTimeout(() => {
      if (particle.parentNode) {
        particle.remove();
      }
    }, duration * 1000);
  }

  /**
   * 启动热应力波脉冲
   */
  function startHeatPulse() {
    const pulseContainer = $('heat-pulse-container');
    if (!pulseContainer) return;

    // 立即创建第一个脉冲
    setTimeout(() => spawnHeatPulse(pulseContainer), 2000);

    // 每 10-15 秒随机生成脉冲
    const scheduleNextPulse = () => {
      const delay = 10000 + Math.random() * 5000;
      pulseInterval = setTimeout(() => {
        spawnHeatPulse(pulseContainer);
        scheduleNextPulse();
      }, delay);
    };

    scheduleNextPulse();
  }

  /**
   * 生成热应力波脉冲
   */
  function spawnHeatPulse(container) {
    const pulse = document.createElement('div');
    pulse.className = 'heat-pulse';

    // 随机选择脉冲颜色（青色为主，偶尔红色/橙色）
    const rand = Math.random();
    if (rand > 0.85) {
      pulse.classList.add('red');
    } else if (rand > 0.65) {
      pulse.classList.add('orange');
    } else {
      pulse.classList.add('cyan');
    }

    // 随机位置（网格节点附近）
    const x = 15 + Math.random() * 70;
    const y = 20 + Math.random() * 60;
    pulse.style.left = `${x}%`;
    pulse.style.top = `${y}%`;

    container.appendChild(pulse);

    // 动画结束后移除
    setTimeout(() => {
      if (pulse.parentNode) {
        pulse.remove();
      }
    }, 3000);
  }

  /**
   * 设置事件监听器
   */
  function setupEventListeners() {
    searchInput?.addEventListener('keypress', e => {
      if (e.key === 'Enter') performSearch();
    });

    searchBtn?.addEventListener('click', performSearch);
  }

  /**
   * 设置标签过滤器 - 钛合金铭牌交互
   */
  function setupTagFilters() {
    if (!knowledgeTags) return;

    const tags = knowledgeTags.querySelectorAll('.knowledge-tag');
    tags.forEach(tag => {
      tag.addEventListener('click', () => {
        // 如果点击的是已选中的标签，不执行任何操作
        if (tag.classList.contains('active')) return;

        // 移除所有 active 状态并重置动画
        tags.forEach(t => {
          t.classList.remove('active');
          // 强制重绘以重置动画
          t.style.animation = 'none';
          void t.offsetHeight; // 触发重排
          t.style.animation = '';
        });

        // 添加当前 active - 触发热应力抖动动画
        tag.classList.add('active');

        // 播放机械点击音效（如果支持）
        playMechanicalClick();

        // 创建热应力波纹效果
        createHeatRipple(tag);

        // 更新过滤器
        currentFilter = tag.dataset.filter;

        // 滚动到可视区域（如果标签在边缘）
        tag.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });

        // 如果有搜索内容，重新搜索
        if (searchInput?.value.trim()) {
          performSearch();
        }
      });

      // 鼠标悬停效果 - 轻微热应力预激活
      tag.addEventListener('mouseenter', () => {
        if (!tag.classList.contains('active')) {
          tag.style.transform = 'translateY(-2px) scale(1.02)';
        }
      });

      tag.addEventListener('mouseleave', () => {
        if (!tag.classList.contains('active')) {
          tag.style.transform = '';
        }
      });
    });
  }

  /**
   * 播放机械点击音效
   */
  function playMechanicalClick() {
    try {
      // 使用 Web Audio API 创建简单的机械点击声
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();

      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);

      // 机械点击声参数
      oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
      oscillator.frequency.exponentialRampToValueAtTime(100, audioContext.currentTime + 0.05);

      gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.05);

      oscillator.start(audioContext.currentTime);
      oscillator.stop(audioContext.currentTime + 0.05);
    } catch (e) {
      // 音频播放失败时静默处理
    }
  }

  /**
   * 创建热应力波纹效果
   * @param {HTMLElement} tag - 点击的标签元素
   */
  function createHeatRipple(tag) {
    const rect = tag.getBoundingClientRect();
    const ripple = document.createElement('div');
    ripple.className = 'tag-heat-ripple';
    ripple.style.cssText = `
      position: absolute;
      left: 50%;
      top: 50%;
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(255, 80, 60, 0.4) 0%, transparent 70%);
      transform: translate(-50%, -50%);
      pointer-events: none;
      z-index: -1;
    `;

    // 添加动画
    ripple.animate([
      { width: '10px', height: '10px', opacity: 0.6 },
      { width: '60px', height: '60px', opacity: 0 }
    ], {
      duration: 400,
      easing: 'ease-out'
    }).onfinish = () => ripple.remove();

    tag.appendChild(ripple);
  }

  /**
   * 执行搜索
   */
  async function performSearch() {
    const query = searchInput?.value.trim();
    if (!query) {
      // 如果没有搜索词，显示所有结果
      displayResults(mockResults.slice(0, 8));
      return;
    }

    showLoading();
    searchHistory.unshift(query);
    if (searchHistory.length > 10) searchHistory.pop();

    // 模拟搜索延迟
    await new Promise(resolve => setTimeout(resolve, 800));

    try {
      // 过滤结果
      const results = filterResults(mockResults, query, currentFilter);
      displayResults(results, query);
    } catch (error) {
      showError(error.message);
    }
  }

  /**
   * 过滤结果
   * @param {Array} results - 原始结果
   * @param {string} query - 搜索词
   * @param {string} filter - 过滤器类型
   */
  function filterResults(results, query, filter) {
    const filtered = results.filter(r => {
      const matchQuery = !query || 
        r.title.toLowerCase().includes(query.toLowerCase()) ||
        r.content.toLowerCase().includes(query.toLowerCase()) ||
        r.tags.some(t => t.toLowerCase().includes(query.toLowerCase()));
      
      const matchFilter = filter === 'all' || r.type === filter;
      
      return matchQuery && matchFilter;
    });

    // 按分数排序
    return filtered.sort((a, b) => b.score - a.score);
  }

  /**
   * 显示加载状态 - 工业风格
   */
  function showLoading() {
    if (searchResults) {
      searchResults.innerHTML = `
        <div class="industrial-loader">
          <div class="bar"></div>
          <div class="bar"></div>
          <div class="bar"></div>
          <div class="bar"></div>
          <div class="bar"></div>
        </div>
        <div style="text-align: center; color: var(--ind-text-dim); font-size: 12px; letter-spacing: 2px;">
          RETRIEVING DATA...
        </div>
      `;
    }
  }

  /**
   * 显示错误
   * @param {string} message - 错误信息
   */
  function showError(message) {
    if (searchResults) {
      searchResults.innerHTML = `
        <div class="result-placeholder">
          <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="#ff4757" stroke-width="1.5">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          <p style="color: var(--ind-alert);">SYSTEM ERROR</p>
          <span style="font-size: 11px; color: var(--ind-text-dim);">${escapeHtml(message)}</span>
        </div>
      `;
    }
  }

  /**
   * 获取类型标签样式
   * @param {string} type - 类型
   */
  function getTypeBadge(type) {
    const badges = {
      critical: { text: 'CRITICAL', class: 'critical' },
      warning: { text: 'WARNING', class: 'warning' },
      info: { text: 'INFO', class: 'info' },
      manual: { text: 'MANUAL', class: '' },
      spec: { text: 'SPEC', class: '' },
      case: { text: 'CASE', class: '' },
      procedure: { text: 'PROCEDURE', class: '' },
      drawing: { text: 'DRAWING', class: '' },
      standard: { text: 'STANDARD', class: '' },
      maintenance: { text: 'MAINTENANCE', class: '' },
      safety: { text: 'SAFETY', class: '' }
    };
    const badge = badges[type] || { text: type.toUpperCase(), class: '' };
    return `<span class="result-type ${badge.class}">${badge.text}</span>`;
  }

  /**
   * 高亮文本中的关键词
   * @param {string} text - 原始文本
   * @param {string} query - 搜索词
   */
  function highlightKeywords(text, query) {
    let highlighted = escapeHtml(text);

    // 高亮搜索词
    if (query) {
      const queryRegex = new RegExp(`(${escapeHtml(query)})`, 'gi');
      highlighted = highlighted.replace(queryRegex, '<span class="highlight">$1</span>');
    }

    // 高亮预定义关键词
    keywordsToHighlight.forEach(keyword => {
      const keywordRegex = new RegExp(`\\b(${keyword})\\b`, 'gi');
      highlighted = highlighted.replace(keywordRegex, '<span class="highlight">$1</span>');
    });

    return highlighted;
  }

  /**
   * 显示搜索结果 - 钛合金铭牌卡片
   * @param {Array} results - 结果数组
   * @param {string} query - 搜索词
   */
  function displayResults(results, query = '') {
    if (!searchResults) return;

    // 存储当前结果
    currentResults = results || [];

    if (!results || results.length === 0) {
      searchResults.innerHTML = `
        <div class="result-placeholder">
          <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="1">
            <circle cx="11" cy="11" r="8"/>
            <path d="M21 21l-4.35-4.35"/>
          </svg>
          <p>NO DATA FOUND</p>
          <span style="font-size: 11px; color: var(--ind-text-dim);">Try adjusting your search terms or filters</span>
        </div>
      `;
      return;
    }

    searchResults.innerHTML = results.map((result, index) => `
      <div class="result-item ${result.type}" data-index="${index}" style="animation: slideIn 0.4s ease-out ${index * 0.08}s both;">
        <div class="result-title">
          ${getTypeBadge(result.type)}
          ${escapeHtml(result.title)}
        </div>
        <div class="result-snippet">${highlightKeywords(result.content, query)}</div>
        <div class="result-meta">
          <span>RELEVANCE: ${(result.score * 100).toFixed(0)}%</span>
          <span>SRC: ${escapeHtml(result.source)}</span>
          <span>DATE: ${result.date}</span>
        </div>
      </div>
    `).join('');

    // 添加卡片入场动画后的3D效果初始化
    setTimeout(() => {
      initCard3DEffects();
    }, results.length * 80 + 200);
  }

  /**
   * 初始化卡片3D悬停效果
   */
  function initCard3DEffects() {
    const cards = searchResults.querySelectorAll('.result-item');
    cards.forEach((card) => {
      card.addEventListener('mouseenter', () => {
        // 播放轻微的机械声
        playCardHoverSound();
      });

      card.addEventListener('click', () => {
        // 点击时创建热应力波纹
        createCardClickEffect(card);

        // 获取对应的数据并打开抽屉
        const index = parseInt(card.dataset.index);
        if (currentResults[index]) {
          openDetailDrawer(currentResults[index]);
        }
      });
    });
  }

  /**
   * 播放卡片悬停音效
   */
  function playCardHoverSound() {
    try {
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();

      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);

      // 低沉的机械嗡鸣声
      oscillator.frequency.setValueAtTime(120, audioContext.currentTime);
      oscillator.frequency.exponentialRampToValueAtTime(80, audioContext.currentTime + 0.15);

      gainNode.gain.setValueAtTime(0.03, audioContext.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.15);

      oscillator.start(audioContext.currentTime);
      oscillator.stop(audioContext.currentTime + 0.15);
    } catch (e) {
      // 静默处理
    }
  }

  /**
   * 创建卡片点击效果
   * @param {HTMLElement} card - 卡片元素
   */
  function createCardClickEffect(card) {
    // 添加点击时的热应力闪烁
    card.style.animation = 'none';
    void card.offsetHeight; // 触发重排
    card.style.animation = 'heatStressShake 0.3s ease-out';

    // 创建边缘发光效果
    const glow = document.createElement('div');
    glow.style.cssText = `
      position: absolute;
      inset: -2px;
      border-radius: 8px;
      background: linear-gradient(165deg, rgba(0, 230, 255, 0.5), transparent 50%, rgba(255, 107, 53, 0.3));
      opacity: 0;
      pointer-events: none;
      z-index: -1;
    `;
    card.appendChild(glow);

    glow.animate([
      { opacity: 0 },
      { opacity: 1 },
      { opacity: 0 }
    ], {
      duration: 400,
      easing: 'ease-out'
    }).onfinish = () => glow.remove();
  }

  // ==================== 详情抽屉功能 ====================

  /**
   * 设置抽屉事件监听器
   */
  function setupDrawerListeners() {
    // 关闭按钮
    drawerClose?.addEventListener('click', closeDetailDrawer);

    // 点击遮罩关闭
    detailOverlay?.addEventListener('click', closeDetailDrawer);

    // ESC键关闭
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && detailDrawer?.classList.contains('active')) {
        closeDetailDrawer();
      }
    });
  }

  /**
   * 打开详情抽屉
   * @param {Object} result - 知识库条目数据
   */
  function openDetailDrawer(result) {
    if (!detailOverlay || !detailDrawer) return;

    // 填充内容
    if (drawerTitle) drawerTitle.textContent = result.title;
    if (drawerBadges) drawerBadges.innerHTML = getTypeBadge(result.type);
    if (drawerMeta) {
      drawerMeta.innerHTML = `
        <span>RELEVANCE: ${(result.score * 100).toFixed(0)}%</span>
        <span>SRC: ${escapeHtml(result.source)}</span>
        <span>DATE: ${result.date}</span>
        <span>ID: ${generateArchiveId()}</span>
      `;
    }

    // 渲染Markdown内容
    if (drawerBody) {
      drawerBody.innerHTML = generateDetailContent(result);
    }

    // 设置来源链接
    if (drawerSource) {
      drawerSource.href = `#archive-${result.source.replace(/\s+/g, '-').toLowerCase()}`;
    }

    // 播放打开音效
    playDrawerOpenSound();

    // 显示抽屉
    detailOverlay.classList.add('active');
    detailDrawer.classList.add('active');

    // 禁止背景滚动
    document.body.style.overflow = 'hidden';
  }

  /**
   * 关闭详情抽屉
   */
  function closeDetailDrawer() {
    if (!detailOverlay || !detailDrawer) return;

    // 播放关闭音效
    playDrawerCloseSound();

    // 隐藏抽屉
    detailOverlay.classList.remove('active');
    detailDrawer.classList.remove('active');

    // 恢复背景滚动
    document.body.style.overflow = '';
  }

  /**
   * 生成档案ID
   */
  function generateArchiveId() {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    let id = '';
    for (let i = 0; i < 8; i++) {
      id += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return id;
  }

  /**
   * 生成详情内容（Markdown格式）
   * @param {Object} result - 知识库条目
   */
  function generateDetailContent(result) {
    const templates = {
      critical: generateCriticalContent(result),
      warning: generateWarningContent(result),
      info: generateInfoContent(result),
      manual: generateManualContent(result),
      spec: generateSpecContent(result),
      case: generateCaseContent(result)
    };

    return templates[result.type] || generateDefaultContent(result);
  }

  /**
   * CRITICAL级别内容模板
   */
  function generateCriticalContent(result) {
    return `
      <h2>⚠️ Critical Alert Details</h2>
      <p><strong>Severity Level:</strong> <span style="color: #ff6b6b;">CRITICAL - Immediate Action Required</span></p>

      <h3>Issue Description</h3>
      <p>${result.content}</p>

      <h3>Immediate Actions</h3>
      <ul>
        <li>Stop all related equipment immediately</li>
        <li>Notify maintenance team and safety officer</li>
        <li>Isolate the affected system</li>
        <li>Document the incident with photos if possible</li>
      </ul>

      <h3>Diagnostic Data</h3>
      <pre><code>// System Status Log
ERROR_CODE: ${generateArchiveId()}
TIMESTAMP: ${new Date().toISOString()}
SEVERITY: CRITICAL
AFFECTED_SYSTEMS: ["${result.tags.join('", "')}"]
RECOMMENDED_ACTION: IMMEDIATE_SHUTDOWN</code></pre>

      ${generateStressCloud()}

      <h3>Contact Information</h3>
      <p>Emergency Maintenance Hotline: <strong>EXT-991</strong><br>
      Safety Department: <strong>EXT-992</strong></p>
    `;
  }

  /**
   * WARNING级别内容模板
   */
  function generateWarningContent(result) {
    return `
      <h2>⚡ Warning Alert Details</h2>
      <p><strong>Severity Level:</strong> <span style="color: #ffa502;">WARNING - Attention Required</span></p>

      <h3>Condition Report</h3>
      <p>${result.content}</p>

      <h3>Recommended Actions</h3>
      <ul>
        <li>Schedule inspection within 24 hours</li>
        <li>Monitor system parameters closely</li>
        <li>Prepare replacement parts if needed</li>
        <li>Update maintenance log</li>
      </ul>

      <h3>Trend Analysis</h3>
      <table>
        <tr>
          <th>Parameter</th>
          <th>Current</th>
          <th>Threshold</th>
          <th>Status</th>
        </tr>
        <tr>
          <td>Vibration</td>
          <td>4.5 mm/s</td>
          <td>4.0 mm/s</td>
          <td style="color: #ffa502;">⚠️ Exceeded</td>
        </tr>
        <tr>
          <td>Temperature</td>
          <td>75°C</td>
          <td>70°C</td>
          <td style="color: #ffa502;">⚠️ Warning</td>
        </tr>
        <tr>
          <td>Pressure</td>
          <td>2.8 bar</td>
          <td>3.0 bar</td>
          <td style="color: #7bed9f;">✓ Normal</td>
        </tr>
      </table>
    `;
  }

  /**
   * INFO级别内容模板
   */
  function generateInfoContent(result) {
    return `
      <h2>ℹ️ Technical Information</h2>

      <h3>Overview</h3>
      <p>${result.content}</p>

      <h3>Technical Specifications</h3>
      <table>
        <tr>
          <th>Parameter</th>
          <th>Value</th>
          <th>Unit</th>
        </tr>
        <tr>
          <td>Operating Temperature</td>
          <td>40-65</td>
          <td>°C</td>
        </tr>
        <tr>
          <td>Warning Threshold</td>
          <td>75</td>
          <td>°C</td>
        </tr>
        <tr>
          <td>Critical Threshold</td>
          <td>85</td>
          <td>°C</td>
        </tr>
        <tr>
          <td>Lubrication Pressure</td>
          <td>2.5-3.0</td>
          <td>bar</td>
        </tr>
      </table>

      <h3>Related Documents</h3>
      <ul>
        <li>Equipment Manual v2.3</li>
        <li>Maintenance Schedule Q1 2024</li>
        <li>Safety Guidelines Section 4.2</li>
      </ul>
    `;
  }

  /**
   * MANUAL级别内容模板
   */
  function generateManualContent(result) {
    return `
      <h2>📋 Procedure Manual</h2>

      <h3>Scope</h3>
      <p>${result.content}</p>

      <h3>Required Tools</h3>
      <ul>
        <li>Laser interferometer</li>
        <li>Precision dial indicator (0.001mm)</li>
        <li>Torque wrench set</li>
        <li>Calibration standards</li>
      </ul>

      <h3>Step-by-Step Procedure</h3>
      <ol>
        <li><strong>Preparation</strong>: Ensure machine is powered off and locked out</li>
        <li><strong>Initial Check</strong>: Verify all axes are at home position</li>
        <li><strong>Measurement</strong>: Use laser interferometer to measure positioning accuracy</li>
        <li><strong>Adjustment</strong>: Compensate for detected errors in control parameters</li>
        <li><strong>Verification</strong>: Run test program to confirm calibration</li>
        <li><strong>Documentation</strong>: Record results in calibration log</li>
      </ol>

      <h3>Quality Standards</h3>
      <pre><code>Positioning Accuracy: ±0.005mm
Repeatability: ±0.003mm
Angular Accuracy: ±0.001°
Spindle Runout: <0.002mm</code></pre>
    `;
  }

  /**
   * SPEC级别内容模板
   */
  function generateSpecContent(result) {
    return `
      <h2>📐 Technical Specification</h2>

      <h3>Product Overview</h3>
      <p>${result.content}</p>

      <h3>Performance Specifications</h3>
      <table>
        <tr>
          <th>Specification</th>
          <th>Value</th>
        </tr>
        <tr>
          <td>Max Torque</td>
          <td>4500 Nm</td>
        </tr>
        <tr>
          <td>Gear Ratio</td>
          <td>15.5:1</td>
        </tr>
        <tr>
          <td>Efficiency</td>
          <td>96%</td>
        </tr>
        <tr>
          <td>Max Input Speed</td>
          <td>1800 RPM</td>
        </tr>
        <tr>
          <td>Service Life</td>
          <td>20,000 hours</td>
        </tr>
      </table>

      <h3>Maintenance Requirements</h3>
      <ul>
        <li><strong>Interval:</strong> Every 8000 operating hours</li>
        <li><strong>Oil Type:</strong> ISO VG 320 synthetic</li>
        <li><strong>Oil Capacity:</strong> 12 liters</li>
        <li><strong>Filter Change:</strong> Every 2 oil changes</li>
      </ul>
    `;
  }

  /**
   * CASE级别内容模板
   */
  function generateCaseContent(result) {
    return `
      <h2>📊 Case Study Analysis</h2>

      <h3>Background</h3>
      <p>${result.content}</p>

      <h3>Problem Statement</h3>
      <blockquote>
        Original welding cycle time was 45 seconds per chassis, 
        with inconsistent weld quality affecting structural integrity.
      </blockquote>

      <h3>Solution Implementation</h3>
      <ol>
        <li>Analyzed existing robot paths using genetic algorithm optimization</li>
        <li>Redesigned welding sequence to minimize robot arm movement</li>
        <li>Optimized torch angles and speeds for each weld point</li>
        <li>Implemented collision avoidance for multi-robot cells</li>
      </ol>

      <h3>Results</h3>
      <table>
        <tr>
          <th>Metric</th>
          <th>Before</th>
          <th>After</th>
          <th>Improvement</th>
        </tr>
        <tr>
          <td>Cycle Time</td>
          <td>45s</td>
          <td>38s</td>
          <td style="color: #7bed9f;">-15%</td>
        </tr>
        <tr>
          <td>Power Consumption</td>
          <td>100%</td>
          <td>92%</td>
          <td style="color: #7bed9f;">-8%</td>
        </tr>
        <tr>
          <td>Weld Quality</td>
          <td>94%</td>
          <td>98%</td>
          <td style="color: #7bed9f;">+4%</td>
        </tr>
      </table>

      ${generateStressCloud()}
    `;
  }

  /**
   * 默认内容模板
   */
  function generateDefaultContent(result) {
    return `
      <h2>Document Details</h2>
      <p>${result.content}</p>

      <h3>Tags</h3>
      <p>${result.tags.map(tag => `<code>${tag}</code>`).join(' ')}</p>
    `;
  }

  /**
   * 生成应力云图示意
   */
  function generateStressCloud() {
    const cells = [];
    const levels = ['low', 'low', 'medium', 'medium', 'high', 'critical'];

    for (let i = 0; i < 100; i++) {
      const level = levels[Math.floor(Math.random() * levels.length)];
      cells.push(`<div class="stress-cell ${level}"></div>`);
    }

    return `
      <h3>Stress Distribution Analysis</h3>
      <div class="stress-cloud-visualization">
        <div class="stress-cloud-grid">
          ${cells.join('')}
        </div>
        <div class="stress-legend">
          <div class="stress-legend-item">
            <div class="stress-legend-color" style="background: rgba(0, 212, 255, 0.3);"></div>
            <span>Low Stress</span>
          </div>
          <div class="stress-legend-item">
            <div class="stress-legend-color" style="background: rgba(138, 43, 226, 0.4);"></div>
            <span>Medium</span>
          </div>
          <div class="stress-legend-item">
            <div class="stress-legend-color" style="background: rgba(255, 107, 53, 0.5);"></div>
            <span>High</span>
          </div>
          <div class="stress-legend-item">
            <div class="stress-legend-color" style="background: rgba(255, 71, 87, 0.6);"></div>
            <span>Critical</span>
          </div>
        </div>
      </div>
    `;
  }

  /**
   * 播放抽屉打开音效
   */
  function playDrawerOpenSound() {
    try {
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();

      // 主音调 - 机械滑动声
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();
      const filter = audioContext.createBiquadFilter();

      oscillator.connect(filter);
      filter.connect(gainNode);
      gainNode.connect(audioContext.destination);

      filter.type = 'lowpass';
      filter.frequency.setValueAtTime(800, audioContext.currentTime);
      filter.frequency.exponentialRampToValueAtTime(200, audioContext.currentTime + 0.4);

      oscillator.frequency.setValueAtTime(150, audioContext.currentTime);
      oscillator.frequency.exponentialRampToValueAtTime(80, audioContext.currentTime + 0.4);

      gainNode.gain.setValueAtTime(0.15, audioContext.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.4);

      oscillator.start(audioContext.currentTime);
      oscillator.stop(audioContext.currentTime + 0.4);

      // 能量激活音效
      setTimeout(() => {
        const osc2 = audioContext.createOscillator();
        const gain2 = audioContext.createGain();
        osc2.connect(gain2);
        gain2.connect(audioContext.destination);

        osc2.frequency.setValueAtTime(400, audioContext.currentTime);
        osc2.frequency.exponentialRampToValueAtTime(600, audioContext.currentTime + 0.2);

        gain2.gain.setValueAtTime(0.05, audioContext.currentTime);
        gain2.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);

        osc2.start(audioContext.currentTime);
        osc2.stop(audioContext.currentTime + 0.3);
      }, 200);
    } catch (e) {
      // 静默处理
    }
  }

  /**
   * 播放抽屉关闭音效
   */
  function playDrawerCloseSound() {
    try {
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();
      const filter = audioContext.createBiquadFilter();

      oscillator.connect(filter);
      filter.connect(gainNode);
      gainNode.connect(audioContext.destination);

      filter.type = 'lowpass';
      filter.frequency.setValueAtTime(300, audioContext.currentTime);
      filter.frequency.exponentialRampToValueAtTime(100, audioContext.currentTime + 0.3);

      oscillator.frequency.setValueAtTime(80, audioContext.currentTime);
      oscillator.frequency.exponentialRampToValueAtTime(40, audioContext.currentTime + 0.3);

      gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);

      oscillator.start(audioContext.currentTime);
      oscillator.stop(audioContext.currentTime + 0.3);
    } catch (e) {
      // 静默处理
    }
  }

  // ==================== 导出 ====================
  window.KnowledgeUI = {
    init,
    performSearch,
    openDetailDrawer,
    closeDetailDrawer
  };

})();
