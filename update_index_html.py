# -*- coding: utf-8 -*-
"""
Script to update index.html with:
- Title and Brand: 'Nombres para Chiquitina'
- 4 Categories (Favoritos, Posibles, Similares a Excluidos, Excluidos)
- Mobile-first responsive UI and Sticky Bottom Dock
- Santoral badges and Compound filters
- Embedding all 3,672 enriched names
"""

import json
import re

with open('names_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

print(f"Loaded {len(db)} names from names_db.json")

# Prepare minified or clean json string for embedded script
embedded_json = json.dumps(db, ensure_ascii=False, indent=2)

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update Title
html = re.sub(r'<title>.*?</title>', '<title>Nombres para Chiquitina</title>', html)

# 2. Update Header Brand
html = re.sub(
    r'<h1 class="text-2xl font-bold font-display tracking-tight text-neutral-900">.*?</h1>',
    '<h1 class="text-2xl font-bold font-display tracking-tight text-neutral-900">Nombres para Chiquitina</h1>',
    html
)
html = re.sub(
    r'<p class="text-xs text-neutral-500 font-medium">Gestor de Nombres:.*?</p>',
    '<p class="text-xs text-neutral-500 font-medium">Selección de Nombres Femeninos: Favoritos, Posibles, Similares a Excluidos & Descartados</p>',
    html
)

# 3. Update Version Control buttons in index.html
ver_buttons_html = '''        <!-- Right: Version Segmented Toggle Buttons -->
        <div class="inline-flex p-1.5 bg-neutral-100/90 rounded-2xl border border-neutral-200/80 gap-1 flex-wrap sm:flex-nowrap">
          
          <!-- Option 1: PDF Versión 1.0 Original -->
          <button 
            id="verBtn_pdf" 
            onclick="setVersionFilter('pdf')" 
            class="px-3 py-2 rounded-xl text-xs sm:text-sm font-semibold transition flex items-center gap-1.5 text-neutral-600 hover:text-neutral-900"
          >
            <span>📜</span>
            <span>Versión 1.0 (PDF)</span>
            <span id="verBadgePdf" class="px-2 py-0.5 text-[11px] font-bold rounded-lg bg-neutral-200 text-neutral-700">1,172</span>
          </button>

          <!-- Option 2: Nuevos Hispanos y Latinos (+2500) -->
          <button 
            id="verBtn_new" 
            onclick="setVersionFilter('new')" 
            class="px-3 py-2 rounded-xl text-xs sm:text-sm font-semibold transition flex items-center gap-1.5 text-neutral-600 hover:text-neutral-900"
          >
            <span>✨</span>
            <span>Nuevos Hispanos (+2,500)</span>
            <span id="verBadgeNew" class="px-2 py-0.5 text-[11px] font-bold rounded-lg bg-neutral-200 text-neutral-700">2,500</span>
          </button>

          <!-- Option 3: Todas las Versiones -->
          <button 
            id="verBtn_all" 
            onclick="setVersionFilter('all')" 
            class="px-3 py-2 rounded-xl text-xs sm:text-sm font-semibold transition flex items-center gap-1.5 bg-white text-neutral-900 shadow-sm border border-neutral-200/60"
          >
            <span>🌟</span>
            <span>Todo el Catálogo</span>
            <span id="verBadgeAll" class="px-2 py-0.5 text-[11px] font-bold rounded-lg bg-rose-100 text-rose-800">3,672</span>
          </button>

        </div>'''

html = re.sub(
    r'<!-- Right: Version Segmented Toggle Buttons -->\s*<div class="inline-flex.*?</div>\s*</div>\s*</div>\s*</div>',
    ver_buttons_html + '\n      </div>\n    </div>',
    html,
    flags=re.DOTALL
)

# 4. Replace Metrics Cards Banner with 5 responsive cards (Total + 4 Categories)
metrics_banner_html = '''    <!-- Metrics Cards Banner (4 Categories + Total) -->
    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 sm:gap-4 mb-6">
      
      <!-- Total -->
      <div onclick="setStatusFilter('all')" class="cursor-pointer bg-white rounded-2xl p-4 border border-neutral-200/80 shadow-sm hover:border-neutral-400 transition card-transition">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-neutral-500 uppercase tracking-wider">Total</span>
          <span class="text-xl">📚</span>
        </div>
        <div class="mt-2 flex items-baseline gap-2">
          <span id="metricTotal" class="text-2xl sm:text-3xl font-bold font-accent text-neutral-900">0</span>
          <span class="text-xs text-neutral-400">nombres</span>
        </div>
        <div id="metricTotalSubtitle" class="mt-1 text-[11px] text-neutral-400">PDF + Hispanos</div>
      </div>

      <!-- Favorites (Tier 1) -->
      <div onclick="setStatusFilter('favorites')" class="cursor-pointer bg-gradient-to-br from-amber-50 to-orange-50/50 rounded-2xl p-4 border border-amber-200 shadow-sm hover:border-amber-400 transition card-transition">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-amber-800 uppercase tracking-wider">⭐ Favoritos</span>
          <span class="text-xl">⭐</span>
        </div>
        <div class="mt-2 flex items-baseline gap-2">
          <span id="metricFavorites" class="text-2xl sm:text-3xl font-bold font-accent text-amber-900">0</span>
          <span class="text-xs text-amber-700/80">top elegidos</span>
        </div>
        <div id="metricFavoritesSubtitle" class="mt-1 text-[11px] text-amber-600">Para ronda final</div>
      </div>

      <!-- Possible (Tier 2) -->
      <div onclick="setStatusFilter('possible')" class="cursor-pointer bg-gradient-to-br from-sky-50 to-blue-50/50 rounded-2xl p-4 border border-sky-200 shadow-sm hover:border-sky-400 transition card-transition">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-sky-800 uppercase tracking-wider">👍 Posibles</span>
          <span class="text-xl">👍</span>
        </div>
        <div class="mt-2 flex items-baseline gap-2">
          <span id="metricPossible" class="text-2xl sm:text-3xl font-bold font-accent text-sky-900">0</span>
          <span class="text-xs text-sky-700/80">prometedores</span>
        </div>
        <div id="metricPossibleSubtitle" class="mt-1 text-[11px] text-sky-600">Sin conflicto</div>
      </div>

      <!-- Similar to Excluded (Tier 3) -->
      <div onclick="setStatusFilter('similar_excluded')" class="cursor-pointer bg-gradient-to-br from-orange-50 to-amber-50/50 rounded-2xl p-4 border border-orange-200 shadow-sm hover:border-orange-400 transition card-transition">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-orange-900 uppercase tracking-wider">⚠️ En Duda</span>
          <span class="text-xl">⚠️</span>
        </div>
        <div class="mt-2 flex items-baseline gap-2">
          <span id="metricSimilar" class="text-2xl sm:text-3xl font-bold font-accent text-orange-900">0</span>
          <span class="text-xs text-orange-700/80">similares</span>
        </div>
        <div id="metricSimilarSubtitle" class="mt-1 text-[11px] text-orange-600">Similares a descartados</div>
      </div>

      <!-- Excluded (Tier 4) -->
      <div onclick="setStatusFilter('excluded')" class="cursor-pointer bg-white rounded-2xl p-4 border border-neutral-200/80 shadow-sm hover:border-neutral-400 transition card-transition col-span-2 sm:col-span-1">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-neutral-500 uppercase tracking-wider">❌ Excluidos</span>
          <span class="text-xl">❌</span>
        </div>
        <div class="mt-2 flex items-baseline gap-2">
          <span id="metricExcluded" class="text-2xl sm:text-3xl font-bold font-accent text-neutral-700">0</span>
          <span class="text-xs text-neutral-400">descartados</span>
        </div>
        <div id="metricExcludedSubtitle" class="mt-1 text-[11px] text-neutral-400">Tachados en revisión</div>
      </div>

    </div>'''

html = re.sub(
    r'<!-- Metrics Cards Banner -->\s*<div class="grid grid-cols-2.*?<!-- Controls & Filters Section -->',
    metrics_banner_html + '\n\n    <!-- Controls & Filters Section -->',
    html,
    flags=re.DOTALL
)

# 5. Update Status Tabs to include similar_excluded and add compound filter
status_tabs_html = '''      <!-- Status Tabs Ribbon -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between border-t border-neutral-100 pt-3 gap-2">
        <div class="flex flex-wrap items-center gap-1.5 sm:gap-2 overflow-x-auto pb-1 custom-scrollbar">
          
          <button onclick="setStatusFilter('all')" id="tab_all" class="px-3 py-1.5 rounded-xl text-xs sm:text-sm font-semibold bg-neutral-900 text-white transition shrink-0">
            Todos <span id="tabCountAll" class="ml-1 text-[11px] opacity-70">(0)</span>
          </button>

          <button onclick="setStatusFilter('favorites')" id="tab_favorites" class="px-3 py-1.5 rounded-xl text-xs sm:text-sm font-semibold bg-neutral-100 text-neutral-600 hover:bg-neutral-200 transition shrink-0">
            ⭐ Favoritos <span id="tabCountFavorites" class="ml-1 text-[11px] opacity-70">(0)</span>
          </button>

          <button onclick="setStatusFilter('possible')" id="tab_possible" class="px-3 py-1.5 rounded-xl text-xs sm:text-sm font-semibold bg-neutral-100 text-neutral-600 hover:bg-neutral-200 transition shrink-0">
            👍 Posibles <span id="tabCountPossible" class="ml-1 text-[11px] opacity-70">(0)</span>
          </button>

          <button onclick="setStatusFilter('similar_excluded')" id="tab_similar_excluded" class="px-3 py-1.5 rounded-xl text-xs sm:text-sm font-semibold bg-orange-50 text-orange-800 border border-orange-200 hover:bg-orange-100 transition shrink-0">
            ⚠️ Similares a Excluidos <span id="tabCountSimilar" class="ml-1 text-[11px] opacity-70">(0)</span>
          </button>

          <button onclick="setStatusFilter('excluded')" id="tab_excluded" class="px-3 py-1.5 rounded-xl text-xs sm:text-sm font-semibold bg-neutral-100 text-neutral-600 hover:bg-neutral-200 transition shrink-0">
            ❌ Excluidos <span id="tabCountExcluded" class="ml-1 text-[11px] opacity-70">(0)</span>
          </button>

        </div>

        <div class="text-xs text-neutral-400 font-medium self-end sm:self-center">
          Mostrando <span id="showingCount" class="font-bold text-neutral-700">0</span> nombres
        </div>
      </div>'''

html = re.sub(
    r'<!-- Status Tabs Ribbon -->\s*<div class="flex items-center justify-between border-t border-neutral-100 pt-3">.*?<!-- Alphabet Letter Filter Ribbon -->',
    status_tabs_html + '\n\n      <!-- Alphabet Letter Filter Ribbon -->',
    html,
    flags=re.DOTALL
)

# 6. Add Compound / Santoral Filter to filter dropdowns row
type_filter_html = '''          <!-- Type / Compound Filter -->
          <select id="typeFilter" onchange="handleFilterChange()" class="py-2.5 px-3 bg-neutral-50 border border-neutral-200 rounded-xl text-xs sm:text-sm font-medium text-neutral-700 focus:outline-none focus:ring-2 focus:ring-rose-400">
            <option value="all">Simples & Compuestos</option>
            <option value="compound">Solo Compuestos (ej. María José)</option>
            <option value="single">Solo Nombres Simples</option>
            <option value="with_saint">Con Santoral Conocido</option>
          </select>'''

if '<select id="typeFilter"' not in html:
    html = html.replace(
        '<select id="originFilter"',
        type_filter_html + '\n\n          <!-- Origin Filter -->\n          <select id="originFilter"'
    )

print("Updated HTML markup elements (Title, Brand, 5 Metrics, 4 Category Tabs, Type Filter).")

# Save partial to verify
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
