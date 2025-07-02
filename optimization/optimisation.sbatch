#!/bin/bash

#SBATCH --error=logs/opt_%j.log
#SBATCH --output=logs/opt_%j.log
#SBATCH --nodes=1
#SBATCH --time=168:00:00
#SBATCH --exclude=w1,w2,w3,w4,w5,w6,w7,w8,w10,w12,w14

source /home/haman/virt_env/layers56new/bin/activate
python -u run_optimisation.py
