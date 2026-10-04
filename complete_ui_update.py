# -*- coding: utf-8 -*-
"""
Completes the full UI and JS update on index.html:
- Embeds 3,672 names in <script id="embeddedNamesData">
- Updates JS state and handlers for 4 categories (favorites, possible, similar_excluded, excluded)
- Adds mobile sticky dock and 4-action card status buttons
- Adds 4-action Swipe Discovery Mode
"""

import json
import re

with open('names_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

print(f"Loaded {len(db)} names for embedding.")
embedded_json = json.dumps(db, ensure_ascii=False, indent=2)

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update embeddedNamesData script
script_start = '<script id="embeddedNamesData" type="application/json">'
script_end = '</script>'

if script_start in content:
    idx_start = content.find(script_start) + len(script_start)
    idx_end = content.find(script_end, idx_start)
    content = content[:idx_start] + '\n' + embedded_json + '\n' + content[idx_end:]
    print("Replaced embeddedNamesData with 3,672 names.")

# 2. Add Mobile Sticky Bottom Dock right before </body> if not present
mobile_dock_html = '''
  <!-- Mobile Sticky Bottom Navigation Dock (Facilita navegacion en móvil) -->
  <nav class="sm:hidden fixed bottom-0 left-0 right-0 z-40 bg-white/95 backdrop-blur-xl border-t border-rose-100 px-3 py-2 flex items-center justify-around shadow-2xl">
    <button onclick="setStatusFilter('all'); window.scrollTo({ top: 350, behavior: 'smooth' });" class="flex flex-col items-center justify-center text-[10px] font-semibold text-neutral-600 hover:text-rose-600 transition active:scale-95">
      <span class="text-xl">📚</span>
      <span class="mt-0.5">Todos</span>
    </button>
    <button onclick="setStatusFilter('favorites'); window.scrollTo({ top: 350, behavior: 'smooth' });" class="flex flex-col items-center justify-center text-[10px] font-semibold text-amber-800 hover:text-amber-900 transition active:scale-95">
      <span class="text-xl">⭐</span>
      <span class="mt-0.5">Favoritos</span>
    </button>
    <button onclick="openSwipeModal()" class="flex flex-col items-center justify-center -mt-6 bg-gradient-to-tr from-amber-500 to-rose-500 text-white rounded-2xl w-14 h-14 p-2 shadow-lg shadow-rose-300 transition active:scale-90 border-2 border-white">
      <span class="text-2xl">✨</span>
      <span class="text-[9px] font-bold">Swipe</span>
    </button>
    <button onclick="setStatusFilter('similar_excluded'); window.scrollTo({ top: 350, behavior: 'smooth' });" class="flex flex-col items-center justify-center text-[10px] font-semibold text-orange-700 hover:text-orange-900 transition active:scale-95">
      <span class="text-xl">⚠️</span>
      <span class="mt-0.5">En Duda</span>
    </button>
    <button onclick="openAddModal()" class="flex flex-col items-center justify-center text-[10px] font-semibold text-neutral-600 hover:text-rose-600 transition active:scale-95">
      <span class="text-xl">➕</span>
      <span class="mt-0.5">Añadir</span>
    </button>
  </nav>

  <!-- Bottom padding spacer for mobile dock -->
  <div class="h-16 sm:hidden"></div>
'''

if 'Mobile Sticky Bottom Navigation Dock' not in content:
    content = content.replace('</body>', mobile_dock_html + '\n</body>')

# 3. Update JavaScript logic
# Replace getStatusBadgeHTML
new_get_status_badge = '''    function getStatusBadgeHTML(status) {
      if (status === 'favorites') {
        return `<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold badge-fav">⭐ Favorito</span>`;
      } else if (status === 'possible') {
        return `<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold badge-pos">👍 Posible</span>`;
      } else if (status === 'similar_excluded') {
        return `<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-orange-100 text-orange-800 border border-orange-300 shadow-2xs">⚠️ Similar a Excluido</span>`;
      } else {
        return `<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold badge-exc">❌ Excluido</span>`;
      }
    }'''

content = re.sub(
    r'function getStatusBadgeHTML\(status\)\s*\{.*?return `<span class="inline-flex items-center gap-1 px-2\.5 py-0\.5 rounded-full text-xs font-semibold badge-exc">❌ Excluido</span>`;\s*\}',
    new_get_status_badge,
    content,
    flags=re.DOTALL
)

# Replace renderStats function
new_render_stats = '''    // Render Metrics (Respects active version filter & 4 Categories)
    function renderStats() {
      let scopedNames = allNames;
      if (currentVersionFilter === 'pdf') {
        scopedNames = allNames.filter(x => x.source && x.source.includes('PDF'));
      } else if (currentVersionFilter === 'new') {
        scopedNames = allNames.filter(x => !x.source || !x.source.includes('PDF'));
      }

      const favs = scopedNames.filter(x => x.status === 'favorites').length;
      const poss = scopedNames.filter(x => x.status === 'possible').length;
      const sims = scopedNames.filter(x => x.status === 'similar_excluded').length;
      const excl = scopedNames.filter(x => x.status === 'excluded').length;

      document.getElementById('metricTotal').innerText = scopedNames.length.toLocaleString();
      document.getElementById('metricFavorites').innerText = favs.toLocaleString();
      document.getElementById('metricPossible').innerText = poss.toLocaleString();
      const elSim = document.getElementById('metricSimilar');
      if (elSim) elSim.innerText = sims.toLocaleString();
      document.getElementById('metricExcluded').innerText = excl.toLocaleString();

      document.getElementById('tabCountAll').innerText = `(${scopedNames.length})`;
      document.getElementById('tabCountFavorites').innerText = `(${favs})`;
      document.getElementById('tabCountPossible').innerText = `(${poss})`;
      const elTabSim = document.getElementById('tabCountSimilar');
      if (elTabSim) elTabSim.innerText = `(${sims})`;
      document.getElementById('tabCountExcluded').innerText = `(${excl})`;

      // Update Version Control badges with total counts
      const pdfCount = allNames.filter(x => x.source && x.source.includes('PDF')).length;
      const newCount = allNames.filter(x => !x.source || !x.source.includes('PDF')).length;
      const bPdf = document.getElementById('verBadgePdf');
      const bNew = document.getElementById('verBadgeNew');
      const bAll = document.getElementById('verBadgeAll');
      if (bPdf) bPdf.innerText = pdfCount.toLocaleString();
      if (bNew) bNew.innerText = newCount.toLocaleString();
      if (bAll) bAll.innerText = allNames.length.toLocaleString();

      // Update subtitle descriptions in metrics
      const subTot = document.getElementById('metricTotalSubtitle');
      const subFav = document.getElementById('metricFavoritesSubtitle');
      const subPos = document.getElementById('metricPossibleSubtitle');
      const subSim = document.getElementById('metricSimilarSubtitle');
      const subExc = document.getElementById('metricExcludedSubtitle');

      if (currentVersionFilter === 'pdf') {
        if (subTot) subTot.innerText = 'Lista PDF Original';
        if (subFav) subFav.innerText = '23 Resaltados c/ Flecha';
        if (subPos) subPos.innerText = '58 Marcados c/ Flecha';
        if (subSim) subSim.innerText = '0 en lista original';
        if (subExc) subExc.innerText = '1,091 Números Tachados';
      } else if (currentVersionFilter === 'new') {
        if (subTot) subTot.innerText = 'Nuevos Hispanos/Latinos';
        if (subFav) subFav.innerText = 'Favoritos Nuevos';
        if (subPos) subPos.innerText = 'Candidatos Limpios';
        if (subSim) subSim.innerText = 'Similares a Excluidos v1';
        if (subExc) subExc.innerText = 'Nuevos Descartados';
      } else {
        if (subTot) subTot.innerText = 'PDF + 2,500 Hispanos';
        if (subFav) subFav.innerText = 'Marcados del PDF & App';
        if (subPos) subPos.innerText = 'Flechas PDF + Nuevos';
        if (subSim) subSim.innerText = 'Similares a descartados';
        if (subExc) subExc.innerText = 'Tachados en revisión';
      }
    }'''

content = re.sub(
    r'// Render Metrics \(Respects active version filter\)\s*function renderStats\(\)\s*\{.*?if \(subExc\) subExc\.innerText = \'Tachados en revisión\';\s*\}\s*\}',
    new_render_stats,
    content,
    flags=re.DOTALL
)

# 4. Update setStatusFilter to handle 'similar_excluded' tab styles
new_set_status_filter = '''    function setStatusFilter(status) {
      currentFilterStatus = status;
      currentPage = 1;

      // Update tab styles for all 5 tabs
      ['all', 'favorites', 'possible', 'similar_excluded', 'excluded'].forEach(st => {
        const btn = document.getElementById(`tab_${st}`);
        if (!btn) return;
        if (st === status) {
          if (st === 'similar_excluded') {
            btn.className = 'px-3 py-1.5 rounded-xl text-xs sm:text-sm font-bold bg-orange-600 text-white shadow-sm transition shrink-0';
          } else if (st === 'favorites') {
            btn.className = 'px-3 py-1.5 rounded-xl text-xs sm:text-sm font-bold bg-amber-500 text-white shadow-sm transition shrink-0';
          } else if (st === 'possible') {
            btn.className = 'px-3 py-1.5 rounded-xl text-xs sm:text-sm font-bold bg-sky-600 text-white shadow-sm transition shrink-0';
          } else {
            btn.className = 'px-3 py-1.5 rounded-xl text-xs sm:text-sm font-semibold bg-neutral-900 text-white transition shrink-0';
          }
        } else {
          if (st === 'similar_excluded') {
            btn.className = 'px-3 py-1.5 rounded-xl text-xs sm:text-sm font-semibold bg-orange-50 text-orange-800 border border-orange-200 hover:bg-orange-100 transition shrink-0';
          } else {
            btn.className = 'px-3 py-1.5 rounded-xl text-xs sm:text-sm font-semibold bg-neutral-100 text-neutral-600 hover:bg-neutral-200 transition shrink-0';
          }
        }
      });

      applyFilters();
    }'''

content = re.sub(
    r'function setStatusFilter\(status\)\s*\{.*?applyFilters\(\);\s*\}',
    new_set_status_filter,
    content,
    flags=re.DOTALL
)

# 5. Update setItemStatus to handle similar_excluded
new_set_item_status = '''    // Set Status for a name (Supports 4 Categories)
    async function setItemStatus(id, newStatus) {
      const item = allNames.find(x => x.id === id);
      if (!item) return;
      item.status = newStatus;
      await saveNameChange(item);

      // Smoothly update UI element in place
      const statusBadge = document.getElementById(`status_badge_${id}`);
      if (statusBadge) {
        statusBadge.innerHTML = getStatusBadgeHTML(newStatus);
      }
      
      // Update 4 button highlights on card
      const favBtn = document.getElementById(`btn_fav_${id}`);
      const posBtn = document.getElementById(`btn_pos_${id}`);
      const simBtn = document.getElementById(`btn_sim_${id}`);
      const excBtn = document.getElementById(`btn_exc_${id}`);

      if (favBtn && posBtn && simBtn && excBtn) {
        favBtn.className = `flex-1 py-2 rounded-xl text-xs font-bold transition flex items-center justify-center gap-1 ${newStatus === 'favorites' ? 'bg-amber-400 text-amber-950 font-bold shadow-sm' : 'text-neutral-500 hover:text-amber-700 hover:bg-amber-50'}`;
        posBtn.className = `flex-1 py-2 rounded-xl text-xs font-bold transition flex items-center justify-center gap-1 ${newStatus === 'possible' ? 'bg-sky-400 text-sky-950 font-bold shadow-sm' : 'text-neutral-500 hover:text-sky-700 hover:bg-sky-50'}`;
        simBtn.className = `flex-1 py-2 rounded-xl text-xs font-bold transition flex items-center justify-center gap-1 ${newStatus === 'similar_excluded' ? 'bg-orange-400 text-orange-950 font-bold shadow-sm' : 'text-neutral-500 hover:text-orange-700 hover:bg-orange-50'}`;
        excBtn.className = `flex-1 py-2 rounded-xl text-xs font-bold transition flex items-center justify-center gap-1 ${newStatus === 'excluded' ? 'bg-neutral-300 text-neutral-800 font-bold shadow-sm' : 'text-neutral-500 hover:text-neutral-700 hover:bg-neutral-100'}`;
      }

      // If active filter is not 'all' and not newStatus, remove from view
      if (currentFilterStatus !== 'all' && currentFilterStatus !== newStatus) {
        applyFilters();
      } else {
        renderStats();
      }

      const statusLabels = { favorites: '⭐ Favoritos', possible: '👍 Posibles', similar_excluded: '⚠️ Similares a Excluidos', excluded: '❌ Excluidos' };
      showToast(`${item.name} movido a ${statusLabels[newStatus] || newStatus}`);
    }'''

content = re.sub(
    r'// Set Status for a name.*?showToast\(`\$\{item\.name\} movido a \$\{statusLabels\[newStatus\]\}`\);\s*\}',
    new_set_item_status,
    content,
    flags=re.DOTALL
)

# 6. Update applyFilters to handle typeFilter (compound/single/with_saint) and similar_excluded
new_apply_filters = '''    let currentTypeFilter = 'all';

    function handleFilterChange() {
      currentSourceFilter = document.getElementById('sourceFilter').value;
      currentOriginFilter = document.getElementById('originFilter').value;
      const typeEl = document.getElementById('typeFilter');
      if (typeEl) currentTypeFilter = typeEl.value;

      if (currentSourceFilter === 'pdf') {
        currentVersionFilter = 'pdf';
      } else if (currentSourceFilter === 'latin500' || currentSourceFilter === 'user') {
        currentVersionFilter = 'new';
      } else {
        currentVersionFilter = 'all';
      }

      // Update button styling
      ['all', 'pdf', 'new'].forEach(v => {
        const btn = document.getElementById(`verBtn_${v}`);
        if (!btn) return;
        if (v === currentVersionFilter) {
          btn.className = 'px-3.5 py-2 rounded-xl text-xs sm:text-sm font-semibold transition flex items-center gap-2 bg-white text-neutral-900 shadow-sm border border-neutral-200/60';
        } else {
          btn.className = 'px-3.5 py-2 rounded-xl text-xs sm:text-sm font-semibold transition flex items-center gap-2 text-neutral-600 hover:text-neutral-900';
        }
      });

      currentPage = 1;
      renderStats();
      applyFilters();
    }

    // Apply all filters and render
    function applyFilters() {
      filteredNames = allNames.filter(item => {
        // Version filter
        if (currentVersionFilter === 'pdf' && (!item.source || !item.source.includes('PDF'))) return false;
        if (currentVersionFilter === 'new' && item.source && item.source.includes('PDF')) return false;

        // Status filter (4 categories)
        if (currentFilterStatus !== 'all' && item.status !== currentFilterStatus) return false;

        // Type / Compound filter
        if (currentTypeFilter === 'compound' && !item.is_compound) return false;
        if (currentTypeFilter === 'single' && item.is_compound) return false;
        if (currentTypeFilter === 'with_saint') {
          if (!item.saint_day || item.saint_day.includes('Sin santoral')) return false;
        }

        // Secondary Source dropdown filter
        if (currentSourceFilter === 'pdf' && !item.source?.includes('PDF')) return false;
        if (currentSourceFilter === 'latin500' && !item.source?.includes('500') && !item.source?.includes('2000') && !item.is_new) return false;
        if (currentSourceFilter === 'user' && item.source !== 'User Added') return false;

        // Origin filter
        if (currentOriginFilter !== 'all' && item.origin !== currentOriginFilter) return false;

        // Letter filter
        if (currentLetterFilter && item.letter !== currentLetterFilter) return false;

        // Search query
        if (searchQuery) {
          const nameStr = (item.name || '').toLowerCase();
          const origStr = (item.origin || '').toLowerCase();
          const meanStr = (item.meaning || '').toLowerCase();
          const noteStr = (item.notes || '').toLowerCase();
          const saintStr = (item.saint_day || '').toLowerCase();
          const simStr = (item.similar_to || '').toLowerCase();
          if (!nameStr.includes(searchQuery) && !origStr.includes(searchQuery) && 
              !meanStr.includes(searchQuery) && !noteStr.includes(searchQuery) &&
              !saintStr.includes(searchQuery) && !simStr.includes(searchQuery)) {
            return false;
          }
        }

        return true;
      });

      // Sort
      filteredNames.sort((a, b) => {
        if (currentSort === 'name_asc') return a.name.localeCompare(b.name, 'es');
        if (currentSort === 'name_desc') return b.name.localeCompare(a.name, 'es');
        if (currentSort === 'origin_asc') return (a.origin || '').localeCompare(b.origin || '', 'es');
        if (currentSort === 'status_priority') {
          const rank = { favorites: 1, possible: 2, similar_excluded: 3, excluded: 4 };
          return (rank[a.status] || 9) - (rank[b.status] || 9);
        }
        return 0;
      });

      // Update counters
      document.getElementById('showingCount').innerText = filteredNames.length.toLocaleString();

      // Render pagination & cards
      renderPagination();
      renderContent();
    }'''

content = re.sub(
    r'function handleFilterChange\(\)\s*\{.*?renderContent\(\);\s*\}',
    new_apply_filters,
    content,
    flags=re.DOTALL
)

# 7. Update renderContent to render the 4 buttons and Santoral badge on each card
new_render_content = '''    function renderContent() {
      const emptyState = document.getElementById('emptyState');
      const grid = document.getElementById('namesGrid');
      const tbody = document.getElementById('namesTableBody');

      if (filteredNames.length === 0) {
        emptyState.className = 'text-center py-16 bg-white rounded-3xl border border-neutral-200/80 shadow-sm';
        grid.innerHTML = '';
        tbody.innerHTML = '';
        return;
      }
      emptyState.className = 'hidden';

      const startIdx = (currentPage - 1) * pageSize;
      const pageItems = filteredNames.slice(startIdx, startIdx + pageSize);

      // Render Grid (Mobile-First Touch Cards)
      grid.innerHTML = pageItems.map(item => {
        const color = getOriginColor(item.origin);
        const isFav = item.status === 'favorites';
        const isPos = item.status === 'possible';
        const isSim = item.status === 'similar_excluded';
        const isExc = item.status === 'excluded';

        return `
          <div class="bg-white rounded-3xl p-5 border border-neutral-200/80 shadow-xs hover:shadow-md transition card-transition flex flex-col justify-between group relative ${isFav ? 'ring-2 ring-amber-300 bg-amber-50/20' : ''} ${isSim ? 'border-orange-200 bg-orange-50/10' : ''}">
            
            <div>
              <!-- Top Row: Avatar & Status Badge -->
              <div class="flex items-start justify-between gap-2 mb-3">
                <div class="flex items-center gap-3">
                  <div class="w-11 h-11 rounded-2xl bg-gradient-to-tr from-rose-100 to-pink-200 text-rose-800 font-bold font-accent flex items-center justify-center text-lg shadow-2xs shrink-0">
                    ${item.name.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <h3 class="text-xl font-bold font-display text-neutral-900 leading-tight group-hover:text-rose-600 transition">${item.name}</h3>
                    <div class="flex items-center gap-1.5 mt-1 flex-wrap">
                      <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold ${color.bg} ${color.text} border ${color.border}">
                        ${item.origin || 'Origen'}
                      </span>
                      ${item.is_compound ? '<span class="inline-flex items-center px-1.5 py-0.5 rounded-full text-[10px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-200">🏷️ Compuesto</span>' : ''}
                      ${getVersionBadgeHTML(item)}
                    </div>
                  </div>
                </div>

                <div id="status_badge_${item.id}">
                  ${getStatusBadgeHTML(item.status)}
                </div>
              </div>

              <!-- Meaning in Spanish -->
              <p class="text-xs text-neutral-700 italic line-clamp-3 mb-2.5 font-serif leading-relaxed">
                "${item.meaning || 'Sin significado registrado'}"
              </p>

              <!-- Santoral / Onomástica if available -->
              ${item.saint_day && !item.saint_day.includes('Sin santoral') ? `
                <div class="text-[11px] text-purple-900 bg-purple-50/90 border border-purple-200/80 rounded-xl px-2.5 py-1 mb-2.5 flex items-center gap-1.5">
                  <span class="shrink-0 text-xs">📅</span>
                  <span class="truncate font-medium">${item.saint_day}</span>
                </div>
              ` : ''}

              <!-- Similarity Alert Box if Similar to Excluded -->
              ${item.similar_to ? `
                <div class="text-[11px] text-orange-900 bg-orange-50/90 border border-orange-200 rounded-xl px-2.5 py-1.5 mb-2.5 flex items-start gap-1.5">
                  <span class="shrink-0 text-xs mt-0.5">⚠️</span>
                  <span class="leading-tight">${item.similar_to}</span>
                </div>
              ` : ''}

              <!-- Notes tag if available -->
              ${item.notes && !item.similar_to ? `
                <div class="text-[11px] text-amber-800 bg-amber-50/80 border border-amber-200/80 rounded-xl px-2.5 py-1 mb-2.5 flex items-center gap-1">
                  <span>📌</span>
                  <span class="truncate">${item.notes}</span>
                </div>
              ` : ''}
            </div>

            <!-- Card Bottom: 4 Quick Touch Status Chips (Mobile-Friendly) -->
            <div class="pt-3 border-t border-neutral-100 flex flex-col gap-2">
              <div class="text-[10px] uppercase tracking-wider font-bold text-neutral-400 flex items-center justify-between">
                <span>Cambiar estado:</span>
                <button onclick="openEditModal('${item.id}')" class="text-rose-600 hover:underline">✏️ Editar</button>
              </div>

              <!-- 4 Touch Action Buttons -->
              <div class="flex items-center gap-1 bg-neutral-100/80 p-1 rounded-2xl border border-neutral-200/60">
                <button 
                  id="btn_fav_${item.id}"
                  title="Marcar Favorito" 
                  onclick="setItemStatus('${item.id}', 'favorites')" 
                  class="flex-1 py-2 rounded-xl text-xs font-bold transition flex items-center justify-center gap-1 ${isFav ? 'bg-amber-400 text-amber-950 font-bold shadow-sm' : 'text-neutral-500 hover:text-amber-700 hover:bg-amber-50'}"
                >
                  <span>⭐</span>
                  <span class="text-[10px] hidden xs:inline">Fav</span>
                </button>
                <button 
                  id="btn_pos_${item.id}"
                  title="Marcar Posible" 
                  onclick="setItemStatus('${item.id}', 'possible')" 
                  class="flex-1 py-2 rounded-xl text-xs font-bold transition flex items-center justify-center gap-1 ${isPos ? 'bg-sky-400 text-sky-950 font-bold shadow-sm' : 'text-neutral-500 hover:text-sky-700 hover:bg-sky-50'}"
                >
                  <span>👍</span>
                  <span class="text-[10px] hidden xs:inline">Posible</span>
                </button>
                <button 
                  id="btn_sim_${item.id}"
                  title="Marcar Similar / En Duda" 
                  onclick="setItemStatus('${item.id}', 'similar_excluded')" 
                  class="flex-1 py-2 rounded-xl text-xs font-bold transition flex items-center justify-center gap-1 ${isSim ? 'bg-orange-400 text-orange-950 font-bold shadow-sm' : 'text-neutral-500 hover:text-orange-700 hover:bg-orange-50'}"
                >
                  <span>⚠️</span>
                  <span class="text-[10px] hidden xs:inline">Duda</span>
                </button>
                <button 
                  id="btn_exc_${item.id}"
                  title="Excluir" 
                  onclick="setItemStatus('${item.id}', 'excluded')" 
                  class="flex-1 py-2 rounded-xl text-xs font-bold transition flex items-center justify-center gap-1 ${isExc ? 'bg-neutral-300 text-neutral-800 font-bold shadow-sm' : 'text-neutral-500 hover:text-neutral-700 hover:bg-neutral-100'}"
                >
                  <span>❌</span>
                  <span class="text-[10px] hidden xs:inline">Descartar</span>
                </button>
              </div>

            </div>

          </div>
        `;
      }).join('');

      // Render Table
      tbody.innerHTML = pageItems.map(item => {
        const color = getOriginColor(item.origin);
        return `
          <tr class="hover:bg-neutral-50/70 transition">
            <td class="py-3 px-4 font-bold text-neutral-900 flex items-center gap-2">
              <span class="w-7 h-7 rounded-xl bg-rose-100 text-rose-800 font-bold font-accent flex items-center justify-center text-xs">
                ${item.name.charAt(0).toUpperCase()}
              </span>
              <div>
                <div>${item.name}</div>
                ${item.is_compound ? '<span class="text-[10px] text-indigo-600 font-semibold">Compuesto</span>' : ''}
              </div>
            </td>
            <td class="py-3 px-4">
              <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold ${color.bg} ${color.text} border ${color.border}">
                ${item.origin}
              </span>
            </td>
            <td class="py-3 px-4 text-xs italic text-neutral-700 max-w-xs">
              <div class="line-clamp-2">${item.meaning}</div>
              ${item.saint_day && !item.saint_day.includes('Sin santoral') ? `<div class="text-[10px] text-purple-700 font-medium not-italic mt-0.5">📅 ${item.saint_day}</div>` : ''}
            </td>
            <td class="py-3 px-4" id="status_badge_tbl_${item.id}">
              ${getStatusBadgeHTML(item.status)}
            </td>
            <td class="py-3 px-4 text-xs text-neutral-500">
              <div class="flex items-center gap-1.5 flex-wrap">
                ${getVersionBadgeHTML(item)}
                ${item.page ? `<span class="text-[10px] text-neutral-400 font-mono">(${item.page.replace('.png','')})</span>` : ''}
              </div>
              ${item.similar_to ? `<div class="text-[10px] text-orange-700 font-medium mt-1">⚠️ ${item.similar_to}</div>` : ''}
            </td>
            <td class="py-3 px-4 text-right">
              <div class="inline-flex items-center gap-1 bg-neutral-100 p-1 rounded-xl">
                <button onclick="setItemStatus('${item.id}', 'favorites')" class="p-1 hover:scale-110 transition" title="Favorito">⭐</button>
                <button onclick="setItemStatus('${item.id}', 'possible')" class="p-1 hover:scale-110 transition" title="Posible">👍</button>
                <button onclick="setItemStatus('${item.id}', 'similar_excluded')" class="p-1 hover:scale-110 transition" title="Similar a Excluido">⚠️</button>
                <button onclick="setItemStatus('${item.id}', 'excluded')" class="p-1 hover:scale-110 transition" title="Excluir">❌</button>
                <button onclick="openEditModal('${item.id}')" class="p-1 text-neutral-400 hover:text-neutral-700" title="Editar">✏️</button>
              </div>
            </td>
          </tr>
        `;
      }).join('');
    }'''

content = re.sub(
    r'function renderContent\(\)\s*\{.*?tbody\.innerHTML = pageItems\.map\(item => \{.*?\}\)\.join\(\'\'\);\s*\}',
    new_render_content,
    content,
    flags=re.DOTALL
)

# 8. Update Swipe Action in Swipe Mode
new_swipe_controls = '''      <!-- Control Buttons (4 Actions) -->
      <div class="w-full grid grid-cols-4 gap-2 mt-5">
        <button onclick="handleSwipeAction('excluded')" class="flex flex-col items-center justify-center py-3 px-2 bg-white/10 hover:bg-red-500 hover:text-white text-white rounded-2xl border border-white/20 transition active:scale-95 group">
          <span class="text-xl group-hover:scale-110 transition">❌</span>
          <span class="text-[10px] font-bold mt-1">Excluir (←)</span>
        </button>

        <button onclick="handleSwipeAction('similar_excluded')" class="flex flex-col items-center justify-center py-3 px-2 bg-white/10 hover:bg-orange-500 hover:text-white text-white rounded-2xl border border-white/20 transition active:scale-95 group">
          <span class="text-xl group-hover:scale-110 transition">⚠️</span>
          <span class="text-[10px] font-bold mt-1">Duda (↓)</span>
        </button>

        <button onclick="handleSwipeAction('possible')" class="flex flex-col items-center justify-center py-3 px-2 bg-white/10 hover:bg-sky-500 hover:text-white text-white rounded-2xl border border-white/20 transition active:scale-95 group">
          <span class="text-xl group-hover:scale-110 transition">👍</span>
          <span class="text-[10px] font-bold mt-1">Posible (↑)</span>
        </button>

        <button onclick="handleSwipeAction('favorites')" class="flex flex-col items-center justify-center py-3 px-2 bg-gradient-to-r from-amber-400 to-orange-500 hover:from-amber-500 hover:to-orange-600 text-white rounded-2xl shadow-lg shadow-orange-500/30 transition active:scale-95 group">
          <span class="text-xl group-hover:scale-110 transition">⭐</span>
          <span class="text-[10px] font-bold mt-1">Favorito (→)</span>
        </button>
      </div>'''

content = re.sub(
    r'<!-- Control Buttons -->\s*<div class="w-full grid grid-cols-3.*?</div>\s*</div>\s*</div>',
    new_swipe_controls + '\n    </div>\n  </div>',
    content,
    flags=re.DOTALL
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS! Completed all updates on index.html.")
