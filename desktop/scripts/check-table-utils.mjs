import assert from "node:assert/strict"
import { readFileSync, writeFileSync } from "node:fs"
import { tmpdir } from "node:os"
import { join } from "node:path"
import { pathToFileURL } from "node:url"
import { transformSync } from "esbuild"

const sourcePath = new URL("../src/tableUtils.ts", import.meta.url)
const source = readFileSync(sourcePath, "utf8")
const compiled = transformSync(source, {
  format: "esm",
  loader: "ts",
  target: "es2022",
}).code

const outputPath = join(tmpdir(), `table-utils-${Date.now()}.mjs`)
writeFileSync(outputPath, compiled)

const {
  getDouyinWebProfileUrl,
  nextSortState,
  sortCreatorRows,
} = await import(pathToFileURL(outputPath).href)

const rows = [
  {
    nickname: "B",
    douyin_id: "beta id",
    web_profile_url: "",
    fans: 100,
    creator_level: 2,
    video_count: 10,
    median_likes: 4,
    like_fan_ratio: 0.02,
    product_count: 2,
    settlement_mid: 100,
    score: 20,
  },
  {
    nickname: "A",
    douyin_id: "alpha",
    web_profile_url: "https://www.douyin.com/user/real-sec-id?from_tab_name=main",
    fans: 300,
    creator_level: 5,
    video_count: 20,
    median_likes: 8,
    like_fan_ratio: 0.05,
    product_count: 8,
    settlement_mid: 900,
    score: 80,
  },
]

assert.deepEqual(
  sortCreatorRows(rows, { key: "fans", direction: "asc" }).map((row) => row.nickname),
  ["B", "A"],
)
assert.deepEqual(
  sortCreatorRows(rows, { key: "fans", direction: "desc" }).map((row) => row.nickname),
  ["A", "B"],
)
assert.deepEqual(
  sortCreatorRows(rows, { key: "nickname", direction: "asc" }).map((row) => row.nickname),
  ["A", "B"],
)
assert.deepEqual(nextSortState({ key: "score", direction: "desc" }, "score"), {
  key: "score",
  direction: "asc",
})
assert.deepEqual(nextSortState({ key: "score", direction: "asc" }, "fans"), {
  key: "fans",
  direction: "desc",
})
assert.equal(
  getDouyinWebProfileUrl({ douyin_id: "alpha", web_profile_url: "https://www.douyin.com/user/real-sec-id?from_tab_name=main" }),
  "https://www.douyin.com/user/real-sec-id?from_tab_name=main",
)
assert.equal(
  getDouyinWebProfileUrl({ douyin_id: "beta id", web_profile_url: "" }),
  "https://www.douyin.com/search/beta%20id?type=user",
)

console.log("table utils ok")
