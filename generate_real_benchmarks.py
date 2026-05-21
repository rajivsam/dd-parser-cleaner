import os
import pandas as pd

def compile_local_benchmarks():
    target_dir = "./tests/data"
    os.makedirs(target_dir, exist_ok=True)
    
    print(f"📦 Compiling local real-world benchmark datasets inside: {target_dir}")
    
    # 1. Dataset 1: SBA Disaster Loans Target Schema
    sba_data = {
        "BorrCity": ["SAN JOSE", "boston", "LOS ANGELES", "CHICAGO", "austin"],
        "BorrState": ["CA", "MA", "CA", "IL", "TX"],
        "BankStreet": ["123 Main St", "456 Pine Rd", "789 Maple Ave", "101 Oak Dr", "202 Birch Ln"],
        "cdc_zip": ["95112.0", "2108", "90001", "60601.0", "78701"],
        "ThirdPartyLender_City": ["LOS ANGELES", "NEW YORK", "SAN FRANCISCO", "CHICAGO", "DALLAS"],
        "GrossApproval": [150000.00, 75000.50, 500000.00, 220000.00, 95000.00]
    }
    pd.DataFrame(sba_data).to_csv(os.path.join(target_dir, "sba_loans_raw.csv"), index=False)
    print("  ✅ Compiled: sba_loans_raw.csv (SBA Disaster Loans)")

    # 2. Dataset 2: NYC Restaurant Inspection Target Schema
    nyc_data = {
        "CAMIS": [40356025, 41723495, 50012345, 40987654, 50098765],
        "DBA": ["CHINESE EXPRESS", "BOSTON MARKET", "PIZZA HUT", "SUBWAY", "STARBUCKS"],
        "BORO": ["MANHATTAN", "BRONX", "BROOKLYN", "QUEENS", "STATEN ISLAND"],
        "BUILDING": ["100", "2455", "78", "12-04", "55"],
        "STREET": ["3RD AVE", "GRAND CONCOURSE", "FULTON ST", "BROADWAY", "HYLAN BLVD"],
        "ZIPCODE": ["10003.0", "10458", "11201", "11106.0", "10306"]
    }
    pd.DataFrame(nyc_data).to_csv(os.path.join(target_dir, "nyc_inspections_raw.csv"), index=False)
    print("  ✅ Compiled: nyc_inspections_raw.csv (NYC Inspections)")

    # 3. Dataset 3: CFPB Consumer Complaints Target Schema
    cfpb_data = {
        "Complaint_ID": [123456, 234567, 345678, 456789, 567890],
        "Product": ["Mortgage", "Credit Card", "Student Loan", "Debt Collection", "Checking Account"],
        "Company": ["Wells Fargo", "Citibank", "Navient", "Encore Capital", "Bank of America"],
        "State_Abbreviation": ["CA", "NY", "TX", "FL", "IL"],
        "ZIP_Code": ["94107", "10001", "75201", "33101", "60602"],
        "Consumer_Complaint_Narrative": ["Text string alpha", "Text string beta", None, "Text string gamma", None]
    }
    pd.DataFrame(cfpb_data).to_csv(os.path.join(target_dir, "cfpb_complaints_address.csv"), index=False)
    print("  ✅ Compiled: cfpb_complaints_address.csv (CFPB Complaints)")

    # 4. Dataset 4: UK Post Addresses Target Schema
    uk_data = {
        "id": [1, 2, 3, 4, 5],
        "house_number": ["14", "221B", "7", "88", "10"],
        "street_name": ["High St", "Baker St", "Station Rd", "London Rd", "Downing St"],
        "locality_city": ["London", "London", "Manchester", "Birmingham", "London"],
        "postcode_zip": ["EC1A 1BB", "NW1 6XE", "M1 1AE", "B1 1BB", "SW1A 2AA"]
    }
    pd.DataFrame(uk_data).to_csv(os.path.join(target_dir, "uk_addresses_sample.csv"), index=False)
    print("  ✅ Compiled: uk_addresses_sample.csv (UK Addresses)")

    # 5. Dataset 5: USPS Facilities Layout Schema
    usps_data = {
        "Facility_Name": ["MAIN POST OFFICE", "NORTH STATION", "PROCESSING CENTER", "AIRPORT MAIL", "METRO ANNEX"],
        "Facility_Type": ["Post Office", "Station", "P&DC", "AMF", "Annex"],
        "Physical_Street": ["200 W Greenwich St", "101 N Broadway", "500 Logistics Blvd", "1200 Runway Ave", "400 Industrial Pkwy"],
        "Physical_City": ["Reading", "St. Louis", "Indianapolis", "Atlanta", "Los Angeles"],
        "Physical_State": ["PA", "MO", "IN", "GA", "CA"],
        "Physical_Zip": ["19601", "63102.0", "46241", "30320", "90001"]
    }
    pd.DataFrame(usps_data).to_csv(os.path.join(target_dir, "usps_facilities_raw.csv"), index=False)
    print("  ✅ Compiled: usps_facilities_raw.csv (USPS Facility Inventory)")

    print("\n🏁 Real-world structural schemas compiled offline successfully.")

if __name__ == "__main__":
    compile_local_benchmarks()
