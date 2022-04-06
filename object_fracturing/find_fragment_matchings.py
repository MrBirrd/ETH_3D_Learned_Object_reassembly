import os
from multiprocessing import Pool

import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial.distance import cdist
from tqdm import tqdm

VISUALIZE = False
# Root data folder. (such that DATA_FOLDER/{name} contains pointcloud npys.
DATA_FOLDER = os.path.join('data')


def find_matching_matrix(name):
    print(f'\nProcessing {name}...')
    fragments = []

    # Load the pointcloud of each fragment.
    num_parts = 0
    while True:
        path = os.path.join(DATA_FOLDER, name, 'subdv', f'{name}_subdv.{num_parts}.npy')
        try:
            fragments.append(np.load(path))
        except:
            print(f'{num_parts} parts loaded.\n')
            break

        if num_parts == 999:
            print('WARNING: part limit reached, only loaded the first 1000 parts.')
        num_parts += 1

    if num_parts == 0:
        print(f'WARNING: No data found: {path}')
        return

    # Scatter plot of pointcloud.
    if VISUALIZE:
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        for i in range(num_parts):
            ax.scatter(fragments[i][:, 0], fragments[i][:, 2], fragments[i][:, 1], s=1, label=i)
        legend = plt.legend(bbox_to_anchor=(0, 1), loc="upper left", bbox_transform=fig.transFigure)
        for handle in legend.legendHandles:
            handle.set_sizes([50.0])
        plt.show()
        plt.close(fig)

    # Compute and save matchings.
    matching_matrix = np.zeros((num_parts, num_parts))
    for i in tqdm(range(num_parts)):
        for j in range(i):
            # Search for corresponding points in two parts (distance below a treshold).
            matches = np.sum(cdist(fragments[i][:, :3], fragments[j][:, :3]) < 1e-3)
            # print(f'Fragments {i} and {j} have {matches} matches')

            # If there are more than 100 matches, the parts are considered neighbours.
            if matches > 100:
                # print(f'{name}: {i} and {j} match!')
                matching_matrix[i, j] = matching_matrix[j, i] = 1

    # Save.
    matching_folder_path = os.path.join(DATA_FOLDER, name, 'matching')
    os.makedirs(matching_folder_path, exist_ok=True)
    print(f'Saving to {matching_folder_path}.')
    np.save(os.path.join(matching_folder_path, f'{name}_matching_matrix.npy'), matching_matrix)
    idxes = np.stack(np.where(matching_matrix)).T  # Warning: each pair appears in the csv file as a, b and as b, a.
    np.savetxt(os.path.join(matching_folder_path, f'{name}_pair_list.csv'), idxes, fmt='%d', delimiter=',')


def main():
    # names = ['bottle_10_seed_1']
    names = os.listdir(DATA_FOLDER)

    with Pool(4) as p:
        p.map(find_matching_matrix, names)


if __name__ == '__main__':
    main()
