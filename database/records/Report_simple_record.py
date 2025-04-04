import sqlite3
import re
import filtering_functions.find_file as find_file
import os

def Report_simple_record(table_name, id, folder_path, sftp, success, db_name):
    if (table_name=="PIPELINE"):
        file_path= os.path.join(folder_path, "output/exp_informaticsReportSimple.txt")
    else:
        file_path = find_file.find_file(sftp, folder_path, "exp_informaticsReportSimple.txt")
    
    with sftp.open(file_path, 'r') as file:
        try:
            content = file.read().decode('utf-8')
            data = parse_report_content(content, table_name)

            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()

            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?'] * len(data))
            values = list(data.values())

            query = f"INSERT INTO {table_name} (id, success, {columns}) VALUES (?, ?, {placeholders})"
            cursor.execute(query, [id]+ [success]+ values)

            conn.commit()
            conn.close()

            print(f"Záznam s ID {id} byl úspěšně vložen do tabulky {table_name}.\n")
        finally:
            file.close() 
            
        

def parse_report_content(content, table_name):
    data = {}

    patterns_single = {
    "refaligner_version": r"RefAligner Version:\s*(\d+)",

    # Noise parameters
    "nlv": r"NLV:\s*([\d.]+)",
    "plv": r"PLV:\s*([\d.]+)",
    "bpp": r"bpp:\s*([\d.]+)",
    "res": r"res:\s*([\d.]+)",
    "sd": r"sd:\s*([\d.]+)",
    "sf": r"sf:\s*([\d.]+)",
    "sr": r"sr:\s*([\d.]+)",

    # Molecule Stats
    "total_molecules": r"Molecule Stats[\s\S]*?Total number of molecules\s*:\s*(\d+)",
    "total_length_mbp": r"Molecule Stats[\s\S]*?Total length\s*\(Mbp\)\s*:\s*([\d.]+)",
    "avg_length_kbp": r"Molecule Stats[\s\S]*?Average length\s*\(kbp\)\s*:\s*([\d.]+)",
    "molecule_n50_kbp": r"Molecule Stats[\s\S]*?Molecule N50\s*\(kbp\)\s*:\s*([\d.]+)",
    "label_density": r"Molecule Stats[\s\S]*?Label density\s*\(/100kb\)\s*:\s*([\d.]+)",

    # Molecules aligned to reference
    "aligned_molecules_ref": r"Molecules aligned to reference[\s\S]*?Total number of aligned molecules\s*:\s*(\d+)",
    "fraction_aligned_molecules": r"Molecules aligned to reference[\s\S]*?Fraction of aligned molecules\s*:\s*([\d.]+)",
    "total_molecule_align_length_mbp": r"Molecules aligned to reference[\s\S]*?Total molecule align length\s*\(Mbp\)\s*:\s*([\d.]+)",
    "total_reference_align_length_mbp": r"Molecules aligned to reference[\s\S]*?Total reference align length\s*\(Mbp\)\s*:\s*([\d.]+)",
    "effective_coverage_ref_x": r"Molecules aligned to reference[\s\S]*?Effective coverage of reference\s*\(X\)\s*:\s*([\d.]+)",
    "avg_aligned_length_kbp": r"Molecules aligned to reference[\s\S]*?Average aligned length\s*\(kbp\)\s*:\s*([\d.]+)",
    "fraction_aligned_length": r"Molecules aligned to reference[\s\S]*?Fraction aligned length\s*:\s*([\d.]+)",
    "avg_confidence_ref": r"Molecules aligned to reference[\s\S]*?Average confidence\s*:\s*([\d.]+)",

    # CNV summary
    "cnv_deletion": r"CNV summary[\s\S]*?deletion:\s*(\d+)",
    "cnv_deletion_masked": r"CNV summary[\s\S]*?deletion_masked:\s*(\d+)",
    "cnv_duplication": r"CNV summary[\s\S]*?duplication:\s*(\d+)",
    "cnv_duplication_masked": r"CNV summary[\s\S]*?duplication_masked:\s*(\d+)",

    # Final SV summary
    "sv_type": r"Final SV summary[\s\S]*?SV type\s*:\s*(\w+)",
    "deletions": r"Final SV summary[\s\S]*?Deletions\s*:\s*(\d+)",
    "insertions": r"Final SV summary[\s\S]*?Insertions\s*:\s*(\d+)",
    "duplications": r"Final SV summary[\s\S]*?Duplications\s*:\s*(\d+)",
    "inversion_breakpoints": r"Final SV summary[\s\S]*?Inversion breakpoints\s*:\s*(\d+)",
    "interchr_translocation_breakpoints": r"Final SV summary[\s\S]*?Interchr\. translocation breakpoints\s*:\s*(\d+)",
    "intrachr_translocation_breakpoints": r"Final SV summary[\s\S]*?Intrachr\. translocation breakpoints\s*:\s*(\d+)"
    }
    
    patterns = {
    # Versions
    "tools_version": r"Tools Version:\s*(.+)",
    "solve_version": r"Solve Version:\s*(.+)",
    "pipeline_version": r"Pipeline Version:\s*(.+)",
    "refaligner_version": r"RefAligner Version:\s*(.+)",

    # Input molecule stats (unfiltered)
    "total_molecules_unfiltered": r"Input molecule stats \(unfiltered\):[\s\S]*?Total number of molecules:\s*(\d+)",
    "total_length_unfiltered_mbp": r"Input molecule stats \(unfiltered\):[\s\S]*?Total length\s*\(Mbp\)\s*:\s*([\d.]+)",
    "avg_length_unfiltered_kbp": r"Input molecule stats \(unfiltered\):[\s\S]*?Average length\s*\(kbp\)\s*:\s*([\d.]+)",
    "n50_unfiltered_kbp": r"Input molecule stats \(unfiltered\):[\s\S]*?Molecule N50\s*\(kbp\)\s*:\s*([\d.]+)",
    "label_density_unfiltered": r"Input molecule stats \(unfiltered\):[\s\S]*?Label density\s*\(/100kb\)\s*:\s*([\d.]+)",

    # Input molecule stats (filtered)
    "total_molecules_filtered": r"Input molecule stats \(filtered\):[\s\S]*?Total number of molecules\s*:\s*(\d+)",
    "total_length_filtered_mbp": r"Input molecule stats \(filtered\):[\s\S]*?Total length\s*\(Mbp\)\s*:\s*([\d.]+)",
    "avg_length_filtered_kbp": r"Input molecule stats \(filtered\):[\s\S]*?Average length\s*\(kbp\)\s*:\s*([\d.]+)",
    "n50_filtered_kbp": r"Input molecule stats \(filtered\):[\s\S]*?Molecule N50\s*\(kbp\)\s*:\s*([\d.]+)",
    "label_density_filtered": r"Input molecule stats \(filtered\):[\s\S]*?Label density\s*\(/100kb\)\s*:\s*([\d.]+)",
    "ref_coverage_filtered_x": r"Input molecule stats \(filtered\):[\s\S]*?Coverage of the reference\s*\(X\)\s*:\s*([\d.]+)",

    # Molecules aligned to the reference
    "aligned_molecules_ref": r"Molecules aligned to the reference:[\s\S]*?Total number of molecules aligned\s*:\s*(\d+)",
    "effective_ref_coverage_x": r"Molecules aligned to the reference:[\s\S]*?Effective coverage of reference\s*\(X\)\s*:\s*([\d.]+)",
    "avg_confidence_ref": r"Molecules aligned to the reference:[\s\S]*?Average confidence\s*:\s*([\d.]+)",

    # De novo assembly - Diploid genome map
    "diploid_map_count": r"De novo assembly:[\s\S]*?Diploid Genome Map Count\s*:\s*(\d+)",
    "diploid_map_length_mbp": r"De novo assembly:[\s\S]*?Diploid Genome Map Length\s*\(Mbp\)\s*:\s*([\d.]+)",
    "diploid_map_n50_mbp": r"De novo assembly:[\s\S]*?Diploid Genome Map N50\s*\(Mbp\)\s*:\s*([\d.]+)",

    # De novo assembly - Haploid genome map
    "haploid_map_count": r"De novo assembly:[\s\S]*?Haploid Genome Map Count\s*:\s*(\d+)",
    "haploid_map_length_mbp": r"De novo assembly:[\s\S]*?Haploid Genome Map Length\s*\(Mbp\)\s*:\s*([\d.]+)",
    "haploid_map_n50_mbp": r"De novo assembly:[\s\S]*?Haploid Genome Map N50\s*\(Mbp\)\s*:\s*([\d.]+)",

    # Genome maps alignment
    "total_reference_length_mbp": r"De novo assembly:[\s\S]*?Total Reference Length\s*\(Mbp\)\s*:\s*([\d.]+)",
    "genome_maps_aligned": r"De novo assembly:[\s\S]*?Total Number of Genome Maps Aligned\s*\(Fraction\)\s*:\s*(\d+)",
    "genome_maps_aligned_fraction": r"De novo assembly:[\s\S]*?Total Number of Genome Maps Aligned\s*\(Fraction\):\s*\d+\s*\(([\d.]+)\)",
    "unique_aligned_length_mbp": r"De novo assembly:[\s\S]*?Total Unique Aligned Length\s*\(Mbp\)\s*:\s*([\d.]+)",
    "unique_aligned_length_fraction": r"De novo assembly:[\s\S]*?Total Unique Aligned Length \/ Reference Length:\s*([\d.]+)",

    # Molecules aligned to the assembly
    "aligned_molecules_assembly": r"Molecules aligned to the assembly:[\s\S]*?Total number of molecules aligned\s*:\s*(\d+)",
    "fraction_aligned_molecules": r"Molecules aligned to the assembly:[\s\S]*?Fraction of molecules aligned\s*:\s*([\d.]+)",
    "effective_coverage_assembly_x": r"Molecules aligned to the assembly:[\s\S]*?Effective coverage of\s*assembly\s*\(X\)\s*:\s*([\d.]+)",
    "avg_confidence_assembly": r"Molecules aligned to the assembly:[\s\S]*?Average confidence\s*:\s*([\d.]+)",

    # Structural Variants (SV Summary)
    "sv_type": r"SV type\s*:\s*(\w+)",
    "deletions": r"Deletions\s*:\s*(\d+)",
    "insertions": r"Insertions\s*:\s*(\d+)",
    "duplications": r"Duplications\s*:\s*(\d+)",
    "inversion_breakpoints": r"Inversion breakpoints\s*:\s*(\d+)",
    "interchr_translocation_breakpoints": r"Interchr\. translocation breakpoints\s*:\s*(\d+)",
    "intrachr_translocation_breakpoints": r"Intrachr\. translocation breakpoints\s*:\s*(\d+)"
    }

    if table_name=="SINGLE":
        patterns = patterns_single

    for key, pattern in patterns.items():
        match = re.search(pattern, content)
        if match:
            value = match.group(1)

            if value.isdigit():
                data[key] = int(value)
            else:
                try:
                    data[key] = float(value)
                except ValueError:
                    data[key] = value.strip()  #bez bílých znaků

    return data
