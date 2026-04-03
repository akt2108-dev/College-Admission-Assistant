from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# --- SET YOUR CHROMEDRIVER PATH ---
driver = webdriver.Chrome()

url = "https://admissions.nic.in/hbtu/Applicant/report/orcrreport.aspx?enc=Nm7QwHILXclJQSv2YVS+7oLKks/GGbnQ7ubUTkehsd6ZYPFTiVJMMyl0WClS+XgX"
driver.get(url)

wait = WebDriverWait(driver, 10)

# Wait for dropdown to load
wait.until(EC.presence_of_element_located((By.TAG_NAME, "select")))

# Find round dropdown (auto detect)
dropdown = driver.find_element(By.TAG_NAME, "select")
select = Select(dropdown)

all_data = []

# Detect number of rounds
dropdown = driver.find_element(By.TAG_NAME, "select")
select = Select(dropdown)
round_count = len(select.options)

for i in range(round_count):

    # Re-fetch dropdown
    dropdown = driver.find_element(By.TAG_NAME, "select")
    select = Select(dropdown)
    options = select.options

    round_name = options[i].text
    print(f"\nScraping Round: {round_name}")

    select.select_by_index(i)
    time.sleep(2)

    while True:
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

        table = driver.find_element(By.TAG_NAME, "table")
        rows = table.find_elements(By.TAG_NAME, "tr")

        headers = [th.text for th in rows[0].find_elements(By.TAG_NAME, "th")]

        for row in rows[1:]:
            cols = row.find_elements(By.TAG_NAME, "td")
            if cols:
                row_data = [col.text for col in cols]
                row_data.append(round_name)
                all_data.append(row_data)

        # Try to find "Next" button
        try:
            next_button = driver.find_element(By.LINK_TEXT, "Next")

            # Check if disabled
            if "disabled" in next_button.get_attribute("class").lower():
                break

            next_button.click()
            time.sleep(2)

        except:
            # No next button found
            break

# Close browser
driver.quit()

# Create DataFrame
headers.append("Round_Name")
df = pd.DataFrame(all_data, columns=headers)

df.to_csv("hbtu_all_rounds_orcr_2023.csv", index=False)

print("Done. CSV saved as hbtu_all_rounds_orcr_2023.csv")