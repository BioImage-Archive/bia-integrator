import pandas as pd
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import numpy as np


def colour_code_data(row: pd.Series, row_map: list):
    row_out = row.replace(1, row_map[row.name] + 1)
    return row_out


if __name__ == "__main__":
    section_types_count = pd.read_csv("biad_field_presence.csv").fillna(value = 0)
    just_numbers = section_types_count.drop(columns="accno")
    study_accno = section_types_count["accno"].to_numpy()

    clusters = 4
    kmeans = KMeans(n_clusters=clusters, random_state=20)
    kmeans_labels = kmeans.fit_predict(just_numbers).tolist()

    clustered_studies = {key: list() for key in range(clusters)}
    for i, value in enumerate(kmeans_labels):
        clustered_studies[value].append(study_accno[i])

    [print(value) for value in clustered_studies.values()]

    out = just_numbers.apply(
        colour_code_data, args=([kmeans_labels]), axis=1, result_type="broadcast"
    )

    plt.figure()
    plt.imshow(out)
    ax = plt.gca()
    ax.set_yticks(
        np.arange(len(study_accno)),
        labels=study_accno,
    )

    plt.show()
