def create_PIPELINE_table(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS PIPELINE (
            id INTEGER PRIMARY KEY ,
            success BOOLEAN CHECK (success IN (0, 1) OR success IS NULL),

            tools_version TEXT,
            solve_version TEXT,
            pipeline_version TEXT,
            refaligner_version TEXT,

            total_molecules_unfiltered INTEGER,
            total_length_unfiltered_mbp REAL,
            avg_length_unfiltered_kbp REAL,
            n50_unfiltered_kbp REAL,
            label_density_unfiltered REAL,

            total_molecules_filtered INTEGER,
            total_length_filtered_mbp REAL,
            avg_length_filtered_kbp REAL,
            n50_filtered_kbp REAL,
            label_density_filtered REAL,
            ref_coverage_filtered_x REAL,

            aligned_molecules_ref INTEGER,
            effective_ref_coverage_x REAL,
            avg_confidence_ref REAL,

            diploid_map_count INTEGER,
            diploid_map_length_mbp REAL,
            diploid_map_n50_mbp REAL,

            haploid_map_count INTEGER,
            haploid_map_length_mbp REAL,
            haploid_map_n50_mbp REAL,

            total_reference_length_mbp REAL,
            genome_maps_aligned INTEGER,
            genome_maps_aligned_fraction REAL,
            unique_aligned_length_mbp REAL,
            unique_aligned_length_fraction REAL,

            aligned_molecules_assembly INTEGER,
            fraction_aligned_molecules REAL,
            effective_coverage_assembly_x REAL,
            avg_confidence_assembly REAL,

            sv_type TEXT,
            deletions INTEGER,
            insertions INTEGER,
            duplications INTEGER,
            inversion_breakpoints INTEGER,
            interchr_translocation_breakpoints INTEGER,
            intrachr_translocation_breakpoints INTEGER
        )
    ''')