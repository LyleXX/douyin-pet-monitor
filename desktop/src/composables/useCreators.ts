import { appLocalDataDir, join } from "@tauri-apps/api/path"
import { ref } from "vue"
import { Command } from "@tauri-apps/plugin-shell"
import type { CreatorRecord, ExportResult, ImportResult } from "../types"

const BACKEND_SIDE_CAR = "binaries/douyin-backend"
const DATABASE_FILE_NAME = "douyin_creator_desk.sqlite"

function parseError(error: unknown): string {
  if (error instanceof Error) {
    return error.message
  }
  return String(error)
}

function parseJson<T>(stdout: string): T {
  return JSON.parse(stdout || "null") as T
}

function toArgList(base: string[], filters: ExportFilters): string[] {
  const args = [...base]

  if (filters.fansMin !== undefined) {
    args.push("--fans-min", String(filters.fansMin))
  }
  if (filters.fansMax !== undefined) {
    args.push("--fans-max", String(filters.fansMax))
  }
  if (filters.salesMin !== undefined) {
    args.push("--sales-min", String(filters.salesMin))
  }
  if (filters.salesMax !== undefined) {
    args.push("--sales-max", String(filters.salesMax))
  }
  if (filters.creatorLevelMin !== undefined) {
    args.push("--creator-level-min", String(filters.creatorLevelMin))
  }
  if (filters.creatorLevelMax !== undefined) {
    args.push("--creator-level-max", String(filters.creatorLevelMax))
  }
  if (filters.productCountMin !== undefined) {
    args.push("--product-count-min", String(filters.productCountMin))
  }
  if (filters.productCountMax !== undefined) {
    args.push("--product-count-max", String(filters.productCountMax))
  }
  if (filters.likeFanRatioMin !== undefined) {
    args.push("--like-fan-ratio-min", String(filters.likeFanRatioMin))
  }
  if (filters.likeFanRatioMax !== undefined) {
    args.push("--like-fan-ratio-max", String(filters.likeFanRatioMax))
  }
  if (filters.settlementMin !== undefined) {
    args.push("--settlement-min", String(filters.settlementMin))
  }
  if (filters.settlementMax !== undefined) {
    args.push("--settlement-max", String(filters.settlementMax))
  }
  for (const category of filters.categories) {
    args.push("--category", category)
  }

  return args
}

interface ExportFilters {
  fansMin?: number
  fansMax?: number
  salesMin?: number
  salesMax?: number
  creatorLevelMin?: number
  creatorLevelMax?: number
  productCountMin?: number
  productCountMax?: number
  likeFanRatioMin?: number
  likeFanRatioMax?: number
  settlementMin?: number
  settlementMax?: number
  categories: string[]
}

export function useCreators() {
  const records = ref<CreatorRecord[]>([])
  const loading = ref(false)
  const errorMessage = ref("")
  const dbPath = ref("")

  async function ensureDbPath() {
    if (!dbPath.value) {
      const dataDir = await appLocalDataDir()
      dbPath.value = await join(dataDir, DATABASE_FILE_NAME)
    }
    return dbPath.value
  }

  async function runBackend<T>(args: string[]): Promise<T> {
    const command = Command.sidecar(BACKEND_SIDE_CAR, args)
    const result = await command.execute()
    if (result.code !== 0) {
      throw new Error(result.stderr.trim() || `后端命令失败：${args[0]}`)
    }
    return parseJson<T>(result.stdout)
  }

  async function loadRecords() {
    const db = await ensureDbPath()
    const next = await runBackend<CreatorRecord[]>(["list", "--db", db])
    records.value = next
    return next
  }

  async function refreshCreators() {
    loading.value = true
    errorMessage.value = ""
    try {
      return await loadRecords()
    } catch (error) {
      errorMessage.value = parseError(error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function importCsvFile(csvPath: string) {
    loading.value = true
    errorMessage.value = ""
    try {
      const db = await ensureDbPath()
      const result = await runBackend<ImportResult>([
        "import-csv",
        "--db",
        db,
        "--csv",
        csvPath,
      ])
      records.value = result.records
      return result
    } catch (error) {
      errorMessage.value = parseError(error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function exportExcelFile(outputPath: string, filters: ExportFilters) {
    loading.value = true
    errorMessage.value = ""
    try {
      const db = await ensureDbPath()
      const args = toArgList(
        ["export-excel", "--db", db, "--output", outputPath],
        filters,
      )
      return await runBackend<ExportResult>(args)
    } catch (error) {
      errorMessage.value = parseError(error)
      throw error
    } finally {
      loading.value = false
    }
  }

  return {
    records,
    loading,
    errorMessage,
    refreshCreators,
    importCsvFile,
    exportExcelFile,
  }
}
