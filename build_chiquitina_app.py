# -*- coding: utf-8 -*-
"""
Builds production-ready index.html with:
1. Bulletproof lightweight votes storage ('chiquitina_user_votes_v1') - saves only ID -> status (~50 KB)
2. Zero risk of QuotaExceededError or data loss across page reloads and sessions
3. Real-time Swipe session counter (⭐ 0 | 👍 0 | ⚠️ 0 | ❌ 0) so the user visibly sees choices accumulating
4. '↩️ Deshacer (Undo)' button in Swipe Mode to restore previous choices
5. Automatic overlay of saved votes on page load
6. Touch drag gestures & keyboard support
7. 2,500 new unrated names waiting for Rob and Ana
"""

import json
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('names_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

print(f"Loaded {len(db)} names from database.")
embedded_json = json.dumps(db, ensure_ascii=False)

html_template = '''<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>🎀 Nombres para Chiquitina | Rob & Ana</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,600;0,700;1,400&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <script>
    tailwind.config = {
      theme: {
        extend: {
          fontFamily: {
            sans: ['"Plus Jakarta Sans"', 'sans-serif'],
            display: ['"Playfair Display"', 'serif'],
            accent: ['"Outfit"', 'sans-serif']
          },
          colors: {
            rose: {
              50: '#fff1f2',
              100: '#ffe4e6',
              200: '#fecdd3',
              300: '#fda4af',
              400: '#fb7185',
              500: '#f43f5e',
              600: '#e11d48',
              700: '#be123c',
            },
            warm: {
              50: '#faf8f5',
              100: '#f5f0ea',
              200: '#ece3d6',
              800: '#2d2824',
              900: '#1c1917'
            }
          }
        }
      }
    }
  </script>
  <style>
    body {
      background-color: #faf8f5;
      color: #2d2824;
      -webkit-tap-highlight-color: transparent;
    }
    .custom-scrollbar::-webkit-scrollbar {
      height: 6px;
      width: 6px;
    }
    .custom-scrollbar::-webkit-scrollbar-track {
      background: #f1ede7;
      border-radius: 9999px;
    }
    .custom-scrollbar::-webkit-scrollbar-thumb {
      background: #d4c8bb;
      border-radius: 9999px;
    }
    .custom-scrollbar::-webkit-scrollbar-thumb:hover {
      background: #b8a896;
    }
    .card-transition {
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .badge-fav {
      background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
      color: #92400e;
      border: 1px solid #fcd34d;
    }
    .badge-pos {
      background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
      color: #0369a1;
      border: 1px solid #7dd3fc;
    }
    .badge-sim {
      background: linear-gradient(135deg, #ffedd5 0%, #fed7aa 100%);
      color: #9a3412;
      border: 1px solid #fdba74;
    }
    .badge-exc {
      background: #f3f4f6;
      color: #6b7280;
      border: 1px solid #e5e7eb;
    }
    .badge-unrated {
      background: #fffbeb;
      color: #b45309;
      border: 1px dashed #f59e0b;
    }
    .badge-super-match {
      background: linear-gradient(135deg, #ff2e93 0%, #ff80bf 50%, #ffa31a 100%);
      color: #ffffff;
      box-shadow: 0 4px 14px 0 rgba(255, 46, 147, 0.35);
    }
    .badge-match {
      background: linear-gradient(135deg, #059669 0%, #34d399 100%);
      color: #ffffff;
      box-shadow: 0 3px 10px 0 rgba(5, 150, 105, 0.25);
    }
    .swipe-card-touch {
      touch-action: pan-y;
      user-select: none;
    }
  </style>
</head>
<body class="min-h-screen flex flex-col font-sans selection:bg-rose-200 selection:text-rose-900 pb-20 sm:pb-8">

  <!-- Header -->
  <header class="sticky top-0 z-40 bg-white/90 backdrop-blur-md border-b border-rose-100 shadow-xs transition-all">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-20">
        
        <!-- Brand Title -->
        <div class="flex items-center space-x-3">
          <div class="w-12 h-12 rounded-2xl bg-gradient-to-tr from-rose-400 via-pink-400 to-amber-300 flex items-center justify-center text-white shadow-md shadow-rose-200 text-2xl shrink-0">
            🎀
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h1 class="text-xl sm:text-2xl font-bold font-display tracking-tight text-neutral-900">Nombres para Chiquitina</h1>
              <span id="storageStatusBadge" class="hidden sm:inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                <span id="storageStatusText">Guardado en tiempo real</span>
              </span>
            </div>
            <p class="text-xs text-neutral-500 font-medium">Rob & Ana — Encuentra el nombre perfecto para nuestra bebé</p>
          </div>
        </div>

        <!-- Person Switcher in Header (Rob / Ana / Ambos) -->
        <div class="hidden md:flex items-center p-1 bg-neutral-100 rounded-2xl border border-neutral-200/80 gap-1">
          <button 
            id="userSwitch_rob" 
            onclick="switchUser('rob')" 
            class="px-3.5 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 bg-blue-600 text-white shadow-xs"
          >
            <span>👨</span>
            <span>Rob</span>
            <span id="headerRobFavBadge" class="px-1.5 py-0.2 text-[10px] rounded-md bg-blue-800/60 text-white font-mono">23</span>
          </button>

          <button 
            id="userSwitch_ana" 
            onclick="switchUser('ana')" 
            class="px-3.5 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 text-neutral-600 hover:text-neutral-900"
          >
            <span>👩</span>
            <span>Ana</span>
            <span id="headerAnaFavBadge" class="px-1.5 py-0.2 text-[10px] rounded-md bg-neutral-200 text-neutral-700 font-mono">23</span>
          </button>

          <button 
            id="userSwitch_both" 
            onclick="switchUser('both')" 
            class="px-3.5 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 text-neutral-600 hover:text-neutral-900"
          >
            <span>💖</span>
            <span>Ambos / Matches</span>
            <span id="headerBothMatchBadge" class="px-1.5 py-0.2 text-[10px] rounded-md bg-pink-100 text-pink-700 font-mono">23</span>
          </button>
        </div>

          <!-- Cloud Sync Button -->
          <button onclick="openGitHubSyncModal()" id="headerGitHubSyncBtn" class="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs sm:text-sm font-semibold bg-white border border-neutral-200 text-neutral-700 shadow-2xs hover:bg-neutral-50 hover:border-neutral-300 transition active:scale-95" title="Sincronizar en la Nube con GitHub">
            <span id="githubSyncIcon" class="text-base">☁️</span>
            <span class="hidden sm:inline" id="githubSyncLabel">GitHub</span>
            <span id="githubSyncStatusDot" class="w-2 h-2 rounded-full bg-emerald-500 inline-block" title="Sincronizado"></span>
          </button>

          <button onclick="openSwipeModal()" class="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-bold bg-gradient-to-r from-amber-500 via-rose-500 to-pink-500 text-white shadow-md shadow-rose-200/60 hover:shadow-lg hover:scale-105 transition active:scale-95 animate-pulse">
            <span class="text-base">✨</span>
            <span class="hidden sm:inline">Modo Swipe (+2,500)</span>
            <span class="sm:hidden">Swipe</span>
          </button>

          <button onclick="openAddModal()" class="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs sm:text-sm font-semibold bg-rose-500 text-white shadow-md shadow-rose-200 hover:bg-rose-600 transition active:scale-95">
            <span>➕</span>
            <span class="hidden sm:inline">Añadir</span>
          </button>

          <!-- Export / Backup Dropdown -->
          <div class="relative group">
            <button class="p-2 sm:px-3 sm:py-2 rounded-xl text-neutral-700 bg-neutral-100 hover:bg-neutral-200 text-xs sm:text-sm font-medium transition flex items-center gap-1.5">
              <span>⚙️</span>
              <span class="text-[10px]">▼</span>
            </button>
            <div class="absolute right-0 mt-2 w-64 bg-white rounded-2xl shadow-xl border border-neutral-100 py-2 hidden group-hover:block z-50">
              <button onclick="openGitHubSyncModal()" class="w-full text-left px-4 py-2 text-xs text-blue-700 font-bold hover:bg-blue-50 flex items-center gap-2">
                <span>☁️</span> Sincronizar en GitHub (Nube)
              </button>
              <button onclick="shareVotesViaWhatsApp()" class="w-full text-left px-4 py-2 text-xs text-emerald-700 font-bold hover:bg-emerald-50 flex items-center gap-2">
                <span>💬</span> Pasar Votos a Pareja por WhatsApp
              </button>
              <button onclick="openSwipeModal()" class="w-full text-left px-4 py-2 text-xs text-rose-700 font-bold hover:bg-rose-50 flex items-center gap-2">
                <span>✨</span> Abrir Modo Swipe (Clasificar Nuevos)
              </button>
              <div class="border-t border-neutral-100 my-1"></div>
              <button onclick="exportToCSV()" class="w-full text-left px-4 py-2 text-xs text-neutral-700 hover:bg-rose-50 hover:text-rose-700 flex items-center gap-2">
                <span>📊</span> Exportar a Excel (c/ Votos Rob & Ana)
              </button>
              <button onclick="exportToJSON()" class="w-full text-left px-4 py-2 text-xs text-neutral-700 hover:bg-rose-50 hover:text-rose-700 flex items-center gap-2">
                <span>📁</span> Descargar Copia JSON Completa
              </button>
              <div class="border-t border-neutral-100 my-1"></div>
              <button onclick="copyRobPreferencesToAna()" class="w-full text-left px-4 py-2 text-xs text-purple-700 hover:bg-purple-50 flex items-center gap-2">
                <span>📋</span> Copiar Preferencias de Rob a Ana
              </button>
              <button onclick="document.getElementById('importFileInput').click()" class="w-full text-left px-4 py-2 text-xs text-neutral-700 hover:bg-rose-50 hover:text-rose-700 flex items-center gap-2">
                <span>📤</span> Importar Backup JSON
              </button>
              <input type="file" id="importFileInput" accept=".json" class="hidden" onchange="importJSON(event)">
              <div class="border-t border-neutral-100 my-1"></div>
              <button onclick="resetDatabase()" class="w-full text-left px-4 py-2 text-xs text-red-600 hover:bg-red-50 flex items-center gap-2">
                <span>🔄</span> Restaurar Lista Original
              </button>
            </div>
          </div>
        </div>

      </div>
    </div>
  </header>

  <!-- Mobile Person Selector Ribbon (Visible on small screens) -->
  <div class="md:hidden bg-gradient-to-r from-blue-50/80 via-pink-50/80 to-rose-50/80 border-b border-rose-100/80 px-4 py-2.5">
    <div class="flex items-center justify-between gap-2">
      <span class="text-xs font-bold text-neutral-600">👤 Votando:</span>
      <div class="inline-flex p-1 bg-white rounded-xl border border-neutral-200/80 shadow-2xs gap-1 flex-1 justify-end">
        <button 
          id="mobUserSwitch_rob" 
          onclick="switchUser('rob')" 
          class="px-2.5 py-1 rounded-lg text-xs font-bold transition flex items-center gap-1 bg-blue-600 text-white"
        >
          <span>👨 Rob</span>
        </button>
        <button 
          id="mobUserSwitch_ana" 
          onclick="switchUser('ana')" 
          class="px-2.5 py-1 rounded-lg text-xs font-bold transition flex items-center gap-1 text-neutral-600"
        >
          <span>👩 Ana</span>
        </button>
        <button 
          id="mobUserSwitch_both" 
          onclick="switchUser('both')" 
          class="px-2.5 py-1 rounded-lg text-xs font-bold transition flex items-center gap-1 text-neutral-600"
        >
          <span>💖 Matches</span>
        </button>
      </div>

      <!-- Mobile Cloud Sync Button -->
      <button onclick="openGitHubSyncModal()" class="p-2 rounded-xl bg-white border border-neutral-200 text-neutral-700 shadow-2xs text-xs font-bold flex items-center gap-1 shrink-0 active:scale-95" title="Sincronizar en la Nube">
        <span>☁️</span>
        <span id="mobSyncStatusDot" class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
      </button>
    </div>
  </div>

  <!-- Main Container -->
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex-1 w-full">

    <!-- Active User & Perspective Banner -->
    <div id="userPerspectiveBanner" class="bg-gradient-to-r from-blue-50 via-indigo-50/30 to-purple-50 rounded-3xl p-4 sm:p-5 border border-blue-200/70 shadow-2xs mb-6">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div class="flex items-center gap-3">
          <div id="userAvatarPill" class="w-12 h-12 rounded-2xl bg-blue-600 text-white flex items-center justify-center text-2xl shadow-sm shrink-0">
            👨
          </div>
          <div>
            <div class="flex items-center gap-2 flex-wrap">
              <span id="userGreetingTitle" class="text-sm sm:text-base font-bold text-neutral-900">Panel de Preferencias de Rob</span>
              <span id="userStatusTag" class="text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-blue-100 text-blue-800 border border-blue-200">
                Modo Activo: Rob
              </span>
            </div>
            <p id="userGreetingSubtitle" class="text-xs text-neutral-600 mt-0.5">
              ¡Tienes 2,500 nombres nuevos listos para clasificar en el modo Swipe o directamente en las tarjetas!
            </p>
          </div>
        </div>
        
        <!-- Fast Switch Quick Buttons -->
        <div class="flex items-center gap-2 shrink-0 self-end sm:self-auto">
          <button onclick="openSwipeModal()" class="px-3.5 py-1.5 rounded-xl text-xs font-bold bg-gradient-to-r from-amber-500 to-rose-500 hover:from-amber-600 hover:to-rose-600 text-white shadow-2xs transition flex items-center gap-1.5">
            <span>✨</span>
            <span>Clasificar en Swipe</span>
          </button>
          <button onclick="switchUser(currentUser === 'rob' ? 'ana' : 'rob')" class="px-3 py-1.5 rounded-xl text-xs font-bold bg-white text-neutral-700 hover:bg-neutral-100 border border-neutral-200 shadow-2xs transition flex items-center gap-1.5">
            <span>⇄</span>
            <span id="toggleUserBtnLabel">Cambiar a Ana</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Version Control Bar (Control de Versiones) -->
    <div class="bg-white rounded-3xl p-4 sm:p-5 border border-rose-100 shadow-xs mb-6">
      <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        
        <!-- Left: Version Title & Description -->
        <div class="flex items-center gap-3">
          <div class="w-11 h-11 rounded-2xl bg-rose-50 border border-rose-200 flex items-center justify-center text-xl shadow-2xs shrink-0">
            📑
          </div>
          <div>
            <div class="flex items-center gap-2 flex-wrap">
              <span class="text-xs font-bold uppercase tracking-wider text-rose-800">Control de Versiones</span>
              <span id="activeVersionTag" class="text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-rose-100 text-rose-800 border border-rose-200">
                Todo el Catálogo (3,672)
              </span>
            </div>
            <p id="activeVersionDescription" class="text-xs text-neutral-600 mt-0.5">
              1,172 nombres del PDF v1.0 original ya clasificados + 2,500 nuevos nombres hispanos y latinos por descubrir.
            </p>
          </div>
        </div>

        <!-- Right: Version Segmented Toggle Buttons -->
        <div class="inline-flex p-1.5 bg-neutral-100/90 rounded-2xl border border-neutral-200/80 gap-1 flex-wrap sm:flex-nowrap">
          
          <!-- Option 1: Nuevos Nombres Añadidos -->
          <button 
            id="verBtn_new" 
            onclick="setVersionFilter('new')" 
            class="px-3.5 py-2 rounded-xl text-xs sm:text-sm font-semibold transition flex items-center gap-2 text-neutral-600 hover:text-neutral-900"
          >
            <span>✨</span>
            <span>Nuevos Hispanos (+2,500)</span>
            <span id="verBadgeNew" class="px-2 py-0.5 text-[11px] font-bold rounded-lg bg-purple-100 text-purple-800">2,500</span>
          </button>

          <!-- Option 2: PDF Versión 1.0 Original -->
          <button 
            id="verBtn_pdf" 
            onclick="setVersionFilter('pdf')" 
            class="px-3.5 py-2 rounded-xl text-xs sm:text-sm font-semibold transition flex items-center gap-2 text-neutral-600 hover:text-neutral-900"
          >
            <span>📜</span>
            <span>Versión 1.0 (PDF)</span>
            <span id="verBadgePdf" class="px-2 py-0.5 text-[11px] font-bold rounded-lg bg-neutral-200 text-neutral-700">1,172</span>
          </button>

          <!-- Option 3: Todas las Versiones -->
          <button 
            id="verBtn_all" 
            onclick="setVersionFilter('all')" 
            class="px-3.5 py-2 rounded-xl text-xs sm:text-sm font-semibold transition flex items-center gap-2 bg-white text-neutral-900 shadow-sm border border-neutral-200/60"
          >
            <span>🌟</span>
            <span>Todo el Catálogo</span>
            <span id="verBadgeAll" class="px-2 py-0.5 text-[11px] font-bold rounded-lg bg-rose-100 text-rose-800">3,672</span>
          </button>

        </div>

      </div>
    </div>

    <!-- Metrics Cards Banner (Adapts dynamically to Rob, Ana or Ambos) -->
    <div id="metricsBanner" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 sm:gap-4 mb-6">
      
      <!-- Total / Coincidencias -->
      <div onclick="setStatusFilter('all')" class="cursor-pointer bg-white rounded-2xl p-4 border border-neutral-200/80 shadow-xs hover:border-neutral-400 transition card-transition">
        <div class="flex items-center justify-between">
          <span id="cardLabelTotal" class="text-xs font-semibold text-neutral-500 uppercase tracking-wider">Total</span>
          <span class="text-xl">📚</span>
        </div>
        <div class="mt-2 flex items-baseline gap-2">
          <span id="metricTotal" class="text-2xl sm:text-3xl font-bold font-accent text-neutral-900">3,672</span>
          <span class="text-xs text-neutral-400">nombres</span>
        </div>
        <div id="metricTotalSubtitle" class="mt-1 text-[11px] text-neutral-400">PDF + Hispanos</div>
      </div>

      <!-- Pendientes por Clasificar (Highlighted prominently!) -->
      <div onclick="setStatusFilter('unrated')" class="cursor-pointer bg-gradient-to-br from-amber-50/90 to-yellow-50/50 rounded-2xl p-4 border-2 border-amber-300 shadow-xs hover:border-amber-400 transition card-transition">
        <div class="flex items-center justify-between">
          <span id="cardLabelUnrated" class="text-xs font-bold text-amber-900 uppercase tracking-wider">⏳ Por Clasificar</span>
          <span class="text-xl">✨</span>
        </div>
        <div class="mt-2 flex items-baseline gap-2">
          <span id="metricUnrated" class="text-2xl sm:text-3xl font-bold font-accent text-amber-950">2,500</span>
          <span class="text-xs text-amber-700/80">listos p/ swipe</span>
        </div>
        <div id="metricUnratedSubtitle" class="mt-1 text-[11px] text-amber-700 font-medium">Nuevos por votar</div>
      </div>

      <!-- Favorites -->
      <div onclick="setStatusFilter('favorites')" class="cursor-pointer bg-gradient-to-br from-rose-50 to-pink-50/50 rounded-2xl p-4 border border-rose-200 shadow-xs hover:border-rose-400 transition card-transition">
        <div class="flex items-center justify-between">
          <span id="cardLabelFavorites" class="text-xs font-semibold text-rose-800 uppercase tracking-wider">⭐ Favoritos</span>
          <span class="text-xl">⭐</span>
        </div>
        <div class="mt-2 flex items-baseline gap-2">
          <span id="metricFavorites" class="text-2xl sm:text-3xl font-bold font-accent text-rose-900">23</span>
          <span class="text-xs text-rose-700/80">elegidos</span>
        </div>
        <div id="metricFavoritesSubtitle" class="mt-1 text-[11px] text-rose-600">Top preferencias</div>
      </div>

      <!-- Possible -->
      <div onclick="setStatusFilter('possible')" class="cursor-pointer bg-gradient-to-br from-sky-50 to-blue-50/50 rounded-2xl p-4 border border-sky-200 shadow-xs hover:border-sky-400 transition card-transition">
        <div class="flex items-center justify-between">
          <span id="cardLabelPossible" class="text-xs font-semibold text-sky-800 uppercase tracking-wider">👍 Posibles</span>
          <span class="text-xl">👍</span>
        </div>
        <div class="mt-2 flex items-baseline gap-2">
          <span id="metricPossible" class="text-2xl sm:text-3xl font-bold font-accent text-sky-900">58</span>
          <span class="text-xs text-sky-700/80">en consideración</span>
        </div>
        <div id="metricPossibleSubtitle" class="mt-1 text-[11px] text-sky-600">Candidatos viables</div>
      </div>

      <!-- Excluded -->
      <div onclick="setStatusFilter('excluded')" class="cursor-pointer bg-white rounded-2xl p-4 border border-neutral-200/80 shadow-xs hover:border-neutral-400 transition card-transition">
        <div class="flex items-center justify-between">
          <span id="cardLabelExcluded" class="text-xs font-semibold text-neutral-500 uppercase tracking-wider">❌ Excluidos</span>
          <span class="text-xl">❌</span>
        </div>
        <div class="mt-2 flex items-baseline gap-2">
          <span id="metricExcluded" class="text-2xl sm:text-3xl font-bold font-accent text-neutral-700">1,091</span>
          <span class="text-xs text-neutral-400">descartados</span>
        </div>
        <div id="metricExcludedSubtitle" class="mt-1 text-[11px] text-neutral-400">Tachados v1.0</div>
      </div>

    </div>

    <!-- Match Highlights Box -->
    <div id="matchHighlightsBanner" class="bg-gradient-to-r from-pink-500 via-rose-500 to-amber-500 rounded-3xl p-4 sm:p-5 text-white shadow-md mb-6 flex flex-col sm:flex-row items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <div class="w-12 h-12 rounded-2xl bg-white/20 backdrop-blur-md flex items-center justify-center text-2xl shadow-inner shrink-0">
          💖
        </div>
        <div>
          <div class="flex items-center gap-2">
            <h3 class="text-lg font-bold font-display">Coincidencias de Pareja (Rob & Ana)</h3>
            <span id="superMatchCountTag" class="px-2 py-0.5 rounded-full text-xs font-bold bg-white text-rose-600">23 Super Matches</span>
          </div>
          <p class="text-xs text-white/90 mt-0.5">
            ¡Descubran qué nombres le gustan a ambos! Cada vez que coincidan en ⭐ Favorito o 👍 Posible, aparecerá aquí como un Match.
          </p>
        </div>
      </div>
      <div class="flex items-center gap-2 self-stretch sm:self-auto justify-end">
        <button onclick="setStatusFilter('super_matches')" class="px-4 py-2 bg-white text-rose-600 hover:bg-rose-50 rounded-xl text-xs font-bold transition shadow-xs">
          ⭐ Ver Super Matches
        </button>
        <button onclick="setStatusFilter('matches')" class="px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-xl text-xs font-bold transition border border-white/30">
          💚 Ver Todas las Coincidencias
        </button>
      </div>
    </div>

    <!-- Controls & Filters Section -->
    <div class="bg-white rounded-3xl p-4 sm:p-6 border border-neutral-200/80 shadow-xs mb-6 space-y-4">
      
      <!-- Top Row: Search & View Mode -->
      <div class="flex flex-col lg:flex-row gap-3 items-stretch lg:items-center justify-between">
        
        <!-- Search Input -->
        <div class="relative flex-1">
          <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-neutral-400 text-lg">
            🔍
          </div>
          <input 
            type="text" 
            id="searchInput" 
            placeholder="Buscar por nombre, origen, significado, santo o similitud..." 
            oninput="handleSearch(this.value)"
            class="w-full pl-10 pr-10 py-3 bg-neutral-50 border border-neutral-200 rounded-2xl text-sm focus:outline-none focus:ring-2 focus:ring-rose-400 focus:bg-white transition"
          >
          <button id="clearSearchBtn" onclick="clearSearch()" class="hidden absolute inset-y-0 right-0 pr-3.5 flex items-center text-neutral-400 hover:text-neutral-600 text-sm">
            ✕
          </button>
        </div>

        <!-- Filter Dropdowns Row -->
        <div class="flex flex-wrap items-center gap-2">
          
          <!-- Match / Coincidence Filter -->
          <select id="matchFilter" onchange="handleFilterChange()" class="py-2.5 px-3 bg-neutral-50 border border-neutral-200 rounded-xl text-xs sm:text-sm font-medium text-neutral-700 focus:outline-none focus:ring-2 focus:ring-rose-400">
            <option value="all">Todas las calificaciones</option>
            <option value="super_match">💖 Super Matches (Ambos ⭐)</option>
            <option value="any_match">💚 Coincidencias (Ambos ⭐ o 👍)</option>
            <option value="conflict">⚡ En Debate (Opiniones opuestas)</option>
            <option value="pending_ana">⏳ Pendientes de votar por Ana</option>
            <option value="pending_rob">⏳ Pendientes de votar por Rob</option>
          </select>

          <!-- Type Filter -->
          <select id="typeFilter" onchange="handleFilterChange()" class="py-2.5 px-3 bg-neutral-50 border border-neutral-200 rounded-xl text-xs sm:text-sm font-medium text-neutral-700 focus:outline-none focus:ring-2 focus:ring-rose-400">
            <option value="all">Simples & Compuestos</option>
            <option value="compound">Solo Compuestos (ej. María José)</option>
            <option value="single">Solo Simples (1 palabra)</option>
            <option value="with_saint">Con Santoral Conocido 📅</option>
          </select>

          <!-- Origin Filter -->
          <select id="originFilter" onchange="handleFilterChange()" class="py-2.5 px-3 bg-neutral-50 border border-neutral-200 rounded-xl text-xs sm:text-sm font-medium text-neutral-700 focus:outline-none focus:ring-2 focus:ring-rose-400">
            <option value="all">Todas las etimologías</option>
          </select>

          <!-- Sort Select -->
          <select id="sortBy" onchange="handleSortChange()" class="py-2.5 px-3 bg-neutral-50 border border-neutral-200 rounded-xl text-xs sm:text-sm font-medium text-neutral-700 focus:outline-none focus:ring-2 focus:ring-rose-400">
            <option value="name_asc">Nombre (A → Z)</option>
            <option value="name_desc">Nombre (Z → A)</option>
            <option value="status_priority">Preferencia (⭐ → 👍 → ⏳ → ❌)</option>
            <option value="origin_asc">Origen (A → Z)</option>
          </select>

          <!-- View Switcher Toggle -->
          <div class="inline-flex rounded-xl bg-neutral-100 p-1 border border-neutral-200">
            <button id="viewGridBtn" onclick="setViewMode('grid')" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-white text-neutral-800 shadow-xs transition">
              🎴 Cuadrícula
            </button>
            <button id="viewTableBtn" onclick="setViewMode('table')" class="px-3 py-1.5 rounded-lg text-xs font-semibold text-neutral-500 hover:text-neutral-800 transition">
              📋 Tabla
            </button>
          </div>

        </div>

      </div>

      <!-- Status Tabs Ribbon (8 Comprehensive Tabs) -->
      <div class="flex items-center justify-between border-t border-neutral-100 pt-3 overflow-x-auto custom-scrollbar pb-1">
        <div class="flex items-center gap-1.5 sm:gap-2 shrink-0">
          
          <button onclick="setStatusFilter('all')" id="tab_all" class="px-3 py-1.5 rounded-xl text-xs sm:text-sm font-semibold bg-neutral-900 text-white transition shrink-0">
            Todos <span id="tabCountAll" class="ml-1 text-[11px] opacity-70">(3,672)</span>
          </button>

          <button onclick="setStatusFilter('unrated')" id="tab_unrated" class="px-3 py-1.5 rounded-xl text-xs sm:text-sm font-bold bg-amber-500 text-white shadow-xs transition shrink-0 flex items-center gap-1">
            <span>⏳ Por Clasificar</span> <span id="tabCountUnrated" class="text-[11px] font-mono">(2,500)</span>
          </button>

          <button onclick="setStatusFilter('super_matches')" id="tab_super_matches" class="px-3 py-1.5 rounded-xl text-xs sm:text-sm font-bold bg-pink-100 text-pink-800 hover:bg-pink-200 border border-pink-300 transition shrink-0 flex items-center gap-1">
            <span>💖 Super Matches</span> <span id="tabCountSuperMatches" class="text-[11px] font-mono">(23)</span>
          </button>

          <button onclick="setStatusFilter('matches')" id="tab_matches" class="px-3 py-1.5 rounded-xl text-xs sm:text-sm font-bold bg-emerald-100 text-emerald-800 hover:bg-emerald-200 border border-emerald-300 transition shrink-0 flex items-center gap-1">
            <span>💚 Coincidencias</span> <span id="tabCountMatches" class="text-[11px] font-mono">(23)</span>
          </button>

          <button onclick="setStatusFilter('favorites')" id="tab_favorites" class="px-3 py-1.5 rounded-xl text-xs sm:text-sm font-semibold bg-neutral-100 text-neutral-600 hover:bg-neutral-200 transition shrink-0">
            ⭐ Favoritos <span id="tabCountFavorites" class="ml-1 text-[11px] opacity-70">(23)</span>
          </button>

          <button onclick="setStatusFilter('possible')" id="tab_possible" class="px-3 py-1.5 rounded-xl text-xs sm:text-sm font-semibold bg-neutral-100 text-neutral-600 hover:bg-neutral-200 transition shrink-0">
            👍 Posibles <span id="tabCountPossible" class="ml-1 text-[11px] opacity-70">(58)</span>
          </button>

          <button onclick="setStatusFilter('similar_excluded')" id="tab_similar_excluded" class="px-3 py-1.5 rounded-xl text-xs sm:text-sm font-semibold bg-orange-50 text-orange-800 border border-orange-200 hover:bg-orange-100 transition shrink-0">
            ⚠️ En Duda <span id="tabCountSimilar" class="ml-1 text-[11px] opacity-70">(0)</span>
          </button>

          <button onclick="setStatusFilter('excluded')" id="tab_excluded" class="px-3 py-1.5 rounded-xl text-xs sm:text-sm font-semibold bg-neutral-100 text-neutral-600 hover:bg-neutral-200 transition shrink-0">
            ❌ Excluidos <span id="tabCountExcluded" class="ml-1 text-[11px] opacity-70">(1,091)</span>
          </button>

        </div>

        <div class="text-xs text-neutral-400 font-medium hidden lg:block shrink-0 ml-4">
          Mostrando <span id="showingCount" class="font-bold text-neutral-700">0</span> nombres
        </div>
      </div>

      <!-- Alphabet Letter Filter Ribbon -->
      <div class="border-t border-neutral-100 pt-3 flex items-center gap-1 overflow-x-auto custom-scrollbar pb-1">
        <button onclick="setLetterFilter('')" id="letter_ALL" class="px-2.5 py-1 rounded-lg text-xs font-bold bg-rose-500 text-white shrink-0">
          TODOS
        </button>
        <!-- A-Z generated dynamically -->
        <div id="alphabetContainer" class="flex items-center gap-1 shrink-0"></div>
      </div>

    </div>

    <!-- Active Filter Indicators -->
    <div id="filterPills" class="flex flex-wrap items-center gap-2 mb-4 text-xs"></div>

    <!-- Content Area: Grid View -->
    <div id="namesGrid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4"></div>

    <!-- Content Area: Table View (Hidden by default) -->
    <div id="namesTableWrapper" class="hidden bg-white rounded-3xl border border-neutral-200/80 shadow-xs overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-sm text-neutral-700">
          <thead class="bg-neutral-50/80 border-b border-neutral-200 text-xs font-semibold text-neutral-500 uppercase tracking-wider">
            <tr>
              <th scope="col" class="py-3 px-4">Nombre</th>
              <th scope="col" class="py-3 px-4">Origen</th>
              <th scope="col" class="py-3 px-4">Significado</th>
              <th scope="col" class="py-3 px-4">👨 Rob</th>
              <th scope="col" class="py-3 px-4">👩 Ana</th>
              <th scope="col" class="py-3 px-4">💑 Coincidencia</th>
              <th scope="col" class="py-3 px-4 text-right">Acciones</th>
            </tr>
          </thead>
          <tbody id="namesTableBody" class="divide-y divide-neutral-100"></tbody>
        </table>
      </div>
    </div>

    <!-- Empty State -->
    <div id="emptyState" class="hidden text-center py-16 bg-white rounded-3xl border border-neutral-200/80 shadow-xs">
      <div class="text-5xl mb-3">🔍</div>
      <h3 class="text-lg font-bold text-neutral-800">No se encontraron nombres con este criterio</h3>
      <p class="text-sm text-neutral-500 mt-1 max-w-sm mx-auto">Prueba cambiando la pestaña de estado, la letra o limpiando la búsqueda.</p>
      <button onclick="resetFilters()" class="mt-4 px-4 py-2 bg-rose-500 text-white rounded-xl text-xs font-semibold hover:bg-rose-600 transition">
        Restablecer Filtros
      </button>
    </div>

    <!-- Pagination Controls -->
    <div id="paginationControls" class="flex items-center justify-between mt-6 bg-white rounded-2xl p-4 border border-neutral-200/80 shadow-xs">
      <div class="text-xs text-neutral-500">
        Página <span id="currentPageNum" class="font-bold text-neutral-800">1</span> de <span id="totalPagesNum" class="font-bold text-neutral-800">1</span>
      </div>
      <div class="flex items-center gap-2">
        <button id="prevPageBtn" onclick="changePage(-1)" class="px-3.5 py-1.5 rounded-xl border border-neutral-200 text-xs font-semibold text-neutral-700 hover:bg-neutral-50 disabled:opacity-40 disabled:pointer-events-none transition">
          ◀ Anterior
        </button>
        <button id="nextPageBtn" onclick="changePage(1)" class="px-3.5 py-1.5 rounded-xl border border-neutral-200 text-xs font-semibold text-neutral-700 hover:bg-neutral-50 disabled:opacity-40 disabled:pointer-events-none transition">
          Siguiente ▶
        </button>
      </div>
    </div>

  </main>

  <!-- Mobile Sticky Bottom Navigation Dock (Facilita navegación con una mano en móvil) -->
  <nav class="sm:hidden fixed bottom-0 left-0 right-0 z-40 bg-white/95 backdrop-blur-xl border-t border-rose-100 px-3 py-2 flex items-center justify-around shadow-2xl">
    <button onclick="switchUser(currentUser === 'rob' ? 'ana' : 'rob')" class="flex flex-col items-center justify-center text-[10px] font-bold text-neutral-700 hover:text-blue-600 transition active:scale-95">
      <span class="text-lg" id="dockUserIcon">👨</span>
      <span class="mt-0.5" id="dockUserLabel">Rob</span>
    </button>
    
    <button onclick="setStatusFilter('unrated'); window.scrollTo({ top: 380, behavior: 'smooth' });" class="flex flex-col items-center justify-center text-[10px] font-semibold text-amber-800 hover:text-amber-900 transition active:scale-95">
      <span class="text-lg">⏳</span>
      <span class="mt-0.5">Pendientes</span>
    </button>

    <button onclick="openSwipeModal()" class="flex flex-col items-center justify-center -mt-6 bg-gradient-to-tr from-amber-500 via-rose-500 to-pink-500 text-white rounded-2xl w-14 h-14 p-2 shadow-lg shadow-rose-300 transition active:scale-90 border-2 border-white animate-bounce">
      <span class="text-2xl">✨</span>
      <span class="text-[9px] font-bold">Swipe</span>
    </button>

    <button onclick="setStatusFilter('super_matches'); window.scrollTo({ top: 380, behavior: 'smooth' });" class="flex flex-col items-center justify-center text-[10px] font-semibold text-pink-700 hover:text-pink-900 transition active:scale-95">
      <span class="text-lg">💖</span>
      <span class="mt-0.5">Matches</span>
    </button>

    <button onclick="openAddModal()" class="flex flex-col items-center justify-center text-[10px] font-semibold text-neutral-600 hover:text-rose-600 transition active:scale-95">
      <span class="text-lg">➕</span>
      <span class="mt-0.5">Añadir</span>
    </button>
  </nav>

  <!-- Add Name Modal -->
  <div id="addModal" class="fixed inset-0 bg-neutral-900/50 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
    <div class="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl border border-rose-100 animate-in fade-in zoom-in-95 duration-150">
      <div class="flex items-center justify-between border-b border-neutral-100 pb-3 mb-4">
        <div class="flex items-center gap-2">
          <span class="text-xl">🌸</span>
          <h3 class="text-lg font-bold font-display text-neutral-900">Añadir Nuevo Nombre</h3>
        </div>
        <button onclick="closeAddModal()" class="text-neutral-400 hover:text-neutral-600 text-xl font-bold">✕</button>
      </div>

      <form id="addNameForm" onsubmit="submitAddName(event)" class="space-y-4">
        <div>
          <label class="block text-xs font-bold text-neutral-700 uppercase tracking-wider mb-1">Nombre</label>
          <input type="text" id="addNameInput" required placeholder="Ej. Valentina, María José, Lucía..." class="w-full px-3.5 py-2.5 rounded-xl bg-neutral-50 border border-neutral-200 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400 focus:bg-white transition">
          <div id="addNameDuplicateAlert" class="text-xs text-amber-600 font-medium mt-1 hidden">⚠️ Ya existe un nombre con esa denominación en la lista.</div>
        </div>

        <div>
          <label class="block text-xs font-bold text-neutral-700 uppercase tracking-wider mb-1">Origen / Etimología</label>
          <input type="text" id="addOriginInput" list="originsList" required placeholder="Ej. Latino, Griego, Hebreo, Español..." class="w-full px-3.5 py-2.5 rounded-xl bg-neutral-50 border border-neutral-200 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400 focus:bg-white transition">
          <datalist id="originsList">
            <option value="Latino"></option>
            <option value="Español"></option>
            <option value="Griego"></option>
            <option value="Hebreo"></option>
            <option value="Italiano"></option>
            <option value="Francés"></option>
            <option value="Germánico"></option>
            <option value="Vasco"></option>
          </datalist>
        </div>

        <div>
          <label class="block text-xs font-bold text-neutral-700 uppercase tracking-wider mb-1">Significado en Español</label>
          <textarea id="addMeaningInput" rows="2" placeholder="Ej. Fuerte, valiente, llena de salud y gracia..." class="w-full px-3.5 py-2.5 rounded-xl bg-neutral-50 border border-neutral-200 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400 focus:bg-white transition"></textarea>
        </div>

        <div>
          <label class="block text-xs font-bold text-neutral-700 uppercase tracking-wider mb-1">Fecha de Santoral / Santo (Opcional)</label>
          <input type="text" id="addSaintInput" placeholder="Ej. 13 de diciembre (Santa Lucía)..." class="w-full px-3.5 py-2.5 rounded-xl bg-neutral-50 border border-neutral-200 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400 focus:bg-white transition">
        </div>

        <div>
          <label class="block text-xs font-bold text-neutral-700 uppercase tracking-wider mb-1">Preferencia Inicial (<span id="addPersonNameLabel">Rob</span>)</label>
          <div class="grid grid-cols-4 gap-1.5">
            <label class="cursor-pointer border border-neutral-200 rounded-xl p-2 text-center text-xs font-semibold has-[:checked]:border-amber-400 has-[:checked]:bg-amber-50 has-[:checked]:text-amber-800 transition">
              <input type="radio" name="addStatus" value="favorites" class="sr-only">
              ⭐ Fav
            </label>
            <label class="cursor-pointer border border-neutral-200 rounded-xl p-2 text-center text-xs font-semibold has-[:checked]:border-sky-400 has-[:checked]:bg-sky-50 has-[:checked]:text-sky-800 transition">
              <input type="radio" name="addStatus" value="possible" checked class="sr-only">
              👍 Posible
            </label>
            <label class="cursor-pointer border border-neutral-200 rounded-xl p-2 text-center text-xs font-semibold has-[:checked]:border-orange-400 has-[:checked]:bg-orange-50 has-[:checked]:text-orange-800 transition">
              <input type="radio" name="addStatus" value="similar_excluded" class="sr-only">
              ⚠️ Duda
            </label>
            <label class="cursor-pointer border border-neutral-200 rounded-xl p-2 text-center text-xs font-semibold has-[:checked]:border-neutral-400 has-[:checked]:bg-neutral-100 has-[:checked]:text-neutral-800 transition">
              <input type="radio" name="addStatus" value="excluded" class="sr-only">
              ❌ Excluir
            </label>
          </div>
        </div>

        <div>
          <label class="block text-xs font-bold text-neutral-700 uppercase tracking-wider mb-1">Notas Familiares (Opcional)</label>
          <input type="text" id="addNotesInput" placeholder="Ej. Combina con el apellido, le encanta a mamá..." class="w-full px-3.5 py-2.5 rounded-xl bg-neutral-50 border border-neutral-200 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400 focus:bg-white transition">
        </div>

        <div class="flex items-center justify-end gap-2 pt-2 border-t border-neutral-100">
          <button type="button" onclick="closeAddModal()" class="px-4 py-2 rounded-xl text-xs font-semibold text-neutral-600 hover:bg-neutral-100 transition">
            Cancelar
          </button>
          <button type="submit" class="px-5 py-2.5 rounded-xl text-xs font-bold bg-rose-500 text-white shadow-md shadow-rose-200 hover:bg-rose-600 transition">
            Guardar Nombre
          </button>
        </div>
      </form>
    </div>
  </div>

  <!-- Edit Name Modal -->
  <div id="editModal" class="fixed inset-0 bg-neutral-900/50 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
    <div class="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl border border-rose-100">
      <div class="flex items-center justify-between border-b border-neutral-100 pb-3 mb-4">
        <h3 class="text-lg font-bold font-display text-neutral-900">✏️ Editar Nombre</h3>
        <button onclick="closeEditModal()" class="text-neutral-400 hover:text-neutral-600 text-xl font-bold">✕</button>
      </div>

      <form id="editNameForm" onsubmit="submitEditName(event)" class="space-y-4">
        <input type="hidden" id="editIdInput">

        <div>
          <label class="block text-xs font-bold text-neutral-700 uppercase tracking-wider mb-1">Nombre</label>
          <input type="text" id="editNameInput" required class="w-full px-3.5 py-2.5 rounded-xl bg-neutral-50 border border-neutral-200 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400 focus:bg-white transition">
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-bold text-neutral-700 uppercase tracking-wider mb-1">Origen</label>
            <input type="text" id="editOriginInput" required class="w-full px-3.5 py-2.5 rounded-xl bg-neutral-50 border border-neutral-200 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400 focus:bg-white transition">
          </div>
          <div>
            <label class="block text-xs font-bold text-neutral-700 uppercase tracking-wider mb-1">Santoral</label>
            <input type="text" id="editSaintInput" class="w-full px-3.5 py-2.5 rounded-xl bg-neutral-50 border border-neutral-200 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400 focus:bg-white transition">
          </div>
        </div>

        <div>
          <label class="block text-xs font-bold text-neutral-700 uppercase tracking-wider mb-1">Significado</label>
          <textarea id="editMeaningInput" rows="2" class="w-full px-3.5 py-2.5 rounded-xl bg-neutral-50 border border-neutral-200 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400 focus:bg-white transition"></textarea>
        </div>

        <!-- Rob's Vote in Edit Modal -->
        <div class="p-3 bg-blue-50/70 border border-blue-200 rounded-2xl">
          <label class="block text-xs font-bold text-blue-900 uppercase tracking-wider mb-1.5">👨 Voto de Rob</label>
          <div class="grid grid-cols-4 gap-1">
            <label class="cursor-pointer border border-blue-200 bg-white rounded-xl p-1.5 text-center text-xs font-semibold has-[:checked]:bg-amber-400 has-[:checked]:text-amber-950 transition">
              <input type="radio" name="editRobStatus" value="favorites" id="editRobFav" class="sr-only">
              ⭐ Fav
            </label>
            <label class="cursor-pointer border border-blue-200 bg-white rounded-xl p-1.5 text-center text-xs font-semibold has-[:checked]:bg-sky-400 has-[:checked]:text-sky-950 transition">
              <input type="radio" name="editRobStatus" value="possible" id="editRobPos" class="sr-only">
              👍 Pos
            </label>
            <label class="cursor-pointer border border-blue-200 bg-white rounded-xl p-1.5 text-center text-xs font-semibold has-[:checked]:bg-orange-400 has-[:checked]:text-orange-950 transition">
              <input type="radio" name="editRobStatus" value="similar_excluded" id="editRobSim" class="sr-only">
              ⚠️ Duda
            </label>
            <label class="cursor-pointer border border-blue-200 bg-white rounded-xl p-1.5 text-center text-xs font-semibold has-[:checked]:bg-neutral-300 has-[:checked]:text-neutral-900 transition">
              <input type="radio" name="editRobStatus" value="excluded" id="editRobExc" class="sr-only">
              ❌ Excl
            </label>
          </div>
        </div>

        <!-- Ana's Vote in Edit Modal -->
        <div class="p-3 bg-pink-50/70 border border-pink-200 rounded-2xl">
          <label class="block text-xs font-bold text-pink-900 uppercase tracking-wider mb-1.5">👩 Voto de Ana</label>
          <div class="grid grid-cols-4 gap-1">
            <label class="cursor-pointer border border-pink-200 bg-white rounded-xl p-1.5 text-center text-xs font-semibold has-[:checked]:bg-amber-400 has-[:checked]:text-amber-950 transition">
              <input type="radio" name="editAnaStatus" value="favorites" id="editAnaFav" class="sr-only">
              ⭐ Fav
            </label>
            <label class="cursor-pointer border border-pink-200 bg-white rounded-xl p-1.5 text-center text-xs font-semibold has-[:checked]:bg-sky-400 has-[:checked]:text-sky-950 transition">
              <input type="radio" name="editAnaStatus" value="possible" id="editAnaPos" class="sr-only">
              👍 Pos
            </label>
            <label class="cursor-pointer border border-pink-200 bg-white rounded-xl p-1.5 text-center text-xs font-semibold has-[:checked]:bg-orange-400 has-[:checked]:text-orange-950 transition">
              <input type="radio" name="editAnaStatus" value="similar_excluded" id="editAnaSim" class="sr-only">
              ⚠️ Duda
            </label>
            <label class="cursor-pointer border border-pink-200 bg-white rounded-xl p-1.5 text-center text-xs font-semibold has-[:checked]:bg-neutral-300 has-[:checked]:text-neutral-900 transition">
              <input type="radio" name="editAnaStatus" value="excluded" id="editAnaExc" class="sr-only">
              ❌ Excl
            </label>
          </div>
        </div>

        <div>
          <label class="block text-xs font-bold text-neutral-700 uppercase tracking-wider mb-1">Notas Personales</label>
          <input type="text" id="editNotesInput" placeholder="Añadir notas o comentarios familiares..." class="w-full px-3.5 py-2.5 rounded-xl bg-neutral-50 border border-neutral-200 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400 focus:bg-white transition">
        </div>

        <div class="flex items-center justify-between pt-2 border-t border-neutral-100">
          <button type="button" onclick="deleteCurrentEditName()" class="px-3 py-2 text-xs font-semibold text-red-600 hover:bg-red-50 rounded-xl transition">
            🗑️ Eliminar
          </button>
          <div class="flex items-center gap-2">
            <button type="button" onclick="closeEditModal()" class="px-4 py-2 rounded-xl text-xs font-semibold text-neutral-600 hover:bg-neutral-100 transition">
              Cancelar
            </button>
            <button type="submit" class="px-5 py-2.5 rounded-xl text-xs font-bold bg-rose-500 text-white shadow-md shadow-rose-200 hover:bg-rose-600 transition">
              Actualizar
            </button>
          </div>
        </div>
      </form>
    </div>
  </div>

  <!-- Swipe Discovery Mode Modal (Tinder-style with Real-time Persistence & Undo) -->
  <div id="swipeModal" class="fixed inset-0 bg-neutral-950/85 backdrop-blur-md z-50 hidden flex flex-col items-center justify-center p-3 sm:p-4">
    <div class="max-w-md w-full flex flex-col items-center">
      
      <!-- Top header bar -->
      <div class="w-full flex items-center justify-between text-white/90 mb-2 px-1">
        <div class="flex items-center gap-2">
          <span class="text-xl">✨</span>
          <span class="font-bold text-sm">Modo Swipe</span>
          <span id="swipeDeckProgress" class="text-xs font-bold bg-amber-400 text-amber-950 px-2 py-0.5 rounded-full shadow-xs">2,500</span>
          <button onclick="openGitHubSyncModal()" class="text-xs bg-white/10 hover:bg-white/20 text-white/90 px-2 py-0.5 rounded-lg flex items-center gap-1 border border-white/15 transition active:scale-95" title="Sincronización en la nube">
            <span>☁️</span>
            <span id="swipeSyncStatusText" class="text-[10px]">Al día</span>
          </button>
        </div>
        <button onclick="closeSwipeModal()" class="w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center text-sm font-bold text-white transition">✕</button>
      </div>

      <!-- Who is swiping selector & Undo button -->
      <div class="w-full bg-white/10 backdrop-blur-md rounded-2xl p-1.5 mb-2 flex items-center justify-between border border-white/10">
        <div class="inline-flex items-center gap-1">
          <span class="text-xs text-white/90 font-bold px-1">Votando:</span>
          <button 
            id="swipeUser_rob" 
            onclick="setSwipeUser('rob')" 
            class="px-2.5 py-1 rounded-xl text-xs font-bold bg-blue-600 text-white shadow-xs transition"
          >
            👨 Rob
          </button>
          <button 
            id="swipeUser_ana" 
            onclick="setSwipeUser('ana')" 
            class="px-2.5 py-1 rounded-xl text-xs font-bold text-white/70 hover:text-white transition"
          >
            👩 Ana
          </button>
        </div>

        <!-- Undo button -->
        <button onclick="undoLastSwipe()" class="px-2.5 py-1 rounded-xl text-xs font-bold bg-white/15 hover:bg-white/25 text-white transition flex items-center gap-1 border border-white/20 active:scale-95">
          <span>↩️</span>
          <span>Deshacer</span>
        </button>
      </div>

      <!-- Live Session Stats Ribbon -->
      <div class="w-full flex items-center justify-between text-[11px] text-white/80 bg-white/5 border border-white/10 px-3 py-1 rounded-xl mb-2.5">
        <span>Votados en esta sesión:</span>
        <span id="swipeSessionStats" class="font-mono font-bold text-amber-300">⭐ 0 | 👍 0 | ⚠️ 0 | ❌ 0</span>
      </div>

      <!-- Filter deck selector -->
      <div class="w-full flex items-center justify-center gap-1.5 mb-3 flex-wrap">
        <button onclick="setSwipeFilter('new_unrated')" id="swipeFilter_new_unrated" class="px-3 py-1 rounded-full text-xs font-bold bg-rose-500 text-white shadow-xs transition">
          ✨ Nuevos por Clasificar (+2,500)
        </button>
        <button onclick="setSwipeFilter('all_unrated')" id="swipeFilter_all_unrated" class="px-3 py-1 rounded-full text-xs font-semibold bg-white/15 text-white/80 hover:bg-white/25 transition">
          ⏳ Todo lo Pendiente
        </button>
        <button onclick="setSwipeFilter('possible')" id="swipeFilter_possible" class="px-3 py-1 rounded-full text-xs font-semibold bg-white/15 text-white/80 hover:bg-white/25 transition">
          👍 Mis Posibles
        </button>
        <button onclick="setSwipeFilter('favorites')" id="swipeFilter_favorites" class="px-3 py-1 rounded-full text-xs font-semibold bg-white/15 text-white/80 hover:bg-white/25 transition">
          ⭐ Mis Favoritos
        </button>
      </div>

      <!-- The Swipe Card (Touch & Drag Enabled) -->
      <div id="swipeCard" class="swipe-card-touch w-full bg-white rounded-3xl p-6 sm:p-7 shadow-2xl border border-neutral-100 flex flex-col items-center text-center relative min-h-[380px] justify-between transition-all duration-300">
        
        <!-- Letter Tag & Origin Badge -->
        <div class="w-full flex items-center justify-between">
          <span id="swipeLetter" class="w-10 h-10 rounded-2xl bg-rose-100 text-rose-700 font-bold font-accent flex items-center justify-center text-lg shadow-inner">A</span>
          <span id="swipeOrigin" class="px-3 py-1 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200">Latino</span>
          <span id="swipeSource" class="text-[11px] text-neutral-400 font-medium">Nuevo</span>
        </div>

        <!-- Partner's vote tag in Swipe -->
        <div id="swipePartnerVoteTag" class="w-full mt-2"></div>

        <!-- Big Name & Meaning -->
        <div class="my-auto py-3">
          <h2 id="swipeName" class="text-3xl sm:text-4xl font-bold font-display text-neutral-900 tracking-tight mb-2">Abril</h2>
          <p id="swipeMeaning" class="text-sm sm:text-base italic text-neutral-600 font-serif leading-relaxed px-2">"Apertura, frescura y renacer de la primavera"</p>
          <div id="swipeSaint" class="mt-2 text-xs text-purple-800 bg-purple-50 px-3 py-1 rounded-xl border border-purple-200 inline-block font-medium"></div>
          <div id="swipeSimilarity" class="mt-2 text-xs text-orange-800 bg-orange-50 px-3 py-1 rounded-xl border border-orange-200 inline-block font-medium hidden"></div>
        </div>

        <!-- Current Status Pill -->
        <div class="w-full pt-3 border-t border-neutral-100 flex items-center justify-between text-xs text-neutral-400">
          <span>Tu voto actual: <b id="swipeCurrentStatus" class="text-amber-800 font-bold">Por clasificar</b></span>
          <span class="text-[11px] text-neutral-400">Desliza o usa botones</span>
        </div>

      </div>

      <!-- Control Buttons (4 Actions) -->
      <div class="w-full grid grid-cols-4 gap-2 mt-4">
        <button onclick="handleSwipeAction('excluded')" class="flex flex-col items-center justify-center py-3 px-2 bg-white/10 hover:bg-red-500 hover:text-white text-white rounded-2xl border border-white/20 transition active:scale-95 group">
          <span class="text-2xl group-hover:scale-110 transition">❌</span>
          <span class="text-[10px] font-bold mt-1">Excluir (←)</span>
        </button>

        <button onclick="handleSwipeAction('similar_excluded')" class="flex flex-col items-center justify-center py-3 px-2 bg-white/10 hover:bg-orange-500 hover:text-white text-white rounded-2xl border border-white/20 transition active:scale-95 group">
          <span class="text-2xl group-hover:scale-110 transition">⚠️</span>
          <span class="text-[10px] font-bold mt-1">Duda (↓)</span>
        </button>

        <button onclick="handleSwipeAction('possible')" class="flex flex-col items-center justify-center py-3 px-2 bg-white/10 hover:bg-sky-500 hover:text-white text-white rounded-2xl border border-white/20 transition active:scale-95 group">
          <span class="text-2xl group-hover:scale-110 transition">👍</span>
          <span class="text-[10px] font-bold mt-1">Posible (↑)</span>
        </button>

        <button onclick="handleSwipeAction('favorites')" class="flex flex-col items-center justify-center py-3 px-2 bg-gradient-to-r from-amber-400 to-orange-500 hover:from-amber-500 hover:to-orange-600 text-white rounded-2xl shadow-lg shadow-orange-500/30 transition active:scale-95 group">
          <span class="text-2xl group-hover:scale-110 transition">⭐</span>
          <span class="text-[10px] font-bold mt-1">Favorito (→)</span>
        </button>
      </div>

    </div>
  <!-- GitHub Cloud Sync & Partner Pairing Modal -->
  <div id="githubSyncModal" class="fixed inset-0 bg-neutral-900/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-3 sm:p-4">
    <div class="bg-white rounded-3xl max-w-lg w-full p-5 sm:p-6 shadow-2xl border border-neutral-100 max-h-[90vh] overflow-y-auto custom-scrollbar animate-in fade-in zoom-in-95 duration-150">
      
      <!-- Modal Header -->
      <div class="flex items-center justify-between border-b border-neutral-100 pb-3 mb-4">
        <div class="flex items-center gap-2.5">
          <span class="w-10 h-10 rounded-2xl bg-blue-50 border border-blue-200 text-blue-600 flex items-center justify-center text-xl shadow-2xs">☁️</span>
          <div>
            <h3 class="text-base sm:text-lg font-bold font-display text-neutral-900 leading-tight">Sincronización en GitHub & Pareja</h3>
            <p class="text-[11px] text-neutral-500">Comparte tu progreso con Rob o Ana en tiempo real</p>
          </div>
        </div>
        <button onclick="closeGitHubSyncModal()" class="w-8 h-8 rounded-full bg-neutral-100 hover:bg-neutral-200 text-neutral-500 hover:text-neutral-800 flex items-center justify-center font-bold text-sm transition">✕</button>
      </div>

      <!-- Cloud Status Box -->
      <div class="bg-gradient-to-br from-blue-50/70 via-indigo-50/50 to-purple-50/70 rounded-2xl p-4 border border-blue-100 mb-4">
        <div class="flex items-center justify-between mb-2">
          <span class="text-xs font-bold text-neutral-700 flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            Repositorio GitHub:
          </span>
          <a href="https://github.com/robertodelgador/nombres-bebe" target="_blank" class="text-xs font-mono font-semibold text-blue-600 hover:underline flex items-center gap-1">
            <span>robertodelgador/nombres-bebe</span> ↗
          </a>
        </div>
        <div id="githubSyncDetailBox" class="text-xs text-neutral-600 space-y-1.5 bg-white/70 rounded-xl p-3 border border-white">
          <div class="flex justify-between items-center">
            <span>Última sincronización con GitHub:</span>
            <b id="githubLastSyncTimeText" class="font-mono text-neutral-800">Recién iniciada</b>
          </div>
          <div class="flex justify-between items-center">
            <span>Votos registrados de 👨 Rob:</span>
            <b id="syncRobCountText" class="text-blue-700 font-mono">23</b>
          </div>
          <div class="flex justify-between items-center">
            <span>Votos registrados de 👩 Ana:</span>
            <b id="syncAnaCountText" class="text-pink-700 font-mono">0</b>
          </div>
          <div class="flex justify-between items-center pt-1 border-t border-neutral-100 font-bold text-pink-700">
            <span>💖 Super Matches confirmados:</span>
            <b id="syncSuperMatchCountText" class="font-mono">0</b>
          </div>
        </div>
      </div>

      <!-- Main GitHub Action Buttons -->
      <div class="grid grid-cols-2 gap-2 mb-5">
        <button onclick="saveAndPushToGitHub()" class="flex flex-col items-center justify-center p-3 rounded-2xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-md shadow-blue-200 transition active:scale-95 group">
          <span class="text-xl group-hover:-translate-y-0.5 transition">⬆️</span>
          <span class="text-xs font-bold mt-1">Guardar en GitHub</span>
          <span class="text-[10px] text-blue-100">Sube tus votos al repo</span>
        </button>

        <button onclick="pullLatestFromGitHub(true)" class="flex flex-col items-center justify-center p-3 rounded-2xl bg-white border border-neutral-200 hover:bg-neutral-50 text-neutral-800 shadow-2xs transition active:scale-95 group">
          <span class="text-xl group-hover:rotate-45 transition">⬇️</span>
          <span class="text-xs font-bold mt-1">Descargar de GitHub</span>
          <span class="text-[10px] text-neutral-500">Trae los votos de tu pareja</span>
        </button>
      </div>

      <!-- Quick WhatsApp / Direct Share Section (Zero Token Required) -->
      <div class="p-3.5 bg-emerald-50/70 border border-emerald-200 rounded-2xl mb-4">
        <div class="flex items-center gap-2 mb-1.5">
          <span class="text-base">📲</span>
          <h4 class="text-xs font-bold text-emerald-950 uppercase tracking-wider">Pasar Votos Directo a la Pareja (Sin Token)</h4>
        </div>
        <p class="text-[11px] text-emerald-800 mb-3 leading-relaxed">
          Si tu pareja está usando su celular y no tiene token de GitHub, puede tocar aquí para mandar sus votos por WhatsApp o enlace directo. Al abrirlo, se guardarán en GitHub automáticamente.
        </p>
        <div class="flex gap-2">
          <button onclick="shareVotesViaWhatsApp()" class="flex-1 py-2 px-3 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-700 text-white flex items-center justify-center gap-1.5 shadow-xs transition active:scale-95">
            <span>💬</span>
            <span>Enviar por WhatsApp</span>
          </button>
          <button onclick="copyShareSyncLink()" class="py-2 px-3 rounded-xl text-xs font-bold bg-white text-emerald-800 border border-emerald-300 hover:bg-emerald-100/50 flex items-center gap-1 shadow-2xs transition active:scale-95">
            <span>📋</span>
            <span>Copiar Enlace</span>
          </button>
        </div>
      </div>

      <!-- GitHub Token Configuration Accordion -->
      <details class="group bg-neutral-50 rounded-2xl border border-neutral-200 p-3 mb-4">
        <summary class="flex items-center justify-between cursor-pointer text-xs font-bold text-neutral-700 select-none">
          <span class="flex items-center gap-2">
            <span>🔑</span>
            <span>Configurar Token de GitHub (Opcional para subir directo)</span>
          </span>
          <span class="text-neutral-400 group-open:rotate-180 transition">▼</span>
        </summary>
        <div class="mt-3 pt-3 border-t border-neutral-200/80 space-y-2.5">
          <p class="text-[11px] text-neutral-600 leading-relaxed">
            Para que este navegador pueda escribir directamente en el archivo <code class="bg-neutral-200 px-1 py-0.5 rounded text-[10px]">votes.json</code> del repositorio, introduce un <b>Personal Access Token</b> de GitHub con permisos de escritura (<code class="bg-neutral-200 px-1 py-0.5 rounded text-[10px]">repo</code> o <code class="bg-neutral-200 px-1 py-0.5 rounded text-[10px]">contents:write</code>). Se guardará únicamente en este dispositivo.
          </p>
          <div class="flex gap-2">
            <input type="password" id="githubTokenInput" placeholder="ghp_xxxxxxxxxxxxxxxxxxxx" class="flex-1 px-3 py-2 text-xs font-mono rounded-xl bg-white border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-blue-400">
            <button onclick="saveGitHubToken()" class="px-3.5 py-2 text-xs font-bold bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition">
              Guardar
            </button>
          </div>
          <div class="flex items-center justify-between text-[11px] text-neutral-500 pt-1">
            <a href="https://github.com/settings/tokens/new?scopes=repo&description=Nombres+Chiquitina" target="_blank" class="text-blue-600 hover:underline flex items-center gap-1">
              <span>🔗 Crear token en GitHub (1 clic)</span>
            </a>
            <button onclick="clearGitHubToken()" id="clearTokenBtn" class="text-red-500 hover:underline hidden">
              Borrar token guardado
            </button>
          </div>
        </div>
      </details>

      <!-- Local Backup Buttons -->
      <div class="flex items-center justify-between pt-2 border-t border-neutral-100 text-xs text-neutral-500">
        <button onclick="exportToJSON()" class="hover:text-neutral-800 transition">
          💾 Descargar backup .json
        </button>
        <button onclick="document.getElementById('importFileInput').click(); closeGitHubSyncModal();" class="hover:text-neutral-800 transition">
          📂 Cargar backup .json
        </button>
      </div>

    </div>
  </div>

  <!-- Incoming Sync Prompt Modal -->
  <div id="incomingSyncModal" class="fixed inset-0 bg-neutral-900/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
    <div class="bg-white rounded-3xl max-w-sm w-full p-5 shadow-2xl border border-neutral-100 text-center animate-in fade-in zoom-in-95 duration-150">
      <span class="text-4xl block mb-2">🎉</span>
      <h3 class="text-base font-bold text-neutral-900 mb-1">¡Votos Recibidos de tu Pareja!</h3>
      <p id="incomingSyncMsg" class="text-xs text-neutral-600 mb-4 leading-relaxed">
        Se detectaron votos compartidos. ¿Deseas incorporarlos a tu lista para actualizar los matches?
      </p>
      <div class="flex gap-2">
        <button onclick="rejectIncomingSync()" class="flex-1 py-2 text-xs font-semibold text-neutral-600 hover:bg-neutral-100 rounded-xl transition">
          Ignorar
        </button>
        <button onclick="acceptIncomingSync()" class="flex-1 py-2 text-xs font-bold bg-rose-500 text-white rounded-xl hover:bg-rose-600 shadow-md shadow-rose-200 transition">
          Incorporar Votos
        </button>
      </div>
    </div>
  </div>

  <!-- Toast Notification -->
  <div id="toast" class="fixed bottom-20 sm:bottom-6 right-6 bg-neutral-900 text-white px-4 py-3 rounded-2xl shadow-2xl flex items-center gap-3 text-sm z-50 transition-all duration-300 translate-y-24 opacity-0 pointer-events-none">
    <span id="toastIcon">✨</span>
    <span id="toastMessage">Acción completada</span>
  </div>

  <!-- Embedded Core Logic & Lightweight Persistence Engine -->
  <script>
    // Storage Keys
    const VOTES_STORAGE_KEY = 'chiquitina_user_votes_v2';
    const CUSTOM_NAMES_KEY = 'chiquitina_custom_names_v2';
    const GITHUB_TOKEN_KEY = 'chiquitina_github_token';
    const LAST_GITHUB_SYNC_KEY = 'chiquitina_last_github_sync';

    // GitHub Cloud Repository Config
    const GITHUB_REPO = 'robertodelgador/nombres-bebe';
    const GITHUB_RAW_URL = 'https://raw.githubusercontent.com/robertodelgador/nombres-bebe/main/votes.json';
    const GITHUB_API_URL = 'https://api.github.com/repos/robertodelgador/nombres-bebe/contents/votes.json';

    // App State
    let allNames = [];
    let filteredNames = [];
    let isServerMode = false;
    let currentUser = localStorage.getItem('chiquitina_active_user') || 'rob'; // 'rob' | 'ana' | 'both'
    let currentFilterStatus = 'all'; // 'all' | 'favorites' | 'possible' | 'similar_excluded' | 'excluded' | 'unrated' | 'matches' | 'super_matches'
    let currentVersionFilter = 'all'; // 'all' | 'pdf' | 'new'
    let currentMatchFilter = 'all';
    let currentTypeFilter = 'all';
    let currentOriginFilter = 'all';
    let currentLetterFilter = '';
    let searchQuery = '';
    let currentSort = 'name_asc';
    let viewMode = 'grid'; // 'grid' | 'table'
    let currentPage = 1;
    const pageSize = 48;

    // Cloud Sync State
    let hasUnsavedCloudChanges = false;
    let autoSyncTimer = null;
    let pendingIncomingSync = null;

    // Swipe Mode State
    let swipeDeck = [];
    let swipeIndex = 0;
    let swipeUser = currentUser === 'both' ? 'rob' : currentUser;
    let swipeDeckFilter = 'new_unrated';
    let swipeHistory = [];
    let sessionVoteCounts = { favorites: 0, possible: 0, similar_excluded: 0, excluded: 0 };

    // UTF-8 safe base64 encoding/decoding helpers
    function utf8ToBase64(str) {
      return btoa(unescape(encodeURIComponent(str)));
    }
    function base64ToUtf8(b64) {
      return decodeURIComponent(escape(atob(b64.replace(/\\s/g, ''))));
    }

    // Cloud sync UI indicator dots
    function updateCloudSyncDots(isSynced) {
      const dot1 = document.getElementById('githubSyncStatusDot');
      const dot2 = document.getElementById('mobSyncStatusDot');
      const txt = document.getElementById('swipeSyncStatusText');
      if (isSynced) {
        if (dot1) dot1.className = 'w-2 h-2 rounded-full bg-emerald-500 inline-block';
        if (dot2) dot2.className = 'w-1.5 h-1.5 rounded-full bg-emerald-500';
        if (txt) txt.innerText = 'Al día';
      } else {
        if (dot1) dot1.className = 'w-2 h-2 rounded-full bg-amber-400 inline-block';
        if (dot2) dot2.className = 'w-1.5 h-1.5 rounded-full bg-amber-400';
        if (txt) txt.innerText = 'Pendiente';
      }
    }

    // Modal controls for GitHub sync
    function openGitHubSyncModal() {
      updateGitHubSyncUI();
      const tokenInput = document.getElementById('githubTokenInput');
      const token = localStorage.getItem(GITHUB_TOKEN_KEY) || '';
      if (tokenInput) tokenInput.value = token;
      const clearBtn = document.getElementById('clearTokenBtn');
      if (clearBtn) clearBtn.className = token ? 'text-red-500 hover:underline' : 'hidden';
      document.getElementById('githubSyncModal')?.classList.remove('hidden');
    }

    function closeGitHubSyncModal() {
      document.getElementById('githubSyncModal')?.classList.add('hidden');
    }

    function saveGitHubToken() {
      const token = (document.getElementById('githubTokenInput')?.value || '').trim();
      if (!token) {
        alert("Por favor ingresa un token válido de GitHub.");
        return;
      }
      localStorage.setItem(GITHUB_TOKEN_KEY, token);
      showToast("🔑 Token de GitHub guardado en este dispositivo");
      const clearBtn = document.getElementById('clearTokenBtn');
      if (clearBtn) clearBtn.className = 'text-red-500 hover:underline';
      saveAndPushToGitHub(false);
    }

    function clearGitHubToken() {
      if (confirm("¿Deseas eliminar el token de GitHub guardado en este dispositivo?")) {
        localStorage.removeItem(GITHUB_TOKEN_KEY);
        const tokenInput = document.getElementById('githubTokenInput');
        if (tokenInput) tokenInput.value = '';
        const clearBtn = document.getElementById('clearTokenBtn');
        if (clearBtn) clearBtn.className = 'hidden';
        showToast("Token eliminado");
      }
    }

    function updateGitHubSyncUI() {
      const lastSync = localStorage.getItem(LAST_GITHUB_SYNC_KEY);
      const timeEl = document.getElementById('githubLastSyncTimeText');
      if (timeEl) {
        if (lastSync) {
          const d = new Date(lastSync);
          timeEl.innerText = `${d.toLocaleDateString()} ${d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
        } else {
          timeEl.innerText = "Aún no sincronizado";
        }
      }

      let votes = { rob: {}, ana: {} };
      try {
        votes = JSON.parse(localStorage.getItem(VOTES_STORAGE_KEY) || '{"rob":{},"ana":{}}');
      } catch (e) {}

      const robCount = Object.keys(votes.rob || {}).length;
      const anaCount = Object.keys(votes.ana || {}).length;
      const superMatches = allNames.filter(x => x.rob_status === 'favorites' && x.ana_status === 'favorites').length;

      const robEl = document.getElementById('syncRobCountText');
      const anaEl = document.getElementById('syncAnaCountText');
      const superEl = document.getElementById('syncSuperMatchCountText');
      if (robEl) robEl.innerText = `${robCount} nombres calificados`;
      if (anaEl) anaEl.innerText = `${anaCount} nombres calificados`;
      if (superEl) superEl.innerText = `${superMatches} nombres`;
    }

    // Fetch and merge remote votes from GitHub
    async function fetchVotesFromGitHub(showToastNotice = false) {
      try {
        let res = await fetch(`${GITHUB_RAW_URL}?t=${Date.now()}`);
        if (!res.ok) {
          res = await fetch(GITHUB_API_URL, {
            headers: { 'Accept': 'application/vnd.github.v3.raw' }
          });
        }

        if (res.ok) {
          const remoteData = await res.json();
          const changesDetected = mergeRemoteVotes(remoteData);
          localStorage.setItem(LAST_GITHUB_SYNC_KEY, new Date().toISOString());
          hasUnsavedCloudChanges = false;
          updateCloudSyncDots(true);
          updateGitHubSyncUI();
          if (showToastNotice) {
            showToast("☁️ ¡Votos descargados y sincronizados desde GitHub!", "☁️");
          } else if (changesDetected) {
            showToast("☁️ Nuevos votos de tu pareja recibidos desde GitHub", "💖");
          }
          return true;
        }
      } catch (err) {
        console.warn("Could not fetch votes from GitHub:", err);
      }
      return false;
    }

    // Merge remote votes non-destructively
    function mergeRemoteVotes(remoteData) {
      if (!remoteData) return false;
      let localVotes = { rob: {}, ana: {} };
      try {
        localVotes = JSON.parse(localStorage.getItem(VOTES_STORAGE_KEY) || '{"rob":{},"ana":{}}');
      } catch (e) {}
      if (!localVotes.rob) localVotes.rob = {};
      if (!localVotes.ana) localVotes.ana = {};

      let hasNewData = false;

      if (remoteData.rob) {
        for (const [id, st] of Object.entries(remoteData.rob)) {
          if (!localVotes.rob[id] || localVotes.rob[id] !== st) {
            localVotes.rob[id] = st;
            hasNewData = true;
          }
        }
      }

      if (remoteData.ana) {
        for (const [id, st] of Object.entries(remoteData.ana)) {
          if (!localVotes.ana[id] || localVotes.ana[id] !== st) {
            localVotes.ana[id] = st;
            hasNewData = true;
          }
        }
      }

      // Merge custom names
      if (Array.isArray(remoteData.custom_names) && remoteData.custom_names.length > 0) {
        let localCustom = [];
        try {
          localCustom = JSON.parse(localStorage.getItem(CUSTOM_NAMES_KEY) || '[]');
        } catch (e) {}
        for (const item of remoteData.custom_names) {
          if (!localCustom.some(x => x.id === item.id)) {
            localCustom.push(item);
            hasNewData = true;
          }
        }
        localStorage.setItem(CUSTOM_NAMES_KEY, JSON.stringify(localCustom));
      }

      if (hasNewData) {
        localStorage.setItem(VOTES_STORAGE_KEY, JSON.stringify(localVotes));
        applySavedVotes();
        renderStats();
        applyFilters();
      }
      return hasNewData;
    }

    // Push local votes to GitHub repository
    async function saveAndPushToGitHub(silent = false) {
      // If local server is running, push via server endpoint
      if (isServerMode) {
        if (!silent) showToast("🔄 Sincronizando con GitHub vía servidor local...", "☁️");
        try {
          const resp = await fetch('/api/sync-github', { method: 'POST' });
          const resJson = await resp.json();
          if (resJson.success) {
            localStorage.setItem(LAST_GITHUB_SYNC_KEY, new Date().toISOString());
            hasUnsavedCloudChanges = false;
            updateCloudSyncDots(true);
            updateGitHubSyncUI();
            if (!silent) showToast("✅ " + resJson.message, "✅");
            return true;
          } else {
            if (!silent) showToast("⚠️ " + (resJson.error || resJson.message), "⚠️");
            return false;
          }
        } catch (e) {
          console.warn("Server git push error:", e);
        }
      }

      // Browser GitHub API push using Token
      const token = localStorage.getItem(GITHUB_TOKEN_KEY);
      if (!token) {
        if (!silent) {
          openGitHubSyncModal();
          const det = document.querySelector('#githubSyncModal details');
          if (det) det.open = true;
          document.getElementById('githubTokenInput')?.focus();
          showToast("Ingresa un Token de GitHub para guardar directamente", "🔑");
        }
        return false;
      }

      if (!silent) showToast("☁️ Guardando votos en GitHub...", "☁️");

      try {
        // 1. Fetch current file info for SHA and remote votes
        let sha = null;
        let remoteVotes = { rob: {}, ana: {}, custom_names: [] };

        const getRes = await fetch(GITHUB_API_URL, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Accept': 'application/vnd.github.v3+json'
          }
        });

        if (getRes.ok) {
          const fileInfo = await getRes.json();
          sha = fileInfo.sha;
          if (fileInfo.content) {
            try {
              const decoded = base64ToUtf8(fileInfo.content);
              remoteVotes = JSON.parse(decoded);
            } catch (e) {
              console.warn("Could not parse remote content:", e);
            }
          }
        }

        // 2. Prepare merged data
        let localVotes = { rob: {}, ana: {} };
        try {
          localVotes = JSON.parse(localStorage.getItem(VOTES_STORAGE_KEY) || '{"rob":{},"ana":{}}');
        } catch (e) {}

        let localCustom = [];
        try {
          localCustom = JSON.parse(localStorage.getItem(CUSTOM_NAMES_KEY) || '[]');
        } catch (e) {}

        const mergedPayload = {
          version: 2,
          last_updated: new Date().toISOString(),
          updated_by: currentUser,
          rob: { ...(remoteVotes.rob || {}), ...(localVotes.rob || {}) },
          ana: { ...(remoteVotes.ana || {}), ...(localVotes.ana || {}) },
          custom_names: [
            ...(remoteVotes.custom_names || []),
            ...localCustom.filter(c => !(remoteVotes.custom_names || []).some(r => r.id === c.id))
          ]
        };

        const jsonStr = JSON.stringify(mergedPayload, null, 2);
        const encodedContent = utf8ToBase64(jsonStr);

        const putBody = {
          message: `Actualización de votos (${currentUser === 'rob' ? 'Rob' : (currentUser === 'ana' ? 'Ana' : 'Ambos')}) vía Chiquitina Web`,
          content: encodedContent
        };
        if (sha) putBody.sha = sha;

        const putRes = await fetch(GITHUB_API_URL, {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
            'Accept': 'application/vnd.github.v3+json'
          },
          body: JSON.stringify(putBody)
        });

        if (putRes.ok) {
          localStorage.setItem(LAST_GITHUB_SYNC_KEY, new Date().toISOString());
          hasUnsavedCloudChanges = false;
          updateCloudSyncDots(true);
          updateGitHubSyncUI();
          if (!silent) showToast("✅ ¡Votos guardados en GitHub con éxito!", "✅");
          return true;
        } else {
          const errData = await putRes.json().catch(() => ({}));
          console.error("GitHub API error:", errData);
          if (!silent) showToast(`❌ Error GitHub: ${errData.message || 'Verifica tu token'}`, "❌");
          return false;
        }
      } catch (err) {
        console.error("Push to GitHub failed:", err);
        if (!silent) showToast("❌ Error de conexión al guardar en GitHub", "❌");
        return false;
      }
    }

    // Pull Latest from GitHub
    async function pullLatestFromGitHub(notify = true) {
      await fetchVotesFromGitHub(notify);
    }

    // Auto sync debouncer
    function scheduleGitHubAutoSync() {
      if (autoSyncTimer) clearTimeout(autoSyncTimer);
      autoSyncTimer = setTimeout(() => {
        const token = localStorage.getItem(GITHUB_TOKEN_KEY);
        if (token || isServerMode) {
          saveAndPushToGitHub(true);
        }
      }, 4000);
    }

    // Direct WhatsApp and Share Link Generator
    function getSyncPayloadForPartner() {
      let votes = { rob: {}, ana: {} };
      try {
        votes = JSON.parse(localStorage.getItem(VOTES_STORAGE_KEY) || '{"rob":{},"ana":{}}');
      } catch (e) {}

      const userVotes = currentUser === 'ana' ? (votes.ana || {}) : (votes.rob || {});
      const payload = {
        u: currentUser === 'ana' ? 'ana' : 'rob',
        v: userVotes,
        t: Date.now()
      };
      return utf8ToBase64(JSON.stringify(payload));
    }

    function shareVotesViaWhatsApp() {
      const b64 = getSyncPayloadForPartner();
      const currentUrl = window.location.origin + window.location.pathname;
      const shareUrl = `${currentUrl}#sync=${b64}`;
      const partner = currentUser === 'ana' ? 'Rob' : 'Ana';

      let votes = {};
      try { votes = JSON.parse(localStorage.getItem(VOTES_STORAGE_KEY) || '{}'); } catch (e) {}
      const count = Object.keys((currentUser === 'ana' ? votes.ana : votes.rob) || {}).length;

      const text = `¡Hola ${partner}! 👶 Ya clasifiqué ${count} nombres para Chiquitina. Abre este enlace en tu celular para ver mis elecciones y nuestros Super Matches: ${shareUrl}`;
      window.open(`https://api.whatsapp.com/send?text=${encodeURIComponent(text)}`, '_blank');
      showToast("💬 Abriendo WhatsApp para compartir...", "📲");
    }

    function copyShareSyncLink() {
      const b64 = getSyncPayloadForPartner();
      const currentUrl = window.location.origin + window.location.pathname;
      const shareUrl = `${currentUrl}#sync=${b64}`;

      navigator.clipboard.writeText(shareUrl).then(() => {
        showToast("📋 ¡Enlace copiado! Pégalo en WhatsApp o compárteselo a tu pareja", "📋");
      }).catch(() => {
        prompt("Copia este enlace de sincronización:", shareUrl);
      });
    }

    // Incoming URL sync handlers
    function checkIncomingSync() {
      const hash = window.location.hash;
      if (hash && hash.startsWith('#sync=')) {
        const b64 = hash.replace('#sync=', '');
        try {
          const jsonStr = base64ToUtf8(b64);
          const payload = JSON.parse(jsonStr);
          if (payload && payload.v) {
            pendingIncomingSync = payload;
            const sender = payload.u === 'ana' ? '👩 Ana' : '👨 Rob';
            const count = Object.keys(payload.v).length;
            const msgEl = document.getElementById('incomingSyncMsg');
            if (msgEl) {
              msgEl.innerText = `Se recibieron ${count} nombres calificados de ${sender}. ¿Deseas incorporarlos a tu lista para actualizar los matches y guardarlos en GitHub?`;
            }
            document.getElementById('incomingSyncModal')?.classList.remove('hidden');
          }
        } catch (e) {
          console.error("Error reading incoming sync hash:", e);
        }
      }
    }

    function acceptIncomingSync() {
      if (!pendingIncomingSync) return;
      const sender = pendingIncomingSync.u;
      const votes = pendingIncomingSync.v;

      let localVotes = { rob: {}, ana: {} };
      try {
        localVotes = JSON.parse(localStorage.getItem(VOTES_STORAGE_KEY) || '{"rob":{},"ana":{}}');
      } catch (e) {}
      if (!localVotes.rob) localVotes.rob = {};
      if (!localVotes.ana) localVotes.ana = {};

      if (sender === 'ana') {
        localVotes.ana = { ...(localVotes.ana || {}), ...votes };
      } else {
        localVotes.rob = { ...(localVotes.rob || {}), ...votes };
      }

      localStorage.setItem(VOTES_STORAGE_KEY, JSON.stringify(localVotes));
      applySavedVotes();
      renderStats();
      applyFilters();

      document.getElementById('incomingSyncModal')?.classList.add('hidden');
      window.history.replaceState(null, null, window.location.pathname);
      showToast(`🎉 ¡Votos de ${sender === 'ana' ? 'Ana' : 'Rob'} incorporados con éxito!`, "💖");

      // Auto push to GitHub if token or server available
      saveAndPushToGitHub(true);
      pendingIncomingSync = null;
    }

    function rejectIncomingSync() {
      document.getElementById('incomingSyncModal')?.classList.add('hidden');
      window.history.replaceState(null, null, window.location.pathname);
      pendingIncomingSync = null;
    }

    // Color mapper for origins
    const originColors = {
      'español': { bg: 'bg-rose-50', text: 'text-rose-700', border: 'border-rose-200' },
      'latino': { bg: 'bg-purple-50', text: 'text-purple-700', border: 'border-purple-200' },
      'griego': { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200' },
      'hebreo': { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200' },
      'italiano': { bg: 'bg-amber-50', text: 'text-amber-800', border: 'border-amber-200' },
      'francés': { bg: 'bg-indigo-50', text: 'text-indigo-700', border: 'border-indigo-200' },
      'germánico': { bg: 'bg-stone-100', text: 'text-stone-700', border: 'border-stone-200' },
      'árabe': { bg: 'bg-teal-50', text: 'text-teal-700', border: 'border-teal-200' },
      'vasco': { bg: 'bg-lime-50', text: 'text-lime-800', border: 'border-lime-200' }
    };

    function getOriginColor(originStr) {
      if (!originStr) return { bg: 'bg-neutral-100', text: 'text-neutral-700', border: 'border-neutral-200' };
      const low = originStr.toLowerCase();
      for (const [key, val] of Object.entries(originColors)) {
        if (low.includes(key)) return val;
      }
      return { bg: 'bg-neutral-100', text: 'text-neutral-700', border: 'border-neutral-200' };
    }

    // Initialize App
    window.addEventListener('DOMContentLoaded', async () => {
      // 1. Load embedded baseline data
      const embeddedScript = document.getElementById('embeddedNamesData');
      if (embeddedScript) {
        try {
          allNames = JSON.parse(embeddedScript.textContent);
        } catch (e) {
          console.error("Error parsing embedded data:", e);
        }
      }

      // 2. Overlay permanently stored user votes from localStorage (Lightning fast & lightweight)
      applySavedVotes();

      // 3. Check for incoming sync via URL (#sync=...)
      checkIncomingSync();

      buildAlphabetBar();
      await checkServerConnection();
      updateUserUI();
      renderStats();
      populateOriginDropdown();
      applyFilters();
      setupKeyboardListeners();
      setupSwipeGestures();

      // 4. Fetch latest shared votes from GitHub repository (keeps Rob & Ana in sync across sessions)
      await fetchVotesFromGitHub(false);

      // 5. Setup auto-sync when returning to tab
      document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible') {
          fetchVotesFromGitHub(false);
        }
      });
    });

    // Alphabet bar builder
    function buildAlphabetBar() {
      const container = document.getElementById('alphabetContainer');
      const alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");
      container.innerHTML = alphabet.map(letter => `
        <button onclick="setLetterFilter('${letter}')" id="letter_${letter}" class="w-8 h-8 rounded-lg text-xs font-semibold text-neutral-600 hover:bg-neutral-200 hover:text-neutral-900 transition flex items-center justify-center">
          ${letter}
        </button>
      `).join('');
    }

    // Save vote to lightweight store (< 50 KB, never overflows localStorage)
    function saveVoteLocally(id, status, user) {
      try {
        let votes = {};
        try {
          votes = JSON.parse(localStorage.getItem(VOTES_STORAGE_KEY) || '{"rob":{},"ana":{}}');
        } catch (e) { votes = { rob: {}, ana: {} }; }

        if (!votes.rob) votes.rob = {};
        if (!votes.ana) votes.ana = {};

        if (user === 'rob') {
          votes.rob[id] = status;
        } else if (user === 'ana') {
          votes.ana[id] = status;
        }
        localStorage.setItem(VOTES_STORAGE_KEY, JSON.stringify(votes));
        hasUnsavedCloudChanges = true;
        updateCloudSyncDots(false);
        scheduleGitHubAutoSync();
      } catch (err) {
        console.error("Failed to save vote locally:", err);
      }
    }

    // Apply saved votes from localStorage onto allNames
    function applySavedVotes() {
      try {
        // 1. Add custom user-added names if any
        const customNames = JSON.parse(localStorage.getItem(CUSTOM_NAMES_KEY) || '[]');
        if (Array.isArray(customNames) && customNames.length > 0) {
          for (const customItem of customNames) {
            if (!allNames.some(x => x.id === customItem.id)) {
              allNames.unshift(customItem);
            }
          }
        }

        // 2. Overlay votes
        const votes = JSON.parse(localStorage.getItem(VOTES_STORAGE_KEY) || '{"rob":{},"ana":{}}');
        if (votes.rob) {
          for (const [id, st] of Object.entries(votes.rob)) {
            const item = allNames.find(x => x.id === id);
            if (item) item.rob_status = st;
          }
        }
        if (votes.ana) {
          for (const [id, st] of Object.entries(votes.ana)) {
            const item = allNames.find(x => x.id === id);
            if (item) item.ana_status = st;
          }
        }

        // 3. Recompute consensus status
        for (const item of allNames) {
          const r = item.rob_status || 'unrated';
          const a = item.ana_status || 'unrated';
          if (r === 'favorites' && a === 'favorites') item.status = 'favorites';
          else if (r === 'favorites' || a === 'favorites') item.status = 'favorites';
          else if (r === 'possible' || a === 'possible') item.status = 'possible';
          else if (r === 'similar_excluded' || a === 'similar_excluded') item.status = 'similar_excluded';
          else if (r === 'excluded' && a === 'excluded') item.status = 'excluded';
          else if (r !== 'unrated') item.status = r;
          else if (a !== 'unrated') item.status = a;
          else item.status = 'unrated';
        }
      } catch (err) {
        console.error("Error applying saved votes:", err);
      }
    }

    // Check if local server is running (Optional enhancement for local dev)
    async function checkServerConnection() {
      const badge = document.getElementById('storageStatusBadge');
      const text = document.getElementById('storageStatusText');
      try {
        const resp = await fetch('/api/stats');
        if (resp.ok) {
          isServerMode = true;
          if (badge) badge.className = 'hidden sm:inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200';
          if (text) text.innerText = 'Servidor + Nube Sincronizados';
        }
      } catch (e) {
        // GitHub Pages mode (pure client-side with persistent localStorage)
        isServerMode = false;
        if (badge) badge.className = 'hidden sm:inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-purple-50 text-purple-700 border border-purple-200';
        if (text) text.innerText = 'Memoria Local Persistente';
      }
    }

    // Save Name Change
    async function saveNameChange(item, user = currentUser) {
      const targetUser = user === 'both' ? 'rob' : user;
      const newSt = targetUser === 'rob' ? item.rob_status : item.ana_status;

      // 1. Immediately store vote in lightweight permanent storage
      saveVoteLocally(item.id, newSt, targetUser);

      // 2. If local python server is running, also push to backend
      if (isServerMode) {
        try {
          await fetch(`/api/names/${item.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              rob_status: item.rob_status,
              ana_status: item.ana_status,
              status: item.status
            })
          });
        } catch (e) {
          console.warn("Server sync skipped");
        }
      }

      renderStats();
    }

    // User Switching Logic (Rob / Ana / Ambos)
    function switchUser(newUser) {
      currentUser = newUser;
      try {
        localStorage.setItem('chiquitina_active_user', currentUser);
      } catch (e) {}

      swipeUser = currentUser === 'both' ? 'rob' : currentUser;
      updateUserUI();
      renderStats();
      applyFilters();
      showToast(`Modo cambiado a: ${currentUser === 'rob' ? '👨 Rob' : (currentUser === 'ana' ? '👩 Ana' : '💖 Ambos / Matches')}`);
    }

    function updateUserUI() {
      const isRob = currentUser === 'rob';
      const isAna = currentUser === 'ana';
      const isBoth = currentUser === 'both';

      // Desktop Header Buttons
      const btnRob = document.getElementById('userSwitch_rob');
      const btnAna = document.getElementById('userSwitch_ana');
      const btnBoth = document.getElementById('userSwitch_both');

      if (btnRob) btnRob.className = `px-3.5 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 ${isRob ? 'bg-blue-600 text-white shadow-xs' : 'text-neutral-600 hover:text-neutral-900'}`;
      if (btnAna) btnAna.className = `px-3.5 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 ${isAna ? 'bg-pink-600 text-white shadow-xs' : 'text-neutral-600 hover:text-neutral-900'}`;
      if (btnBoth) btnBoth.className = `px-3.5 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 ${isBoth ? 'bg-gradient-to-r from-pink-600 to-amber-600 text-white shadow-xs' : 'text-neutral-600 hover:text-neutral-900'}`;

      // Mobile Buttons
      const mobRob = document.getElementById('mobUserSwitch_rob');
      const mobAna = document.getElementById('mobUserSwitch_ana');
      const mobBoth = document.getElementById('mobUserSwitch_both');

      if (mobRob) mobRob.className = `px-2.5 py-1 rounded-lg text-xs font-bold transition flex items-center gap-1 ${isRob ? 'bg-blue-600 text-white' : 'text-neutral-600'}`;
      if (mobAna) mobAna.className = `px-2.5 py-1 rounded-lg text-xs font-bold transition flex items-center gap-1 ${isAna ? 'bg-pink-600 text-white' : 'text-neutral-600'}`;
      if (mobBoth) mobBoth.className = `px-2.5 py-1 rounded-lg text-xs font-bold transition flex items-center gap-1 ${isBoth ? 'bg-pink-600 text-white' : 'text-neutral-600'}`;

      // Mobile Dock
      const dockIcon = document.getElementById('dockUserIcon');
      const dockLabel = document.getElementById('dockUserLabel');
      if (dockIcon) dockIcon.innerText = isRob ? '👨' : (isAna ? '👩' : '💖');
      if (dockLabel) dockLabel.innerText = isRob ? 'Rob' : (isAna ? 'Ana' : 'Ambos');

      // Banner UI
      const banner = document.getElementById('userPerspectiveBanner');
      const avatarPill = document.getElementById('userAvatarPill');
      const title = document.getElementById('userGreetingTitle');
      const tag = document.getElementById('userStatusTag');
      const sub = document.getElementById('userGreetingSubtitle');
      const toggleLabel = document.getElementById('toggleUserBtnLabel');

      if (isRob) {
        if (banner) banner.className = 'bg-gradient-to-r from-blue-50 via-indigo-50/40 to-sky-50 rounded-3xl p-4 sm:p-5 border border-blue-200 shadow-2xs mb-6';
        if (avatarPill) { avatarPill.innerText = '👨'; avatarPill.className = 'w-12 h-12 rounded-2xl bg-blue-600 text-white flex items-center justify-center text-2xl shadow-sm shrink-0'; }
        if (title) title.innerText = 'Panel de Preferencias de Rob';
        if (tag) { tag.innerText = 'Modo Activo: Rob'; tag.className = 'text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-blue-100 text-blue-800 border border-blue-200'; }
        if (sub) sub.innerText = 'Tienes 2,500 nombres hispanos nuevos por clasificar. ¡Tus decisiones se guardan al instante!';
        if (toggleLabel) toggleLabel.innerText = 'Cambiar a Ana';
      } else if (isAna) {
        if (banner) banner.className = 'bg-gradient-to-r from-pink-50 via-rose-50/40 to-amber-50 rounded-3xl p-4 sm:p-5 border border-pink-200 shadow-2xs mb-6';
        if (avatarPill) { avatarPill.innerText = '👩'; avatarPill.className = 'w-12 h-12 rounded-2xl bg-pink-600 text-white flex items-center justify-center text-2xl shadow-sm shrink-0'; }
        if (title) title.innerText = 'Panel de Preferencias de Ana';
        if (tag) { tag.innerText = 'Modo Activo: Ana'; tag.className = 'text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-pink-100 text-pink-800 border border-pink-200'; }
        if (sub) sub.innerText = '¡Hola Ana! Puedes calificar libremente todos los nombres en modo Swipe. Cuando coincidas con Rob, se creará un Super Match.';
        if (toggleLabel) toggleLabel.innerText = 'Cambiar a Rob';
      } else {
        if (banner) banner.className = 'bg-gradient-to-r from-pink-50 via-purple-50/40 to-amber-50 rounded-3xl p-4 sm:p-5 border border-purple-200 shadow-2xs mb-6';
        if (avatarPill) { avatarPill.innerText = '💖'; avatarPill.className = 'w-12 h-12 rounded-2xl bg-gradient-to-tr from-pink-500 to-amber-500 text-white flex items-center justify-center text-2xl shadow-sm shrink-0'; }
        if (title) title.innerText = 'Comparador de Pareja: Rob & Ana';
        if (tag) { tag.innerText = 'Modo: Ambos / Coincidencias'; tag.className = 'text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-pink-100 text-pink-800 border border-pink-200'; }
        if (sub) sub.innerText = 'Comparando las opiniones de ambos. Los nombres con Super Match o Coincidencia se destacan con orgullo.';
        if (toggleLabel) toggleLabel.innerText = 'Votar como Rob';
      }

      // Add modal person label
      const addPerson = document.getElementById('addPersonNameLabel');
      if (addPerson) addPerson.innerText = isAna ? 'Ana' : 'Rob';
    }

    // Match Calculation Helper
    function getMatchInfo(item) {
      const rob = item.rob_status || 'unrated';
      const ana = item.ana_status || 'unrated';

      const robFav = rob === 'favorites';
      const anaFav = ana === 'favorites';
      const robPos = rob === 'favorites' || rob === 'possible';
      const anaPos = ana === 'favorites' || ana === 'possible';
      const robNeg = rob === 'excluded' || rob === 'similar_excluded';
      const anaNeg = ana === 'excluded' || ana === 'similar_excluded';

      if (robFav && anaFav) {
        return {
          type: 'super_match',
          badge: `<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold badge-super-match">💖 ¡SUPER MATCH! (Rob & Ana ⭐⭐)</span>`,
          pill: `<span class="inline-flex items-center gap-1 text-[11px] font-bold text-pink-700 bg-pink-50 border border-pink-200 px-2 py-0.5 rounded-lg">💖 Super Match</span>`
        };
      }
      if (robPos && anaPos) {
        return {
          type: 'match',
          badge: `<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold badge-match">💚 ¡COINCIDENCIA! (Aprobado por ambos)</span>`,
          pill: `<span class="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-lg">💚 Coincidencia</span>`
        };
      }
      if ((robPos && anaNeg) || (anaPos && robNeg)) {
        return {
          type: 'conflict',
          badge: `<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-purple-100 text-purple-800 border border-purple-300">⚡ En Debate (Opiniones encontradas)</span>`,
          pill: `<span class="inline-flex items-center gap-1 text-[11px] font-medium text-purple-700 bg-purple-50 border border-purple-200 px-2 py-0.5 rounded-lg">⚡ En Debate</span>`
        };
      }
      if (rob === 'unrated' || ana === 'unrated') {
        const pendingWho = (rob === 'unrated' && ana === 'unrated') ? 'Ambos' : (rob === 'unrated' ? 'Rob' : 'Ana');
        return {
          type: 'pending',
          badge: `<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium bg-neutral-100 text-neutral-600 border border-neutral-200">⏳ Falta voto de ${pendingWho}</span>`,
          pill: `<span class="inline-flex items-center gap-1 text-[10px] text-neutral-500 bg-neutral-100 px-1.5 py-0.5 rounded-md">⏳ Pendiente (${pendingWho})</span>`
        };
      }
      return {
        type: 'none',
        badge: '',
        pill: `<span class="text-[10px] text-neutral-400">Sin coincidencia</span>`
      };
    }

    // Get User Status Helper
    function getUserStatus(item, user = currentUser) {
      if (user === 'rob') return item.rob_status || 'unrated';
      if (user === 'ana') return item.ana_status || 'unrated';
      if (item.rob_status === 'favorites' && item.ana_status === 'favorites') return 'favorites';
      if (item.rob_status === 'favorites' || item.ana_status === 'favorites') return 'favorites';
      if (item.rob_status === 'possible' || item.ana_status === 'possible') return 'possible';
      if (item.rob_status === 'similar_excluded' || item.ana_status === 'similar_excluded') return 'similar_excluded';
      return item.rob_status || 'unrated';
    }

    // Set Person Vote (1-Tap Fast Action)
    async function setPersonVote(id, newStatus, targetPerson = null) {
      const person = targetPerson || (currentUser === 'both' ? 'rob' : currentUser);
      const item = allNames.find(x => x.id === id);
      if (!item) return;

      if (person === 'rob') {
        item.rob_status = newStatus;
      } else if (person === 'ana') {
        item.ana_status = newStatus;
      }

      // Update consensus status
      if (item.rob_status === 'favorites' && item.ana_status === 'favorites') {
        item.status = 'favorites';
      } else if (item.rob_status === 'favorites' || item.ana_status === 'favorites') {
        item.status = 'favorites';
      } else if (item.rob_status === 'possible' || item.ana_status === 'possible') {
        item.status = 'possible';
      } else if (item.rob_status === 'similar_excluded' || item.ana_status === 'similar_excluded') {
        item.status = 'similar_excluded';
      } else {
        item.status = newStatus;
      }

      await saveNameChange(item, person);

      // Check for Super Match celebration!
      if (item.rob_status === 'favorites' && item.ana_status === 'favorites') {
        showToast(`💖 ¡SUPER MATCH! A Rob y a Ana les fascina "${item.name}"`, '💖');
      } else {
        const labels = { favorites: '⭐ Favorito', possible: '👍 Posible', similar_excluded: '⚠️ En Duda', excluded: '❌ Excluido' };
        showToast(`${person === 'rob' ? '👨 Rob' : '👩 Ana'} marcó "${item.name}" como ${labels[newStatus] || newStatus}`);
      }

      renderStats();
      applyFilters();
    }

    // Copy Rob preferences to Ana
    async function copyRobPreferencesToAna() {
      if (!confirm("¿Deseas copiar todas las preferencias actuales de Rob hacia Ana? Esto dará a Ana el mismo punto de partida.")) {
        return;
      }
      allNames.forEach(x => {
        x.ana_status = x.rob_status || 'unrated';
        saveVoteLocally(x.id, x.ana_status, 'ana');
      });

      renderStats();
      applyFilters();
      showToast("📋 ¡Preferencias de Rob copiadas a Ana con éxito!");
    }

    function getStatusBadgeHTML(status) {
      if (status === 'favorites') {
        return `<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold badge-fav">⭐ Favorito</span>`;
      } else if (status === 'possible') {
        return `<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold badge-pos">👍 Posible</span>`;
      } else if (status === 'similar_excluded') {
        return `<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold badge-sim">⚠️ En Duda</span>`;
      } else if (status === 'excluded') {
        return `<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold badge-exc">❌ Excluido</span>`;
      } else {
        return `<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-bold badge-unrated animate-pulse">⏳ Por clasificar</span>`;
      }
    }

    function getVersionBadgeHTML(item) {
      if (item.source && item.source.includes('PDF')) {
        return `<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-50 text-amber-900 border border-amber-200" title="Lista original del PDF v1.0">📜 v1.0 PDF</span>`;
      } else if (item.is_new || (item.source && (item.source.includes('500') || item.source.includes('2000')))) {
        return `<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-purple-50 text-purple-800 border border-purple-200" title="Nuevos nombres hispanos y latinos">✨ Nuevo Hispano</span>`;
      } else {
        return `<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-800 border border-emerald-200" title="Añadido manualmente">➕ Añadido</span>`;
      }
    }

    // Render Metrics (Respects currentUser & version filter)
    function renderStats() {
      let scopedNames = allNames;
      if (currentVersionFilter === 'pdf') {
        scopedNames = allNames.filter(x => x.source && x.source.includes('PDF'));
      } else if (currentVersionFilter === 'new') {
        scopedNames = allNames.filter(x => !x.source || !x.source.includes('PDF'));
      }

      // Stats for Rob
      const robFavs = scopedNames.filter(x => x.rob_status === 'favorites').length;
      const robPoss = scopedNames.filter(x => x.rob_status === 'possible').length;
      const robSims = scopedNames.filter(x => x.rob_status === 'similar_excluded').length;
      const robExcl = scopedNames.filter(x => x.rob_status === 'excluded').length;
      const robUnrated = scopedNames.filter(x => !x.rob_status || x.rob_status === 'unrated').length;

      // Stats for Ana
      const anaFavs = scopedNames.filter(x => x.ana_status === 'favorites').length;
      const anaPoss = scopedNames.filter(x => x.ana_status === 'possible').length;
      const anaSims = scopedNames.filter(x => x.ana_status === 'similar_excluded').length;
      const anaExcl = scopedNames.filter(x => x.ana_status === 'excluded').length;
      const anaUnrated = scopedNames.filter(x => !x.ana_status || x.ana_status === 'unrated').length;

      // Super Matches and Mutual Positive Matches
      const superMatches = scopedNames.filter(x => x.rob_status === 'favorites' && x.ana_status === 'favorites').length;
      const allMatches = scopedNames.filter(x => {
        const rPos = x.rob_status === 'favorites' || x.rob_status === 'possible';
        const aPos = x.ana_status === 'favorites' || x.ana_status === 'possible';
        return rPos && aPos;
      }).length;

      // Update Header Badges
      const hRob = document.getElementById('headerRobFavBadge');
      const hAna = document.getElementById('headerAnaFavBadge');
      const hBoth = document.getElementById('headerBothMatchBadge');
      if (hRob) hRob.innerText = robFavs;
      if (hAna) hAna.innerText = anaFavs;
      if (hBoth) hBoth.innerText = superMatches;

      const smTag = document.getElementById('superMatchCountTag');
      if (smTag) smTag.innerText = `${superMatches} Super Matches`;

      // Update Active Perspective Metrics
      let curFavs = robFavs, curPoss = robPoss, curSims = robSims, curExcl = robExcl, curUnrated = robUnrated;
      let userName = 'Rob';

      if (currentUser === 'ana') {
        curFavs = anaFavs; curPoss = anaPoss; curSims = anaSims; curExcl = anaExcl; curUnrated = anaUnrated;
        userName = 'Ana';
      } else if (currentUser === 'both') {
        curFavs = superMatches; curPoss = allMatches; curSims = robSims + anaSims; curExcl = robExcl; curUnrated = anaUnrated;
        userName = 'Ambos';
      }

      document.getElementById('metricTotal').innerText = scopedNames.length.toLocaleString();
      document.getElementById('metricUnrated').innerText = curUnrated.toLocaleString();
      document.getElementById('metricFavorites').innerText = curFavs.toLocaleString();
      document.getElementById('metricPossible').innerText = curPoss.toLocaleString();
      document.getElementById('metricExcluded').innerText = curExcl.toLocaleString();

      // Tab Counts
      document.getElementById('tabCountAll').innerText = `(${scopedNames.length})`;
      document.getElementById('tabCountUnrated').innerText = `(${curUnrated})`;
      document.getElementById('tabCountSuperMatches').innerText = `(${superMatches})`;
      document.getElementById('tabCountMatches').innerText = `(${allMatches})`;
      document.getElementById('tabCountFavorites').innerText = `(${curFavs})`;
      document.getElementById('tabCountPossible').innerText = `(${curPoss})`;
      document.getElementById('tabCountSimilar').innerText = `(${curSims})`;
      document.getElementById('tabCountExcluded').innerText = `(${curExcl})`;

      // Version badges
      const pdfCount = allNames.filter(x => x.source && x.source.includes('PDF')).length;
      const newCount = allNames.filter(x => !x.source || !x.source.includes('PDF')).length;
      const bPdf = document.getElementById('verBadgePdf');
      const bNew = document.getElementById('verBadgeNew');
      const bAll = document.getElementById('verBadgeAll');
      if (bPdf) bPdf.innerText = pdfCount.toLocaleString();
      if (bNew) bNew.innerText = newCount.toLocaleString();
      if (bAll) bAll.innerText = allNames.length.toLocaleString();
    }

    // Version Filter Handler
    function setVersionFilter(ver) {
      currentVersionFilter = ver;
      currentPage = 1;

      ['all', 'pdf', 'new'].forEach(v => {
        const btn = document.getElementById(`verBtn_${v}`);
        if (!btn) return;
        if (v === ver) {
          btn.className = 'px-3 py-2 rounded-xl text-xs sm:text-sm font-semibold transition flex items-center gap-2 bg-white text-neutral-900 shadow-sm border border-neutral-200/60';
        } else {
          btn.className = 'px-3 py-2 rounded-xl text-xs sm:text-sm font-semibold transition flex items-center gap-2 text-neutral-600 hover:text-neutral-900';
        }
      });

      const tag = document.getElementById('activeVersionTag');
      const desc = document.getElementById('activeVersionDescription');

      if (ver === 'pdf') {
        if (tag) {
          tag.innerText = 'Versión 1.0 (PDF Original)';
          tag.className = 'text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-amber-100 text-amber-900 border border-amber-200';
        }
        if (desc) desc.innerText = 'Mostrando únicamente los 1,172 nombres originales del documento PDF (23 favoritos, 58 posibles, 1,091 excluidos).';
      } else if (ver === 'new') {
        if (tag) {
          tag.innerText = 'Nuevos Nombres Añadidos (+2,500)';
          tag.className = 'text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-purple-100 text-purple-900 border border-purple-200';
        }
        if (desc) desc.innerText = 'Mostrando los 2,500 nuevos nombres femeninos de origen hispano y latino pendientes de clasificar por ustedes.';
      } else {
        if (tag) {
          tag.innerText = 'Todo el Catálogo (3,672)';
          tag.className = 'text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-rose-100 text-rose-800 border border-rose-200';
        }
        if (desc) desc.innerText = '1,172 nombres del PDF v1.0 original ya clasificados + 2,500 nuevos nombres hispanos y latinos por descubrir.';
      }

      renderStats();
      applyFilters();
    }

    // Populate Origins dropdown
    function populateOriginDropdown() {
      const originsMap = {};
      allNames.forEach(x => {
        const o = (x.origin || 'Desconocido').trim();
        originsMap[o] = (originsMap[o] || 0) + 1;
      });

      const select = document.getElementById('originFilter');
      const sorted = Object.entries(originsMap).sort((a, b) => b[1] - a[1]);
      
      select.innerHTML = '<option value="all">Todas las etimologías (' + allNames.length + ')</option>' +
        sorted.map(([orig, count]) => `<option value="${orig}">${orig} (${count})</option>`).join('');
    }

    // Status Filter Handler
    function setStatusFilter(status) {
      currentFilterStatus = status;
      currentPage = 1;

      const tabs = ['all', 'unrated', 'super_matches', 'matches', 'favorites', 'possible', 'similar_excluded', 'excluded'];
      tabs.forEach(st => {
        const btn = document.getElementById(`tab_${st}`);
        if (!btn) return;
        if (st === status) {
          if (st === 'unrated') {
            btn.className = 'px-3 py-1.5 rounded-xl text-xs sm:text-sm font-bold bg-amber-500 text-white shadow-sm transition shrink-0';
          } else if (st === 'super_matches') {
            btn.className = 'px-3 py-1.5 rounded-xl text-xs sm:text-sm font-bold bg-pink-600 text-white shadow-sm transition shrink-0';
          } else if (st === 'matches') {
            btn.className = 'px-3 py-1.5 rounded-xl text-xs sm:text-sm font-bold bg-emerald-600 text-white shadow-sm transition shrink-0';
          } else if (st === 'favorites') {
            btn.className = 'px-3 py-1.5 rounded-xl text-xs sm:text-sm font-bold bg-rose-500 text-white shadow-sm transition shrink-0';
          } else if (st === 'possible') {
            btn.className = 'px-3 py-1.5 rounded-xl text-xs sm:text-sm font-bold bg-sky-600 text-white shadow-sm transition shrink-0';
          } else if (st === 'similar_excluded') {
            btn.className = 'px-3 py-1.5 rounded-xl text-xs sm:text-sm font-bold bg-orange-600 text-white shadow-sm transition shrink-0';
          } else {
            btn.className = 'px-3 py-1.5 rounded-xl text-xs sm:text-sm font-semibold bg-neutral-900 text-white transition shrink-0';
          }
        } else {
          if (st === 'unrated') {
            btn.className = 'px-3 py-1.5 rounded-xl text-xs sm:text-sm font-bold bg-amber-50 text-amber-800 border border-amber-300 hover:bg-amber-100 transition shrink-0';
          } else if (st === 'super_matches') {
            btn.className = 'px-3 py-1.5 rounded-xl text-xs sm:text-sm font-bold bg-pink-50 text-pink-700 border border-pink-200 hover:bg-pink-100 transition shrink-0';
          } else if (st === 'matches') {
            btn.className = 'px-3 py-1.5 rounded-xl text-xs sm:text-sm font-bold bg-emerald-50 text-emerald-800 border border-emerald-200 hover:bg-emerald-100 transition shrink-0';
          } else if (st === 'similar_excluded') {
            btn.className = 'px-3 py-1.5 rounded-xl text-xs sm:text-sm font-semibold bg-orange-50 text-orange-800 border border-orange-200 hover:bg-orange-100 transition shrink-0';
          } else {
            btn.className = 'px-3 py-1.5 rounded-xl text-xs sm:text-sm font-semibold bg-neutral-100 text-neutral-600 hover:bg-neutral-200 transition shrink-0';
          }
        }
      });

      applyFilters();
    }

    function setLetterFilter(letter) {
      currentLetterFilter = letter;
      currentPage = 1;

      document.getElementById('letter_ALL').className = letter === '' 
        ? 'px-2.5 py-1 rounded-lg text-xs font-bold bg-rose-500 text-white shrink-0'
        : 'px-2.5 py-1 rounded-lg text-xs font-bold bg-neutral-100 text-neutral-600 hover:bg-neutral-200 shrink-0';

      "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("").forEach(l => {
        const el = document.getElementById(`letter_${l}`);
        if (el) {
          el.className = l === letter 
            ? 'w-8 h-8 rounded-lg text-xs font-bold bg-rose-500 text-white shadow-sm flex items-center justify-center'
            : 'w-8 h-8 rounded-lg text-xs font-semibold text-neutral-600 hover:bg-neutral-200 hover:text-neutral-900 transition flex items-center justify-center';
        }
      });

      applyFilters();
    }

    function handleFilterChange() {
      currentMatchFilter = document.getElementById('matchFilter')?.value || 'all';
      currentTypeFilter = document.getElementById('typeFilter')?.value || 'all';
      currentOriginFilter = document.getElementById('originFilter')?.value || 'all';

      currentPage = 1;
      applyFilters();
    }

    function handleSearch(val) {
      searchQuery = val.trim().toLowerCase();
      document.getElementById('clearSearchBtn').className = searchQuery ? 'absolute inset-y-0 right-0 pr-3.5 flex items-center text-neutral-400 hover:text-neutral-600 text-sm' : 'hidden';
      currentPage = 1;
      applyFilters();
    }

    function clearSearch() {
      document.getElementById('searchInput').value = '';
      searchQuery = '';
      document.getElementById('clearSearchBtn').className = 'hidden';
      applyFilters();
    }

    function handleSortChange() {
      currentSort = document.getElementById('sortBy').value;
      applyFilters();
    }

    function setViewMode(mode) {
      viewMode = mode;
      document.getElementById('viewGridBtn').className = mode === 'grid' 
        ? 'px-3 py-1.5 rounded-lg text-xs font-semibold bg-white text-neutral-800 shadow-xs transition'
        : 'px-3 py-1.5 rounded-lg text-xs font-semibold text-neutral-500 hover:text-neutral-800 transition';
      document.getElementById('viewTableBtn').className = mode === 'table' 
        ? 'px-3 py-1.5 rounded-lg text-xs font-semibold bg-white text-neutral-800 shadow-xs transition'
        : 'px-3 py-1.5 rounded-lg text-xs font-semibold text-neutral-500 hover:text-neutral-800 transition';

      document.getElementById('namesGrid').className = mode === 'grid' ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4' : 'hidden';
      document.getElementById('namesTableWrapper').className = mode === 'table' ? 'bg-white rounded-3xl border border-neutral-200/80 shadow-xs overflow-hidden' : 'hidden';
      renderContent();
    }

    function resetFilters() {
      currentFilterStatus = 'all';
      currentVersionFilter = 'all';
      currentMatchFilter = 'all';
      currentTypeFilter = 'all';
      currentOriginFilter = 'all';
      currentLetterFilter = '';
      searchQuery = '';
      document.getElementById('searchInput').value = '';
      document.getElementById('matchFilter').value = 'all';
      document.getElementById('typeFilter').value = 'all';
      document.getElementById('originFilter').value = 'all';
      document.getElementById('sortBy').value = 'name_asc';
      setStatusFilter('all');
      setVersionFilter('all');
      setLetterFilter('');
    }

    // Apply all filters and render
    function applyFilters() {
      filteredNames = allNames.filter(item => {
        // Version filter
        if (currentVersionFilter === 'pdf' && (!item.source || !item.source.includes('PDF'))) return false;
        if (currentVersionFilter === 'new' && item.source && item.source.includes('PDF')) return false;

        const robSt = item.rob_status || 'unrated';
        const anaSt = item.ana_status || 'unrated';
        const userSt = getUserStatus(item, currentUser);

        // Status tab filter
        if (currentFilterStatus === 'super_matches') {
          if (!(robSt === 'favorites' && anaSt === 'favorites')) return false;
        } else if (currentFilterStatus === 'matches') {
          const rPos = (robSt === 'favorites' || robSt === 'possible');
          const aPos = (anaSt === 'favorites' || anaSt === 'possible');
          if (!(rPos && aPos)) return false;
        } else if (currentFilterStatus === 'unrated') {
          if (currentUser === 'ana' && anaSt !== 'unrated') return false;
          if (currentUser === 'rob' && robSt !== 'unrated') return false;
          if (currentUser === 'both' && anaSt !== 'unrated' && robSt !== 'unrated') return false;
        } else if (currentFilterStatus !== 'all') {
          if (userSt !== currentFilterStatus) return false;
        }

        // Match dropdown filter
        if (currentMatchFilter === 'super_match' && !(robSt === 'favorites' && anaSt === 'favorites')) return false;
        if (currentMatchFilter === 'any_match') {
          const rPos = (robSt === 'favorites' || robSt === 'possible');
          const aPos = (anaSt === 'favorites' || anaSt === 'possible');
          if (!(rPos && aPos)) return false;
        }
        if (currentMatchFilter === 'conflict') {
          const rPos = (robSt === 'favorites' || robSt === 'possible');
          const aPos = (anaSt === 'favorites' || anaSt === 'possible');
          const rNeg = (robSt === 'excluded' || robSt === 'similar_excluded');
          const aNeg = (anaSt === 'excluded' || anaSt === 'similar_excluded');
          if (!((rPos && aNeg) || (aPos && rNeg))) return false;
        }
        if (currentMatchFilter === 'pending_ana' && anaSt !== 'unrated') return false;
        if (currentMatchFilter === 'pending_rob' && robSt !== 'unrated') return false;

        // Type filter
        if (currentTypeFilter === 'compound' && !item.is_compound) return false;
        if (currentTypeFilter === 'single' && item.is_compound) return false;
        if (currentTypeFilter === 'with_saint') {
          if (!item.saint_day || item.saint_day.includes('Sin santoral')) return false;
        }

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
          const rank = { favorites: 1, possible: 2, unrated: 3, similar_excluded: 4, excluded: 5 };
          const uA = getUserStatus(a, currentUser);
          const uB = getUserStatus(b, currentUser);
          return (rank[uA] || 9) - (rank[uB] || 9);
        }
        return 0;
      });

      // Update counters
      document.getElementById('showingCount').innerText = filteredNames.length.toLocaleString();

      renderPagination();
      renderContent();
    }

    function renderPagination() {
      const totalPages = Math.ceil(filteredNames.length / pageSize) || 1;
      if (currentPage > totalPages) currentPage = totalPages;
      if (currentPage < 1) currentPage = 1;

      document.getElementById('currentPageNum').innerText = currentPage;
      document.getElementById('totalPagesNum').innerText = totalPages;
      document.getElementById('prevPageBtn').disabled = currentPage <= 1;
      document.getElementById('nextPageBtn').disabled = currentPage >= totalPages;

      const paginationContainer = document.getElementById('paginationControls');
      paginationContainer.className = filteredNames.length > pageSize 
        ? 'flex items-center justify-between mt-6 bg-white rounded-2xl p-4 border border-neutral-200/80 shadow-xs'
        : 'hidden';
    }

    function changePage(delta) {
      currentPage += delta;
      applyFilters();
      window.scrollTo({ top: 380, behavior: 'smooth' });
    }

    // Render Cards & Table
    function renderContent() {
      const emptyState = document.getElementById('emptyState');
      const grid = document.getElementById('namesGrid');
      const tbody = document.getElementById('namesTableBody');

      if (filteredNames.length === 0) {
        emptyState.className = 'text-center py-16 bg-white rounded-3xl border border-neutral-200/80 shadow-xs';
        grid.innerHTML = '';
        tbody.innerHTML = '';
        return;
      }
      emptyState.className = 'hidden';

      const startIdx = (currentPage - 1) * pageSize;
      const pageItems = filteredNames.slice(startIdx, startIdx + pageSize);

      const activePerson = currentUser === 'both' ? 'rob' : currentUser;
      const partnerPerson = activePerson === 'rob' ? 'ana' : 'rob';

      // Render Grid
      grid.innerHTML = pageItems.map(item => {
        const color = getOriginColor(item.origin);
        const myVote = activePerson === 'rob' ? (item.rob_status || 'unrated') : (item.ana_status || 'unrated');
        const partnerVote = partnerPerson === 'rob' ? (item.rob_status || 'unrated') : (item.ana_status || 'unrated');
        
        const isFav = myVote === 'favorites';
        const isPos = myVote === 'possible';
        const isSim = myVote === 'similar_excluded';
        const isExc = myVote === 'excluded';

        const match = getMatchInfo(item);

        const partnerLabels = {
          favorites: '⭐ Le encanta (Favorito)',
          possible: '👍 Le parece Posible',
          similar_excluded: '⚠️ Tiene dudas',
          excluded: '❌ Lo descartó',
          unrated: '⏳ Aún no ha votado'
        };

        const partnerColor = {
          favorites: 'text-amber-800 bg-amber-50 border-amber-200',
          possible: 'text-sky-800 bg-sky-50 border-sky-200',
          similar_excluded: 'text-orange-800 bg-orange-50 border-orange-200',
          excluded: 'text-neutral-600 bg-neutral-100 border-neutral-200',
          unrated: 'text-neutral-500 bg-neutral-50 border-dashed border-neutral-300'
        }[partnerVote] || 'text-neutral-500 bg-neutral-50 border-neutral-200';

        return `
          <div class="bg-white rounded-3xl p-5 border border-neutral-200/80 shadow-xs hover:shadow-md transition card-transition flex flex-col justify-between group relative ${match.type === 'super_match' ? 'ring-2 ring-pink-400 bg-gradient-to-b from-pink-50/30 to-white' : (isFav ? 'ring-2 ring-amber-300 bg-amber-50/20' : '')}">
            
            <div>
              <!-- Top Match Banner if applicable -->
              ${match.badge ? `<div class="mb-3">${match.badge}</div>` : ''}

              <!-- Name & Origin Row -->
              <div class="flex items-start justify-between gap-2 mb-2.5">
                <div class="flex items-center gap-3">
                  <div class="w-11 h-11 rounded-2xl bg-gradient-to-tr ${activePerson === 'ana' ? 'from-pink-100 to-rose-200 text-pink-800' : 'from-blue-100 to-indigo-200 text-blue-800'} font-bold font-accent flex items-center justify-center text-lg shadow-2xs shrink-0">
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

                <div class="shrink-0">
                  ${getStatusBadgeHTML(myVote)}
                </div>
              </div>

              <!-- Spanish Meaning -->
              <p class="text-xs text-neutral-700 italic line-clamp-3 mb-2.5 font-serif leading-relaxed">
                "${item.meaning || 'Sin significado registrado'}"
              </p>

              <!-- Santoral if available -->
              ${item.saint_day && !item.saint_day.includes('Sin santoral') ? `
                <div class="text-[11px] text-purple-900 bg-purple-50/90 border border-purple-200/80 rounded-xl px-2.5 py-1 mb-2.5 flex items-center gap-1.5">
                  <span class="shrink-0 text-xs">📅</span>
                  <span class="truncate font-medium">${item.saint_day}</span>
                </div>
              ` : ''}

              <!-- Similarity Alert Box -->
              ${item.similar_to ? `
                <div class="text-[11px] text-orange-900 bg-orange-50/90 border border-orange-200 rounded-xl px-2.5 py-1.5 mb-2.5 flex items-start gap-1.5">
                  <span class="shrink-0 text-xs mt-0.5">⚠️</span>
                  <span class="leading-tight">${item.similar_to}</span>
                </div>
              ` : ''}

              <!-- Partner Status Pill (What Rob or Ana thinks) -->
              <div class="mb-3 p-2 rounded-xl border text-[11px] flex items-center justify-between gap-1.5 ${partnerColor}">
                <div class="flex items-center gap-1.5 truncate">
                  <span class="font-bold">${partnerPerson === 'rob' ? '👨 Rob:' : '👩 Ana:'}</span>
                  <span class="truncate">${partnerLabels[partnerVote] || partnerVote}</span>
                </div>
                <button onclick="switchUser('${partnerPerson}')" class="text-[10px] underline shrink-0 hover:opacity-80">
                  Votar como ${partnerPerson === 'rob' ? 'Rob' : 'Ana'}
                </button>
              </div>

            </div>

            <!-- Card Bottom: 1-Tap Quick Action Selector for Active User -->
            <div class="pt-3 border-t border-neutral-100 flex flex-col gap-1.5">
              <div class="text-[10px] uppercase tracking-wider font-bold text-neutral-400 flex items-center justify-between">
                <span>Tu voto (${activePerson === 'rob' ? '👨 Rob' : '👩 Ana'}):</span>
                <button onclick="openEditModal('${item.id}')" class="text-rose-600 hover:underline">✏️ Editar</button>
              </div>

              <!-- 4 Touch Action Buttons -->
              <div class="flex items-center gap-1 bg-neutral-100/80 p-1 rounded-2xl border border-neutral-200/60">
                <button 
                  title="Marcar Favorito" 
                  onclick="setPersonVote('${item.id}', 'favorites', '${activePerson}')" 
                  class="flex-1 py-2 rounded-xl text-xs font-bold transition flex items-center justify-center gap-1 ${isFav ? 'bg-amber-400 text-amber-950 shadow-xs' : 'text-neutral-500 hover:text-amber-700 hover:bg-amber-50'}"
                >
                  <span>⭐</span>
                  <span class="text-[10px] hidden xs:inline">Fav</span>
                </button>
                <button 
                  title="Marcar Posible" 
                  onclick="setPersonVote('${item.id}', 'possible', '${activePerson}')" 
                  class="flex-1 py-2 rounded-xl text-xs font-bold transition flex items-center justify-center gap-1 ${isPos ? 'bg-sky-400 text-sky-950 shadow-xs' : 'text-neutral-500 hover:text-sky-700 hover:bg-sky-50'}"
                >
                  <span>👍</span>
                  <span class="text-[10px] hidden xs:inline">Posible</span>
                </button>
                <button 
                  title="Marcar Similar / En Duda" 
                  onclick="setPersonVote('${item.id}', 'similar_excluded', '${activePerson}')" 
                  class="flex-1 py-2 rounded-xl text-xs font-bold transition flex items-center justify-center gap-1 ${isSim ? 'bg-orange-400 text-orange-950 shadow-xs' : 'text-neutral-500 hover:text-orange-700 hover:bg-orange-50'}"
                >
                  <span>⚠️</span>
                  <span class="text-[10px] hidden xs:inline">Duda</span>
                </button>
                <button 
                  title="Excluir" 
                  onclick="setPersonVote('${item.id}', 'excluded', '${activePerson}')" 
                  class="flex-1 py-2 rounded-xl text-xs font-bold transition flex items-center justify-center gap-1 ${isExc ? 'bg-neutral-300 text-neutral-800 shadow-xs' : 'text-neutral-500 hover:text-neutral-700 hover:bg-neutral-100'}"
                >
                  <span>❌</span>
                  <span class="text-[10px] hidden xs:inline">Descartar</span>
                </button>
              </div>

            </div>

          </div>
        `;
      }).join('');

      // Render Table View
      tbody.innerHTML = pageItems.map(item => {
        const color = getOriginColor(item.origin);
        const match = getMatchInfo(item);
        const robSt = item.rob_status || 'unrated';
        const anaSt = item.ana_status || 'unrated';

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
            <td class="py-3 px-4">
              ${getStatusBadgeHTML(robSt)}
            </td>
            <td class="py-3 px-4">
              ${getStatusBadgeHTML(anaSt)}
            </td>
            <td class="py-3 px-4">
              ${match.pill}
            </td>
            <td class="py-3 px-4 text-right">
              <div class="inline-flex items-center gap-1 bg-neutral-100 p-1 rounded-xl">
                <button onclick="setPersonVote('${item.id}', 'favorites')" class="p-1 hover:scale-110 transition" title="Marcar Favorito">⭐</button>
                <button onclick="setPersonVote('${item.id}', 'possible')" class="p-1 hover:scale-110 transition" title="Marcar Posible">👍</button>
                <button onclick="setPersonVote('${item.id}', 'similar_excluded')" class="p-1 hover:scale-110 transition" title="Marcar En Duda">⚠️</button>
                <button onclick="setPersonVote('${item.id}', 'excluded')" class="p-1 hover:scale-110 transition" title="Descartar">❌</button>
                <button onclick="openEditModal('${item.id}')" class="p-1 text-neutral-400 hover:text-neutral-700" title="Editar">✏️</button>
              </div>
            </td>
          </tr>
        `;
      }).join('');
    }

    // Modal: Add Name
    function openAddModal() {
      document.getElementById('addNameForm').reset();
      document.getElementById('addNameDuplicateAlert').className = 'text-xs text-amber-600 font-medium mt-1 hidden';
      document.getElementById('addModal').classList.remove('hidden');
      setTimeout(() => document.getElementById('addNameInput').focus(), 50);

      document.getElementById('addNameInput').oninput = function() {
        const val = this.value.trim().toLowerCase();
        const exists = allNames.some(x => x.name.toLowerCase() === val);
        document.getElementById('addNameDuplicateAlert').className = exists ? 'text-xs text-amber-600 font-medium mt-1 block' : 'hidden';
      };
    }

    function closeAddModal() {
      document.getElementById('addModal').classList.add('hidden');
    }

    async function submitAddName(e) {
      e.preventDefault();
      const name = document.getElementById('addNameInput').value.trim();
      const origin = document.getElementById('addOriginInput').value.trim();
      const meaning = document.getElementById('addMeaningInput').value.trim();
      const notes = document.getElementById('addNotesInput').value.trim();
      const saint = document.getElementById('addSaintInput')?.value.trim() || '';
      const initialVote = document.querySelector('input[name="addStatus"]:checked')?.value || 'possible';

      if (!name) return;

      const newItem = {
        id: `user-${Date.now()}`,
        name: name,
        origin: origin || 'Latino / Español',
        meaning: meaning || '',
        letter: name.charAt(0).toUpperCase(),
        status: initialVote,
        rob_status: currentUser === 'ana' ? 'unrated' : initialVote,
        ana_status: currentUser === 'ana' ? initialVote : 'unrated',
        notes: notes || '',
        source: 'User Added',
        gender: 'Female',
        saint_day: saint || 'Sin santoral registrado en el martirologio común',
        similar_to: '',
        is_compound: (name.includes(' ') || name.includes('-'))
      };

      allNames.unshift(newItem);
      closeAddModal();

      // Store in custom names list
      try {
        const customNames = JSON.parse(localStorage.getItem(CUSTOM_NAMES_KEY) || '[]');
        customNames.unshift(newItem);
        localStorage.setItem(CUSTOM_NAMES_KEY, JSON.stringify(customNames));
      } catch (err) {}

      // Save initial vote
      saveVoteLocally(newItem.id, initialVote, currentUser === 'ana' ? 'ana' : 'rob');

      if (isServerMode) {
        try {
          await fetch('/api/names', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(newItem)
          });
        } catch (err) {
          console.error("Server add error:", err);
        }
      }

      renderStats();
      populateOriginDropdown();
      applyFilters();
      showToast(`🌸 ¡Nombre "${name}" guardado exitosamente!`);
    }

    // Modal: Edit Name
    function openEditModal(id) {
      const item = allNames.find(x => x.id === id);
      if (!item) return;

      document.getElementById('editIdInput').value = item.id;
      document.getElementById('editNameInput').value = item.name;
      document.getElementById('editOriginInput').value = item.origin || '';
      document.getElementById('editMeaningInput').value = item.meaning || '';
      document.getElementById('editNotesInput').value = item.notes || '';
      const saintEl = document.getElementById('editSaintInput');
      if (saintEl) saintEl.value = item.saint_day || '';

      // Rob radios
      const rSt = item.rob_status || 'possible';
      if (rSt === 'favorites') document.getElementById('editRobFav').checked = true;
      else if (rSt === 'possible') document.getElementById('editRobPos').checked = true;
      else if (rSt === 'similar_excluded') document.getElementById('editRobSim').checked = true;
      else document.getElementById('editRobExc').checked = true;

      // Ana radios
      const aSt = item.ana_status || 'unrated';
      if (aSt === 'favorites') document.getElementById('editAnaFav').checked = true;
      else if (aSt === 'possible') document.getElementById('editAnaPos').checked = true;
      else if (aSt === 'similar_excluded') document.getElementById('editAnaSim').checked = true;
      else if (aSt === 'excluded') document.getElementById('editAnaExc').checked = true;
      else {
        document.getElementById('editAnaPos').checked = true;
      }

      document.getElementById('editModal').classList.remove('hidden');
    }

    function closeEditModal() {
      document.getElementById('editModal').classList.add('hidden');
    }

    async function submitEditName(e) {
      e.preventDefault();
      const id = document.getElementById('editIdInput').value;
      const item = allNames.find(x => x.id === id);
      if (!item) return;

      item.name = document.getElementById('editNameInput').value.trim();
      item.origin = document.getElementById('editOriginInput').value.trim();
      item.meaning = document.getElementById('editMeaningInput').value.trim();
      item.notes = document.getElementById('editNotesInput').value.trim();
      const saintEl = document.getElementById('editSaintInput');
      if (saintEl) item.saint_day = saintEl.value.trim();

      item.rob_status = document.querySelector('input[name="editRobStatus"]:checked')?.value || item.rob_status;
      item.ana_status = document.querySelector('input[name="editAnaStatus"]:checked')?.value || item.ana_status;

      item.letter = item.name.charAt(0).toUpperCase();
      item.is_compound = (item.name.includes(' ') || item.name.includes('-'));

      saveVoteLocally(item.id, item.rob_status, 'rob');
      saveVoteLocally(item.id, item.ana_status, 'ana');

      closeEditModal();
      await saveNameChange(item);
      applyFilters();
      showToast(`✏️ Cambios guardados para "${item.name}"`);
    }

    async function deleteCurrentEditName() {
      const id = document.getElementById('editIdInput').value;
      const item = allNames.find(x => x.id === id);
      if (!item) return;

      if (!confirm(`¿Eliminar permanentemente "${item.name}" de la lista?`)) return;

      allNames = allNames.filter(x => x.id !== id);
      closeEditModal();

      if (isServerMode) {
        try {
          await fetch(`/api/names/${id}`, { method: 'DELETE' });
        } catch (e) {
          console.error("Delete failed:", e);
        }
      }

      renderStats();
      applyFilters();
      showToast(`🗑️ "${item.name}" ha sido eliminado`);
    }

    // Swipe Discovery Mode with 2,500 new unrated names and Undo
    function openSwipeModal() {
      swipeUser = currentUser === 'both' ? 'rob' : currentUser;
      swipeDeckFilter = 'new_unrated';
      setSwipeUser(swipeUser);
      document.getElementById('swipeModal').classList.remove('hidden');
    }

    function closeSwipeModal() {
      document.getElementById('swipeModal').classList.add('hidden');
      applyFilters();
      showToast("✨ Tus elecciones se han guardado permanentemente.");
    }

    function setSwipeUser(user) {
      swipeUser = user;
      const btnRob = document.getElementById('swipeUser_rob');
      const btnAna = document.getElementById('swipeUser_ana');
      if (btnRob) btnRob.className = `px-3.5 py-1.5 rounded-xl text-xs font-bold transition ${user === 'rob' ? 'bg-blue-600 text-white shadow-xs' : 'text-white/70 hover:text-white'}`;
      if (btnAna) btnAna.className = `px-3.5 py-1.5 rounded-xl text-xs font-bold transition ${user === 'ana' ? 'bg-pink-600 text-white shadow-xs' : 'text-white/70 hover:text-white'}`;
      setSwipeFilter(swipeDeckFilter);
    }

    function setSwipeFilter(filterType) {
      swipeDeckFilter = filterType;

      const filters = ['new_unrated', 'all_unrated', 'possible', 'favorites'];
      filters.forEach(f => {
        const btn = document.getElementById(`swipeFilter_${f}`);
        if (!btn) return;
        if (f === filterType) {
          btn.className = 'px-3 py-1 rounded-full text-xs font-bold bg-rose-500 text-white shadow-xs transition';
        } else {
          btn.className = 'px-3 py-1 rounded-full text-xs font-semibold bg-white/15 text-white/80 hover:bg-white/25 transition';
        }
      });

      const isRob = swipeUser === 'rob';

      if (filterType === 'new_unrated') {
        // Show all new additions that are unrated for active user
        swipeDeck = allNames.filter(x => {
          const isNew = !x.source || !x.source.includes('PDF');
          const st = isRob ? (x.rob_status || 'unrated') : (x.ana_status || 'unrated');
          return isNew && (!st || st === 'unrated');
        });
      } else if (filterType === 'all_unrated') {
        // Show all unrated for active user
        swipeDeck = allNames.filter(x => {
          const st = isRob ? (x.rob_status || 'unrated') : (x.ana_status || 'unrated');
          return !st || st === 'unrated';
        });
      } else if (filterType === 'possible') {
        swipeDeck = allNames.filter(x => {
          const st = isRob ? (x.rob_status || 'unrated') : (x.ana_status || 'unrated');
          return st === 'possible';
        });
      } else if (filterType === 'favorites') {
        swipeDeck = allNames.filter(x => {
          const st = isRob ? (x.rob_status || 'unrated') : (x.ana_status || 'unrated');
          return st === 'favorites';
        });
      } else {
        swipeDeck = [...allNames];
      }

      swipeIndex = 0;
      renderSwipeCard();
    }

    function renderSwipeCard() {
      const card = document.getElementById('swipeCard');
      const progress = document.getElementById('swipeDeckProgress');

      // Update session counter
      const sessEl = document.getElementById('swipeSessionStats');
      if (sessEl) {
        sessEl.innerText = `⭐ ${sessionVoteCounts.favorites} | 👍 ${sessionVoteCounts.possible} | ⚠️ ${sessionVoteCounts.similar_excluded} | ❌ ${sessionVoteCounts.excluded}`;
      }

      if (swipeIndex >= swipeDeck.length || swipeDeck.length === 0) {
        card.innerHTML = `
          <div class="py-12 flex flex-col items-center">
            <span class="text-5xl mb-3">🎉</span>
            <h3 class="text-2xl font-bold font-display text-neutral-800">¡Has completado esta ronda!</h3>
            <p class="text-sm text-neutral-500 mt-2 max-w-xs">No quedan más nombres en este filtro para ${swipeUser === 'rob' ? 'Rob' : 'Ana'}.</p>
            <div class="flex items-center gap-2 mt-5">
              <button onclick="setSwipeFilter('favorites')" class="px-4 py-2 bg-amber-500 text-white rounded-xl text-xs font-bold hover:bg-amber-600 transition shadow-xs">
                ⭐ Ver Mis Favoritos
              </button>
              <button onclick="closeSwipeModal()" class="px-4 py-2 bg-neutral-800 text-white rounded-xl text-xs font-bold hover:bg-neutral-900 transition shadow-xs">
                Volver al Catálogo
              </button>
            </div>
          </div>
        `;
        progress.innerText = '0 restantes';
        return;
      }

      const item = swipeDeck[swipeIndex];
      progress.innerText = `${(swipeDeck.length - swipeIndex).toLocaleString()} restantes`;

      document.getElementById('swipeLetter').innerText = item.name.charAt(0).toUpperCase();
      document.getElementById('swipeOrigin').innerText = item.origin || 'Latino';
      document.getElementById('swipeSource').innerText = item.is_compound ? '🏷️ Compuesto' : (item.source?.includes('PDF') ? '📜 v1.0 PDF' : '✨ Nuevo Hispano');
      document.getElementById('swipeName').innerText = item.name;
      document.getElementById('swipeMeaning').innerText = `"${item.meaning || 'Sin significado registrado'}"`;

      const saintEl = document.getElementById('swipeSaint');
      if (item.saint_day && !item.saint_day.includes('Sin santoral')) {
        saintEl.innerText = `📅 ${item.saint_day}`;
        saintEl.classList.remove('hidden');
      } else {
        saintEl.classList.add('hidden');
      }

      const simEl = document.getElementById('swipeSimilarity');
      if (item.similar_to) {
        simEl.innerText = `⚠️ ${item.similar_to}`;
        simEl.classList.remove('hidden');
      } else {
        simEl.classList.add('hidden');
      }

      // Partner's vote tag in Swipe
      const partner = swipeUser === 'rob' ? 'ana' : 'rob';
      const partnerVote = partner === 'rob' ? (item.rob_status || 'unrated') : (item.ana_status || 'unrated');
      const partnerLabels = { favorites: '⭐ Favorito', possible: '👍 Posible', similar_excluded: '⚠️ En Duda', excluded: '❌ Excluido', unrated: '⏳ Aún sin calificar' };
      const partnerTag = document.getElementById('swipePartnerVoteTag');
      if (partnerTag) {
        partnerTag.innerHTML = `
          <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-neutral-100 text-neutral-700 border border-neutral-200">
            <span>${partner === 'rob' ? '👨 Rob opina:' : '👩 Ana opina:'}</span>
            <span class="font-bold">${partnerLabels[partnerVote] || partnerVote}</span>
          </div>
        `;
      }

      const myCurrent = swipeUser === 'rob' ? (item.rob_status || 'unrated') : (item.ana_status || 'unrated');
      const statusMap = { favorites: '⭐ Favorito', possible: '👍 Posible', similar_excluded: '⚠️ En Duda', excluded: '❌ Excluido', unrated: '⏳ Por clasificar' };
      document.getElementById('swipeCurrentStatus').innerText = statusMap[myCurrent] || myCurrent;
    }

    async function handleSwipeAction(actionStatus) {
      if (swipeIndex >= swipeDeck.length) return;
      const currentItem = swipeDeck[swipeIndex];

      // Record to undo history
      swipeHistory.push({
        item: currentItem,
        user: swipeUser,
        prevRob: currentItem.rob_status || 'unrated',
        prevAna: currentItem.ana_status || 'unrated',
        prevIndex: swipeIndex
      });

      // Update session vote stats
      if (sessionVoteCounts[actionStatus] !== undefined) {
        sessionVoteCounts[actionStatus]++;
      }

      const card = document.getElementById('swipeCard');
      if (card) {
        if (actionStatus === 'favorites') {
          card.classList.add('translate-x-16', 'rotate-6', 'opacity-0');
        } else if (actionStatus === 'excluded') {
          card.classList.add('-translate-x-16', '-rotate-6', 'opacity-0');
        } else if (actionStatus === 'possible') {
          card.classList.add('-translate-y-12', 'opacity-0');
        } else {
          card.classList.add('translate-y-12', 'opacity-0');
        }
      }

      // Persist choice immediately
      await setPersonVote(currentItem.id, actionStatus, swipeUser);

      setTimeout(() => {
        if (card) {
          card.classList.remove('translate-x-16', '-translate-x-16', 'translate-y-12', '-translate-y-12', 'rotate-6', '-rotate-6', 'opacity-0');
        }
        swipeIndex++;
        renderSwipeCard();
      }, 160);
    }

    // Undo Last Swipe
    function undoLastSwipe() {
      if (swipeHistory.length === 0) {
        showToast("No hay votos recientes para deshacer");
        return;
      }
      const last = swipeHistory.pop();
      if (last.user === 'rob') {
        last.item.rob_status = last.prevRob;
      } else {
        last.item.ana_status = last.prevAna;
      }

      saveVoteLocally(last.item.id, last.user === 'rob' ? last.prevRob : last.prevAna, last.user);

      if (swipeIndex > 0) {
        swipeIndex--;
      }

      renderSwipeCard();
      renderStats();
      applyFilters();
      showToast(`↩️ Voto deshecho para "${last.item.name}"`);
    }

    // Touch Swipe Gestures
    let touchStartX = 0;
    let touchStartY = 0;
    let touchEndX = 0;
    let touchEndY = 0;

    function setupSwipeGestures() {
      const card = document.getElementById('swipeCard');
      if (!card) return;

      card.addEventListener('touchstart', (e) => {
        touchStartX = e.changedTouches[0].screenX;
        touchStartY = e.changedTouches[0].screenY;
      }, { passive: true });

      card.addEventListener('touchend', (e) => {
        touchEndX = e.changedTouches[0].screenX;
        touchEndY = e.changedTouches[0].screenY;
        const dx = touchEndX - touchStartX;
        const dy = touchEndY - touchStartY;
        const absX = Math.abs(dx);
        const absY = Math.abs(dy);

        if (Math.max(absX, absY) < 45) return;

        if (absX > absY) {
          if (dx > 0) handleSwipeAction('favorites');
          else handleSwipeAction('excluded');
        } else {
          if (dy < 0) handleSwipeAction('possible');
          else handleSwipeAction('similar_excluded');
        }
      }, { passive: true });
    }

    // Keyboard navigation for Swipe Mode
    function setupKeyboardListeners() {
      window.addEventListener('keydown', (e) => {
        const swipeModal = document.getElementById('swipeModal');
        if (swipeModal.classList.contains('hidden')) return;

        if (e.key === 'ArrowRight') {
          handleSwipeAction('favorites');
        } else if (e.key === 'ArrowLeft') {
          handleSwipeAction('excluded');
        } else if (e.key === 'ArrowUp') {
          handleSwipeAction('possible');
        } else if (e.key === 'ArrowDown') {
          handleSwipeAction('similar_excluded');
        } else if (e.key === 'Backspace' || (e.ctrlKey && e.key === 'z')) {
          undoLastSwipe();
        } else if (e.key === 'Escape') {
          closeSwipeModal();
        }
      });
    }

    // Export to Excel / CSV with Rob & Ana Columns
    function exportToCSV() {
      const headers = ["Nombre", "Origen", "Santoral", "Significado", "Voto Rob", "Voto Ana", "Coincidencia", "Tipo", "Similar A", "Fuente", "Notas"];
      const rows = allNames.map(x => {
        const m = getMatchInfo(x);
        return [
          `"${(x.name || '').replace(/"/g, '""')}"`,
          `"${(x.origin || '').replace(/"/g, '""')}"`,
          `"${(x.saint_day || '').replace(/"/g, '""')}"`,
          `"${(x.meaning || '').replace(/"/g, '""')}"`,
          `"${x.rob_status || ''}"`,
          `"${x.ana_status || ''}"`,
          `"${m.type}"`,
          `"${x.is_compound ? 'Compuesto' : 'Simple'}"`,
          `"${(x.similar_to || '').replace(/"/g, '""')}"`,
          `"${(x.source || '').replace(/"/g, '""')}"`,
          `"${(x.notes || '').replace(/"/g, '""')}"`
        ];
      });

      const csvContent = "\\uFEFF" + [headers.join(","), ...rows.map(r => r.join(","))].join("\\r\\n");
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.setAttribute("href", url);
      link.setAttribute("download", `Nombres_Para_Chiquitina_Rob_Ana_${new Date().toISOString().slice(0, 10)}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      showToast("📊 Archivo Excel CSV descargado exitosamente!");
    }

    // Export to JSON Backup
    function exportToJSON() {
      const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(allNames, null, 2));
      const link = document.createElement('a');
      link.setAttribute("href", dataStr);
      link.setAttribute("download", `nombres_chiquitina_backup_${new Date().toISOString().slice(0, 10)}.json`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      showToast("💾 Copia de seguridad JSON descargada!");
    }

    // Import JSON
    function importJSON(e) {
      const file = e.target.files[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = async function(evt) {
        try {
          const imported = JSON.parse(evt.target.result);
          if (Array.isArray(imported)) {
            if (confirm(`¿Restaurar base de datos con ${imported.length} nombres del archivo?`)) {
              allNames = imported;
              for (const item of allNames) {
                if (item.rob_status) saveVoteLocally(item.id, item.rob_status, 'rob');
                if (item.ana_status) saveVoteLocally(item.id, item.ana_status, 'ana');
              }
              renderStats();
              populateOriginDropdown();
              applyFilters();
              showToast("📤 Base de datos restaurada correctamente");
            }
          } else {
            alert("El archivo JSON no tiene un formato de lista válido.");
          }
        } catch (err) {
          alert("Error al leer el archivo JSON: " + err.message);
        }
      };
      reader.readAsText(file);
    }

    // Reset to Original State
    async function resetDatabase() {
      if (!confirm("¿Deseas restaurar la base de datos a su estado original?")) {
        return;
      }

      localStorage.removeItem(VOTES_STORAGE_KEY);
      localStorage.removeItem(CUSTOM_NAMES_KEY);
      window.location.reload();
    }

    // Toast notification helper
    function showToast(msg, icon = '🌸') {
      const toast = document.getElementById('toast');
      document.getElementById('toastMessage').innerText = msg;
      document.getElementById('toastIcon').innerText = icon;
      toast.classList.remove('translate-y-24', 'opacity-0', 'pointer-events-none');

      setTimeout(() => {
        toast.classList.add('translate-y-24', 'opacity-0', 'pointer-events-none');
      }, 2500);
    }
  </script>

  <script id="embeddedNamesData" type="application/json">
''' + embedded_json + '''
  </script>
</body>
</html>
'''

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

print("Successfully written index.html with lightweight votes storage, session counter, and undo.")
