def create_SINGLE_table(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS SINGLE (
            id INTEGER PRIMARY KEY,
            success BOOLEAN CHECK (success IN (0, 1) OR success IS NULL),

            
            refaligner_version TEXT,

            nlv REAL,
            plv REAL,
            bpp REAL,
            res REAL,
            sd REAL,
            sf REAL,
            sr REAL,

            
            total_molecules INTEGER,
            total_length_mbp REAL,
            avg_length_kbp REAL,
            molecule_n50_kbp REAL,
            label_density REAL,

           
            aligned_molecules_ref INTEGER,
            fraction_aligned_molecules REAL,
            total_molecule_align_length_mbp REAL,
            total_reference_align_length_mbp REAL,
            effective_coverage_ref_x REAL,
            avg_aligned_length_kbp REAL,
            fraction_aligned_length REAL,
            avg_confidence_ref REAL,

            
            cnv_deletion INTEGER,
            cnv_deletion_masked INTEGER,
            cnv_duplication INTEGER,
            cnv_duplication_masked INTEGER,

            sv_type TEXT,
            deletions INTEGER,
            insertions INTEGER,
            duplications INTEGER,
            inversion_breakpoints INTEGER,
            interchr_translocation_breakpoints INTEGER,
            intrachr_translocation_breakpoints INTEGER
        )
    ''')