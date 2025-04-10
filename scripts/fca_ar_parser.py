from playwright.sync_api import sync_playwright
import time, json


def get_firm_id_from_frn(frn):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=50)
        page = browser.new_page()

        search_url = f"https://register.fca.org.uk/s/search?q={frn}&type=Companies"
        page.goto(search_url)

        page.wait_for_selector(".result-card", timeout=10000)
        cards = page.locator(".result-card")
        count = cards.count()

        for i in range(count):
            card = cards.nth(i)
            if frn in card.inner_text():
                firm_link = card.locator("a").first
                href = firm_link.get_attribute("href")
                firm_id = href.split("id=")[-1]
                browser.close()
                return firm_id

        browser.close()
        return None


def scrape_all_reps_using_show_all_button(firm_id):
    url = f"https://register.fca.org.uk/s/firm?id={firm_id}#who-is-this-firm-connected-to-appointed-representatives"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=50)
        page = browser.new_page()
        page.goto(url)

        try:
            page.wait_for_selector("button:has-text('Allow All')", timeout=5000)
            page.click("button:has-text('Allow All')")
            print("[✓] Accepted cookies")
        except:
            print("[✓] No cookie prompt appeared")

        try:
            accordion = page.locator("#who-is-this-firm-connected-to-appointed-representatives-button")
            if accordion.get_attribute("aria-expanded") == "false":
                accordion.click()
                print("[✓] Expanded section")
                time.sleep(1)
        except:
            print("[!] Accordion section already open or failed")

        try:
            print("[INFO] Clicking 'Show all results' button...")
            show_all_button = page.locator("#appointed-rep-table-resultcountselect-button")
            show_all_button.click()
            time.sleep(3)
        except Exception as e:
            print("[ERROR] Could not click 'Show all results':", e)
            browser.close()
            return []

        page.wait_for_selector("table", timeout=10000)
        rows = page.query_selector_all("tr.data-table__row")

        reps = []
        for row in rows:
            tds = row.query_selector_all("td")
            if any(td.get_attribute("id") and td.get_attribute("id").startswith("appointed-rep-table-all-results-table") for td in tds):
                if len(tds) >= 7:
                    rep = {
                        "name": tds[0].inner_text().strip(),
                        "insurance_distribution": tds[1].inner_text().strip(),
                        "tied_agent": tds[2].inner_text().strip(),
                        "eea_tied_agent": tds[3].inner_text().strip(),
                        "ar_relationship": tds[4].inner_text().strip(),
                        "firm_reference_number": tds[5].inner_text().strip(),
                        "effective_from": tds[6].inner_text().strip(),
                    }
                    reps.append(rep)

        print(f"[✓] Scraped {len(reps)} reps using 'Show all results'")
        browser.close()
        return reps

import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

def process_row(index, row, df, file):
    frn = row["SearchedFCANumber"]
    print(f"[INFO] FRN: {frn}")

    total_reps = row["NumberOfCurrentARs"]
    print(f"[INFO] Reported Total ARs: {total_reps}")

    if total_reps < 10:
        return

    firm_id = get_firm_id_from_frn(str(frn))
    print(f"[✓] Found Firm ID: {firm_id}")

    if firm_id:
        reps = scrape_all_reps_using_show_all_button(firm_id)
        df.at[index, 'ARDetails'] = json.dumps(reps)
        df.to_csv(file, index=False)
    else:
        print("[X] Could not find firm.")

if __name__ == "__main__":
    file = "path_to_your_file.csv"
    df = pd.read_csv(file)

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_row, index, row, df, file): index for index, row in df.iterrows()}

        for future in as_completed(futures):
            index = futures[future]
            try:
                future.result()
            except Exception as e:
                print(f"[ERROR] Exception occurred for index {index}: {e}")
