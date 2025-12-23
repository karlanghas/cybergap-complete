<template>
  <div class="area-tree-item">
    <div 
      class="flex items-center gap-3 p-3 rounded-lg hover:bg-slate-800/50 group transition-colors"
      :style="{ paddingLeft: `${level * 24 + 12}px` }"
    >
      <!-- Expand/Collapse Toggle -->
      <button 
        v-if="area.children && area.children.length > 0"
        @click="expanded = !expanded"
        class="w-6 h-6 flex items-center justify-center text-slate-400 hover:text-white transition-colors"
      >
        <svg 
          class="w-4 h-4 transition-transform duration-200" 
          :class="{ 'rotate-90': expanded }"
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
        </svg>
      </button>
      <div v-else class="w-6"></div>

      <!-- Icon -->
      <div 
        class="w-8 h-8 rounded-lg flex items-center justify-center"
        :class="area.is_active ? 'bg-emerald-500/20 text-emerald-400' : 'bg-slate-700 text-slate-400'"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
        </svg>
      </div>

      <!-- Info -->
      <div class="flex-1 min-w-0">
        <div class="text-white font-medium truncate">{{ area.name }}</div>
        <div class="text-xs text-slate-500">
          {{ area.users_count || 0 }} usuarios
          <span v-if="area.children?.length"> · {{ area.children.length }} sub-áreas</span>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        <button 
          @click="$emit('add-child', area.id)"
          class="p-1.5 text-slate-400 hover:text-emerald-400 hover:bg-slate-700 rounded transition-colors"
          title="Agregar sub-área"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
          </svg>
        </button>
        <button 
          @click="$emit('edit', area)"
          class="p-1.5 text-slate-400 hover:text-blue-400 hover:bg-slate-700 rounded transition-colors"
          title="Editar"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
          </svg>
        </button>
        <button 
          @click="$emit('delete', area)"
          class="p-1.5 text-slate-400 hover:text-red-400 hover:bg-slate-700 rounded transition-colors"
          title="Eliminar"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- Children -->
    <div v-if="expanded && area.children && area.children.length > 0">
      <AreaTreeItem
        v-for="child in area.children"
        :key="child.id"
        :area="child"
        :level="level + 1"
        @edit="$emit('edit', $event)"
        @delete="$emit('delete', $event)"
        @add-child="$emit('add-child', $event)"
      />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  area: { type: Object, required: true },
  level: { type: Number, default: 0 }
})

defineEmits(['edit', 'delete', 'add-child'])

const expanded = ref(true)
</script>
