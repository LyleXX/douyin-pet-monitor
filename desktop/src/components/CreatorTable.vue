<script setup lang="ts">
import { computed, ref } from "vue"
import type { CreatorRecord } from "../types"
import {
  getDouyinWebProfileUrl,
  nextSortState,
  sortCreatorRows,
  type SortKey,
  type SortState,
} from "../tableUtils"

const props = defineProps<{
  rows: CreatorRecord[]
}>()

const numberFormat = new Intl.NumberFormat("zh-CN")
const sortState = ref<SortState>({ key: "score", direction: "desc" })

const columns: Array<{ label: string; key: SortKey }> = [
  { label: "得分", key: "score" },
  { label: "达人名称", key: "nickname" },
  { label: "抖音 ID", key: "douyin_id" },
  { label: "粉丝", key: "fans" },
  { label: "带货等级", key: "creator_level" },
  { label: "视频数", key: "video_count" },
  { label: "平均获赞", key: "median_likes" },
  { label: "赞粉比", key: "like_fan_ratio" },
  { label: "商品数", key: "product_count" },
  { label: "预估结算", key: "settlement_mid" },
]

const sortedRows = computed(() => sortCreatorRows(props.rows, sortState.value))

function formatNumber(value: number) {
  return numberFormat.format(value)
}

function formatPercent(value: number) {
  return `${(value * 100).toFixed(2)}%`
}

function formatScore(value: number) {
  return value.toFixed(2)
}

function formatSettlement(row: CreatorRecord) {
  if (row.settlement_range) {
    return row.settlement_range
  }
  return formatNumber(Math.round(row.settlement_mid))
}

function handleSort(key: SortKey) {
  sortState.value = nextSortState(sortState.value, key)
}

function sortLabel(key: SortKey) {
  if (sortState.value.key !== key) {
    return "未排序"
  }
  return sortState.value.direction === "asc" ? "升序" : "降序"
}

function sortIndicator(key: SortKey) {
  if (sortState.value.key !== key) {
    return "↕"
  }
  return sortState.value.direction === "asc" ? "↑" : "↓"
}
</script>

<template>
  <div class="table-shell">
    <table>
      <thead>
        <tr>
          <th>排名</th>
          <th v-for="column in columns" :key="column.key">
            <button
              class="sort-button"
              type="button"
              :aria-label="`${column.label} ${sortLabel(column.key)}，点击切换排序`"
              @click="handleSort(column.key)"
            >
              <span>{{ column.label }}</span>
              <span class="sort-indicator">{{ sortIndicator(column.key) }}</span>
            </button>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, index) in sortedRows" :key="row.profile_url">
          <td class="rank">{{ index + 1 }}</td>
          <td><span class="score-pill">{{ formatScore(row.score) }}</span></td>
          <td class="name">{{ row.nickname }}</td>
          <td class="url-cell">
            <a
              v-if="getDouyinWebProfileUrl(row)"
              :href="getDouyinWebProfileUrl(row)"
              target="_blank"
              rel="noreferrer"
              :title="row.web_profile_url ? `打开 ${row.douyin_id} 的抖音网页版主页` : `搜索抖音 ID：${row.douyin_id}`"
            >
              {{ row.douyin_id }}
            </a>
            <span v-else>{{ row.profile_url }}</span>
          </td>
          <td>{{ formatNumber(row.fans) }}</td>
          <td>{{ formatNumber(row.creator_level) }}</td>
          <td>{{ formatNumber(row.video_count) }}</td>
          <td>{{ formatNumber(row.median_likes) }}</td>
          <td>{{ formatPercent(row.like_fan_ratio) }}</td>
          <td>{{ formatNumber(row.product_count) }}</td>
          <td>{{ formatSettlement(row) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
