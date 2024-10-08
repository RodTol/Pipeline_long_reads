#__author__      ="Rodolfo Tolloi"
#__subject__     ="Nastro Pipeline"
#__tags__        ="Bioinformatics, Nanopore, Dorado"
#__copyright__   ="Copyright 2021, AREA SCIENCE PARK - RIT"
#__credits__     =
#__license__     ="Apache License 2.0"
#__version__     =
#__maintainer__  =
#__status__      ="Development"

import sys
import json

# Function to load JSON data from a file
def load_json(path):
    with open(path, 'r') as file:
        data = json.load(file)
        return data

def create_sbatch_file(path_to_config, path_to_sbatch):
    '''
    Function to create a Slurm sbatch script based on a configuration
    file (config.json). See the documentation to understand what each 
    parameter represents
    '''
    # Get the number of nodes that will be used for the basecalling
    data = load_json(path_to_config)
    how_many_nodes = len(data['ComputingResources']['nodes_list'])

    # Open the sbatch file for writing
    with open(path_to_sbatch, "w") as sbatch_file:
        # Write the basic sbatch directives
        sbatch_file.write('#!/bin/bash\n')
        sbatch_file.write(f"#SBATCH --job-name={data['General']['name']}\n")
        sbatch_file.write(f"#SBATCH --time={data['General']['run_time']}\n")
        sbatch_file.write(f"#SBATCH --output={data['Slurm']['output_path']}\n")
        sbatch_file.write(f"#SBATCH --error={data['Slurm']['error_path']}\n")
        
        sbatch_file.write("\n")

        # Loop through each node and write its directives
        for i in range(how_many_nodes):
            sbatch_file.write(f"#SBATCH -A lage -p {data['ComputingResources']['nodes_queue'][i]}")
            # If a specific node is not specified let slurm decide
            if data['ComputingResources']['nodes_list'][i] != "":
                sbatch_file.write(f" --nodelist={data['ComputingResources']['nodes_list'][i]}")
            
            sbatch_file.write(f" --nodes=1 --ntasks-per-node=1")
            sbatch_file.write(f" --cpus-per-task={data['ComputingResources']['nodes_cpus'][i]}")
            sbatch_file.write(f" --mem={data['ComputingResources']['nodes_mem'][i]}")

            if data['ComputingResources']['nodes_gpus'][i] != "None":
                sbatch_file.write(f" --gpus {data['ComputingResources']['nodes_gpus'][i]}\n")
            else:
                sbatch_file.write("\n")

            # Add a hetjob directive after each node except the last one
            if i != how_many_nodes-1:
                sbatch_file.write("#SBATCH hetjob\n\n")
            else:
                sbatch_file.write("\n")

        sbatch_file.write("\n")
        
        # Write additional sbatch directives for script execution
        sbatch_file.write('config_file=$1\n')
        sbatch_file.write('run_params_path=$2\n')
        sbatch_file.write('samplesheet=$3\n')        
        sbatch_file.write("index_host=$(jq -r '.ComputingResources.index_host' ")
        sbatch_file.write('"$config_file")\n')
        sbatch_file.write("echo 'INDEX_HOST' $index_host\n")

        sbatch_file.write("\n")

        # Loop through each node and write srun commands
        for i in range(how_many_nodes):
            # If I have only one node I do not need to use het-group
            if how_many_nodes == 1:
                sbatch_file.write(f"srun ")
            else:
                sbatch_file.write(f"srun --het-group={i} ")

            sbatch_file.write(f"{data['Slurm']['main_script']} $samplesheet $config_file $((index_host + {i})) $run_params_path &\n")

            # FIXME can I remove it ?
            # Add a sleep command after each srun command except the last one
            if i != how_many_nodes-1:
                sbatch_file.write("sleep 10\n")
            else:
                sbatch_file.write("wait\n")

        # Add a comment indicating the script was generated by configuration.py
        sbatch_file.write('#**********WRITTEN BY CONFIGURATION.PY**********\n')