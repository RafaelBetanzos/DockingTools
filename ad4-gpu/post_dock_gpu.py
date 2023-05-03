import os
import time
import pandas as pd
import matplotlib.pyplot as plt
from statistics import mean
import sys

def Grafico_Clusters_Pob(enegy_df,rmsd_df):

     
    Eje_X = enegy_df['mean energy'].tolist()
    Eje_Y = enegy_df['cluster'].tolist()
    Values = rmsd_df['rmsd'].tolist()

    fig, ax = plt.subplots()
    ax.scatter(Eje_X,Eje_Y , label='Docking')
    for i, txt in enumerate(Values):
        ax.annotate(txt, (Eje_X[i], Eje_Y[i]))

    plt.grid()

    plt.title('Autodock GPU')

    plt.legend(loc='upper right')
	
    plt.xlabel('Energia')
	
    plt.ylabel('% Poblacion')

    plt.savefig('Cluster_Poblaciones.jpg')
	
    plt.show()



if __name__ == '__main__':
    
    
    if (len(sys.argv)) == 1:
        print('falta dlg filename')
        sys. exit()
    else:
        file_name = sys.argv[1]

    #### Obtengo PDB y RMSD ####

    input_file = open('{}'.format(file_name),'r').readlines()
    rank_value = 1
    ranks = {}

    for lines in input_file:
        if lines[0:6] == 'DOCKED':
            mark = (lines.split(' '))[1]
            if mark == 'USER':
                if 'Run' in lines:
                    rank = int(lines[22:25])
                    pdbqt_out = open('Run{}.pdbqt'.format(rank),'w')
            if mark in ['REMARK' , 'HETATM' , 'ATOM' ,'ROOT', 'ENDROOT' , 'BRANCH' ,'ENDBRANCH' ,'TORSDOF' , 'TER']:
                pdbqt_out.write(lines[8:])
            if mark in ['ENDMDL']:
                pdbqt_out.close()
        if 'RANKING' in lines:
            ranks[int(lines[13:20])] = rank_value
            rank_value = rank_value + 1
    pdbqt_out.close()
    
    # Renombrar el archivo
    for keys in ranks:  
        os.rename('Run{}.pdbqt'.format(keys), 'Rank{}.pdbqt'.format(ranks[keys]))

    time.sleep(3)

    for j in range(1,rank_value-1):
        print(j)
        os.system('obabel -ipdbqt Rank{}.pdbqt -opdb -O rank{}.pdb'.format(j,j))

    os.system('python generate_rms.py ligand.pdbqt -p {}'.format(rank_value-1))

    #### Histogramas y Tablas ####
    
    #Carga las energías del archivo DLG

    # Extrae las energías de acoplamiento de todas las poses
    energies = []
    enegy_df = pd.DataFrame(columns=['rank', 'lowest energy', 'run', 'mean energy', 'cluster'])
    rmsd_df = pd.DataFrame(columns=['rank', 'run', 'rmsd'])
    for j in range(0,len(input_file)):
        if 'CLUSTERING HISTOGRAM' in input_file[j]:
            flag = True
            pos = j + 10
            while flag == True:
                if input_file[pos][0:5] != '_____':
                    data = input_file[pos].split('|')
                    valores = [int(data[0]),float(data[1]),int(data[2]),float(data[3]),int(data[4])]
                    temp_df = pd.DataFrame([valores], columns=enegy_df.columns)
                    enegy_df = pd.concat([enegy_df, temp_df], ignore_index=True)
                    pos = pos + 1
                else:
                    flag = False
        if 'RMSD TABLE' in input_file[j]:
            flag = True
            pos = j + 9
            while flag == True:
                if len(input_file[pos]) != 1:
                    valores = [int(input_file[pos][0:5]),int(input_file[pos][14:20]),float(input_file[pos][44:59])]
                    temp_df = pd.DataFrame([valores], columns=rmsd_df.columns)
                    rmsd_df = pd.concat([rmsd_df, temp_df], ignore_index=True)
                    pos = pos + 1
                else:
                    flag = False

    print(enegy_df)


    rmsd_other = open('summary_rms_results.txt' , 'r').readlines()
    rmsd_values = []
    
    for j in range(1,len(rmsd_other)):
        rmsd_values.append(float(rmsd_other[j][28:40]))

    rmsd_df['RMSD Ext'] = rmsd_values

    print(rmsd_df)

    ## Grafico ##

    Grafico_Clusters_Pob(enegy_df,rmsd_df)

