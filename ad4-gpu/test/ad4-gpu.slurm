#!/bin/bash
#SBATCH  --job-name=ad4-gpu           # Job name
#SBATCH --nodes=1                    # Run all processes on a single node       
#SBATCH --ntasks=1                   # Run a single task         
#SBATCH --cpus-per-task=1            # Number of CPU cores per task
#SBATCH --gpus-per-task=1            # Number of GPU cores per task
#SBATCH --gres=gpu:1                 # Sólo usa los que tienen GPUs
#SBATCH --exclude=nodo13        # Excluye los nodos
##SBATCH -e slurm-%j.err
#SBATCH -p gpu

#srun conda activate ~/enviroments/SSDockTools 
srun python3 ad4-gpu.py dockparms.txt 1000       # nombre del script a correr 
#conda deactivate
