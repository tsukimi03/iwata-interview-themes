#!/usr/bin/env python3
"""
編集モード追加 + HTML保存をローカルストレージ保存に変更
"""
import re

# 既存HTMLを読み込む
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. ツールバーに「編集」ボタンを追加
old_toolbar = '''<div class="save-toolbar">
  <span class="toolbar-note">全てのテキストをクリックして直接編集できます</span>
  <div class="toolbar-buttons">
    <button class="btn-html" onclick="saveAsHTML()">HTML保存</button>'''

new_toolbar = '''<div class="save-toolbar">
  <span class="toolbar-note" id="toolbar-note">📖 閲覧モード</span>
  <div class="toolbar-buttons">
    <button class="btn-edit" id="btn-edit" onclick="toggleEditMode()">編集</button>
    <button class="btn-save" id="btn-save" onclick="saveContent()" style="display:none;">保存</button>'''

html = html.replace(old_toolbar, new_toolbar)

# 2. 「HTML保存」を「GitHubで編集」に変更、PDF保存は残す
html = html.replace(
    '''<button class="btn-pdf" onclick="saveAsPDF()">PDF保存</button>''',
    '''<button class="btn-pdf" onclick="saveAsPDF()">PDF保存</button>
    <button class="btn-github" onclick="openGitHubEdit()" style="background:#333; color:#fff; border:none; padding:8px 16px; border-radius:6px; cursor:pointer; font-size:13px;">GitHubで編集</button>'''
)

# 3. CSS追加
edit_mode_css = """
/* ========== 編集モード用CSS ========== */
.edit-mode [contenteditable="true"] {
  outline: 2px dashed #3b82f6 !important;
  background: #f0f9ff;
  padding: 2px 4px;
  border-radius: 3px;
}
.edit-mode .toolbar-note {
  color: #3b82f6;
  font-weight: 700;
}
.btn-edit {
  background: #3b82f6;
  color: #fff;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
}
.btn-edit.active {
  background: #ef4444;
}
.btn-save {
  background: #10b981;
  color: #fff;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}
"""

html = html.replace('</style>', edit_mode_css + '\n</style>')

# 4. JavaScript追加
edit_mode_js = """
// ========== 編集モード機能 ==========
const CONTENT_STORAGE_KEY = 'iwata-interview-content';
let isEditMode = false;

// 編集モードの切り替え
function toggleEditMode() {
  isEditMode = !isEditMode;
  const btn = document.getElementById('btn-edit');
  const saveBtn = document.getElementById('btn-save');
  const note = document.getElementById('toolbar-note');
  const body = document.body;

  if (isEditMode) {
    // 編集モードON
    body.classList.add('edit-mode');
    btn.textContent = '編集終了';
    btn.classList.add('active');
    saveBtn.style.display = 'inline-block';
    note.textContent = '✏️ 編集モード（テキストをクリックして編集）';
    enableContentEditable();
  } else {
    // 編集モードOFF
    body.classList.remove('edit-mode');
    btn.textContent = '編集';
    btn.classList.remove('active');
    saveBtn.style.display = 'none';
    note.textContent = '📖 閲覧モード';
    disableContentEditable();
  }
}

// 編集可能にする
function enableContentEditable() {
  // タイトル、サブタイトル
  const h1 = document.querySelector('h1');
  const subtitle = document.querySelector('.subtitle');
  if (h1) h1.contentEditable = 'true';
  if (subtitle) subtitle.contentEditable = 'true';

  // 各種テキスト要素
  document.querySelectorAll('.exec-summary p, .exec-summary li, .topic-title-text, .field-value, .article-title-suggestion, .questions li').forEach(el => {
    el.contentEditable = 'true';
  });
}

// 編集不可にする
function disableContentEditable() {
  document.querySelectorAll('[contenteditable="true"]').forEach(el => {
    el.contentEditable = 'false';
  });
}

// 内容を保存（ローカルストレージ）
function saveContent() {
  const contentData = {
    title: document.querySelector('h1')?.textContent || '',
    subtitle: document.querySelector('.subtitle')?.textContent || '',
    timestamp: new Date().toISOString()
  };

  // 編集可能な全要素の内容を保存
  const editableElements = {};
  document.querySelectorAll('[contenteditable="true"]').forEach((el, index) => {
    const id = el.id || `editable-${index}`;
    editableElements[id] = el.innerHTML;
  });

  contentData.elements = editableElements;

  localStorage.setItem(CONTENT_STORAGE_KEY, JSON.stringify(contentData));

  // 保存成功の通知
  const saveBtn = document.getElementById('btn-save');
  const originalText = saveBtn.textContent;
  saveBtn.textContent = '✓ 保存しました';
  saveBtn.style.background = '#10b981';

  setTimeout(() => {
    saveBtn.textContent = originalText;
  }, 2000);

  console.log('保存しました:', new Date().toLocaleString());
}

// 保存された内容を復元
function restoreContent() {
  const saved = localStorage.getItem(CONTENT_STORAGE_KEY);
  if (!saved) return;

  try {
    const contentData = JSON.parse(saved);

    // タイトル・サブタイトルを復元
    const h1 = document.querySelector('h1');
    const subtitle = document.querySelector('.subtitle');
    if (h1 && contentData.title) h1.textContent = contentData.title;
    if (subtitle && contentData.subtitle) subtitle.textContent = contentData.subtitle;

    // 各要素を復元
    if (contentData.elements) {
      Object.entries(contentData.elements).forEach(([id, content]) => {
        const el = document.getElementById(id) || document.querySelector(`[contenteditable]:nth-of-type(${id.replace('editable-', '')})`);
        if (el) {
          el.innerHTML = content;
        }
      });
    }

    console.log('保存された内容を復元しました:', contentData.timestamp);
  } catch (e) {
    console.error('復元エラー:', e);
  }
}

// GitHubで編集を開く
function openGitHubEdit() {
  const url = 'https://github.com/tsukimi03/iwata-interview-themes/edit/master/index.html';
  window.open(url, '_blank');
}

// ページ読み込み時に復元
document.addEventListener('DOMContentLoaded', function() {
  // 少し遅延させて他の初期化の後に実行
  setTimeout(() => {
    restoreContent();
  }, 500);
});

// Ctrl+S で保存（編集モード時）
document.addEventListener('keydown', function(e) {
  if (e.ctrlKey && e.key === 's' && isEditMode) {
    e.preventDefault();
    saveContent();
  }
});
"""

# </script>の直前に挿入
html = html.replace('</script>', edit_mode_js + '\n</script>')

# 5. saveAsHTML関数を無効化（または削除）
html = html.replace(
    'function saveAsHTML() {',
    'function saveAsHTML_old() {  // 使用停止'
)

# 保存
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ 編集モード追加完了:")
print("   - 「編集」ボタン: クリックで編集モードON/OFF")
print("   - 「保存」ボタン: 編集内容をローカルストレージに保存（ダウンロードなし）")
print("   - 「GitHubで編集」ボタン: GitHub Web UIで直接編集")
print("   - Ctrl+S で保存可能")
print("   - ページリロード時に自動復元")
