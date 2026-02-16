#!/usr/bin/env python3
"""
リセットボタン追加 + 初期化ロジック修正
"""
import re

# 既存HTMLを読み込む
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. 保存ツールバーにリセットボタンを追加
old_toolbar = '''<button class="btn-pdf" onclick="saveAsPDF()">PDF保存</button>
  </div>
</div>'''

new_toolbar = '''<button class="btn-pdf" onclick="saveAsPDF()">PDF保存</button>
    <button class="btn-reset" onclick="resetAllProgress()" style="background:#ef4444; color:#fff; border:none; padding:8px 16px; border-radius:6px; cursor:pointer; font-size:13px; margin-left:auto;">リセット</button>
  </div>
</div>'''

html = html.replace(old_toolbar, new_toolbar)

# 2. リセット機能のJavaScriptを追加
reset_js = """
// ========== リセット機能 ==========
function resetAllProgress() {
  if (confirm('全ての進捗データをリセットしますか？\\n（この操作は取り消せません）')) {
    // ローカルストレージをクリア
    localStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem(STATUS_STORAGE_KEY);

    // 全チェックボックスをOFF
    document.querySelectorAll('input[type="checkbox"]').forEach(cb => {
      cb.checked = false;
    });

    // 全ステータスを「未着手」に
    document.querySelectorAll('select[id$="-status"]').forEach(sel => {
      sel.value = 'not-started';
      sel.className = 'status-select status-not-started';
    });

    // 全カードから完了・スキップクラスを削除
    document.querySelectorAll('.topic-card').forEach(card => {
      card.classList.remove('completed', 'skipped');
    });

    // 進捗を再計算
    updateProgress();
    updateStatusManagement();

    alert('リセットしました！');
    location.reload();
  }
}
"""

# </script>の直前に挿入
html = html.replace('</script>', reset_js + '\n</script>')

# 3. 初期化時にデータ検証を追加（完了数が異常に多い場合は自動リセット）
init_validation = """
// ========== 初期化時のデータ検証 ==========
(function validateInitialData() {
  const progress = loadProgress();
  const completedCount = Object.values(progress.completed).filter(v => v).length;

  // 完了数が90以上の場合（異常値）、自動リセット
  if (completedCount >= 90) {
    console.warn('異常なデータを検出したため、リセットします');
    localStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem(STATUS_STORAGE_KEY);
    location.reload();
  }
})();
"""

# DOMContentLoadedの前に挿入
html = html.replace(
    "// ========== ゲーミフィケーション機能 ==========",
    init_validation + "\n// ========== ゲーミフィケーション機能 =========="
)

# 4. 進捗読み込みロジックを完全に修正
old_render_logic = """// 進捗の表示
function renderProgress(progress) {
  const completed = Object.values(progress.completed).filter(v => v).length;"""

new_render_logic = """// 進捗の表示
function renderProgress(progress) {
  // 「公開済み」のステータスを持つテーマのみをカウント
  let completed = 0;
  document.querySelectorAll('select[id$="-status"]').forEach(sel => {
    if (sel.value === 'published') {
      completed++;
    }
  });

  // progressオブジェクトとの整合性チェック
  const progressCompleted = Object.values(progress.completed).filter(v => v).length;
  if (progressCompleted !== completed) {
    // 不整合がある場合は実際のステータスを優先
    console.log('進捗データを再計算:', completed);
  }"""

html = html.replace(old_render_logic, new_render_logic)

# 保存
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ リセット機能追加完了:")
print("   - ツールバーに「リセット」ボタン追加")
print("   - 異常データの自動検出・リセット")
print("   - 進捗計算を「公開済み」ベースに完全修正")
print("")
print("⚠️  殿へ:")
print("   GitHub Pagesが更新されたら、一度「リセット」ボタンを押してください。")
print("   古いローカルストレージデータがクリアされます。")
