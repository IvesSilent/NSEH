// ════════════════════════════════════════════════════════
// NSEH i18n — 中英双语切换（zh / en）
// 依赖：无。必须在 NSEH_main.js / NSEH_login.js / NSEH_rank.js 之前加载
// 用法：
//   HTML:  <span data-i18n="key">默认文本</span>
//          <input data-i18n-placeholder="key">
//   JS:    I18N.t('key', arg1, arg2)   → 支持 {0} {1} 占位符
//   JS:    I18N.t('key') 无匹配时返回 key 本身，保证不白屏
// ════════════════════════════════════════════════════════
(function (global) {
  'use strict';

  const STORAGE_KEY = 'nseh_lang';

  const DICT = {
    zh: {
      // ── 页面标题 ──
      'app.title': 'NSEH — 启发式组合优化进化框架',
      'login.title': 'NSEH — 登录',
      'rank.title': 'NSEH — 排行榜',

      // ── 顶栏 ──
      'header.welcome': '欢迎，',
      'header.admin': '⚙️ 管理后台',
      'header.theme': '主题',
      'header.logout': '退出',
      'header.langBtn': 'English',        // 中文模式下按钮显示 English（目标语言）
      'header.langTitle': '切换语言 / Switch language',

      // ── 标签页 ──
      'tab.setting': '设置',
      'tab.evolution': '进化',
      'tab.results': '结果',

      // ── 设置页 ──
      'setting.evoParams': '进化参数',
      'setting.popSize': '种群容量',
      'setting.gens': '进化迭代次数',
      'setting.mutation': '每次突变个数',
      'setting.hybridization': '参与交配的启发式数',
      'setting.reflection': '参与反思的启发式数',
      'setting.llmConfig': 'LLM 配置',
      'setting.apiKey': 'API Key',
      'setting.apiKeyPh': '你的 api key',
      'setting.baseUrl': 'Base URL',
      'setting.llmModel': 'LLM 模型选单',
      'setting.customModelPh': '自定义模型名称',
      'setting.llmHint': '选择预设或输入自定义模型名',
      'setting.scenario': '问题情景',
      'setting.selectScenario': '选择问题情景',
      'setting.selfAdapt': '场景自适应',
      'setting.problemDesc': '问题情景描述',
      'setting.funName': '函数名',
      'setting.funArgs': '函数参数',
      'setting.addArg': '添加参数',
      'setting.funReturn': '函数返回值',
      'setting.addReturn': '添加返回值',
      'setting.funNotes': '注意事项',
      'setting.ascend': '进化方向',
      'setting.ascendMin': '适应度越小越好',
      'setting.ascendMax': '适应度越大越好',
      'setting.problemPath': '问题目录',
      'setting.browse': '浏览',
      'setting.trainData': '训练数据',
      'setting.trainSolution': '标准解',
      'setting.startEvo': '开始进化',
      'setting.loadPop': '加载种群续训',

      // ── 进化页 ──
      'evo.title': '进化过程',
      'evo.scenario': '情景',
      'evo.loading': '加载中...',
      'evo.progress': '⏳ 进化进度',
      'evo.genCount': '{0} / {1} 代',
      'evo.details': '启发式详情',
      'evo.close': '关闭',
      'evo.concept': '启发式概念',
      'evo.fitness': '适应度',
      'evo.features': '特征',
      'evo.code': '算法代码',
      'evo.copy': '复制',
      'evo.copied': '已复制！',
      'evo.waiting': '等待启动',
      'evo.pause': '⏸ 暂停',
      'evo.resume': '▶ 继续',
      'evo.prompt': '📝 提示词',
      'evo.stop': '⏹ 终止',

      // ── 结果页 ──
      'results.title': '进化结果',
      'results.chartLine': '历代最优',
      'results.chartMulti': '最优/均值/方差',
      'results.chartTop3': '前三条形',
      'results.chartAll': '全部启发式',
      'results.chartTokens': 'Token 消耗',
      'results.openDir': '打开结果目录',
      'results.viewRank': '查看用户排行榜',

      // ── 弹窗 ──
      'modal.loadPopTitle': '加载已有种群',
      'modal.loadPopDesc': '选择要加载的种群文件，NSEH 将从该代继续进化。',
      'modal.problemDir': '问题目录：',
      'modal.scan': '扫描刷新',
      'modal.loadingPops': '正在加载已保存的种群...',
      'modal.noPops': '暂无已保存的种群',
      'modal.selfAdaptTitle': '场景自适应',
      'modal.selfAdaptDesc': '描述你想要的组合优化问题场景，AI 将自动生成问题组件、数据集制备脚本和评估代码。',
      'modal.scenarioName': '场景名称（英文，如 vehicle_routing）',
      'modal.scenarioDesc': '场景描述',
      'modal.scenarioPh': '例如：我需要解决一个带有时间窗约束的车辆路径问题（VRPTW），有1个仓库和50个客户节点，每辆车有容量限制，目标是最小化总行驶距离。',
      'modal.genScenario': '生成场景',
      'modal.stepConfig': '生成问题配置...',
      'modal.stepHeuristic': '生成缺省启发式...',
      'modal.stepDatagen': '生成数据集脚本...',
      'modal.stepTraineval': '生成评估代码...',
      'modal.stepFinish': '完成生成...',
      'modal.adminTitle': '管理后台',
      'modal.loading': '加载中...',

      // ── JS 动态文本 ──
      't.loadingUsers': '加载用户数据...',
      't.userList': '用户列表',
      't.colName': '名称',
      't.colAccount': '账号',
      't.colRole': '角色',
      't.colBest': '最佳',
      't.colExpCount': '实验数',
      't.colRegistered': '注册',
      't.expRecords': '实验记录（最近100条）',
      't.colUser': '用户',
      't.colStart': '开始',
      't.colEnd': '结束',
      't.colStatus': '状态',
      't.colBestVal': '最佳值',
      't.loadFailed': '加载失败: ',
      't.configSavedSession': '配置保存在会话中，开始进化后自动生效',
      't.finishSettingsFirst': '请先完成设置再切换页面',
      't.paramsAutoFixed': '已自动填充无效的进化参数',
      't.loadingCfg': '正在加载 {0} 的配置...',
      't.cfgLoaded': '已切换到 {0}',
      't.loadCfgFailed': '获取配置失败',
      't.loadCfgFailed2': '[FAIL] 加载问题配置失败: {0}',
      't.customModelHint': '输入自定义模型名称，并手动填写 BASE_URL',
      't.modelInfo': '模型: {0}',
      't.newArg': '新参数',
      't.newReturn': '新返回值',
      't.fileSelected': '已选择文件',
      't.dirSelected': '已选择目录: {0}',
      't.dirFailed': '无法获取目录路径，请手动输入',
      't.unknown': '未知',
      't.custom': '自定义',
      't.offlineFallback': ' (离线备用)',
      't.timerGen': '⏱ {0}/{1} 代 耗时 {2}',
      't.timerInit': '⏱ 初始化中... 耗时 {0}',
      't.timerGenCount': '{0} / {1} 代',
      't.confirm': '确认',
      't.cancel': '取消',
      't.needApiKey': '请填写 API Key',
      't.needBaseUrl': '请填写 BASE_URL',
      't.needModel': '请选择或输入 LLM 模型名称',
      't.needProblemPath': '请填写问题目录',
      't.starting': '正在启动...',
      't.savingAndStart': '正在保存配置并启动进化...',
      't.configSaved': '配置保存成功，正在启动进化...',
      't.saveFailed': '保存配置失败',
      't.evoStarted': '进化已启动 ✓',
      't.startEvo': '开始进化',
      't.evoPaused': '进化已暂停',
      't.evoResumed': '进化继续中...',
      't.confirmStop': '确定要终止当前进化吗？所有当前代的进度将丢失。',
      't.evoStopped': '进化已终止',
      't.promptFetchFailed': '获取提示词模板失败: {0}',
      't.statusRunning': '进化运行中...',
      't.statusCompleted': '进化已完成 ✓',
      't.statusPaused': '已暂停',
      't.statusWaiting': '等待启动',
      't.evoDoneToast': '进化完成 ✓ 切换到结果页查看',
      't.genFallback': '第{0}代',
      't.waiting': '等待中',
      't.bestFitness': '最优适应度：',
      't.posFeatures': '积极特征',
      't.negFeatures': '消极特征',
      't.noHeuristics': '暂无启发式',
      't.unnamedHeuristic': '未命名启发式',
      't.noTags': '无标签',
      't.detailNotFound': '未找到启发式详情',
      't.heuristicN': '启发式 {0}',
      't.clipboardFail': '无法访问剪贴板，请手动复制',
      't.customPrompt': '自定义提示词',
      't.funReq': '函数要求',
      't.mutation': 'MUTATION 突变',
      't.hybridization': 'HYBRIDIZATION 杂交',
      't.optimization': 'OPTIMIZATION 优化',
      't.analyze': '分析过程',
      't.confirmUpdate': '确认更新',
      't.promptUpdated': '提示词已更新',
      't.cannotOpenDir': '无法打开结果目录',
      't.chartBestFitness': '最优适应度',
      't.chartBest': '最优: ',
      't.chartGen': '进化代数',
      't.chartFitness': '适应度',
      't.chartBestVal': '最优值',
      't.chartAvg': '均值',
      't.chartVar': '方差',
      't.chartRank': '排名',
      't.chartHeurRank': '启发式排名',
      't.chartTop3Label': '最新代 TOP{0}',
      't.chartAllLabel': '当前代全部启发式',
      't.chartMutation': '突变',
      't.chartHybridization': '杂交',
      't.chartOptimization': '优化',
      't.scenarioNameReq': '请输入场景名称',
      't.scenarioDescReq': '请输入场景描述',
      't.scenarioNameInvalid': '场景名只能包含字母、数字和下划线，且必须以字母开头',
      't.generating': '正在生成...',
      't.scenarioInfo': '场景信息：',
      't.name': '名称：',
      't.dir': '目录：',
      't.applyScenario': '应用此场景',
      't.genFailed': '生成失败: ',
      't.scenarioApplied': '已切换到场景: {0}',
      't.newScenarioFailed': '加载新场景失败: {0}',
      't.scanningPops': '正在扫描所有问题的已保存种群...',
      't.genN': '第 {0} 代',
      't.loadingPop': '正在加载种群...',
      't.startGen': '起始代数',
      't.heurCount': '启发式数量',
      't.posCount': '积极特征',
      't.negCount': '消极特征',
      't.countUnit': '{0} 个',
      't.itemsUnit': '{0} 条',
      't.startWithPop': '用此种群开始进化',
      't.popListFailed': '加载种群列表失败: {0}',
      't.statusGenerating': '正在生成',
      't.statusStartGen': '开始生成',
      't.statusDone': '已完成',
      't.statusLoaded': '已加载',
      't.statusMutating': '正在进行 突变',
      't.statusHybridizing': '正在进行 杂交',
      't.statusOptimizing': '正在进行 优化',
      't.statusSelecting': '正在进行 筛选与反思',
      't.statusInitializing': '初始化中',
      't.titleInit': '初始化种群',
      't.genPopulation': '第{0}代种群',
      't.titleResume': '续训起点 (第{0}代)',

      // ── 排行榜 / 登录 ──
      'rank.title2': '用户排行榜',
      'rank.subtitle': '根据每次进化实验的最佳适应度排名',
      'rank.back': '返回主页',
      'rank.colRank': '排名',
      'rank.colUser': '用户',
      'rank.colBest': '最佳适应度',
      'rank.empty': '暂无排行数据',
      'rank.loadFailed': '加载失败',
      'rank.me': '(我)',
      'login.brandSub': '启发式组合优化进化框架',
      'login.userId': '用户 ID',
      'login.userIdPh': '输入用户ID',
      'login.password': '密码',
      'login.passwordPh': '输入密码',
      'login.showPwd': '显示密码',
      'login.hidePwd': '隐藏密码',
      'login.loginBtn': '登 录',
      'login.noAccount': '还没有账号？',
      'login.registerNow': '立即注册',
      'login.regUserId': '用户 ID',
      'login.regUserIdPh': '设置用户ID',
      'login.regPasswordPh': '设置密码',
      'login.regUserName': '昵称（可选）',
      'login.regUserNamePh': '输入昵称',
      'login.regBtn': '注 册',
      'login.hasAccount': '已有账号？',
      'login.loginNow': '立即登录',
      'login.needCredentials': '请输入用户ID和密码',
      'login.loggingIn': '登录中...',
      'login.failed': '登录失败，请重试',
      'login.networkError': '网络错误，请稍后重试',
      'login.needRegFields': '用户ID和密码不能为空',
      'login.pwdTooShort': '密码至少6位',
      'login.regSuccess': '注册成功！即将跳转登录...',
      'login.registering': '注册中...',
      'login.regFailed': '注册失败'
    },

    en: {
      // ── Page titles ──
      'app.title': 'NSEH — LLM-Powered Heuristic Optimization Evolution',
      'login.title': 'NSEH — Login',
      'rank.title': 'NSEH — Leaderboard',

      // ── Header ──
      'header.welcome': 'Welcome, ',
      'header.admin': '⚙️ Admin',
      'header.theme': 'Theme',
      'header.logout': 'Logout',
      'header.langBtn': '中文',          // 英文模式下按钮显示 中文（目标语言）
      'header.langTitle': '切换语言 / Switch language',

      // ── Tabs ──
      'tab.setting': 'Settings',
      'tab.evolution': 'Evolution',
      'tab.results': 'Results',

      // ── Settings page ──
      'setting.evoParams': 'Evolution Parameters',
      'setting.popSize': 'Population Size',
      'setting.gens': 'Generations',
      'setting.mutation': 'Mutations per Generation',
      'setting.hybridization': 'Hybridization Parents',
      'setting.reflection': 'Reflection Features',
      'setting.llmConfig': 'LLM Configuration',
      'setting.apiKey': 'API Key',
      'setting.apiKeyPh': 'your api key',
      'setting.baseUrl': 'Base URL',
      'setting.llmModel': 'LLM Model',
      'setting.customModelPh': 'Custom model name',
      'setting.llmHint': 'Select a preset or enter a custom model name',
      'setting.scenario': 'Problem Scenario',
      'setting.selectScenario': 'Select Scenario',
      'setting.selfAdapt': 'Self-Adaptation',
      'setting.problemDesc': 'Problem Description',
      'setting.funName': 'Function Name',
      'setting.funArgs': 'Function Arguments',
      'setting.addArg': 'Add Argument',
      'setting.funReturn': 'Return Values',
      'setting.addReturn': 'Add Return Value',
      'setting.funNotes': 'Notes',
      'setting.ascend': 'Optimization Direction',
      'setting.ascendMin': 'Minimize fitness',
      'setting.ascendMax': 'Maximize fitness',
      'setting.problemPath': 'Problem Directory',
      'setting.browse': 'Browse',
      'setting.trainData': 'Training Data',
      'setting.trainSolution': 'Reference Solution',
      'setting.startEvo': 'Start Evolution',
      'setting.loadPop': 'Load Population',

      // ── Evolution page ──
      'evo.title': 'Evolution Process',
      'evo.scenario': 'Scenario',
      'evo.loading': 'Loading...',
      'evo.progress': '⏳ Evolution Progress',
      'evo.genCount': '{0} / {1} gens',
      'evo.details': 'Heuristic Details',
      'evo.close': 'Close',
      'evo.concept': 'Concept',
      'evo.fitness': 'Fitness',
      'evo.features': 'Features',
      'evo.code': 'Algorithm Code',
      'evo.copy': 'Copy',
      'evo.copied': 'Copied!',
      'evo.waiting': 'Waiting to start',
      'evo.pause': '⏸ Pause',
      'evo.resume': '▶ Resume',
      'evo.prompt': '📝 Prompt',
      'evo.stop': '⏹ Stop',

      // ── Results page ──
      'results.title': 'Evolution Results',
      'results.chartLine': 'Best per Gen',
      'results.chartMulti': 'Best·Mean·Var',
      'results.chartTop3': 'Top-3 Bars',
      'results.chartAll': 'All Heuristics',
      'results.chartTokens': 'Token Usage',
      'results.openDir': 'Open Results Folder',
      'results.viewRank': 'View Leaderboard',

      // ── Modals ──
      'modal.loadPopTitle': 'Load Existing Population',
      'modal.loadPopDesc': 'Select a population file; NSEH will continue evolving from that generation.',
      'modal.problemDir': 'Problem Directory: ',
      'modal.scan': 'Scan & Refresh',
      'modal.loadingPops': 'Loading saved populations...',
      'modal.noPops': 'No saved populations',
      'modal.selfAdaptTitle': 'Scenario Self-Adaptation',
      'modal.selfAdaptDesc': 'Describe the combinatorial optimization scenario you want; AI will generate problem components, dataset scripts and evaluation code automatically.',
      'modal.scenarioName': 'Scenario name (English, e.g. vehicle_routing)',
      'modal.scenarioDesc': 'Scenario Description',
      'modal.scenarioPh': 'e.g. I need to solve a vehicle routing problem with time windows (VRPTW): 1 depot and 50 customer nodes, each vehicle has a capacity limit, minimize total travel distance.',
      'modal.genScenario': 'Generate Scenario',
      'modal.stepConfig': 'Generating problem config...',
      'modal.stepHeuristic': 'Generating default heuristic...',
      'modal.stepDatagen': 'Generating dataset scripts...',
      'modal.stepTraineval': 'Generating evaluation code...',
      'modal.stepFinish': 'Done...',
      'modal.adminTitle': 'Admin Panel',
      'modal.loading': 'Loading...',

      // ── JS dynamic text ──
      't.loadingUsers': 'Loading user data...',
      't.userList': 'User List',
      't.colName': 'Name',
      't.colAccount': 'Account',
      't.colRole': 'Role',
      't.colBest': 'Best',
      't.colExpCount': 'Experiments',
      't.colRegistered': 'Registered',
      't.expRecords': 'Experiment Records (last 100)',
      't.colUser': 'User',
      't.colStart': 'Start',
      't.colEnd': 'End',
      't.colStatus': 'Status',
      't.colBestVal': 'Best Value',
      't.loadFailed': 'Failed to load: ',
      't.configSavedSession': 'Config is saved in this session and takes effect when evolution starts',
      't.finishSettingsFirst': 'Please complete the settings before switching pages',
      't.paramsAutoFixed': 'Invalid evolution parameters auto-filled',
      't.loadingCfg': 'Loading config for {0}...',
      't.cfgLoaded': 'Switched to {0}',
      't.loadCfgFailed': 'Failed to load config',
      't.loadCfgFailed2': '[FAIL] Failed to load problem config: {0}',
      't.customModelHint': 'Enter a custom model name and fill in BASE_URL manually',
      't.modelInfo': 'Model: {0}',
      't.newArg': 'new_arg',
      't.newReturn': 'new_return',
      't.fileSelected': 'File selected',
      't.dirSelected': 'Directory selected: {0}',
      't.dirFailed': 'Could not resolve directory path; please enter it manually',
      't.unknown': 'Unknown',
      't.custom': 'Custom',
      't.offlineFallback': ' (offline)',
      't.timerGen': '⏱ Gen {0}/{1} · {2}',
      't.timerInit': '⏱ Initializing... {0}',
      't.timerGenCount': '{0} / {1} gens',
      't.confirm': 'Confirm',
      't.cancel': 'Cancel',
      't.needApiKey': 'Please enter API Key',
      't.needBaseUrl': 'Please enter BASE_URL',
      't.needModel': 'Please select or enter an LLM model name',
      't.needProblemPath': 'Please enter the problem directory',
      't.starting': 'Starting...',
      't.savingAndStart': 'Saving config and starting evolution...',
      't.configSaved': 'Config saved, starting evolution...',
      't.saveFailed': 'Failed to save config',
      't.evoStarted': 'Evolution started ✓',
      't.startEvo': 'Start Evolution',
      't.evoPaused': 'Evolution paused',
      't.evoResumed': 'Evolution resumed...',
      't.confirmStop': 'Stop the current evolution? Progress of the current generation will be lost.',
      't.evoStopped': 'Evolution stopped',
      't.promptFetchFailed': 'Failed to fetch prompt template: {0}',
      't.statusRunning': 'Evolving...',
      't.statusCompleted': 'Evolution completed ✓',
      't.statusPaused': 'Paused',
      't.statusWaiting': 'Waiting to start',
      't.evoDoneToast': 'Evolution complete ✓ Switch to results page',
      't.genFallback': 'Gen {0}',
      't.waiting': 'Waiting',
      't.bestFitness': 'Best Fitness: ',
      't.posFeatures': 'Positive Features',
      't.negFeatures': 'Negative Features',
      't.noHeuristics': 'No heuristics yet',
      't.unnamedHeuristic': 'Unnamed heuristic',
      't.noTags': 'No tags',
      't.detailNotFound': 'Heuristic details not found',
      't.heuristicN': 'Heuristic {0}',
      't.clipboardFail': 'Clipboard unavailable; please copy manually',
      't.customPrompt': 'Custom Prompts',
      't.funReq': 'Function Requirements',
      't.mutation': 'MUTATION',
      't.hybridization': 'HYBRIDIZATION',
      't.optimization': 'OPTIMIZATION',
      't.analyze': 'Analysis',
      't.confirmUpdate': 'Confirm Update',
      't.promptUpdated': 'Prompt updated',
      't.cannotOpenDir': 'Could not open results directory',
      't.chartBestFitness': 'Best Fitness',
      't.chartBest': 'Best: ',
      't.chartGen': 'Generation',
      't.chartFitness': 'Fitness',
      't.chartBestVal': 'Best',
      't.chartAvg': 'Mean',
      't.chartVar': 'Variance',
      't.chartRank': 'Rank',
      't.chartHeurRank': 'Heuristic Rank',
      't.chartTop3Label': 'Latest Gen TOP{0}',
      't.chartAllLabel': 'All Heuristics (Current Gen)',
      't.chartMutation': 'Mutation',
      't.chartHybridization': 'Hybridization',
      't.chartOptimization': 'Optimization',
      't.scenarioNameReq': 'Please enter a scenario name',
      't.scenarioDescReq': 'Please enter a scenario description',
      't.scenarioNameInvalid': 'Name may only contain letters, digits and underscores, and must start with a letter',
      't.generating': 'Generating...',
      't.scenarioInfo': 'Scenario Info:',
      't.name': 'Name: ',
      't.dir': 'Path: ',
      't.applyScenario': 'Apply This Scenario',
      't.genFailed': 'Generation failed: ',
      't.scenarioApplied': 'Switched to scenario: {0}',
      't.newScenarioFailed': 'Failed to load new scenario: {0}',
      't.scanningPops': 'Scanning saved populations across all problems...',
      't.genN': 'Gen {0}',
      't.loadingPop': 'Loading population...',
      't.startGen': 'Start Generation',
      't.heurCount': 'Heuristics',
      't.posCount': 'Positive Features',
      't.negCount': 'Negative Features',
      't.countUnit': '{0}',
      't.itemsUnit': '{0}',
      't.startWithPop': 'Start Evolution with This Population',
      't.popListFailed': 'Failed to load population list: {0}',
      't.statusGenerating': 'Generating...',
      't.statusStartGen': 'Generating...',
      't.statusDone': 'Completed',
      't.statusLoaded': 'Loaded',
      't.statusMutating': 'Mutating...',
      't.statusHybridizing': 'Hybridizing...',
      't.statusOptimizing': 'Optimizing...',
      't.statusSelecting': 'Selecting & Reflecting...',
      't.statusInitializing': 'Initializing...',
      't.titleInit': 'Initial Population',
      't.genPopulation': 'Generation {0}',
      't.titleResume': 'Resume Point (Gen {0})',

      // ── Rank / Login ──
      'rank.title2': 'User Leaderboard',
      'rank.subtitle': 'Ranked by best fitness across evolution experiments',
      'rank.back': 'Back to Home',
      'rank.colRank': 'Rank',
      'rank.colUser': 'User',
      'rank.colBest': 'Best Fitness',
      'rank.empty': 'No ranking data yet',
      'rank.loadFailed': 'Failed to load',
      'rank.me': '(me)',
      'login.brandSub': 'Heuristic Combinatorial Optimization Evolution Framework',
      'login.userId': 'User ID',
      'login.userIdPh': 'Enter user ID',
      'login.password': 'Password',
      'login.passwordPh': 'Enter password',
      'login.showPwd': 'Show password',
      'login.hidePwd': 'Hide password',
      'login.loginBtn': 'Log In',
      'login.noAccount': "Don't have an account?",
      'login.registerNow': 'Register now',
      'login.regUserId': 'User ID',
      'login.regUserIdPh': 'Set user ID',
      'login.regPasswordPh': 'Set password',
      'login.regUserName': 'Nickname (optional)',
      'login.regUserNamePh': 'Enter nickname',
      'login.regBtn': 'Register',
      'login.hasAccount': 'Already have an account?',
      'login.loginNow': 'Log in now',
      'login.needCredentials': 'Please enter user ID and password',
      'login.loggingIn': 'Logging in...',
      'login.failed': 'Login failed, please retry',
      'login.networkError': 'Network error, please retry later',
      'login.needRegFields': 'User ID and password cannot be empty',
      'login.pwdTooShort': 'Password must be at least 6 characters',
      'login.regSuccess': 'Registration successful! Redirecting to login...',
      'login.registering': 'Registering...',
      'login.regFailed': 'Registration failed'
    }
  };

  const I18N = {
    lang: 'zh',

    init() {
      let saved = 'zh';
      try {
        saved = localStorage.getItem(STORAGE_KEY) || 'zh';
      } catch (e) { /* ignore */ }
      if (saved !== 'zh' && saved !== 'en') saved = 'zh';
      this.lang = saved;
      this._syncCookie();
      // 初始应用（幂等，可重复调用）
      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => this.apply());
      } else {
        this.apply();
      }
    },

    t(key) {
      const dict = DICT[this.lang] || DICT.zh;
      let text = dict[key];
      if (text === undefined) {
        // 回退到中文，再不行返回 key 本身
        text = DICT.zh[key];
        if (text === undefined) return key;
      }
      const args = Array.prototype.slice.call(arguments, 1);
      if (args.length) {
        text = String(text).replace(/\{(\d+)\}/g, (m, i) => (args[+i] !== undefined ? args[+i] : m));
      }
      return text;
    },

    isZh() { return this.lang === 'zh'; },

    _syncCookie() {
      try {
        document.cookie = 'lang=' + this.lang + '; path=/; max-age=31536000';
      } catch (e) { /* ignore */ }
    },

    setLang(lang) {
      if (lang !== 'zh' && lang !== 'en') return;
      if (this.lang === lang) return;
      this.lang = lang;
      try { localStorage.setItem(STORAGE_KEY, lang); } catch (e) { /* ignore */ }
      this._syncCookie();
      this.apply();
      // 通知页面重绘动态内容（图表、种群卡片、排行榜等）
      try {
        document.dispatchEvent(new CustomEvent('i18n:changed', { detail: { lang } }));
      } catch (e) { /* ignore */ }
    },

    toggle() {
      this.setLang(this.isZh() ? 'en' : 'zh');
    },

    // 翻译 DOM 中带 data-i18n / data-i18n-placeholder 的元素
    apply() {
      const langAttr = this.isZh() ? 'zh-CN' : 'en';
      document.documentElement.setAttribute('lang', langAttr);

      document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (!key) return;
        const text = this.t(key);
        // 仅当元素没有子元素节点时才用 textContent，否则只替换纯文本首节点
        const hasElementChildren = Array.prototype.some.call(el.childNodes, n => n.nodeType === 1);
        if (!hasElementChildren) {
          el.textContent = text;
        } else {
          // 保留子元素（如 svg + span），只更新最后一个文本节点（span 内容）
          const span = el.querySelector('[data-i18n]') || el;
          if (span === el) {
            // 递归由外层 querySelectorAll 处理子元素，这里不动
          }
        }
      });

      document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        if (key) el.setAttribute('placeholder', this.t(key));
      });

      document.querySelectorAll('[data-i18n-title]').forEach(el => {
        const key = el.getAttribute('data-i18n-title');
        if (key) el.setAttribute('title', this.t(key));
      });

      // 页面标题
      const titleKey = document.body.getAttribute('data-i18n-title-key');
      if (titleKey) document.title = this.t(titleKey);

      // 语言切换按钮文本（显示目标语言）
      document.querySelectorAll('[data-i18n-lang-btn]').forEach(btn => {
        btn.textContent = this.t('header.langBtn');
      });
    }
  };

  // 自动初始化 + 绑定切换按钮（事件委托，兼容动态添加）
  I18N.init();
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-i18n-lang-btn]');
    if (btn) I18N.toggle();
  });

  global.I18N = I18N;
  global.T = function (key) {
    return I18N.t.apply(I18N, arguments);
  };
})(window);
