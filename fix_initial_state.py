#!/usr/bin/env python3
"""
初期状態を未完了に修正 + 使い方ガイドを追加
"""
import re

# 既存HTMLを読み込む
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. 「やる」チェックボックスのchecked属性を削除
html = re.sub(
    r'(<input type="checkbox" id="topic-\d+-do"[^>]*) checked',
    r'\1',
    html
)

# 2. 完了チェックボックスのchecked属性も削除（念のため）
html = re.sub(
    r'(<input type="checkbox" id="topic-\d+"[^>]*) checked',
    r'\1',
    html
)

# 3. 使い方ガイドを追加
usage_guide = """
<div style="background: rgba(255,255,255,0.15); border: 2px solid rgba(255,255,255,0.3); border-radius: 10px; padding: 20px; margin-top: 20px;">
  <h3 style="margin:0 0 15px 0; font-size:1.2em;">📖 使い方ガイド</h3>
  <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px; font-size: 0.9em; line-height: 1.8;">
    <div>
      <strong>1️⃣ テーマを選ぶ</strong><br>
      各テーマをクリックして内容を確認 → 「やる」にチェックを入れる
    </div>
    <div>
      <strong>2️⃣ 作業を進める</strong><br>
      録音 → 記事化 → 公開の順にステータスを更新していく
    </div>
    <div>
      <strong>3️⃣ レベルアップ</strong><br>
      公開済みにするとカウントされ、レベルが上がる！<br>
      <span style="opacity:0.8;">Lv1:1個 → Lv2:10個 → Lv3:30個 → Lv4:60個 → Lv5:100個</span>
    </div>
    <div>
      <strong>4️⃣ 実績をアンロック</strong><br>
      Sランク全制覇など、特定の条件で実績バッジが光る！
    </div>
  </div>
</div>
"""

# ダッシュボード内の最後（モチベーションメッセージの後）に挿入
html = html.replace(
    '</div>\n</div>\n\n<h1 contenteditable="true">',
    usage_guide + '\n</div>\n</div>\n\n<h1 contenteditable="true">'
)

# 4. JavaScriptの進捗計算ロジックを修正（公開済みのみをカウント）
# 既存のupdateProgress関数を修正
old_progress_logic = '''  // 全チェックボックスの状態を取得
  document.querySelectorAll('input[type="checkbox"][id^="topic-"]').forEach(cb => {
    progress.completed[cb.id] = cb.checked;'''

new_progress_logic = '''  // ステータスが「公開済み」のものをカウント
  document.querySelectorAll('select[id$="-status"]').forEach(sel => {
    const topicId = sel.id.replace('-status', '');
    const isPublished = sel.value === 'published';
    progress.completed[topicId] = isPublished;

    // 対応するチェックボックスも連動
    const cb = document.getElementById(topicId);
    if (cb) {
      cb.checked = isPublished;
    }
  });

  // チェックボックスの状態も保存（後方互換性のため）
  document.querySelectorAll('input[type="checkbox"][id^="topic-"]').forEach(cb => {
    if (!cb.id.includes('-do') && !cb.id.includes('-status')) {
      const topicId = cb.id;
      const statusSelect = document.getElementById(topicId + '-status');
      if (statusSelect && statusSelect.value === 'published') {
        progress.completed[topicId] = true;'''

html = html.replace(old_progress_logic, new_progress_logic)

# 5. モチベーションメッセージの初期値を変更
html = html.replace(
    'さあ、最初のテーマから始めましょう！',
    '最初のテーマを選んで「やる」にチェック → ステータスを更新していこう！'
)

# 保存
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ 修正完了:")
print("   - 初期状態: 全て未完了（チェックなし）")
print("   - 使い方ガイドを追加")
print("   - レベルアップ条件を明示（公開済みのみカウント）")
print("   - 進捗計算ロジックを修正")
