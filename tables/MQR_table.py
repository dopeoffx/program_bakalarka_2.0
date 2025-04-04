def create_MQR_table(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS MQR (
            id INTEGER PRIMARY KEY,
            success BOOLEAN CHECK (success IN (0, 1) OR success IS NULL),

            input_bnx_file TEXT,
            input_reference_file TEXT,
            output_folder TEXT,
            min_nicks_channel1 INTEGER,
            min_length_kb INTEGER,
            snr_cutoff_channel1 REAL,

            instrument_sn TEXT,
            chip_sn TEXT,
            run_id TEXT,
            sample TEXT,
            flowcell INTEGER,
            total_scan_count TEXT,
            job_id INTEGER,
            job_created_on TEXT,
            total_molecules_input_bnx INTEGER,

            refaligner_path TEXT,

            num_molecules_filtered INTEGER,
            total_molecule_length_bp REAL,
            avg_molecule_length_bp REAL,
            molecule_length_n50_bp REAL,
            total_dna_20kb REAL,
            n50_20kb REAL,
            total_dna_150kb_min9 REAL,
            n50_150kb_min9 REAL,
            num_molecules_20kb INTEGER,
            num_molecules_150kb INTEGER,
            num_molecules_150kb_min9 INTEGER,

            avg_label_density REAL,
            avg_label_snr REAL,
            avg_molecule_snr REAL,
            avg_label_intensity REAL,
            avg_molecule_intensity REAL
        )
    ''')