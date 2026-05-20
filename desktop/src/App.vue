<script setup lang="ts">
import { computed, ref } from "vue"
import { open, save } from "@tauri-apps/plugin-dialog"
import { Download, RefreshCw, RotateCcw, Upload } from "lucide-vue-next"
import CreatorTable from "./components/CreatorTable.vue"
import { useCreators } from "./composables/useCreators"
import logoUrl from "./assets/logo.svg"
import type { FilterState } from "./types"

const { records, loading, errorMessage, refreshCreators, importCsvFile, exportExcelFile } =
  useCreators()

const statusMessage = ref("点击“刷新”加载本地数据，或直接导入 CSV/Excel。")
const filters = ref<FilterState>({
  fansMin: 0,
  fansMax: 0,
  salesMin: 0,
  salesMax: 0,
  creatorLevelMin: 0,
  creatorLevelMax: 0,
  productCountMin: 0,
  productCountMax: 0,
  likeFanRatioMin: 0,
  likeFanRatioMax: 0,
  settlementMin: 0,
  settlementMax: 0,
  categories: [],
})

const availableCategories = computed(() => {
  return Array.from(new Set(records.value.map((item) => item.category).filter(Boolean))).sort()
})

function toNumber(value: number | string, fallback: number) {
  if (value === "" || value === null || value === undefined) {
    return fallback
  }
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : fallback
}

function datasetBounds() {
  if (!records.value.length) {
    return {
      fansMin: 0,
      fansMax: 0,
      salesMin: 0,
      salesMax: 0,
      creatorLevelMin: 0,
      creatorLevelMax: 0,
      productCountMin: 0,
      productCountMax: 0,
      likeFanRatioMin: 0,
      likeFanRatioMax: 0,
      settlementMin: 0,
      settlementMax: 0,
    }
  }

  const fans = records.value.map((item) => item.fans)
  const sales = records.value.map((item) => item.sales_30d)
  const creatorLevels = records.value.map((item) => item.creator_level)
  const productCounts = records.value.map((item) => item.product_count)
  const likeFanRatios = records.value.map((item) => item.like_fan_ratio * 100)
  const settlements = records.value.map((item) => item.settlement_mid)

  return {
    fansMin: Math.min(...fans),
    fansMax: Math.max(...fans),
    salesMin: Math.min(...sales),
    salesMax: Math.max(...sales),
    creatorLevelMin: Math.min(...creatorLevels),
    creatorLevelMax: Math.max(...creatorLevels),
    productCountMin: Math.min(...productCounts),
    productCountMax: Math.max(...productCounts),
    likeFanRatioMin: Math.min(...likeFanRatios),
    likeFanRatioMax: Math.max(...likeFanRatios),
    settlementMin: Math.min(...settlements),
    settlementMax: Math.max(...settlements),
  }
}

function resetFiltersToDataset() {
  const bounds = datasetBounds()
  filters.value = {
    fansMin: bounds.fansMin,
    fansMax: bounds.fansMax,
    salesMin: bounds.salesMin,
    salesMax: bounds.salesMax,
    creatorLevelMin: bounds.creatorLevelMin,
    creatorLevelMax: bounds.creatorLevelMax,
    productCountMin: bounds.productCountMin,
    productCountMax: bounds.productCountMax,
    likeFanRatioMin: bounds.likeFanRatioMin,
    likeFanRatioMax: bounds.likeFanRatioMax,
    settlementMin: bounds.settlementMin,
    settlementMax: bounds.settlementMax,
    categories: [...availableCategories.value],
  }
}

const filteredRecords = computed(() => {
  const bounds = datasetBounds()
  const fansMin = toNumber(filters.value.fansMin, bounds.fansMin)
  const fansMax = toNumber(filters.value.fansMax, bounds.fansMax)
  const salesMin = toNumber(filters.value.salesMin, bounds.salesMin)
  const salesMax = toNumber(filters.value.salesMax, bounds.salesMax)
  const creatorLevelMin = toNumber(filters.value.creatorLevelMin, bounds.creatorLevelMin)
  const creatorLevelMax = toNumber(filters.value.creatorLevelMax, bounds.creatorLevelMax)
  const productCountMin = toNumber(filters.value.productCountMin, bounds.productCountMin)
  const productCountMax = toNumber(filters.value.productCountMax, bounds.productCountMax)
  const likeFanRatioMin = toNumber(filters.value.likeFanRatioMin, bounds.likeFanRatioMin)
  const likeFanRatioMax = toNumber(filters.value.likeFanRatioMax, bounds.likeFanRatioMax)
  const settlementMin = toNumber(filters.value.settlementMin, bounds.settlementMin)
  const settlementMax = toNumber(filters.value.settlementMax, bounds.settlementMax)
  const selectedCategories =
    filters.value.categories.length > 0 ? filters.value.categories : availableCategories.value

  return [...records.value]
    .filter((row) => row.fans >= fansMin && row.fans <= fansMax)
    .filter((row) => row.sales_30d >= salesMin && row.sales_30d <= salesMax)
    .filter((row) => row.creator_level >= creatorLevelMin && row.creator_level <= creatorLevelMax)
    .filter((row) => row.product_count >= productCountMin && row.product_count <= productCountMax)
    .filter((row) => row.like_fan_ratio * 100 >= likeFanRatioMin && row.like_fan_ratio * 100 <= likeFanRatioMax)
    .filter((row) => row.settlement_mid >= settlementMin && row.settlement_mid <= settlementMax)
    .filter((row) => selectedCategories.length === 0 || selectedCategories.includes(row.category))
    .sort((a, b) => b.score - a.score || b.settlement_mid - a.settlement_mid || b.sales_30d - a.sales_30d)
})

const metrics = computed(() => {
  const rows = filteredRecords.value
  const count = rows.length
  const totalFans = rows.reduce((sum, row) => sum + row.fans, 0)
  const totalSettlement = rows.reduce((sum, row) => sum + row.settlement_mid, 0)
  const avgLikeFanRatio = count > 0 ? rows.reduce((sum, row) => sum + row.like_fan_ratio, 0) / count : 0
  const avgScore = count > 0 ? rows.reduce((sum, row) => sum + row.score, 0) / count : 0

  return [
    { label: "达人数量", value: count.toString() },
    { label: "总粉丝", value: new Intl.NumberFormat("zh-CN").format(totalFans) },
    { label: "预估结算合计", value: new Intl.NumberFormat("zh-CN").format(Math.round(totalSettlement)) },
    { label: "平均赞粉比", value: `${(avgLikeFanRatio * 100).toFixed(2)}%` },
    { label: "平均得分", value: avgScore.toFixed(2) },
  ]
})

async function reloadData() {
  try {
    await refreshCreators()
    resetFiltersToDataset()
    statusMessage.value = `已加载 ${records.value.length} 条记录。`
  } catch {
    // Error message is surfaced by the composable.
  }
}

async function handleImportClick() {
  const selection = await open({
    multiple: false,
    directory: false,
    filters: [{ name: "CSV / Excel", extensions: ["csv", "xlsx", "xls"] }],
  })
  if (typeof selection !== "string" || !selection) {
    return
  }

  try {
    const result = await importCsvFile(selection)
    statusMessage.value = `已导入或更新 ${result.imported} 条记录，当前共 ${result.total} 条。`
    resetFiltersToDataset()
  } catch {
    // Error message is surfaced by the composable.
  }
}

async function handleExportClick() {
  if (!filteredRecords.value.length) {
    statusMessage.value = "当前没有可导出的数据。"
    return
  }

  const filePath = await save({
    defaultPath: "达人榜单.xlsx",
    filters: [{ name: "Excel", extensions: ["xlsx"] }],
  })
  if (!filePath) {
    return
  }

  try {
    const bounds = datasetBounds()
    const result = await exportExcelFile(filePath, {
      fansMin: toNumber(filters.value.fansMin, bounds.fansMin),
      fansMax: toNumber(filters.value.fansMax, bounds.fansMax),
      salesMin: toNumber(filters.value.salesMin, bounds.salesMin),
      salesMax: toNumber(filters.value.salesMax, bounds.salesMax),
      creatorLevelMin: toNumber(filters.value.creatorLevelMin, bounds.creatorLevelMin),
      creatorLevelMax: toNumber(filters.value.creatorLevelMax, bounds.creatorLevelMax),
      productCountMin: toNumber(filters.value.productCountMin, bounds.productCountMin),
      productCountMax: toNumber(filters.value.productCountMax, bounds.productCountMax),
      likeFanRatioMin: toNumber(filters.value.likeFanRatioMin, bounds.likeFanRatioMin) / 100,
      likeFanRatioMax: toNumber(filters.value.likeFanRatioMax, bounds.likeFanRatioMax) / 100,
      settlementMin: toNumber(filters.value.settlementMin, bounds.settlementMin),
      settlementMax: toNumber(filters.value.settlementMax, bounds.settlementMax),
      categories:
        filters.value.categories.length > 0 ? filters.value.categories : availableCategories.value,
    })
    statusMessage.value = `已导出 ${result.rows} 条记录到 ${result.output_path}`
  } catch {
    // Error message is surfaced by the composable.
  }
}

function resetFilters() {
  resetFiltersToDataset()
}
</script>

<template>
  <div class="app-shell">
    <header class="topbar">
      <div class="title-block">
        <div class="brand-row">
          <img class="brand-logo" :src="logoUrl" alt="达人榜单 Logo" />
          <div>
            <p class="eyebrow">本地达人榜单</p>
            <h1>达人榜单</h1>
          </div>
        </div>
        <p class="subtitle">CSV/Excel 导入、按 profile_url 更新、筛选、导出 Excel，全部保存在本机。</p>
      </div>

      <div class="actions">
        <button class="button primary" :disabled="loading" @click="handleImportClick">
          <Upload :size="16" />
          <span>导入 CSV/Excel</span>
        </button>
        <button class="button" :disabled="loading || !filteredRecords.length" @click="handleExportClick">
          <Download :size="16" />
          <span>导出 Excel</span>
        </button>
        <button class="button" :disabled="loading" @click="reloadData">
          <RefreshCw :size="16" />
          <span>刷新</span>
        </button>
      </div>
    </header>

    <div v-if="errorMessage || statusMessage" class="notice" :class="{ error: Boolean(errorMessage) }">
      <span>{{ errorMessage || statusMessage }}</span>
    </div>

    <main class="workspace">
      <aside class="filters">
        <section class="panel">
          <div class="panel-header">
            <div>
              <p class="panel-kicker">筛选</p>
              <h2>按粉丝、带货等级、商品数和结算缩小榜单</h2>
            </div>
            <button class="ghost-button" :disabled="loading" @click="resetFilters">
              <RotateCcw :size="16" />
              <span>重置</span>
            </button>
          </div>

          <div class="control-group">
            <label class="control-label">类目</label>
            <div class="category-list">
              <label v-for="category in availableCategories" :key="category" class="checkbox-row">
                <input v-model="filters.categories" type="checkbox" :value="category" />
                <span>{{ category }}</span>
              </label>
            </div>
          </div>

          <div class="control-grid">
            <label class="input-field">
              <span>粉丝数最小</span>
              <input v-model="filters.fansMin" type="number" min="0" step="1" />
            </label>
            <label class="input-field">
              <span>粉丝数最大</span>
              <input v-model="filters.fansMax" type="number" min="0" step="1" />
            </label>
          </div>

          <div class="control-grid">
            <label class="input-field">
              <span>近 30 天销量最小</span>
              <input v-model="filters.salesMin" type="number" min="0" step="1" />
            </label>
            <label class="input-field">
              <span>近 30 天销量最大</span>
              <input v-model="filters.salesMax" type="number" min="0" step="1" />
            </label>
          </div>

          <div class="control-grid">
            <label class="input-field">
              <span>带货等级最小</span>
              <input v-model="filters.creatorLevelMin" type="number" min="0" step="1" />
            </label>
            <label class="input-field">
              <span>带货等级最大</span>
              <input v-model="filters.creatorLevelMax" type="number" min="0" step="1" />
            </label>
          </div>

          <div class="control-grid">
            <label class="input-field">
              <span>推广商品数最小</span>
              <input v-model="filters.productCountMin" type="number" min="0" step="1" />
            </label>
            <label class="input-field">
              <span>推广商品数最大</span>
              <input v-model="filters.productCountMax" type="number" min="0" step="1" />
            </label>
          </div>

          <div class="control-grid">
            <label class="input-field">
              <span>赞粉比最小（%）</span>
              <input v-model="filters.likeFanRatioMin" type="number" min="0" step="0.01" />
            </label>
            <label class="input-field">
              <span>赞粉比最大（%）</span>
              <input v-model="filters.likeFanRatioMax" type="number" min="0" step="0.01" />
            </label>
          </div>

          <div class="control-grid">
            <label class="input-field">
              <span>预估结算最小</span>
              <input v-model="filters.settlementMin" type="number" min="0" step="1" />
            </label>
            <label class="input-field">
              <span>预估结算最大</span>
              <input v-model="filters.settlementMax" type="number" min="0" step="1" />
            </label>
          </div>
        </section>
      </aside>

      <section class="content">
        <div class="metric-grid">
          <article v-for="metric in metrics" :key="metric.label" class="metric">
            <span class="metric-label">{{ metric.label }}</span>
            <strong class="metric-value">{{ metric.value }}</strong>
          </article>
        </div>

        <section class="table-panel">
          <div class="table-header">
            <div>
              <p class="panel-kicker">榜单</p>
              <h2>当前筛选结果</h2>
            </div>
            <p class="count">{{ filteredRecords.length }} / {{ records.length }}</p>
          </div>

          <div v-if="!records.length" class="empty-state">
            <h3>还没有数据</h3>
            <p>导入 CSV/Excel，或点击刷新加载本机已有数据。</p>
          </div>

          <CreatorTable v-else :rows="filteredRecords" />
        </section>
      </section>
    </main>
  </div>
</template>
