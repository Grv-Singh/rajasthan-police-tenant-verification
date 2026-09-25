#!/usr/bin/env python3
"""
Rajasthan Police Tenant Verification Automation Tool
Automates online tenant police verification submission on the Rajasthan Police portal.
Portal URL: https://police.rajasthan.gov.in/old/verificationform.aspx
"""

import os
import sys
import json
import time
import argparse
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

PORTAL_URL = "https://police.rajasthan.gov.in/old/verificationform.aspx"

def compress_image_if_needed(image_path, max_kb=180):
    """Ensure images comply with portal's strict < 200 KB limit."""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"File not found: {image_path}")

    size_kb = os.path.getsize(image_path) / 1024
    if size_kb <= max_kb:
        return image_path

    out_path = f"/tmp/compressed_{os.path.basename(image_path)}"
    im = Image.open(image_path)
    im = im.convert("RGB")
    
    # Resize if dimensions are overly large
    w, h = im.size
    if max(w, h) > 1200:
        scale = 1200 / max(w, h)
        im = im.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
    
    quality = 80
    while quality >= 30:
        im.save(out_path, "JPEG", quality=quality, optimize=True)
        if os.path.getsize(out_path) / 1024 <= max_kb:
            break
        quality -= 10

    print(f"Compressed {image_path} ({size_kb:.1f} KB -> {os.path.getsize(out_path)/1024:.1f} KB)")
    return out_path

def run_verification(config, headless=True):
    tenant = config.get("tenant", {})
    landlord = config.get("landlord", {})
    rented = config.get("rented_property", {})

    # Compress photos
    photo_file = compress_image_if_needed(tenant["photo_path"])
    id_file = compress_image_if_needed(tenant["id_proof_path"])

    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    # Auto-detect chrome
    chrome_bin = "/usr/bin/google-chrome"
    if os.path.exists(chrome_bin):
        options.binary_location = chrome_bin

    driver = webdriver.Chrome(options=options)
    try:
        print(f"Connecting to Rajasthan Police portal: {PORTAL_URL}")
        driver.get(PORTAL_URL)
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_rbtnType_1")))

        print("1. Selecting Tenant Uploads...")
        driver.find_element(By.ID, "ContentPlaceHolder1_rbtnType_1").click()
        time.sleep(2.5)

        print("2. Filling Photo ID details...")
        Select(driver.find_element(By.ID, "ContentPlaceHolder1_ddlTIdCardType")).select_by_visible_text(tenant.get("id_type", "Aadhar Card"))
        driver.find_element(By.ID, "ContentPlaceHolder1_txtTIdNo").send_keys(tenant.get("id_number", "").replace(" ", ""))

        print("3. Filling Tenant Name & Parentage...")
        driver.find_element(By.ID, "ContentPlaceHolder1_txtTFirstName").send_keys(tenant.get("first_name", ""))
        driver.find_element(By.ID, "ContentPlaceHolder1_txtTLastName").send_keys(tenant.get("last_name", ""))
        driver.find_element(By.ID, "ContentPlaceHolder1_txtTFirstFName").send_keys(tenant.get("father_first_name", ""))
        driver.find_element(By.ID, "ContentPlaceHolder1_txtTMIddleFName").send_keys(tenant.get("father_middle_name", ""))
        driver.find_element(By.ID, "ContentPlaceHolder1_txtTLastFName").send_keys(tenant.get("father_last_name", ""))

        print("4. Filling Gender & Caste...")
        Select(driver.find_element(By.ID, "ContentPlaceHolder1_ddlTSex")).select_by_visible_text(tenant.get("gender", "Male"))
        Select(driver.find_element(By.ID, "ContentPlaceHolder1_ddlTCaste")).select_by_visible_text(tenant.get("caste", "BRAHMIN"))

        print("5. Setting DOB & Age...")
        driver.find_element(By.ID, "ContentPlaceHolder1_rdbtnTDOB_0").click()
        time.sleep(1)
        dob = driver.find_element(By.ID, "ContentPlaceHolder1_txtTDOB")
        driver.execute_script("arguments[0].value = arguments[1];", dob, tenant.get("dob", ""))
        age = driver.find_element(By.ID, "ContentPlaceHolder1_txtTAge")
        driver.execute_script("arguments[0].value = arguments[1];", age, str(tenant.get("age", "")))

        print(f"6. Selecting Tenant Location ({tenant.get('state')}, {tenant.get('district')}, {tenant.get('police_station')})...")
        Select(driver.find_element(By.ID, "ContentPlaceHolder1_ddlTState")).select_by_visible_text(tenant.get("state", "RAJASTHAN"))
        time.sleep(3)
        Select(driver.find_element(By.ID, "ContentPlaceHolder1_ddlTDistrict")).select_by_visible_text(tenant.get("district", "RAJSAMAND"))
        time.sleep(3)
        Select(driver.find_element(By.ID, "ContentPlaceHolder1_ddlTStation")).select_by_visible_text(tenant.get("police_station", "NATHADAWARA"))

        print("7. Setting Tenant Mobile & Permanent Address...")
        driver.find_element(By.ID, "ContentPlaceHolder1_txtTtntNo").send_keys(tenant.get("mobile", ""))
        driver.find_element(By.ID, "ContentPlaceHolder1_txtTAddress").send_keys(tenant.get("permanent_address", ""))

        print("8. Setting Property Address...")
        Select(driver.find_element(By.ID, "ContentPlaceHolder1_ddlpurpose")).select_by_visible_text(rented.get("purpose", "Residence"))
        driver.find_element(By.ID, "ContentPlaceHolder1_txtaddressofrented").send_keys(rented.get("address", ""))

        print("9. Filling Landlord Information...")
        driver.find_element(By.ID, "ContentPlaceHolder1_txtLFirstName").send_keys(landlord.get("first_name", ""))
        driver.find_element(By.ID, "ContentPlaceHolder1_txtLLastName").send_keys(landlord.get("last_name", ""))
        driver.find_element(By.ID, "ContentPlaceHolder1_txtLFirstFName").send_keys(landlord.get("father_first_name", ""))
        driver.find_element(By.ID, "ContentPlaceHolder1_txtLMIddleFName").send_keys(landlord.get("father_middle_name", ""))
        driver.find_element(By.ID, "ContentPlaceHolder1_txtLLastFName").send_keys(landlord.get("father_last_name", ""))
        driver.find_element(By.ID, "ContentPlaceHolder1_txtlandMobno").send_keys(landlord.get("mobile", ""))
        driver.find_element(By.ID, "ContentPlaceHolder1_txtlandPAddress").send_keys(landlord.get("address", ""))

        print(f"10. Selecting Landlord Police Station ({landlord.get('district')}, {landlord.get('police_station')})...")
        Select(driver.find_element(By.ID, "ContentPlaceHolder1_ddlLdistrict")).select_by_visible_text(landlord.get("district", "JAIPUR SOUTH"))
        time.sleep(3)
        Select(driver.find_element(By.ID, "ContentPlaceHolder1_ddlLStation")).select_by_visible_text(landlord.get("police_station", "JYOTI NAGAR"))

        driver.find_element(By.ID, "ContentPlaceHolder1_txtLRefer").send_keys(landlord.get("referenced_by", ""))

        print("11. Uploading Documents...")
        driver.find_element(By.ID, "ContentPlaceHolder1_flTPhoto").send_keys(os.path.abspath(photo_file))
        driver.find_element(By.ID, "ContentPlaceHolder1_flTPhotoId").send_keys(os.path.abspath(id_file))
        time.sleep(1)

        print("12. Submitting Form...")
        save_btn = driver.find_element(By.ID, "ContentPlaceHolder1_btnTSave")
        driver.execute_script("arguments[0].scrollIntoView(true);", save_btn)
        time.sleep(1)
        save_btn.click()

        # Handle post-submission alert
        time.sleep(4)
        reference_no = None
        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            print(f"Portal Response: {alert_text}")
            alert.accept()
            # Extract reference number if present
            if "Reference Number is" in alert_text:
                reference_no = alert_text.split("Reference Number is")[-1].replace(".", "").strip()
        except Exception:
            pass

        screenshot_path = "verification_submission.png"
        driver.save_screenshot(screenshot_path)
        print(f"Saved confirmation screenshot to {screenshot_path}")

        if reference_no:
            print(f"\nSUCCESS! Verification Reference Number: {reference_no}")
        else:
            print("\nSubmission completed. Please check confirmation screenshot.")

        return reference_no

    finally:
        driver.quit()

def main():
    parser = argparse.ArgumentParser(description="Rajasthan Police Tenant Verification Automation")
    parser.add_argument("--config", "-c", default="config.json", help="Path to JSON configuration file")
    parser.add_argument("--no-headless", action="store_true", help="Run with browser window visible")
    args = parser.parse_args()

    if not os.path.exists(args.config):
        print(f"Error: Config file '{args.config}' not found. Please create one using config.example.json.")
        sys.exit(1)

    with open(args.config, "r", encoding="utf-8") as f:
        config = json.load(f)

    run_verification(config, headless=not args.no_headless)

if __name__ == "__main__":
    main()
