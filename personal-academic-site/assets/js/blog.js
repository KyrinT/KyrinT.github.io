(() => {
  const buttons = [...document.querySelectorAll('[data-category][aria-pressed]')];
  const posts = [...document.querySelectorAll('.post-card')];
  const search = document.getElementById('search');
  const allowed = buttons.map(b => b.dataset.category);
  let category = '全部';
  function apply() {
    const q = search.value.trim().toLocaleLowerCase();
    let visible = 0;
    for (const post of posts) {
      const match = (category === '全部' || post.dataset.category === category)
        && post.dataset.search.toLocaleLowerCase().includes(q);
      post.hidden = !match;
      if (match) visible++;
    }
    for (const button of buttons) button.setAttribute('aria-pressed', String(button.dataset.category === category));
    document.getElementById('empty').hidden = visible > 0;
    document.getElementById('empty-title').textContent = q ? '没有找到相关记录。' : (category === '全部' ? '第一篇记录，敬请期待。' : '暂无' + category + '，敬请期待。');
    document.getElementById('empty-description').textContent = q ? '试试其他关键词，或切换文章分类。' : '新的记录将在这里陆续更新。';
  }
  function restore() {
    const p = new URLSearchParams(location.search);
    category = allowed.includes(p.get('category')) ? p.get('category') : '全部';
    search.value = p.get('q') || '';
    apply();
  }
  function updateUrl(push) {
    const u = new URL(location.href);
    if (category === '全部') u.searchParams.delete('category'); else u.searchParams.set('category', category);
    if (search.value.trim()) u.searchParams.set('q', search.value.trim()); else u.searchParams.delete('q');
    // file:// 离线预览中某些浏览器不允许修改历史；筛选本身仍然可用。
    try { if (push) history.pushState({}, '', u); else history.replaceState({}, '', u); } catch (_) {}
    apply();
  }
  buttons.forEach(b => b.addEventListener('click', () => { category = b.dataset.category; updateUrl(true); }));
  search.addEventListener('input', () => updateUrl(false));
  window.addEventListener('popstate', restore);
  restore();
})();
