import type { CreatorRecord } from "./types"

export type SortDirection = "asc" | "desc"

export type SortKey =
  | "score"
  | "nickname"
  | "douyin_id"
  | "fans"
  | "creator_level"
  | "video_count"
  | "median_likes"
  | "like_fan_ratio"
  | "product_count"
  | "settlement_mid"

export interface SortState {
  key: SortKey
  direction: SortDirection
}

const TEXT_SORT_KEYS = new Set<SortKey>(["nickname", "douyin_id"])

function defaultDirectionForKey(key: SortKey): SortDirection {
  return TEXT_SORT_KEYS.has(key) ? "asc" : "desc"
}

function compareValues(left: unknown, right: unknown) {
  if (typeof left === "number" && typeof right === "number") {
    return left - right
  }
  return String(left ?? "").localeCompare(String(right ?? ""), "zh-CN", {
    numeric: true,
    sensitivity: "base",
  })
}

export function nextSortState(current: SortState, key: SortKey): SortState {
  if (current.key === key) {
    return {
      key,
      direction: current.direction === "asc" ? "desc" : "asc",
    }
  }
  return {
    key,
    direction: defaultDirectionForKey(key),
  }
}

export function sortCreatorRows(rows: CreatorRecord[], sort: SortState): CreatorRecord[] {
  const directionMultiplier = sort.direction === "asc" ? 1 : -1
  return [...rows].sort((left, right) => {
    const primary = compareValues(left[sort.key], right[sort.key])
    if (primary !== 0) {
      return primary * directionMultiplier
    }

    const fallback = compareValues(left.nickname, right.nickname)
    if (fallback !== 0) {
      return fallback
    }
    return compareValues(left.douyin_id, right.douyin_id)
  })
}

export function getDouyinWebProfileUrl(row: Pick<CreatorRecord, "douyin_id" | "web_profile_url">): string {
  const webProfileUrl = row.web_profile_url.trim()
  if (webProfileUrl.startsWith("https://www.douyin.com/user/")) {
    return webProfileUrl
  }

  const douyinId = row.douyin_id.trim()
  if (!douyinId) {
    return ""
  }
  return `https://www.douyin.com/search/${encodeURIComponent(douyinId)}?type=user`
}
