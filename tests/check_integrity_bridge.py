"""
Standalone diagnostic tool for debugging Integrity Bridge mismatches.
Dataset-agnostic: Resolves paths dynamically via PathCoordinator.
"""

import argparse
import pandas as pd
import logging
from dd_common.path_coordinator import PathCoordinator
from dd_parser.rules import IntegrityEngine

def run_diagnostic(config_file: str):
    """Executes the diagnostic check and prints a summary report."""
    # Silence info logs to focus on report output
    logging.getLogger("dd_common").setLevel(logging.WARNING)
    logging.getLogger("dd_parser").setLevel(logging.WARNING)
    
    print("\n" + "="*70)
    print("🌉 INTEGRITY BRIDGE DIAGNOSTIC REPORT")
    print("="*70 + "\n")
    
    try:
        # 1. Initialize Path Coordinator
        coord = PathCoordinator(config_path=config_file)
        
        # 2. Load Dictionary
        try:
            df_dict = pd.read_csv(coord.data_dictionary_path, engine='c', low_memory=False)
        except Exception:
            df_dict = pd.read_csv(coord.data_dictionary_path, sep=None, engine='python')

        attr_col = coord.data_dictionary_attribute_col_name or df_dict.columns[0]
        dd_attributes = df_dict[attr_col].dropna().astype(str).str.strip().tolist()
        
        # 3. Load Raw Headers
        try:
            # nrows=0 is fast, but we prioritize C engine for consistency across the suite
            df_raw = pd.read_csv(coord.raw_dataset_path, engine='c', nrows=0)
        except Exception:
            df_raw = pd.read_csv(coord.raw_dataset_path, sep=None, engine='python', nrows=0)

        raw_headers = list(df_raw.columns)

        print(f"📂 Workspace:  {coord.working_dir}")
        print(f"📂 Dictionary: {coord.data_dictionary_path.name} ({len(dd_attributes)} fields)")
        print(f"📂 Raw Data:   {coord.raw_dataset_path.name} ({len(raw_headers)} headers)\n")

        # 4. Evaluate using the core engine logic
        bridge = IntegrityEngine.evaluate_bridge(dd_attributes, raw_headers)
        
        print(f"✅ [Operational]: {len(bridge['operational'])} matches")
        print(f"❌ [Orphans]:     {len(bridge['orphans'])} (In Dictionary, Missing in Data)")
        print(f"👻 [Ghosts]:      {len(bridge['ghosts'])} (In Data, Missing in Dictionary)\n")

        if bridge['orphans']:
            print("📋 ORPHAN DETAIL:")
            for item in sorted(bridge['orphans']):
                print(f"  - {item}")
            print()

        if bridge['ghosts']:
            print("📋 GHOST DETAIL:")
            for item in sorted(bridge['ghosts']):
                print(f"  - {item}")
            print()

        print("="*70)
        print("Diagnostic Complete.")
        print("="*70 + "\n")

    except Exception as e:
        print(f"❌ Diagnostic Failed: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check the bridge between Data Dictionary and Raw Data.")
    parser.add_argument("--config", default="config.yaml", help="Configuration file path")
    
    args = parser.parse_args()
    run_diagnostic(args.config)