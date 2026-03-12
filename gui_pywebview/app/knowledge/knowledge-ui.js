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

  // ==================== 书籍数据 ====================
  const mockResults = [
    {
      title: '机械设计手册',
      type: 'design',
      author: '闻邦椿',
      edition: '第6版',
      publisher: '机械工业出版社',
      year: 2018,
      pages: 3200,
      isbn: '978-7-111-58876-3',
      rating: 4.9,
      content: '机械设计领域最权威的工具书，涵盖常用设计资料、机械零件设计、传动设计、液压与气压传动等。工程师案头必备参考手册。',
      tags: ['设计', '手册', '传动', '零件'],
      chapters: ['常用设计资料', '机构设计', '连接与紧固', '轴系零件', '传动设计', '弹簧', '液压气压传动', '润滑与密封']
    },
    {
      title: '材料力学',
      type: 'mechanics',
      author: '刘鸿文',
      edition: '第6版',
      publisher: '高等教育出版社',
      year: 2017,
      pages: 580,
      isbn: '978-7-04-047764-9',
      rating: 4.8,
      content: '经典材料力学教材，系统介绍杆件的强度、刚度和稳定性问题。包含拉压、扭转、弯曲、应力状态、能量法等核心理论。',
      tags: ['力学', '强度', '应力', '变形'],
      chapters: ['轴向拉压', '剪切与挤压', '扭转', '弯曲内力', '弯曲应力', '弯曲变形', '应力状态', '强度理论', '组合变形', '压杆稳定', '能量法']
    },
    {
      title: '理论力学',
      type: 'mechanics',
      author: '哈尔滨工业大学理论力学教研室',
      edition: '第9版',
      publisher: '高等教育出版社',
      year: 2021,
      pages: 560,
      isbn: '978-7-04-055653-5',
      rating: 4.7,
      content: '国内理论力学经典教材，内容包括静力学、运动学和动力学三大部分。以简明严谨的方式阐述力学基本原理。',
      tags: ['力学', '静力学', '运动学', '动力学'],
      chapters: ['静力学公理', '力系简化', '力系平衡', '点的运动学', '刚体运动', '点的合成运动', '质点动力学', '动量定理', '动能定理', '达朗贝尔原理', '虚位移原理']
    },
    {
      title: '机械原理',
      type: 'design',
      author: '孙桓 陈作模',
      edition: '第9版',
      publisher: '高等教育出版社',
      year: 2021,
      pages: 420,
      isbn: '978-7-04-055857-7',
      rating: 4.6,
      content: '系统讲述机构学和机器动力学基础理论，包括连杆机构、凸轮机构、齿轮机构、轮系、间歇运动机构等核心内容。',
      tags: ['设计', '机构', '齿轮', '凸轮'],
      chapters: ['平面机构', '平面连杆机构', '凸轮机构', '齿轮机构', '轮系', '间歇运动机构', '机器动力学', '机构平衡', '机械效率']
    },
    {
      title: '工程材料及成形技术基础',
      type: 'materials',
      author: '吕广庶 张远明',
      edition: '第3版',
      publisher: '高等教育出版社',
      year: 2018,
      pages: 450,
      isbn: '978-7-04-049376-2',
      rating: 4.5,
      content: '全面介绍金属材料、高分子材料、陶瓷材料和复合材料的组织结构、性能特点及成形方法。涵盖铸造、锻压、焊接等工艺。',
      tags: ['材料', '金属', '成形', '工艺'],
      chapters: ['金属的晶体结构', '合金相图', '钢的热处理', '工业用钢', '铸铁', '有色金属', '高分子材料', '陶瓷材料', '铸造', '锻压', '焊接']
    },
    {
      title: '工程热力学',
      type: 'thermo',
      author: '曾丹苓 敖越',
      edition: '第5版',
      publisher: '高等教育出版社',
      year: 2020,
      pages: 480,
      isbn: '978-7-04-053765-7',
      rating: 4.6,
      content: '系统阐述热力学基本定律及其工程应用，包括理想气体、蒸汽、湿空气的热力过程，动力循环与制冷循环。',
      tags: ['热力学', '传热', '循环', '能量'],
      chapters: ['基本概念', '热力学第一定律', '理想气体', '热力学第二定律', '水蒸气', '湿空气', '气体流动', '动力循环', '制冷循环', '化学热力学']
    },
    {
      title: '流体力学',
      type: 'fluid',
      author: '蔡增基 龙天渝',
      edition: '第3版',
      publisher: '中国建筑工业出版社',
      year: 2019,
      pages: 420,
      isbn: '978-7-112-23456-7',
      rating: 4.5,
      content: '涵盖流体静力学、流体动力学、管流阻力、边界层理论、可压缩流动等内容。工程流体力学的经典教材。',
      tags: ['流体', '液压', '管道', '压力'],
      chapters: ['流体的性质', '流体静力学', '流体运动学', '流体动力学', '相似与量纲分析', '管流阻力', '边界层', '绕流', '可压缩流动', '非牛顿流体']
    },
    {
      title: '有限元方法及其应用',
      type: 'fea',
      author: '马永其 柴山',
      edition: '第2版',
      publisher: '机械工业出版社',
      year: 2020,
      pages: 380,
      isbn: '978-7-111-65432-1',
      rating: 4.7,
      content: '从弹性力学基础出发，系统介绍有限元方法的基本原理、单元构造、整体分析和工程应用。包含ANSYS实例教程。',
      tags: ['有限元', '仿真', 'ANSYS', '分析'],
      chapters: ['弹性力学基础', '有限元基本原理', '平面问题', '轴对称问题', '空间问题', '板壳单元', '等参单元', '动力学分析', '非线性分析', 'ANSYS应用']
    },
    {
      title: '机械制造技术基础',
      type: 'manufacturing',
      author: '卢秉恒',
      edition: '第4版',
      publisher: '机械工业出版社',
      year: 2019,
      pages: 520,
      isbn: '978-7-111-62345-6',
      rating: 4.6,
      content: '涵盖金属切削原理、机床、刀具、工艺规程设计、加工精度、表面质量等核心内容。机械制造工程师必备基础。',
      tags: ['制造', '切削', '工艺', '加工'],
      chapters: ['金属切削原理', '金属切削刀具', '金属切削机床', '机械加工工艺规程', '机床夹具', '加工精度', '表面质量', '先进制造技术']
    },
    {
      title: '互换性与测量技术基础',
      type: 'manufacturing',
      author: '刘巽尔',
      edition: '第7版',
      publisher: '机械工业出版社',
      year: 2018,
      pages: 350,
      isbn: '978-7-111-59432-0',
      rating: 4.4,
      content: '介绍公差与配合、形位公差、表面粗糙度、量规设计、测量技术等内容。精密制造和质量控制的理论基础。',
      tags: ['制造', '公差', '测量', '质量'],
      chapters: ['尺寸公差', '配合制', '形位公差', '表面粗糙度', '量规设计', '光滑极限量规', '螺纹公差', '齿轮精度', '键连接公差', '测量技术基础']
    },
    {
      title: '自动控制原理',
      type: 'control',
      author: '胡寿松',
      edition: '第7版',
      publisher: '科学出版社',
      year: 2019,
      pages: 640,
      isbn: '978-7-03-061234-5',
      rating: 4.8,
      content: '自动控制理论经典教材，涵盖经典控制论和现代控制论。包括传递函数、根轨迹、频率响应、状态空间等核心方法。',
      tags: ['控制', '自动化', '传递函数', '反馈'],
      chapters: ['控制系统导论', '数学模型', '时域分析', '根轨迹', '频域分析', 'PID控制', '校正与设计', '非线性系统', '离散系统', '状态空间分析']
    },
    {
      title: '摩擦学原理',
      type: 'tribology',
      author: '温诗铸 黄平',
      edition: '第5版',
      publisher: '清华大学出版社',
      year: 2020,
      pages: 480,
      isbn: '978-7-302-54321-0',
      rating: 4.7,
      content: '系统阐述摩擦、磨损与润滑的基本理论，包括表面形貌、接触力学、流体润滑、弹流润滑和磨损机理。',
      tags: ['摩擦学', '磨损', '润滑', '表面'],
      chapters: ['表面形貌', '接触力学', '摩擦理论', '磨损机理', '流体动力润滑', '弹性流体动力润滑', '边界润滑', '润滑剂', '密封技术', '纳米摩擦学']
    },
    {
      title: '机械振动',
      type: 'mechanics',
      author: '张义民',
      edition: '第3版',
      publisher: '清华大学出版社',
      year: 2019,
      pages: 400,
      isbn: '978-7-302-52345-8',
      rating: 4.5,
      content: '讲述机械系统振动分析的理论和方法，包括单自由度和多自由度系统的自由振动、受迫振动及振动控制。',
      tags: ['力学', '振动', '动力学', '控制'],
      chapters: ['单自由度自由振动', '单自由度受迫振动', '两自由度系统', '多自由度系统', '连续系统振动', '振动测试', '隔振与减振', '转子动力学', '随机振动']
    },
    {
      title: '液压与气压传动',
      type: 'design',
      author: '左健民',
      edition: '第6版',
      publisher: '机械工业出版社',
      year: 2019,
      pages: 380,
      isbn: '978-7-111-61234-4',
      rating: 4.5,
      content: '全面介绍液压传动的基本原理、液压元件、基本回路和典型系统。同时涵盖气压传动的原理与应用。',
      tags: ['设计', '液压', '气压', '传动'],
      chapters: ['流体力学基础', '液压泵', '液压马达与液压缸', '液压控制阀', '液压辅件', '液压基本回路', '典型液压系统', '气压传动', '气动控制系统']
    },
    {
      title: '金属材料学',
      type: 'materials',
      author: '戴起勋',
      edition: '第3版',
      publisher: '化学工业出版社',
      year: 2020,
      pages: 440,
      isbn: '978-7-122-36543-2',
      rating: 4.4,
      content: '详细介绍各类工程金属材料的成分、组织、性能及应用。涵盖碳钢、合金钢、铸铁、铝合金、钛合金等。',
      tags: ['材料', '金属', '合金', '热处理'],
      chapters: ['金属的结构', '合金相图', '碳钢', '合金钢', '不锈钢与耐热钢', '工具钢', '铸铁', '铝及铝合金', '铜合金', '钛合金', '粉末冶金']
    },
    {
      title: '传热学',
      type: 'thermo',
      author: '杨世铭 陶文铨',
      edition: '第5版',
      publisher: '高等教育出版社',
      year: 2019,
      pages: 560,
      isbn: '978-7-04-051234-0',
      rating: 4.8,
      content: '传热学经典教材，系统讲述导热、对流换热和辐射换热三种基本传热方式。包含传热强化和数值计算方法。',
      tags: ['热力学', '传热', '导热', '辐射'],
      chapters: ['导热基本理论', '稳态导热', '非稳态导热', '导热的数值方法', '对流换热分析', '内部流动换热', '外部流动换热', '自然对流换热', '沸腾与凝结', '辐射换热', '传热强化']
    },
    {
      title: 'ANSYS Workbench 有限元分析实例详解',
      type: 'fea',
      author: '周炬 苏金明',
      edition: '第2版',
      publisher: '机械工业出版社',
      year: 2021,
      pages: 520,
      isbn: '978-7-111-68765-9',
      rating: 4.6,
      content: '以大量工程实例为主线，详细介绍ANSYS Workbench的操作方法和有限元分析技巧。涵盖结构、热、流体和多物理场耦合分析。',
      tags: ['有限元', 'ANSYS', '仿真', '工程'],
      chapters: ['Workbench入门', '几何建模', '网格划分', '静力学分析', '模态分析', '谐响应分析', '瞬态分析', '热分析', '流体分析', '优化设计']
    },
    {
      title: '数控加工工艺与编程',
      type: 'manufacturing',
      author: '华茂发',
      edition: '第4版',
      publisher: '机械工业出版社',
      year: 2020,
      pages: 360,
      isbn: '978-7-111-65678-3',
      rating: 4.3,
      content: '系统讲述数控加工工艺设计与程序编制，包括数控车削、铣削、加工中心编程及CAM自动编程技术。',
      tags: ['制造', '数控', '编程', 'CAM'],
      chapters: ['数控加工基础', '数控编程基础', '数控车削编程', '数控铣削编程', '加工中心编程', '宏程序编程', 'CAM自动编程', '特种加工', '高速切削']
    },
    {
      title: '机电一体化系统设计',
      type: 'control',
      author: '赵松年',
      edition: '第3版',
      publisher: '机械工业出版社',
      year: 2019,
      pages: 400,
      isbn: '978-7-111-62456-9',
      rating: 4.5,
      content: '讲述机电一体化系统的设计原理和方法，包括传感器、执行器、微控制器、接口技术和系统集成。',
      tags: ['控制', '机电', '传感器', '系统'],
      chapters: ['机电一体化概论', '机械系统设计', '传感检测技术', '伺服驱动系统', '控制系统设计', '计算机控制接口', '信号处理', '系统建模', '典型系统设计']
    },
    {
      title: '弹性力学',
      type: 'mechanics',
      author: '徐芝纶',
      edition: '第5版',
      publisher: '高等教育出版社',
      year: 2016,
      pages: 400,
      isbn: '978-7-04-044321-7',
      rating: 4.7,
      content: '弹性力学经典教材，以简明清晰的风格讲述弹性力学的基本理论，包括平面问题、空间问题和薄板弯曲问题。',
      tags: ['力学', '弹性', '应力', '应变'],
      chapters: ['绪论', '平面应力问题', '平面应变问题', '极坐标中的解', '空间问题', '等截面杆的扭转', '能量方法', '薄板弯曲', '有限元法简介']
    },
    {
      title: '计算流体力学',
      type: 'fluid',
      author: '王福军',
      edition: '第2版',
      publisher: '清华大学出版社',
      year: 2020,
      pages: 420,
      isbn: '978-7-302-55678-4',
      rating: 4.6,
      content: '系统介绍CFD的基本理论和数值方法，包括有限差分法、有限体积法、有限元法及湍流模型。结合Fluent实例。',
      tags: ['流体', 'CFD', '仿真', '湍流'],
      chapters: ['控制方程', '有限差分法', '有限体积法', '网格技术', 'SIMPLE算法', '湍流模型', '多相流', '传热计算', 'Fluent应用', '后处理']
    },
    {
      title: '焊接冶金学',
      type: 'materials',
      author: '张文钺',
      edition: '第4版',
      publisher: '机械工业出版社',
      year: 2018,
      pages: 360,
      isbn: '978-7-111-59876-2',
      rating: 4.4,
      content: '系统讲述焊接过程中的冶金反应、焊缝金属凝固、热影响区组织转变及焊接缺陷的形成机理与控制方法。',
      tags: ['材料', '焊接', '冶金', '缺陷'],
      chapters: ['焊接热过程', '焊接化学冶金', '焊缝金属凝固', '焊接热影响区', '焊接裂纹', '焊接缺陷', '异种金属焊接', '特种焊接', '焊接质量控制']
    },
    {
      title: '机器人学导论',
      type: 'control',
      author: '[美] John J. Craig / 贠超 译',
      edition: '第4版',
      publisher: '机械工业出版社',
      year: 2020,
      pages: 450,
      isbn: '978-7-111-65234-1',
      rating: 4.8,
      content: '全面介绍机器人运动学、动力学和控制。包括齐次坐标变换、DH参数、正逆运动学、轨迹规划和力控制。',
      tags: ['控制', '机器人', '运动学', '动力学'],
      chapters: ['空间描述与变换', '操作臂运动学', '逆运动学', '雅可比矩阵', '操作臂动力学', '轨迹生成', '操作臂控制', '力控制', '机器人编程']
    },
    {
      title: '模具设计与制造',
      type: 'manufacturing',
      author: '李奇',
      edition: '第4版',
      publisher: '机械工业出版社',
      year: 2019,
      pages: 420,
      isbn: '978-7-111-62789-8',
      rating: 4.3,
      content: '涵盖冲压模具和塑料模具的设计原理与制造工艺，包括冲裁、弯曲、拉深模具及注射模具设计。',
      tags: ['制造', '模具', '冲压', '注塑'],
      chapters: ['冲裁模设计', '弯曲模设计', '拉深模设计', '成形模设计', '注射模设计', '压缩模设计', '模具材料', '模具制造', '特种加工']
    },
    {
      title: '工程制图',
      type: 'design',
      author: '唐克中 朱同钧',
      edition: '第4版',
      publisher: '高等教育出版社',
      year: 2018,
      pages: 440,
      isbn: '978-7-04-050123-8',
      rating: 4.4,
      content: '工程制图经典教材，系统讲述投影理论、机件表达方法、标准件常用件、零件图和装配图的绘制。',
      tags: ['设计', '制图', 'CAD', '标准'],
      chapters: ['制图基本规范', '点线面投影', '立体投影', '轴测图', '组合体', '机件表达方法', '标准件与常用件', '零件图', '装配图', 'CAD基础']
    },
    {
      title: '疲劳与断裂',
      type: 'mechanics',
      author: '刘文珽',
      edition: '第2版',
      publisher: '北京航空航天大学出版社',
      year: 2018,
      pages: 380,
      isbn: '978-7-512-42345-6',
      rating: 4.5,
      content: '讲述金属疲劳和断裂力学的基本理论，包括S-N曲线、裂纹扩展、应力强度因子、损伤容限设计等核心概念。',
      tags: ['力学', '疲劳', '断裂', '可靠性'],
      chapters: ['应力与疲劳', 'S-N曲线', '疲劳裂纹萌生', '线弹性断裂力学', '裂纹扩展', '疲劳寿命预测', '损伤容限', '环境疲劳', '多轴疲劳', '概率疲劳']
    },
    {
      title: '现代焊接技术',
      type: 'manufacturing',
      author: '邹增大',
      edition: '第2版',
      publisher: '机械工业出版社',
      year: 2021,
      pages: 400,
      isbn: '978-7-111-68234-0',
      rating: 4.3,
      content: '介绍各种现代焊接方法的原理、工艺和应用，包括激光焊、电子束焊、搅拌摩擦焊、钎焊和增材制造焊接。',
      tags: ['制造', '焊接', '激光', '工艺'],
      chapters: ['焊接概论', '电弧焊', 'MIG/MAG焊', 'TIG焊', '电阻焊', '激光焊接', '电子束焊', '搅拌摩擦焊', '钎焊', '焊接自动化']
    },
    {
      title: '润滑理论与轴承设计',
      type: 'tribology',
      author: '杨沛然',
      edition: '第2版',
      publisher: '机械工业出版社',
      year: 2019,
      pages: 360,
      isbn: '978-7-111-63456-8',
      rating: 4.5,
      content: '系统讲述流体润滑理论和轴承设计方法，包括Reynolds方程、滑动轴承和滚动轴承的分析与优化。',
      tags: ['摩擦学', '轴承', '润滑', '设计'],
      chapters: ['润滑基础理论', 'Reynolds方程', '动压滑动轴承', '静压滑动轴承', '弹流润滑', '滚动轴承原理', '轴承选型与计算', '轴承装配与维护', '特种轴承', '轴承故障诊断']
    },
    {
      title: '复合材料力学',
      type: 'materials',
      author: '沈观林 胡更开',
      edition: '第2版',
      publisher: '清华大学出版社',
      year: 2019,
      pages: 380,
      isbn: '978-7-302-53456-3',
      rating: 4.6,
      content: '讲述纤维增强复合材料的力学分析方法，包括单层力学、层合板理论、强度准则和损伤力学。航空航天工程的重要参考。',
      tags: ['材料', '复合材料', '强度', '层合板'],
      chapters: ['复合材料概述', '各向异性弹性理论', '单层力学', '经典层合板理论', '复合材料强度', '细观力学', '损伤与失效', '疲劳与蠕变', '实验方法']
    }
  ];

  // 书籍封面颜色映射
  const bookColors = {
    mechanics: { primary: '#00e6ff', secondary: '#004d5c', icon: '⚙️' },
    materials: { primary: '#7bed9f', secondary: '#1a472a', icon: '🔬' },
    design: { primary: '#ffa502', secondary: '#5c3d00', icon: '📐' },
    manufacturing: { primary: '#ff6b6b', secondary: '#5c1a1a', icon: '🏭' },
    thermo: { primary: '#ff7f50', secondary: '#5c2e1f', icon: '🔥' },
    control: { primary: '#70a1ff', secondary: '#1a365c', icon: '🤖' },
    fea: { primary: '#a29bfe', secondary: '#2d1b69', icon: '📊' },
    fluid: { primary: '#55efc4', secondary: '#1a5c4c', icon: '🌊' },
    tribology: { primary: '#fdcb6e', secondary: '#5c4a1a', icon: '⚡' }
  };

  // 分类名称映射
  const categoryNames = {
    mechanics: '力学', materials: '材料', design: '设计',
    manufacturing: '制造', thermo: '热力学', control: '控制',
    fea: '有限元', fluid: '流体', tribology: '摩擦学'
  };

  // 轮播状态
  let carouselOffset = 0;
  let carouselContainer = null;
  let slidePreviewTimer = null;

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
    carouselContainer = $('book-carousel');

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
    setupCarousel();

    displayResults(mockResults);
  }

  // ==================== 书籍轮播 ====================

  function setupCarousel() {
    if (!carouselContainer) return;

    renderCarousel(mockResults);
    setupCarouselNav();
    setupCarouselDrag();
  }

  function renderCarousel(books) {
    if (!carouselContainer) return;
    carouselContainer.innerHTML = books.map((book, i) => {
      const color = bookColors[book.type] || bookColors.design;
      return `
        <div class="book-card" data-index="${i}" style="--book-color: ${color.primary}; --book-bg: ${color.secondary};">
          <div class="book-cover">
            <div class="book-spine" style="background: linear-gradient(180deg, ${color.primary}22, ${color.primary}44);"></div>
            <div class="book-face">
              <div class="book-icon">${color.icon}</div>
              <div class="book-cover-title">${escapeHtml(book.title)}</div>
              <div class="book-cover-author">${escapeHtml(book.author)}</div>
              <div class="book-cover-edition">${escapeHtml(book.edition)}</div>
              <div class="book-cover-badge">${escapeHtml(categoryNames[book.type] || book.type)}</div>
            </div>
          </div>
          <div class="book-slide-preview">
            <div class="slide-preview-header">
              <span class="slide-preview-category" style="color: ${color.primary};">${escapeHtml(categoryNames[book.type] || book.type)}</span>
              <span class="slide-preview-rating">${'★'.repeat(Math.floor(book.rating))}${'☆'.repeat(5 - Math.floor(book.rating))} ${book.rating}</span>
            </div>
            <p class="slide-preview-desc">${escapeHtml(book.content)}</p>
            <div class="slide-preview-meta">
              <span>${escapeHtml(book.publisher)}</span>
              <span>${book.pages}页</span>
            </div>
            <div class="slide-preview-chapters">
              ${book.chapters.slice(0, 4).map(ch => `<span class="slide-ch">${escapeHtml(ch)}</span>`).join('')}
              ${book.chapters.length > 4 ? `<span class="slide-ch more">+${book.chapters.length - 4}</span>` : ''}
            </div>
          </div>
        </div>
      `;
    }).join('');

    carouselContainer.querySelectorAll('.book-card').forEach(card => {
      card.addEventListener('click', () => {
        const idx = parseInt(card.dataset.index);
        if (mockResults[idx]) openBookDrawer(mockResults[idx]);
      });
    });
  }

  function setupCarouselNav() {
    const prevBtn = $('carousel-prev');
    const nextBtn = $('carousel-next');
    if (!prevBtn || !nextBtn || !carouselContainer) return;

    const scrollAmount = 280;
    prevBtn.addEventListener('click', () => {
      carouselContainer.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
    });
    nextBtn.addEventListener('click', () => {
      carouselContainer.scrollBy({ left: scrollAmount, behavior: 'smooth' });
    });
  }

  function setupCarouselDrag() {
    if (!carouselContainer) return;
    let isDown = false, startX, scrollLeft;

    carouselContainer.addEventListener('mousedown', e => {
      isDown = true;
      carouselContainer.classList.add('dragging');
      startX = e.pageX - carouselContainer.offsetLeft;
      scrollLeft = carouselContainer.scrollLeft;
    });
    carouselContainer.addEventListener('mouseleave', () => { isDown = false; carouselContainer.classList.remove('dragging'); });
    carouselContainer.addEventListener('mouseup', () => { isDown = false; carouselContainer.classList.remove('dragging'); });
    carouselContainer.addEventListener('mousemove', e => {
      if (!isDown) return;
      e.preventDefault();
      const x = e.pageX - carouselContainer.offsetLeft;
      carouselContainer.scrollLeft = scrollLeft - (x - startX) * 1.5;
    });
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

        currentFilter = tag.dataset.filter;
        tag.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
        applyFilter();
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

  function applyFilter() {
    const filtered = currentFilter === 'all' 
      ? mockResults 
      : mockResults.filter(b => b.type === currentFilter);
    renderCarousel(filtered);
    if (carouselContainer) carouselContainer.scrollLeft = 0;
    displayResults(filtered, searchInput?.value.trim() || '');
  }

  async function performSearch() {
    const query = searchInput?.value.trim();
    if (!query) {
      applyFilter();
      return;
    }

    showLoading();
    searchHistory.unshift(query);
    if (searchHistory.length > 10) searchHistory.pop();

    await new Promise(resolve => setTimeout(resolve, 400));

    try {
      const results = filterResults(mockResults, query, currentFilter);
      renderCarousel(results.length > 0 ? results : []);
      displayResults(results, query);
    } catch (error) {
      showError(error.message);
    }
  }

  function filterResults(results, query, filter) {
    const q = query.toLowerCase();
    return results.filter(r => {
      const matchQuery = !query ||
        r.title.toLowerCase().includes(q) ||
        r.content.toLowerCase().includes(q) ||
        r.author.toLowerCase().includes(q) ||
        r.tags.some(t => t.toLowerCase().includes(q)) ||
        (r.chapters || []).some(ch => ch.toLowerCase().includes(q));
      const matchFilter = filter === 'all' || r.type === filter;
      return matchQuery && matchFilter;
    }).sort((a, b) => b.rating - a.rating);
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

  function getTypeBadge(type) {
    const color = bookColors[type] || bookColors.design;
    const name = categoryNames[type] || type;
    return `<span class="result-type" style="background: ${color.primary}22; color: ${color.primary}; border-color: ${color.primary}44;">${color.icon} ${name}</span>`;
  }

  function highlightKeywords(text, query) {
    let highlighted = escapeHtml(text);
    if (query) {
      const queryRegex = new RegExp(`(${escapeHtml(query)})`, 'gi');
      highlighted = highlighted.replace(queryRegex, '<span class="highlight">$1</span>');
    }
    return highlighted;
  }

  function displayResults(results, query = '') {
    if (!searchResults) return;
    currentResults = results || [];

    if (!results || results.length === 0) {
      searchResults.innerHTML = `
        <div class="result-placeholder">
          <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="1">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
          </svg>
          <p>未找到匹配的书籍</p>
          <span style="font-size: 11px; color: var(--ind-text-dim);">尝试其他关键词或分类</span>
        </div>
      `;
      return;
    }

    searchResults.innerHTML = `<div class="book-list-header">全部书籍 (${results.length})</div>` +
      results.map((book, index) => {
        const color = bookColors[book.type] || bookColors.design;
        return `
        <div class="book-list-item" data-index="${index}" style="animation: slideIn 0.3s ease-out ${index * 0.05}s both; --book-color: ${color.primary};">
          <div class="book-list-cover" style="background: linear-gradient(135deg, ${color.secondary}, ${color.primary}22);">
            <span class="book-list-icon">${color.icon}</span>
          </div>
          <div class="book-list-info">
            <div class="book-list-title">
              ${getTypeBadge(book.type)}
              ${highlightKeywords(book.title, query)}
            </div>
            <div class="book-list-author">${escapeHtml(book.author)} · ${escapeHtml(book.edition)}</div>
            <div class="book-list-desc">${highlightKeywords(book.content, query)}</div>
            <div class="book-list-meta">
              <span>${escapeHtml(book.publisher)}</span>
              <span>${book.pages}页</span>
              <span>${'★'.repeat(Math.floor(book.rating))} ${book.rating}</span>
            </div>
          </div>
        </div>
      `}).join('');

    setTimeout(() => initBookListEvents(), results.length * 50 + 100);
  }

  function initBookListEvents() {
    searchResults.querySelectorAll('.book-list-item').forEach(item => {
      item.addEventListener('click', () => {
        const idx = parseInt(item.dataset.index);
        if (currentResults[idx]) openBookDrawer(currentResults[idx]);
      });
    });
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

  function openBookDrawer(book) {
    if (!detailOverlay || !detailDrawer) return;

    const color = bookColors[book.type] || bookColors.design;

    if (drawerTitle) drawerTitle.textContent = book.title;
    if (drawerBadges) drawerBadges.innerHTML = getTypeBadge(book.type);
    if (drawerMeta) {
      drawerMeta.innerHTML = `
        <span>作者: ${escapeHtml(book.author)}</span>
        <span>版本: ${escapeHtml(book.edition)}</span>
        <span>出版社: ${escapeHtml(book.publisher)}</span>
        <span>ISBN: ${book.isbn}</span>
      `;
    }

    if (drawerBody) {
      drawerBody.innerHTML = generateBookContent(book, color);
    }

    if (drawerSource) {
      drawerSource.href = '#';
      drawerSource.textContent = '查看详情';
    }

    playDrawerOpenSound();
    detailOverlay.classList.add('active');
    detailDrawer.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function generateBookContent(book, color) {
    return `
      <div class="book-detail-header" style="border-left: 3px solid ${color.primary}; padding-left: 16px; margin-bottom: 20px;">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
          <span style="font-size: 28px;">${color.icon}</span>
          <div>
            <div style="color: ${color.primary}; font-size: 12px; text-transform: uppercase; letter-spacing: 1px;">${categoryNames[book.type] || book.type}</div>
            <div style="color: var(--ind-text-dim); font-size: 12px;">${book.year} · ${book.pages}页 · ${'★'.repeat(Math.floor(book.rating))} ${book.rating}</div>
          </div>
        </div>
      </div>

      <h3>内容简介</h3>
      <p>${escapeHtml(book.content)}</p>

      <h3>目录章节</h3>
      <div class="book-chapters-grid">
        ${book.chapters.map((ch, i) => `
          <div class="book-chapter-item" style="--ch-color: ${color.primary};">
            <span class="ch-num">${String(i + 1).padStart(2, '0')}</span>
            <span class="ch-name">${escapeHtml(ch)}</span>
          </div>
        `).join('')}
      </div>

      <h3>相关标签</h3>
      <div style="display: flex; flex-wrap: wrap; gap: 6px;">
        ${book.tags.map(t => `<span style="padding: 3px 10px; background: ${color.primary}15; border: 1px solid ${color.primary}33; border-radius: 12px; font-size: 11px; color: ${color.primary};">${escapeHtml(t)}</span>`).join('')}
      </div>

      <h3>出版信息</h3>
      <table>
        <tr><th>出版社</th><td>${escapeHtml(book.publisher)}</td></tr>
        <tr><th>版本</th><td>${escapeHtml(book.edition)}</td></tr>
        <tr><th>出版年份</th><td>${book.year}</td></tr>
        <tr><th>页数</th><td>${book.pages}</td></tr>
        <tr><th>ISBN</th><td>${book.isbn}</td></tr>
      </table>
    `;
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
    openBookDrawer,
    closeDetailDrawer
  };

})();
