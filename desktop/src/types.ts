export interface CreatorRecord {
  nickname: string
  profile_url: string
  douyin_id: string
  web_profile_url: string
  fans: number
  category: string
  sales_30d: number
  gmv_30d: number
  product_count: number
  live_count_7d: number
  median_likes: number
  creator_level: number
  video_count: number
  like_fan_ratio: number
  settlement_range: string
  settlement_min: number
  settlement_max: number
  settlement_mid: number
  sales_per_fan: number
  score: number
  imported_at: string
  updated_at: string
}

export interface ImportResult {
  imported: number
  total: number
  records: CreatorRecord[]
}

export interface ExportResult {
  output_path: string
  rows: number
}

export interface FilterState {
  fansMin: number | string
  fansMax: number | string
  salesMin: number | string
  salesMax: number | string
  creatorLevelMin: number | string
  creatorLevelMax: number | string
  productCountMin: number | string
  productCountMax: number | string
  likeFanRatioMin: number | string
  likeFanRatioMax: number | string
  settlementMin: number | string
  settlementMax: number | string
  categories: string[]
}
