#!/usr/bin/env python3
"""
インタビューテーマ100にゲーミフィケーション要素を追加
"""
import re

# 既存HTMLを読み込む
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ゲーミフィケーション用CSSを追加
gamification_css = """
/* ========== ゲーミフィケーション用CSS ========== */
.progress-dashboard {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 30px;
  border-radius: 12px;
  margin: 20px 0 30px;
  box-shadow: 0 4px 20px rgba(102,126,234,0.3);
}
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-top: 20px;
}
.dashboard-card {
  background: rgba(255,255,255,0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 10px;
  padding: 20px;
  text-align: center;
}
.dashboard-card .big-num {
  font-size: 3em;
  font-weight: 900;
  line-height: 1;
  margin-bottom: 5px;
}
.dashboard-card .label {
  font-size: 0.9em;
  opacity: 0.9;
}
.level-badge {
  display: inline-block;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  padding: 8px 20px;
  border-radius: 20px;
  font-weight: 700;
  font-size: 1.1em;
  margin-top: 10px;
  box-shadow: 0 2px 10px rgba(245,87,108,0.3);
}
.achievements {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 15px;
  justify-content: center;
}
.achievement {
  background: rgba(255,255,255,0.2);
  border: 2px solid rgba(255,255,255,0.3);
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.85em;
  display: flex;
  align-items: center;
  gap: 6px;
}
.achievement.unlocked {
  background: rgba(255,215,0,0.3);
  border-color: rgba(255,215,0,0.6);
  box-shadow: 0 0 15px rgba(255,215,0,0.4);
}
.achievement .icon {
  font-size: 1.2em;
}
.progress-bar-container {
  background: rgba(255,255,255,0.2);
  border-radius: 10px;
  height: 20px;
  margin: 10px 0;
  overflow: hidden;
}
.progress-bar {
  background: linear-gradient(90deg, #56CCF2 0%, #2F80ED 100%);
  height: 100%;
  border-radius: 10px;
  transition: width 0.5s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75em;
  font-weight: 700;
}
.priority-progress {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin-top: 15px;
}
.priority-card {
  background: rgba(255,255,255,0.1);
  border-radius: 8px;
  padding: 12px;
  text-align: center;
}
.priority-card .priority-label {
  font-size: 0.8em;
  margin-bottom: 8px;
  font-weight: 600;
}
.priority-card .fraction {
  font-size: 1.5em;
  font-weight: 700;
}
.checkbox-wrapper {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-right: 10px;
  cursor: pointer;
}
.checkbox-wrapper input[type="checkbox"] {
  width: 20px;
  height: 20px;
  cursor: pointer;
  accent-color: #667eea;
}
.topic-card.completed {
  opacity: 0.6;
  background: #f0f0f0;
}
.topic-card.completed summary {
  text-decoration: line-through;
  color: #999;
}
.motivational-message {
  text-align: center;
  font-size: 1.1em;
  font-weight: 600;
  margin-top: 15px;
  padding: 10px;
  background: rgba(255,255,255,0.2);
  border-radius: 8px;
}
"""

# </style>の直前にCSSを挿入
html = html.replace('</style>', gamification_css + '\n</style>')

# ダッシュボードHTMLを作成
dashboard_html = """
<!-- Progress Dashboard -->
<div class="progress-dashboard">
  <h2 style="margin:0 0 10px 0; font-size:1.5em;">🎮 進捗ダッシュボード</h2>
  <div class="dashboard-grid">
    <div class="dashboard-card">
      <div class="big-num" id="overall-progress">0%</div>
      <div class="label">全体進捗</div>
      <div class="progress-bar-container">
        <div class="progress-bar" id="overall-progress-bar" style="width:0%"></div>
      </div>
    </div>
    <div class="dashboard-card">
      <div class="big-num" id="completed-count">0</div>
      <div class="label">完了テーマ / 100</div>
      <div class="level-badge" id="level-badge">Lv.0 初心者</div>
    </div>
    <div class="dashboard-card">
      <div class="big-num" id="streak-count">0</div>
      <div class="label">連続作業日数</div>
    </div>
  </div>

  <div class="priority-progress">
    <div class="priority-card">
      <div class="priority-label">🔥 Sランク</div>
      <div class="fraction"><span id="s-completed">0</span> / 15</div>
    </div>
    <div class="priority-card">
      <div class="priority-label">⭐ Aランク</div>
      <div class="fraction"><span id="a-completed">0</span> / 25</div>
    </div>
    <div class="priority-card">
      <div class="priority-label">💎 Bランク</div>
      <div class="fraction"><span id="b-completed">0</span> / 30</div>
    </div>
    <div class="priority-card">
      <div class="priority-label">📘 Cランク</div>
      <div class="fraction"><span id="c-completed">0</span> / 30</div>
    </div>
  </div>

  <div class="achievements">
    <div class="achievement" id="badge-first" title="最初の1テーマを完了">
      <span class="icon">🎯</span> ファーストステップ
    </div>
    <div class="achievement" id="badge-10" title="10テーマを完了">
      <span class="icon">🌟</span> 駆け出しライター
    </div>
    <div class="achievement" id="badge-30" title="30テーマを完了">
      <span class="icon">🚀</span> 中級マーケター
    </div>
    <div class="achievement" id="badge-60" title="60テーマを完了">
      <span class="icon">👑</span> 上級エキスパート
    </div>
    <div class="achievement" id="badge-100" title="全テーマを完了">
      <span class="icon">🏆</span> コンプリートマスター
    </div>
    <div class="achievement" id="badge-s-all" title="Sランク全て完了">
      <span class="icon">🔥</span> Sランク制覇
    </div>
  </div>

  <div class="motivational-message" id="motivational-message">
    さあ、最初のテーマから始めましょう！
  </div>
</div>
"""

# containerの開始直後にダッシュボードを挿入
html = html.replace('<div class="container">', '<div class="container">\n' + dashboard_html)

# 各<details>タグにチェックボックスを追加
# <details class="topic-card s" data-priority="s" data-cat="beauty"> のようなパターンを探す
# <summary>内の最初に<label class="checkbox-wrapper">を追加

def add_checkbox(match):
    topic_num_match = re.search(r'<span class="topic-num">(#\d+)</span>', match.group(0))
    if topic_num_match:
        topic_id = topic_num_match.group(1).replace('#', 'topic-')
        checkbox_html = f'<label class="checkbox-wrapper" onclick="event.stopPropagation();"><input type="checkbox" id="{topic_id}" onchange="updateProgress()"></label>'
        # <summary>の直後、<span class="topic-num">の前に挿入
        return match.group(0).replace('<span class="topic-num">', checkbox_html + '<span class="topic-num">')
    return match.group(0)

html = re.sub(r'<summary>.*?</summary>', add_checkbox, html, flags=re.DOTALL)

# JavaScriptを追加
gamification_js = """
// ========== ゲーミフィケーション機能 ==========
const STORAGE_KEY = 'iwata-interview-progress';
const PRIORITIES = {s: 15, a: 25, b: 30, c: 30};

// 進捗データの読み込み
function loadProgress() {
  const saved = localStorage.getItem(STORAGE_KEY);
  if (saved) {
    return JSON.parse(saved);
  }
  return {
    completed: {},
    lastUpdate: null,
    streak: 0
  };
}

// 進捗データの保存
function saveProgress(data) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
}

// 進捗の更新
function updateProgress() {
  const progress = loadProgress();

  // 全チェックボックスの状態を取得
  document.querySelectorAll('input[type="checkbox"][id^="topic-"]').forEach(cb => {
    progress.completed[cb.id] = cb.checked;
    // カードの見た目を更新
    const card = cb.closest('.topic-card');
    if (card) {
      if (cb.checked) {
        card.classList.add('completed');
      } else {
        card.classList.remove('completed');
      }
    }
  });

  // 連続作業日数の更新
  const today = new Date().toDateString();
  if (progress.lastUpdate !== today) {
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    if (progress.lastUpdate === yesterday.toDateString()) {
      progress.streak += 1;
    } else if (progress.lastUpdate !== today) {
      progress.streak = 1;
    }
    progress.lastUpdate = today;
  }

  saveProgress(progress);
  renderProgress(progress);
}

// 進捗の表示
function renderProgress(progress) {
  const completed = Object.values(progress.completed).filter(v => v).length;
  const total = 100;
  const percentage = Math.round((completed / total) * 100);

  // 全体進捗
  document.getElementById('overall-progress').textContent = percentage + '%';
  document.getElementById('overall-progress-bar').style.width = percentage + '%';
  document.getElementById('overall-progress-bar').textContent = percentage + '%';
  document.getElementById('completed-count').textContent = completed;

  // 優先度別進捗
  ['s', 'a', 'b', 'c'].forEach(pri => {
    const cards = document.querySelectorAll(`.topic-card[data-priority="${pri}"]`);
    let priCompleted = 0;
    cards.forEach(card => {
      const cb = card.querySelector('input[type="checkbox"]');
      if (cb && progress.completed[cb.id]) {
        priCompleted++;
      }
    });
    const elem = document.getElementById(pri + '-completed');
    if (elem) elem.textContent = priCompleted;
  });

  // レベル判定
  let level = 0;
  let levelName = '初心者';
  if (completed >= 100) { level = 5; levelName = '伝説のマーケター'; }
  else if (completed >= 60) { level = 4; levelName = '上級エキスパート'; }
  else if (completed >= 30) { level = 3; levelName = '中級マーケター'; }
  else if (completed >= 10) { level = 2; levelName = '駆け出しライター'; }
  else if (completed >= 1) { level = 1; levelName = 'スタートダッシュ'; }

  document.getElementById('level-badge').textContent = `Lv.${level} ${levelName}`;

  // 連続作業日数
  document.getElementById('streak-count').textContent = progress.streak || 0;

  // 実績バッジのアンロック
  const badges = {
    'badge-first': completed >= 1,
    'badge-10': completed >= 10,
    'badge-30': completed >= 30,
    'badge-60': completed >= 60,
    'badge-100': completed >= 100,
    'badge-s-all': parseInt(document.getElementById('s-completed').textContent) >= 15
  };

  Object.entries(badges).forEach(([id, unlocked]) => {
    const elem = document.getElementById(id);
    if (elem) {
      if (unlocked) {
        elem.classList.add('unlocked');
      } else {
        elem.classList.remove('unlocked');
      }
    }
  });

  // モチベーションメッセージ
  const messages = [
    [0, 'さあ、最初のテーマから始めましょう！ 🚀'],
    [1, 'おめでとうございます！最初の一歩を踏み出しました！ 🎉'],
    [10, 'すごい！10テーマ達成！調子が出てきましたね！ 💪'],
    [25, '4分の1達成！このペースで進めましょう！ ⭐'],
    [30, '30テーマ突破！中級マーケターの仲間入りです！ 🚀'],
    [50, '半分突破！ゴールが見えてきました！ 🎯'],
    [60, '60テーマ達成！あなたはもう上級者です！ 👑'],
    [75, '75%完了！残りラストスパート！ 🔥'],
    [90, 'あと10テーマ！コンプリートまであと少し！ 🏁'],
    [100, '🏆 全テーマ完了！あなたは伝説のマーケターです！ 🏆']
  ];

  let msg = messages[0][1];
  for (let [threshold, text] of messages) {
    if (completed >= threshold) {
      msg = text;
    }
  }
  document.getElementById('motivational-message').textContent = msg;
}

// 初期化
document.addEventListener('DOMContentLoaded', function() {
  const progress = loadProgress();

  // チェックボックスの状態を復元
  Object.entries(progress.completed).forEach(([id, checked]) => {
    const cb = document.getElementById(id);
    if (cb) {
      cb.checked = checked;
    }
  });

  updateProgress();
});
"""

# </script>の直前にJSを挿入
html = html.replace('</script>', '\n' + gamification_js + '\n</script>')

# 保存
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ ゲーミフィケーション版を作成しました")
print("   - index.html: ゲーミフィケーション版（進捗トラッキング付き）")
print("   - index-simple.html: シンプル版（元のまま）")
