from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright


def main() -> None:
    """Open the desktop frontend dev URL for smoke testing only."""
    url = "http://localhost:1420"
    screenshot_path = Path("exports") / "desktop_frontend.png"
    screenshot_path.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto(url, wait_until="domcontentloaded")
        page.screenshot(path=str(screenshot_path), full_page=True)
        browser.close()

    print(f"Saved screenshot: {screenshot_path}")


if __name__ == "__main__":
    main()
