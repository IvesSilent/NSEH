// 全局变量
let population_data = [];
let lastScrollTime = 0;
const SCROLL_INTERVAL = 15000; // 15秒间隔

document.addEventListener('DOMContentLoaded', function() {
    // 页面切换逻辑
    const pageTabs = document.querySelectorAll('.tab');
    const pages = document.querySelectorAll('.page');

    pageTabs.forEach((tab, index) => {
        tab.addEventListener('click', () => {
            // 移除所有活动状态
            pageTabs.forEach(t => t.classList.remove('active'));
            pages.forEach(p => p.classList.remove('active'));
            // 添加当前活动状态
            tab.classList.add('active');
            pages[index].classList.add('active');
        });

        //【修改内容start】
        tab.addEventListener('click', function () {
        if (this.id !== 'setting-tab') {
            if (!validateSettings()) {
                // 阻止切换页面
                event.preventDefault();
            }
        }
        });
        //【修改内容end】


    });

    //【修改内容start】
    // 为开始进化按钮添加点击事件
    document.getElementById('start-evolution-btn').addEventListener('click', function() {
        if (validateSettings()) {
            // 保存配置并开始进化
            document.getElementById('start-evolution-btn').click();
        }
    });

    // 参数检查函数
    function validateSettings() {
        const populationCapacity = parseInt(document.getElementById('population_capacity').value);
        const numGenerations = parseInt(document.getElementById('num_generations').value);
        const numMutation = parseInt(document.getElementById('num_mutation').value);
        const numHybridization = parseInt(document.getElementById('num_hybridization').value);
        const numReflection = parseInt(document.getElementById('num_reflection').value);

        const apiKey = document.getElementById('api_key').value.trim();
        const baseUrl = document.getElementById('base_url').value.trim();
        const llmModel = document.getElementById('llm_model').value.trim();

        let isValid = true;

        // 检查进化参数
        if (isNaN(populationCapacity) || populationCapacity < 0 ||
            isNaN(numGenerations) || numGenerations < 0 ||
            isNaN(numMutation) || numMutation < 0 ||
            isNaN(numHybridization) || numHybridization < 0 ||
            isNaN(numReflection) || numReflection < 0) {
            alert('进化参数设置有误，请重新设置\n\n请注意，进化参数需为非负整数');
            isValid = false;
        }

        // 检查LLM配置
        if (!apiKey || !baseUrl || !llmModel) {
            alert('LLM配置有误，请重新设置\n\n请确保API_key可用且跟你所选的LLM匹配');
            isValid = false;
        }

        return isValid;
    }
    //【修改内容end】

    // 初始化设置页面
    initSettingPage();
    // 初始化进化页面
    initEvolutionPage();
    // 初始化结果页面
    initResultsPage();

    // 设置定时器，定期获取种群数据
    setInterval(fetchPopulationData, 2000); // 每2秒获取一次数据
    // 检查进化是否完成
    setInterval(checkEvolutionStatus, 2000);

    document.getElementById('logout-btn').addEventListener('click', function() {
        fetch('/api/logout', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // 退出成功，跳转到登录页面
                window.location.href = '/login';
            }
        })
        .catch(error => {
            console.error('Error during logout:', error);
            alert('退出过程中出错，请稍后再试');
        });
    });
});

function fetchPopulationData() {
    fetch('/api/get_population_data')
        .then(response => response.json())
        .then(data => {
            population_data = data.population_data; // 更新全局变量

            renderPopulationData(data.population_data, data.current_population_index);
        })
        .catch(error => {
            console.error('Error fetching population data:', error);
        });
}

function checkEvolutionStatus() {
    fetch('/api/check_evolution_status')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'completed') {
                document.getElementById('results-tab').click();
            }
        })
        .catch(error => {
            console.error('Error checking evolution status:', error);
        });
}

function initSettingPage() {
    // 添加参数
    document.getElementById('add_arg_btn').addEventListener('click', function() {
        const container = document.getElementById('fun_args_container');
        const newItem = document.createElement('div');
        newItem.className = 'arg-item';
        newItem.contentEditable = true;
        newItem.textContent = '新参数';
        container.appendChild(newItem);
    });

    // 添加返回值
    document.getElementById('add_return_btn').addEventListener('click', function() {
        const container = document.getElementById('fun_return_container');
        const newItem = document.createElement('div');
        newItem.className = 'arg-item';
        newItem.contentEditable = true;
        newItem.textContent = '新返回值';
        container.appendChild(newItem);
    });

    // 删除参数和返回值
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('arg-item')) {
            if (e.target.textContent.trim() === '') {
                e.target.remove();
            }
        }
    });

    // 文件浏览按钮
    document.getElementById('browse_problem_path').addEventListener('click', function() {
        document.getElementById('problem_path_file').click();
    });

    document.getElementById('problem_path_file').addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            document.getElementById('problem_path').value = e.target.files[0].path;
        }
    });

    // 文件浏览按钮
    document.querySelectorAll('.browse-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const input = this.previousElementSibling;
            const fileInput = document.createElement('input');
            fileInput.type = 'file';
            fileInput.webkitdirectory = true;
            fileInput.directory = true;
            fileInput.addEventListener('change', function() {
                if (this.files && this.files.length > 0) {
                    input.value = this.files[0].path;
                }
            });
            fileInput.click();
        });
    });

    // 保存配置
    document.getElementById('start-evolution-btn').addEventListener('click', function() {
        const config = {
            population_capacity: parseInt(document.getElementById('population_capacity').value),
            num_generations: parseInt(document.getElementById('num_generations').value),
            num_mutation: parseInt(document.getElementById('num_mutation').value),
            num_hybridization: parseInt(document.getElementById('num_hybridization').value),
            num_reflection: parseInt(document.getElementById('num_reflection').value),
            api_key: document.getElementById('api_key').value,
            base_url: document.getElementById('base_url').value,
            llm_model: document.getElementById('llm_model').value,
            problem: document.getElementById('problem').value,
            fun_name: document.getElementById('fun_name').value,
            fun_args: Array.from(document.querySelectorAll('#fun_args_container .arg-item')).map(item => item.textContent),
            fun_return: Array.from(document.querySelectorAll('#fun_return_container .arg-item')).map(item => item.textContent),
            fun_notes: document.getElementById('fun_notes').value,
            ascend: document.getElementById('ascend').value === 'true',
            problem_path: document.getElementById('problem_path').value,
            train_data: document.getElementById('train_data').value,
            train_solution: document.getElementById('train_solution').value
        };

        // 保存配置到本地存储
        localStorage.setItem('nseh_config', JSON.stringify(config));

        // 发送配置到服务器
        fetch('/api/save_config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // 切换到进化页面
                document.getElementById('evolution-tab').click();
                // 开始进化
                startEvolution();
            }
        });
    });



}

function initEvolutionPage() {
    // 获取种群数据
    fetch('/api/get_population_data')
        .then(response => response.json())
        .then(data => {
            population_data = data.population_data;
            renderPopulationData(data.population_data, data.current_population_index);
        });

    // 进化控制按钮
    document.getElementById('pause-evolution-btn').addEventListener('click', function() {
        fetch('/api/pause_evolution', {
            method: 'POST'
        });
    });

    document.getElementById('resume-evolution-btn').addEventListener('click', function() {
        fetch('/api/resume_evolution', {
            method: 'POST'
        });
    });

    document.getElementById('stop-evolution-btn').addEventListener('click', function() {
        fetch('/api/stop_evolution', {
            method: 'POST'
        }).then(() => {
            document.getElementById('setting-tab').click();
        });
    });

    document.getElementById('edit-prompt-btn').addEventListener('click', function() {
        fetch('/api/get_prompt_template')
            .then(response => response.json())
            .then(data => {
                // 显示提示词编辑卡片
                showPromptEditCard(data);
                // 暂停进化
                fetch('/api/pause_evolution', { method: 'POST' });
            });
    });
}

// 显示提示词编辑卡片
function showPromptEditCard(templateData) {
    // 创建提示词编辑卡片的HTML
    const promptEditCardHTML = `
        <div class="prompt-edit-card">
            <div class="details-header">
                <h3>用户自定义提示词</h3>
                <button class="close-btn" onclick="closePromptEditCard()">取消</button>
            </div>
            <div class="details-content">
                <div class="form-group">
                    <label for="fun_requirement">函数要求</label>
                    <textarea id="fun_requirement" rows="4">${templateData.fun_requirement}</textarea>
                </div>
                <div class="form-group">
                    <label for="strategy_MUT">MUTATION突变</label>
                    <textarea id="strategy_MUT" rows="4">${templateData.strategy_MUT}</textarea>
                </div>
                <div class="form-group">
                    <label for="strategy_HYB">HYBRIDIZATION繁殖</label>
                    <textarea id="strategy_HYB" rows="4">${templateData.strategy_HYB}</textarea>
                </div>
                <div class="form-group">
                    <label for="strategy_OPT">OPTIMIZATION优化</label>
                    <textarea id="strategy_OPT" rows="4">${templateData.strategy_OPT}</textarea>
                </div>
                <div class="form-group">
                    <label for="analyze">分析过程</label>
                    <textarea id="analyze" rows="4">${templateData.analyze}</textarea>
                </div>
                <div class="form-row" style="justify-content: flex-end; margin-top: 20px;">
                    <div class="button-container">
    <button class="control-btn resume-btn" onclick="updateAndClosePromptEditCard()">确认</button>
    <button class="control-btn" onclick="closePromptEditCard()">取消</button>
</div>
                </div>
            </div>
        </div>
    `;

    // 显示卡片
    document.body.insertAdjacentHTML('beforeend', promptEditCardHTML);
    document.body.classList.add('prompt-edit-visible');
}

// 关闭提示词编辑卡片
function closePromptEditCard() {
    document.querySelector('.prompt-edit-card').remove();
    document.body.classList.remove('prompt-edit-visible');
    // 继续进化
    fetch('/api/resume_evolution', { method: 'POST' });
}

// 更新提示词并关闭卡片
function updateAndClosePromptEditCard() {
    const updatedTemplate = {
        fun_requirement: document.getElementById('fun_requirement').value,
        strategy_MUT: document.getElementById('strategy_MUT').value,
        strategy_HYB: document.getElementById('strategy_HYB').value,
        strategy_OPT: document.getElementById('strategy_OPT').value,
        analyze: document.getElementById('analyze').value
    };

    fetch('/api/update_prompt_template', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedTemplate)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            closePromptEditCard();
        } else {
            alert('更新提示词失败: ' + data.message);
        }
    });
}

function initResultsPage() {
    // 打开结果目录
    document.getElementById('open-results-btn').addEventListener('click', function() {
        fetch('/api/open_results_directory')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert('结果目录已打开');
                } else {
                    alert('无法打开结果目录');
                }
            })
            .catch(error => {
                console.error('Error opening results directory:', error);
            });
    });
     // 定期更新结果图表
    setInterval(updateResultsChart, 2000);

// 查看用户排行榜
document.getElementById('open-rank-btn').addEventListener('click', function() {
    window.location.href = '/rank';
});

//    // 获取历史最优适应度数据
//    fetch('/api/get_results_data')
//        .then(response => response.json())
//        .then(data => {
//            renderResultsChart(data);
//        });

}

function updateResultsChart() {
    fetch('/api/get_results_data')
        .then(response => response.json())
        .then(data => {
            renderResultsChart(data);
        })
        .catch(error => {
            console.error('Error updating results chart:', error);
        });

}

let resultsChart = null;

function renderResultsChart(resultsData) {
    const ctx = document.getElementById('results-chart').getContext('2d');

    // 销毁旧的Chart实例
    if (resultsChart) {
        resultsChart.destroy();
    }

    resultsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: resultsData.generation_labels,
            datasets: [{
                label: '最优适应度',
                data: resultsData.objectives,
                borderColor: 'rgba(255, 99, 132, 1)',
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function startEvolution() {
    fetch('/api/start_evolution', {
        method: 'POST'
    });
}

function renderPopulationData(populationData, currentPopulationIndex) {
    document.getElementById('current_population_index').value = currentPopulationIndex;
    console.log("renderPopulationData called");

    const populationContainer = document.getElementById('population-container');
    // 仅处理当前种群（增量更新）
    const currentPopulation = populationData[currentPopulationIndex];
     // 检查是否已存在该种群卡片
    let populationCard = document.querySelector(`.population-card[data-index="${currentPopulationIndex}"]`);

    if (!populationCard) {
        // 创建新卡片
        populationCard = createPopulationCard(currentPopulation);
        populationContainer.appendChild(populationCard);
    } else {
        // 更新现有卡片
        populationCard.replaceWith(createPopulationCard(currentPopulation));
    }


    // 事件委托：仅绑定新卡片的事件
    const newCard = document.querySelector(`.population-card[data-index="${currentPopulationIndex}"]`);
    newCard.querySelectorAll('.heuristic-card').forEach(card => {
        card.addEventListener('click', function() {
            const index = parseInt(this.dataset.index);
            showHeuristicDetails(index);
        });
    });

//    // 滚动到当前种群
//    const currentPopulationCard = document.querySelector(`.population-card[data-index="${currentPopulationIndex}"]`);
//    if (currentPopulationCard) {
//        currentPopulationCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
//    }

    // 滚动逻辑（原代码）
    if (currentPopulationIndex >= 0) {
        const now = Date.now();
        if (now - lastScrollTime > SCROLL_INTERVAL) {
            const currentPopulationCard = document.querySelector(`.population-card[data-index="${currentPopulationIndex}"]`);
            if (currentPopulationCard) {
                currentPopulationCard.scrollIntoView({
                    behavior: 'smooth',
                    block: 'center',
                    // 添加滚动动画时间控制（可选）
                    inline: 'nearest',
                    duration: 15000 // 15秒滚动动画
                });
                lastScrollTime = now;
            }
        }
    }

}


function createPopulationCard(population) {
    const populationCard = document.createElement('div');
    populationCard.className = 'population-card';
    populationCard.dataset.index = population.index;

    // 新增特征格式化逻辑
    const formatFeatures = (features) => {
        return features.length > 0
            ? " - " + features.join("<br> - ")  // 换行并添加前缀
            : "暂无特征";
    };

//const formatFeatures = (features) => {
//    const maxDisplayed = 3;
//    const hasMore = features.length > maxDisplayed;
//
//    const displayedFeatures = features.slice(0, maxDisplayed).map(feature =>
//        `<div class="feature-item">${feature}</div>`
//    ).join('<br>');
//
//    if (hasMore) {
//        const hiddenFeatures = features.slice(maxDisplayed).map(feature =>
//            `<div class="feature-item hidden">${feature}</div>`
//        ).join('');
//        return `
//            <div class="feature-container">
//                ${displayedFeatures}
//                <div class="hidden-features">${hiddenFeatures}</div>
//                <button class="toggle-btn">展开更多</button>
//            </div>
//        `;
//    } else {
//        return `
//            <div class="feature-container">
//                ${displayedFeatures}
//            </div>
//        `;
//    }
//};

    populationCard.innerHTML = `
        <div class="population-header">
            <h3>${population.title}</h3>
            <span class="population-status">${population.status}</span>
        </div>
        <div class="population-stats">
            <div class="stat"><strong>最优适应度：</strong>${population.best_objective !== null ? population.best_objective.toFixed(2) : 'N/A'}</div>
            <div class="stat"><strong>积极特征：</strong><br>${formatFeatures(population.memory.positive_features)}</div>
            <div class="stat"><strong>消极特征：</strong><br>${formatFeatures(population.memory.negative_features)}</div>
        </div>
        <div class="heuristics-container" id="heuristics-container-${population.index}">
            ${renderHeuristics(population.heuristics)}
        </div>
    `;

    return populationCard;
}

function renderHeuristics(heuristics) {
    if (heuristics.length === 0) {
        return '<div class="empty-heuristics">暂无启发式</div>';
    }

    return heuristics.map(heuristic => `
        <div class="heuristic-card" data-index="${heuristic.index}">
            <h4>启发式_${heuristic.index}</h4>
            <div class="heuristic-feature">${heuristic.feature}</div>
            <div class="heuristic-objective">适应度: ${heuristic.objective}</div>
        </div>
    `).join('');
}

function showHeuristicDetails(index) {
    console.log("showHeuristicDetails called with index:", index);

    console.log("showHeuristicDetails called with index:", index);

    // 获取启发式详情
    const heuristic = getHeuristicDetails(index);
    if (!heuristic) {
        console.error("Heuristic not found for index:", index);
        return;
    }


    // 更新详情卡片内容
    document.getElementById('detail-concept').textContent = heuristic.concept;
    document.getElementById('detail-objective').textContent = heuristic.objective;
    document.getElementById('detail-feature').textContent = heuristic.feature;
    document.getElementById('detail-algorithm').textContent = heuristic.algorithm;

    // 显示详情卡片
    const detailsContainer = document.getElementById('heuristic-details-container');
    detailsContainer.style.display = 'block';
    document.body.classList.add('details-visible'); // 添加类以调整布局

    // 动态添加按钮
    const codeContainer = document.getElementById('detail-algorithm').parentElement;
    codeContainer.innerHTML = `
        <pre id="detail-algorithm">${heuristic.algorithm}</pre>
        <button class="copy-btn" onclick="copyAlgorithm()">复制</button>
        <div class="copy-success" id="copy-success">已复制！</div>
    `;

}

function closeDetailsCard() {
    document.getElementById('heuristic-details-container').style.display = 'none';
    document.body.classList.remove('details-visible'); // 移除类以恢复布局
}

function getHeuristicDetails(index) {
    // 从population_data中获取启发式详情
    const currentPopulationIndex = getCurrentPopulationIndex(); // 从前端获取当前种群索引
    const population = population_data[currentPopulationIndex];
    return population.heuristics.find(h => h.index === index);
}
function getCurrentPopulationIndex() {
    // 从前端获取当前种群索引，例如通过隐藏的HTML元素
    return parseInt(document.getElementById('current_population_index').value);
}

// 在文件末尾添加
document.getElementById('theme-toggle').addEventListener('click', function() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? null : 'light';
    document.documentElement.setAttribute('data-theme', newTheme);

    // 可选：保存到 localStorage
    localStorage.setItem('theme', newTheme);
});

// 初始化主题（可选）
const savedTheme = localStorage.getItem('theme');
if (savedTheme) {
    document.documentElement.setAttribute('data-theme', savedTheme);
}

function copyAlgorithm() {
    const code = document.getElementById('detail-algorithm').textContent;
    navigator.clipboard.writeText(code).then(() => {
        const successMsg = document.getElementById('copy-success');
        successMsg.style.opacity = '1';
        setTimeout(() => successMsg.style.opacity = '0', 2000);
    });
}