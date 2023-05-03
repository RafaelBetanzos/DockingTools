import os
import argparse
import ast

os.chdir('/home/rbetanzos/git-holcan/DockingTools/ad4-gpu/test/') #Resolver este problema
""" pdbqtrec(), toma como entrada un diccionario parameters_dict que contiene información sobre los receptores que se van a acoplar.
La función ejecuta el comando de preprocesamiento de receptores de ADT Vina para añadir hidrógenos y convertir los archivos de los
receptores de formato pdb a formato pdbqt."""
def pdbqtrec(parameters_dict):
    receptors_str = parameters_dict['receptors']
    receptors = receptors_str.split(',') 
    for receptor in receptors:
        protein_file = f'{receptor}.pdb'
        os.system(f'bash ~/../shared/programs/autodock/autodock4/pythonsh ~/../shared/programs/autodock/autodock4/prepare_receptor4.py -A hydrogens -r {protein_file} -o {receptor}.pdbqt')
        print(f'Archivo {receptor}.pdbqt generado con éxito')


""" pdbqtlig(), toma como entrada un diccionario parameters_dict que contiene información sobre los ligandos que se van a acoplar.
La función divide el nombre de los ligandos en una cadena separada por comas y luego ejecuta el comando de preprocesamiento de
ligandos de ADT Vina para convertir los archivos de los ligandos de formato pdb a formato pdbqt."""
def pdbqtlig(parameters_dict): 
    print(parameters_dict)
    ligands_str = parameters_dict['ligands']
    ligands = ligands_str.split(',')
    print(ligands)
    for ligand in ligands:
        ligand_file = f'{ligand}.pdb'
        os.system(f'bash ~/../shared/programs/autodock/autodock4/pythonsh ~/../shared/programs/autodock/autodock4/prepare_ligand4.py -A hydrogens -l {ligand_file} -o {ligand}.pdbqt')
        print(f'Archivo {ligand}.pdbqt generado con éxito')

"""autodocking4(), toma como entrada un diccionario parameters_dict que contiene información sobre los parámetros del proceso de acoplamiento.
La función utiliza los nombres de los ligandos y los receptores para crear una serie de directorios para almacenar los archivos de salida de ADT-GPU.
La función luego ejecuta el comando de acoplamiento de ADT-GPU para cada combinación de ligando y receptor y almacena los resultados en los directorios apropiados."""
def autodocking4(paramers_dict):

    receptors_str = parameters_dict.get('receptors')
    receptors = receptors_str.split(',')
    ligands_str = parameters_dict['ligands']
    ligands = ligands_str.split(',')
    grid_center = parameters_dict.get('grid_center')
    print(grid_center)
    #ga_run = parameters_dict.get('ga_run')
    grid_size = parameters_dict.get('grid_size')
    print(grid_size)
    for receptor in receptors:
        # guardar directorio de trabajo actual
        current_dir = os.getcwd()
        print(current_dir)
        receptor_dir = os.path.join(f'{receptor}_ad4')
        os.makedirs(receptor_dir, exist_ok=True)
        for ligand in ligands:
            output_dir = os.path.join(receptor_dir,ligand)
            os.makedirs(output_dir, exist_ok=True)
            if os.system(f'cp {receptor}.pdbqt {output_dir}/') == 0:
                print(f'El archivo {receptor}.pdbqt Se encuentra en el {output_dir}!')
            else:
                print(f'Error al copiar el {receptor}')
            if os.system(f'mv {ligand}.pdbqt {output_dir}/') == 0:
                print(f'El archivo {ligand}.pdbqt Se encuentra en el {output_dir}!')
            else:
                print(f'Error al al mover el {ligand}')
            # cambiar al directorio de salida
            os.chdir(output_dir)
            if os.system(f'bash ~/../shared/programs/autodock/autodock4/pythonsh ~/../shared/programs/autodock/autodock4/prepare_gpf4.py -y -l {ligand}.pdbqt -r {receptor}.pdbqt -o {receptor}_{ligand}.gpf -p gridcenter=\'{grid_center}\' -p npts=\'{grid_size}\'') == 0:
                print(f'preparegpf se ha generado exitosamente!')
            else:
                print(f'Error al ejecutar prepdpf')
            if os.system(f'~/../shared/programs/autodock/autodock4/autogrid4 -p {receptor}_{ligand}.gpf -l {receptor}_{ligand}.glg') == 0:
                print(f'Autogrid se ha ejecutado correctamente!')
            else:
                print(f'Error al ejecutar autogrid')            
            if os.system(f'bash ~/../shared/programs/autodock/autodock4/pythonsh ~/../shared/programs/autodock/autodock4/prepare_dpf42.py -p ga_run={args.ga_run} -l {ligand}.pdbqt -r {receptor}.pdbqt -o {receptor}_{ligand}.dpf')== 0:
                print(f'prepdpf se ha ejecutado correctamente!')
            else:
                print(f'Error al ejecutar prepdpf')
            if os.system(f'~/../shared/programs/autodock/AutoDock-GPU/bin/autodock_gpu_128wi -M {receptor}.maps.fld -L {ligand}.pdbqt --nrun {args.ga_run} --output-cluster-poses 1 -R {ligand}.pdbqt --hsym')== 0:
               print(f'El Docking de {receptor} y {ligand} se ha completado exitosamente!')
            else:
                print(f'Error al ejecutar autodock4')
            os.chdir(current_dir)


# Crear un objeto ArgumentParser
parser = argparse.ArgumentParser(description='Corrida de Docking con GPU')

# Agregar el argumento para el archivo dockparms2.txt
parser.add_argument('dockparms_file', type=str, help='Nombre del archivo dockparameters.txt')

# Agregar el argumento para el número de corridas
parser.add_argument('ga_run', type=str, help='número de corridas o Ga_run')

# Agregar el argumento para el número de corridas
parser.add_argument('--extra_parms', type=str, nargs='?', const='default_value', help='Argumentos extras revisar documentación de ADT-GPU')

# Obtener los argumentos de línea de comandos
args = parser.parse_args()

# Leer el archivo de parámetros
parameters_dict = {}
# Leer el archivo dockparms.txt
with open(args.dockparms_file, 'r') as f:
    dockparms_str = f.read()
# Convertir la cadena a un diccionario de Python
try:
    parameters_dict = ast.literal_eval(dockparms_str)
except SyntaxError:
    print('Error: El archivo dockparms.txt no está en el formato correcto de diccionario de Python.')
    exit()
# Ejecutar las funciones para preparar los archivos
if 'receptors' in parameters_dict:
    pdbqtrec(parameters_dict)
if 'ligands' in parameters_dict:
    pdbqtlig(parameters_dict)
if 'grid_center' in parameters_dict and 'grid_size' in parameters_dict and 'DALGO' in parameters_dict:
    autodocking4(parameters_dict)   
# Obtener el valor del argumento opcional extra_parms
