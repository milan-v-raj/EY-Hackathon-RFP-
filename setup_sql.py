# setup_sql.py
import sqlite3

def create_db():
    conn = sqlite3.connect('pricing_data.db')
    cursor = conn.cursor()

    # 1. Cleanup old data to prevent duplicates
    cursor.execute('DROP TABLE IF EXISTS material_pricing')
    cursor.execute('DROP TABLE IF EXISTS service_pricing')

    # 2. Re-create Tables
    cursor.execute('''
        CREATE TABLE material_pricing (
            sku_id TEXT PRIMARY KEY,
            description TEXT,
            unit_price REAL,
            currency TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE service_pricing (
            service_id TEXT PRIMARY KEY,
            description TEXT,
            cost REAL
        )
    ''')

    # 3. COMPREHENSIVE PRODUCT LIST (Extracted from Datasheets)
    # Prices are estimated based on typical B2B bulk rates (INR per Meter)
    materials = [
        # --- STANDARD (HAVELLS) - HOME SHIELD & FR PVC (Pages 6-8) ---
        ('WSFFDN...A1X507', 'Standard Home Shield 0.5 sq.mm FR PVC Flexible Wire', 12.00, 'INR'),
        ('WSFFDN...A1X757', 'Standard Home Shield 0.75 sq.mm FR PVC Flexible Wire', 16.50, 'INR'),
        ('WSFFDN...A11X07', 'Standard Home Shield 1.0 sq.mm FR PVC Flexible Wire', 22.00, 'INR'),
        ('WSFFDN...A11X57', 'Standard Home Shield 1.5 sq.mm FR PVC Flexible Wire', 32.00, 'INR'),
        ('WSFFDN...A12X57', 'Standard Home Shield 2.5 sq.mm FR PVC Flexible Wire', 48.00, 'INR'),
        ('WSFFDN...A14X07', 'Standard Home Shield 4.0 sq.mm FR PVC Flexible Wire', 72.00, 'INR'),
        ('WSFFDN...A16X07', 'Standard Home Shield 6.0 sq.mm FR PVC Flexible Wire', 105.00, 'INR'),
        
        # --- STANDARD (HAVELLS) - HIGHER SIZE INDUSTRIAL (Page 8) ---
        ('WSFFDN...B1010', 'Standard 10 sq.mm Single Core FR PVC Cable', 180.00, 'INR'),
        ('WSFFDN...B1016', 'Standard 16 sq.mm Single Core FR PVC Cable', 275.00, 'INR'),
        ('WSFFDN...B1035', 'Standard 35 sq.mm Single Core FR PVC Cable', 620.00, 'INR'),
        ('WSFFDN...B1050', 'Standard 50 sq.mm Single Core FR PVC Cable', 890.00, 'INR'),

        # --- STANDARD (HAVELLS) - MULTICORE ROUND (Page 12) ---
        ('WSMFDSKB_2X5', 'Standard 2 Core 2.5 sq.mm Round Flexible Cable', 110.00, 'INR'),
        ('WSMFDSKB_3X1.5', 'Standard 3 Core 1.5 sq.mm Round Flexible Cable', 105.00, 'INR'),
        ('WSMFDSKB_4X0', 'Standard 4 Core 4.0 sq.mm Round Flexible Cable', 310.00, 'INR'),
        ('WSMFDSKB_4X10', 'Standard 4 Core 10 sq.mm Round Flexible Cable', 850.00, 'INR'),

        # --- RIYADH CABLES - SINGLE CORE 450/750V (Page 2-4) ---
        ('OC 010004xx', 'Riyadh 1x1.5mm Solid Copper PVC Wire (450/750V)', 28.00, 'INR'),
        ('OC 010006xx', 'Riyadh 1x4mm Solid Copper PVC Wire (450/750V)', 68.00, 'INR'),
        ('OC 010105xx', 'Riyadh 1x2.5mm Stranded Copper PVC Wire', 45.00, 'INR'),
        ('OC 010106xx', 'Riyadh 1x4mm Stranded Copper PVC Wire', 70.00, 'INR'),
        ('OC 010109xx', 'Riyadh 1x16mm Stranded Copper PVC Wire', 260.00, 'INR'),
        ('OC 010506xx', 'Riyadh 1x4mm Flexible Conductor PVC Wire', 74.00, 'INR'),

        # --- RIYADH CABLES - MULTICORE SHEATHED 300/500V (Page 5) ---
        ('OB 01002508', 'Riyadh 2 Core 2.5mm PVC Sheathed Cable', 115.00, 'INR'),
        ('OB 01003608', 'Riyadh 3 Core 4mm PVC Sheathed Cable', 240.00, 'INR'),
        ('OB 01004808', 'Riyadh 4 Core 10mm PVC Sheathed Cable', 900.00, 'INR'),
        ('OB 01005708', 'Riyadh 5 Core 6mm PVC Sheathed Cable', 650.00, 'INR'),

        # --- RIYADH CABLES - THHN/THWN (US Standard - Page 11) ---
        ('THHN_14_AWG', 'Riyadh THHN/THWN 14 AWG Copper Wire', 25.00, 'INR'),
        ('THHN_12_AWG', 'Riyadh THHN/THWN 12 AWG Copper Wire', 38.00, 'INR'),
        ('THHN_1/0_AWG', 'Riyadh THHN/THWN 1/0 AWG Copper Cable', 450.00, 'INR'),

        # --- FALLBACKS ---
        ('GENERIC_4SQMM', 'Generic 4.0 sq.mm Copper Cable', 65.00, 'INR'),

        # --- NEW: IMPERFECT MATCHES FOR SDSC SHAR RFP (80% Confidence Targets) ---
        # 1. Target: Item 1 (25 Core Armored) - PVC vs HDPE mismatch
        ('CTRL_25C_1.5_PVC', '25 Core 1.5 sq.mm Copper Control Cable, PVC Insulated, Armoured, Black Sheath', 4500.00, 'INR'),

        # 2. Target: Item 2 (12 Pair Armored) - PVC vs PE mismatch, smaller size
        ('INST_12P_0.5_ARM', '12 Pair 0.5 sq.mm ATC Instrumentation Cable, PVC Insulated, Overall Screened, Armoured', 1200.00, 'INR'),

        # 3. Target: Item 5 (18 Pair Armored) - PVC vs PE mismatch
        ('INST_18P_0.5_ARM', '18 Pair 0.5 sq.mm ATC Instrumentation Cable, PVC Insulated, Overall Screened, Armoured', 1850.00, 'INR'),

        # 4. Target: Item 6 (Armored Cat6) - 24 AWG vs 23 AWG mismatch, SWA vs ECCS Tape
        ('LAN_CAT6_ARM_STD', 'Cat6 STP Armoured Cable, 4 Pair, 24 AWG Solid Copper, Steel Wire Armoured (SWA), Outdoor', 85.00, 'INR'),

        # 5. Target: Item 7 (PTFE Wire) - Silver Plated Generic
        ('EQ_PTFE_19_STR', 'PTFE Insulated Hook-up Wire, Silver Plated Copper, 19 Strand, 600V Grade', 45.00, 'INR')
    ]
    
    # 4. SERVICES LIST (Testing, Logistics, Certification)
    services = [
        # Testing Services
        ('TEST_HV_SPARK', 'High Voltage Spark Test (3.5kV)', 2500.00),
        ('TEST_RESISTANCE', 'Conductor Resistance Test (Lab)', 1500.00),
        ('TEST_FLAMMABILITY', 'Flammability & Smoke Density Test (IS:10810)', 4500.00),
        ('TEST_INSULATION', 'Insulation Resistance (IR) Test', 1200.00),
        ('TEST_AGING', 'Thermal Aging Test (7 Days)', 8000.00),
        
        # Logistics & Packaging
        ('PKG_DRUM_WOOD', 'Wooden Drum Packaging (per 500m)', 3500.00),
        ('PKG_DRUM_STEEL', 'Steel Drum Packaging (Heavy Duty)', 7500.00),
        ('LOGISTICS_LOCAL', 'Local Delivery (upto 50km)', 2000.00),
        ('LOGISTICS_NATIONAL', 'National Freight (per ton)', 15000.00),
        
        # Certification & Inspection
        ('CERT_TPI', 'Third Party Inspection (TPI) Charges', 10000.00),
        ('CERT_BIS', 'BIS Conformity Certificate Issue', 500.00)
    ]

    cursor.executemany('INSERT OR REPLACE INTO material_pricing VALUES (?,?,?,?)', materials)
    cursor.executemany('INSERT OR REPLACE INTO service_pricing VALUES (?,?,?)', services)

    conn.commit()
    conn.close()
    print(f"✅ SQL Database updated with {len(materials)} Products and {len(services)} Services.")

if __name__ == "__main__":
    create_db()