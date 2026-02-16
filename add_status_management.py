#!/usr/bin/env python3
"""
やる/やらない判断 + ステータス管理を追加
"""
import re

# 既存HTMLを読み込む
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ステータス管理用CSSを追加
status_css = """
/* ========== ステータス管理用CSS ========== */
.status-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 10px;
  padding: 10px;
  background: #f9f9f9;
  border-radius: 6px;
  flex-wrap: wrap;
}
.status-label {
  font-size: 0.85em;
  font-weight: 600;
  color: #555;
}
.status-select {
  padding: 4px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.85em;
  background: white;
  cursor: pointer;
}
.status-select.status-not-started { border-color: #ddd; background: #fff; }
.status-select.status-recorded { border-color: #3b82f6; background: #eff6ff; color: #3b82f6; }
.status-select.status-written { border-color: #8b5cf6; background: #f5f3ff; color: #8b5cf6; }
.status-select.status-published { border-color: #10b981; background: #ecfdf5; color: #10b981; }
.status-select.status-skipped { border-color: #ef4444; background: #fef2f2; color: #ef4444; }

.do-checkbox-wrapper {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85em;
}
.do-checkbox-wrapper input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: #10b981;
}
.topic-card.skipped {
  opacity: 0.4;
  filter: grayscale(0.5);
}
.topic-card.skipped summary {
  color: #999;
}
"""

# </style>の直前にCSSを挿入（既存のゲーミフィケーションCSSの後）
if '</style>' in html:
    html = html.replace('</style>', status_css + '\n</style>')

# 各<details>の<div class="topic-body">内にステータスコントロールを追加
def add_status_controls(match):
    topic_num_match = re.search(r'<span class="topic-num">(#\d+)</span>', match.group(0))
    if topic_num_match:
        topic_id = topic_num_match.group(1).replace('#', 'topic-')

        status_html = f'''<div class="status-controls">
  <div class="do-checkbox-wrapper">
    <input type="checkbox" id="{topic_id}-do" onchange="updateStatusManagement()" checked>
    <label for="{topic_id}-do" class="status-label">やる</label>
  </div>
  <select class="status-select status-not-started" id="{topic_id}-status" onchange="updateStatusManagement()">
    <option value="not-started">未着手</option>
    <option value="recorded">録音済み</option>
    <option value="written">記事化済み</option>
    <option value="published">公開済み</option>
    <option value="skipped">やらない</option>
  </select>
</div>
'''

        # <div class="topic-body">の直後に挿入
        if '<div class="topic-body">' in match.group(0):
            return match.group(0).replace('<div class="topic-body">', '<div class="topic-body">\n' + status_html)

    return match.group(0)

# 各<details>要素を処理
html = re.sub(r'<details class="topic-card.*?</details>', add_status_controls, html, flags=re.DOTALL)

# JavaScriptを追加（既存のゲーミフィケーションJSの後）
status_js = """
// ========== ステータス管理機能 ==========
const STATUS_STORAGE_KEY = 'iwata-interview-status';

// ステータスデータの読み込み
function loadStatusData() {
  const saved = localStorage.getItem(STATUS_STORAGE_KEY);
  if (saved) {
    return JSON.parse(saved);
  }
  return {
    doStatus: {},    // やる/やらない
    workStatus: {}   // 作業ステータス
  };
}

// ステータスデータの保存
function saveStatusData(data) {
  localStorage.setItem(STATUS_STORAGE_KEY, JSON.stringify(data));
}

// ステータス管理の更新
function updateStatusManagement() {
  const statusData = loadStatusData();

  // 全ての「やる」チェックボックスと作業ステータスを取得
  document.querySelectorAll('input[id$="-do"]').forEach(cb => {
    const topicId = cb.id.replace('-do', '');
    statusData.doStatus[topicId] = cb.checked;

    // カードの見た目を更新
    const card = cb.closest('.topic-card');
    if (card) {
      if (!cb.checked) {
        card.classList.add('skipped');
      } else {
        card.classList.remove('skipped');
      }
    }
  });

  document.querySelectorAll('select[id$="-status"]').forEach(sel => {
    const topicId = sel.id.replace('-status', '');
    statusData.workStatus[topicId] = sel.value;

    // セレクトボックスの色を更新
    sel.className = 'status-select status-' + sel.value;

    // 「やらない」を選択した場合、「やる」チェックボックスも外す
    if (sel.value === 'skipped') {
      const doCheckbox = document.getElementById(topicId + '-do');
      if (doCheckbox) {
        doCheckbox.checked = false;
        const card = doCheckbox.closest('.topic-card');
        if (card) card.classList.add('skipped');
      }
    }
  });

  saveStatusData(statusData);

  // ダッシュボードの統計を更新
  updateStatusStats(statusData);

  // 進捗も更新（ゲーミフィケーション機能との連携）
  if (typeof updateProgress === 'function') {
    updateProgress();
  }
}

// ダッシュボードに統計を追加
function updateStatusStats(statusData) {
  const stats = {
    total: 100,
    doCount: 0,
    notStarted: 0,
    recorded: 0,
    written: 0,
    published: 0,
    skipped: 0
  };

  Object.values(statusData.doStatus).forEach(v => {
    if (v) stats.doCount++;
  });

  Object.values(statusData.workStatus).forEach(v => {
    if (v === 'not-started') stats.notStarted++;
    else if (v === 'recorded') stats.recorded++;
    else if (v === 'written') stats.written++;
    else if (v === 'published') stats.published++;
    else if (v === 'skipped') stats.skipped++;
  });

  // ダッシュボードに表示（既存のダッシュボードに追加）
  let statsHtml = document.getElementById('status-stats-container');
  if (!statsHtml) {
    // 新しいステータス統計セクションを作成
    const dashboard = document.querySelector('.progress-dashboard');
    if (dashboard) {
      const container = document.createElement('div');
      container.id = 'status-stats-container';
      container.innerHTML = `
        <h3 style="margin-top:20px; margin-bottom:10px; font-size:1.1em;">📊 作業ステータス</h3>
        <div class="priority-progress">
          <div class="priority-card">
            <div class="priority-label">📝 未着手</div>
            <div class="fraction" id="stat-not-started">0</div>
          </div>
          <div class="priority-card">
            <div class="priority-label">🎤 録音済み</div>
            <div class="fraction" id="stat-recorded">0</div>
          </div>
          <div class="priority-card">
            <div class="priority-label">✍️ 記事化済み</div>
            <div class="fraction" id="stat-written">0</div>
          </div>
          <div class="priority-card">
            <div class="priority-label">✅ 公開済み</div>
            <div class="fraction" id="stat-published">0</div>
          </div>
          <div class="priority-card">
            <div class="priority-label">やる予定</div>
            <div class="fraction" id="stat-do-count">0</div>
          </div>
        </div>
      `;
      dashboard.appendChild(container);
    }
  }

  // 統計値を更新
  const updateStat = (id, value) => {
    const elem = document.getElementById(id);
    if (elem) elem.textContent = value;
  };

  updateStat('stat-not-started', stats.notStarted);
  updateStat('stat-recorded', stats.recorded);
  updateStat('stat-written', stats.written);
  updateStat('stat-published', stats.published);
  updateStat('stat-do-count', stats.doCount);
}

// 初期化時にステータスを復元
document.addEventListener('DOMContentLoaded', function() {
  // 少し遅延させて、他のDOMContentLoadedの後に実行
  setTimeout(() => {
    const statusData = loadStatusData();

    // 「やる」チェックボックスの復元
    Object.entries(statusData.doStatus).forEach(([id, checked]) => {
      const cb = document.getElementById(id + '-do');
      if (cb) {
        cb.checked = checked;
      }
    });

    // 作業ステータスの復元
    Object.entries(statusData.workStatus).forEach(([id, status]) => {
      const sel = document.getElementById(id + '-status');
      if (sel) {
        sel.value = status;
        sel.className = 'status-select status-' + status;
      }
    });

    updateStatusManagement();
  }, 100);
});
"""

# </script>の直前にJSを挿入
if '</script>' in html:
    html = html.replace('</script>', '\n' + status_js + '\n</script>')

# 保存
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ ステータス管理機能を追加しました")
print("   各テーマごとに:")
print("   - 「やる」チェックボックス（やる/やらない判断）")
print("   - ステータスドロップダウン（未着手/録音済み/記事化済み/公開済み/やらない）")
print("   - ダッシュボードに作業ステータス統計を表示")
