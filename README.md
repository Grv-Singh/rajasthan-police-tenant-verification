# Rajasthan Police Tenant Verification Automation 👮‍♂️🏠

Automate online tenant police verification submission on the official **Rajasthan Police Citizen Portal** (`https://police.rajasthan.gov.in/old/verificationform.aspx`).

Designed for landlords, property owners, and property managers to submit tenant verification forms quickly, avoid manual errors, and automatically handle portal requirements (such as image compression and district/station cascading dropdowns).

---

## Features

- **End-to-End Automation:** Fills tenant details, landlord details, and property addresses seamlessly.
- **Smart Image Compression:** Automatically compresses photos and Aadhaar ID proofs to under 200 KB as strictly mandated by the government portal.
- **Cascading Dropdowns Handled:** Automatically executes ASP.NET PostBacks for State -> District -> Police Station mappings.
- **Zero Captcha/OTP Friction:** Directly captures and prints the official **Verification Reference Number**.
- **Proof Screenshot:** Automatically saves a timestamped confirmation screenshot of the submission.

---

## Prerequisites

1. **Python 3.8+**
2. **Google Chrome** & matching **ChromeDriver** installed on system PATH.

Install Python dependencies:
```bash
pip install -r requirements.txt
```

---

## Quick Start

### 1. Configure Details

Copy `config.example.json` to `config.json`:
```bash
cp config.example.json config.json
```

Edit `config.json` with your tenant and landlord information:
```json
{
  "tenant": {
    "first_name": "Raj",
    "last_name": "Shrimali",
    "father_first_name": "Pratul",
    "father_middle_name": "Kumar",
    "father_last_name": "Shrimali",
    "gender": "Male",
    "caste": "BRAHMIN",
    "dob": "11/12/2001",
    "age": "24",
    "state": "RAJASTHAN",
    "district": "RAJSAMAND",
    "police_station": "NATHADAWARA",
    "mobile": "999999999",
    "permanent_address": "xyz",
    "id_type": "Aadhar Card",
    "id_number": "999999999",
    "photo_path": "tenant_photo.jpg",
    "id_proof_path": "tenant_id.jpg"
  },
  "rented_property": {
    "purpose": "Residence",
    "address": "xyz"
  },
  "landlord": {
    "first_name": "Pramod",
    "last_name": "Chandra",
    "father_first_name": "Ram",
    "father_middle_name": "Charan",
    "father_last_name": "Jagrawal",
    "mobile": "999999999",
    "address": "A-31, Arjunpuri-1, Link Road, Imli Phatak, Jaipur, Rajasthan - 302015",
    "district": "JAIPUR SOUTH",
    "police_station": "JYOTI NAGAR",
    "referenced_by": "GAURAV SINGH 999999999"
  }
}
```

### 2. Run Automation

```bash
python rajasthan_tenant_verification.py --config config.json
```

To run with browser GUI visible:
```bash
python rajasthan_tenant_verification.py --config config.json --no-headless
```

### 3. Output
The tool will submit the verification form and output:
```text
Portal Response: Details Saved Successfully.Your Reference Number is XXXXXX.
Saved confirmation screenshot to verification_submission.png

SUCCESS! Verification Reference Number: XXXXXX
```

---

## License

MIT License. For public utility and open citizen welfare.
