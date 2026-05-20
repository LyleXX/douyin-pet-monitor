import { readFileSync } from "node:fs"

const appSource = readFileSync(new URL("../src/App.vue", import.meta.url), "utf8")
const composableSource = readFileSync(
  new URL("../src/composables/useCreators.ts", import.meta.url),
  "utf8",
)

const failures = []

if (appSource.includes("onMounted")) {
  failures.push("App.vue must not call backend commands from onMounted/startup.")
}

const importCsvBody = composableSource.match(/async function importCsvFile[\s\S]*?\n  }/)
if (importCsvBody?.[0].includes("loadRecords()")) {
  failures.push("Import button must not trigger an extra list command after import-csv.")
}

if (failures.length) {
  console.error(failures.join("\n"))
  process.exit(1)
}
