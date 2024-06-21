import sys
from create_sbatch_file import *
from Basecalling_pipeline.subset_creation.config_file_api import *

sys.path.append("../subset_creation")
from runParameters import runParameters

if __name__ == "__main__":
    run_params = runParameters.from_file(sys.argv[1])
    
    if check_config_json_structure(run_params.config_path) == False:
        print(f"Json file for run {run_params.id} is not correct")
        sys.exit(1)
    
    create_sbatch_file(run_params.config_path, run_params.logs_dir)
    
    