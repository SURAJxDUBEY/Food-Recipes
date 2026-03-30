/* ── State ── */
let ingredients = [];

/* ── DOM refs ── */
const input      = document.getElementById('ingredient-input');
const addBtn     = document.getElementById('add-btn');
const clearBtn   = document.getElementById('clear-btn');
const cookBtn    = document.getElementById('cook-btn');
const list       = document.getElementById('ingredient-list');
const resultsSec = document.getElementById('results-section');
const resultsCon = document.getElementById('results-container');
const loadingOv  = document.getElementById('loading-overlay');
const loadingFill= document.getElementById('loading-bar-fill');
const toast      = document.getElementById('toast');

/* ── Autocomplete: load all known ingredients from DB ── */
fetch('/api/all-ingredients')
  .then(r => r.json())
  .then(items => {
    const dl = document.getElementById('ing-suggestions');
    items.forEach(item => {
      const opt = document.createElement('option');
      opt.value = item;
      dl.appendChild(opt);
    });
  });

/* ── Nav ── */
document.querySelectorAll('.nav-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('view-' + btn.dataset.view).classList.add('active');
    if (btn.dataset.view === 'saved')   loadSaved();
    if (btn.dataset.view === 'history') loadHistory();
  });
});

/* ── Add ingredient ── */
function addIngredient(raw) {
  const name = raw.trim();
  if (!name) return;
  const lower = name.toLowerCase();
  if (ingredients.some(i => i.toLowerCase() === lower)) { showToast('Already added!'); return; }
  ingredients.push(name.charAt(0).toUpperCase() + name.slice(1).toLowerCase());
  renderList();
  input.value = '';
  input.focus();
}

addBtn.addEventListener('click', () => addIngredient(input.value));
input.addEventListener('keydown', e => { if (e.key === 'Enter') addIngredient(input.value); });

document.querySelectorAll('.quick-chips')[0].addEventListener('click', e => {
  if (e.target.classList.contains('chip')) {
    // Strip emoji prefix (everything before first space)
    const parts = e.target.textContent.trim().split(' ');
    parts.shift(); // remove emoji
    addIngredient(parts.join(' '));
  }
});

clearBtn.addEventListener('click', () => {
  ingredients = [];
  renderList();
  resultsSec.style.display = 'none';
});

/* ── Render tags ── */
function renderList() {
  if (!ingredients.length) {
    list.innerHTML = '<p class="empty-list-msg">Your ingredient list is empty — add something above!</p>';
    return;
  }
  list.innerHTML = '<div class="tag-list">' +
    ingredients.map((ing, i) =>
      `<span class="tag">${esc(ing)}
         <button class="tag-remove" data-i="${i}" aria-label="Remove">×</button>
       </span>`
    ).join('') +
    '</div>';
  list.querySelectorAll('.tag-remove').forEach(btn =>
    btn.addEventListener('click', () => { ingredients.splice(+btn.dataset.i, 1); renderList(); })
  );
}

/* ── Find Recipes ── */
cookBtn.addEventListener('click', findRecipes);

async function findRecipes() {
  if (!ingredients.length) { showToast('Add at least one ingredient first!'); return; }
  showLoading();
  try {
    const res  = await fetch('/api/find-recipes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ items: ingredients })
    });
    const data = await res.json();
    if (data.error) { showToast(data.error); return; }
    renderResults(data);
  } catch { showToast('Network error — is the server running?'); }
  finally   { hideLoading(); }
}

/* ── Render Results ── */
function renderResults({ can_make, almost }) {
  resultsSec.style.display = 'block';
  resultsSec.scrollIntoView({ behavior: 'smooth', block: 'start' });

  let html = '';

  /* ---- Recipes we can fully make ---- */
  if (can_make.length) {
    html += `<div class="section-header">
      <h2 class="section-title">You can cook these</h2>
      <span class="section-count">${can_make.length} recipe${can_make.length > 1 ? 's' : ''}</span>
    </div>
    <div class="recipe-grid">`;

    can_make.forEach((r, idx) => {
      html += `<div class="recipe-card">
        <div class="recipe-card-top">
          <div class="card-meta">
            ${r.time      ? `<span class="badge badge-time">⏱ ${esc(r.time)}</span>` : ''}
            ${r.difficulty? `<span class="badge badge-diff">★ ${esc(r.difficulty)}</span>` : ''}
            ${r.cuisine   ? `<span class="badge badge-cuisine">${esc(r.cuisine)}</span>` : ''}
          </div>
          <h3 class="card-title">${esc(r.title)}</h3>
          <p class="card-desc">${esc(r.description)}</p>
        </div>
        <div class="recipe-card-body">
          <div>
            <div class="card-section-label">Ingredients needed</div>
            <div class="ing-chips">
              ${r.ingredients.map(i => `<span class="ing-chip">${esc(i)}</span>`).join('')}
            </div>
          </div>
          <div>
            <div class="card-section-label">Steps</div>
            <ol class="steps-list">
              ${r.steps.map((s, si) => `<li><span class="step-num">${si+1}</span>${esc(s)}</li>`).join('')}
            </ol>
          </div>
          <button class="save-btn" data-id="${r.id}">♡ Save Recipe</button>
        </div>
      </div>`;
    });
    html += '</div>';
  }

  /* ---- Almost-there recommendations ---- */
  if (almost.length) {
    if (can_make.length) html += '<hr class="section-divider" />';

    html += `<div class="section-header">
      <h2 class="section-title">${can_make.length ? 'Almost there too' : 'Close — just missing a little'}</h2>
      <span class="section-count">${almost.length} suggestion${almost.length > 1 ? 's' : ''}</span>
    </div>`;

    if (!can_make.length) {
      html += `<div class="almost-intro">
        <span class="almost-icon">💡</span>
        <p>You don't have enough for a complete dish yet — but you're close!
        <strong>Add just 1–2 more items</strong> and you'll be cooking.</p>
      </div>`;
    }

    html += '<div class="rec-grid">';
    almost.forEach(r => {
      html += `<div class="rec-card">
        <div class="rec-icon">🍽️</div>
        <div class="rec-body">
          <h3>${esc(r.title)}</h3>
          <p>${esc(r.description)} &nbsp;·&nbsp; ${esc(r.time || '')} &nbsp;·&nbsp; ${esc(r.difficulty || '')}</p>
          <div class="rec-missing-label">Just add:</div>
          <div class="rec-missing">
            ${r.missing.map(m => `<span class="rec-missing-chip">+ ${esc(m)}</span>`).join('')}
          </div>
        </div>
      </div>`;
    });
    html += '</div>';
  }

  /* ---- Nothing at all ---- */
  if (!can_make.length && !almost.length) {
    html = `<div class="no-results">
      <div class="no-results-icon">🤷</div>
      <h2>No matches found</h2>
      <p>We couldn't match any recipe with those ingredients.<br/>Try adding more basics like eggs, onion, garlic, oil or butter.</p>
    </div>`;
  }

  resultsCon.innerHTML = html;

  /* Save buttons */
  resultsCon.querySelectorAll('.save-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const id = btn.dataset.id;
      try {
        const res  = await fetch('/api/save-recipe', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ recipe_id: id })
        });
        const data = await res.json();
        if (data.success) {
          btn.textContent = '✓ Saved!';
          btn.classList.add('saved');
          showToast('Recipe saved!');
        }
      } catch { showToast('Could not save.'); }
    });
  });
}

/* ── Saved ── */
async function loadSaved() {
  const el = document.getElementById('saved-list');
  el.innerHTML = '<p class="empty-state">Loading…</p>';
  try {
    const data = await fetch('/api/saved-recipes').then(r => r.json());
    if (!data.length) { el.innerHTML = '<p class="empty-state">No saved recipes yet.</p>'; return; }
    el.innerHTML = data.map(r => `
      <div class="list-item">
        <div style="flex:1">
          <div class="list-item-title">${esc(r.title)}</div>
          <div class="list-item-sub">Saved on ${new Date(r.created).toLocaleDateString()}</div>
          <div class="tag-row">
            ${r.ingredients.map(i => `<span class="mini-tag">${esc(i)}</span>`).join('')}
          </div>
        </div>
        ${r.cuisine ? `<span class="list-item-cuisine">${esc(r.cuisine)}</span>` : ''}
      </div>`).join('');
  } catch { el.innerHTML = '<p class="empty-state">Could not load saved recipes.</p>'; }
}

/* ── History ── */
async function loadHistory() {
  const el = document.getElementById('history-list');
  el.innerHTML = '<p class="empty-state">Loading…</p>';
  try {
    const data = await fetch('/api/history').then(r => r.json());
    if (!data.length) { el.innerHTML = '<p class="empty-state">No history yet.</p>'; return; }
    el.innerHTML = data.map(h => `
      <div class="list-item">
        <div>
          <div class="list-item-sub">${new Date(h.created).toLocaleString()}</div>
          <div class="tag-row" style="margin-top:5px">
            ${h.items.map(i => `<span class="mini-tag">${esc(i)}</span>`).join('')}
          </div>
        </div>
      </div>`).join('');
  } catch { el.innerHTML = '<p class="empty-state">Could not load history.</p>'; }
}

/* ── Loading ── */
let loadT = null;
function showLoading() {
  loadingOv.classList.add('active');
  loadingFill.style.width = '0%';
  let p = 0;
  loadT = setInterval(() => {
    p = Math.min(p + 15, 85);
    loadingFill.style.width = p + '%';
  }, 200);
}
function hideLoading() {
  clearInterval(loadT);
  loadingFill.style.width = '100%';
  setTimeout(() => { loadingOv.classList.remove('active'); loadingFill.style.width = '0%'; }, 300);
}

/* ── Toast ── */
let toastT = null;
function showToast(msg) {
  toast.textContent = msg;
  toast.classList.add('show');
  clearTimeout(toastT);
  toastT = setTimeout(() => toast.classList.remove('show'), 2600);
}

/* ── Util ── */
function esc(s) {
  return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
