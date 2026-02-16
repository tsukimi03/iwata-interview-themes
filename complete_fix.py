#!/usr/bin/env python3
"""
updateProgress関数を完全に書き直し
"""
import re

# 既存HTMLを読み込む
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# updateProgress関数全体を置き換え
old_update_progress = re.search(
    r'// 進捗の更新\nfunction updateProgress\(\) \{.*?saveProgress\(progress\);',
    html,
    re.DOTALL
)

if old_update_progress:
    new_update_progress = """// 進捗の更新
function updateProgress() {
  const progress = loadProgress();

  // 「公開済み」ステータスのみを完了としてカウント
  progress.completed = {};
  document.querySelectorAll('select[id$="-status"]').forEach(sel => {
    const topicId = sel.id.replace('-status', '');
    const isPublished = sel.value === 'published';
    progress.completed[topicId] = isPublished;

    // 対応するチェックボックスも連動（表示用）
    const cb = document.getElementById(topicId);
    if (cb) {
      cb.checked = isPublished;

      // カードの見た目を更新
      const card = cb.closest('.topic-card');
      if (card) {
        if (isPublished) {
          card.classList.add('completed');
        } else {
          card.classList.remove('completed');
        }
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

  saveProgress(progress);"""

    html = html.replace(old_update_progress.group(0), new_update_progress)
    print("✅ updateProgress関数を書き直しました")
else:
    print("⚠️  updateProgress関数が見つかりません")

# 保存
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("完了: 進捗計算ロジックを完全修正しました")
print("これで初期状態は0%になります")
