import pandas as pd
from typing import List


def binarize(data: pd.DataFrame, bins: List[float], by: str, norm_by: str = None) -> pd.DataFrame:
    bins_it = iter(bins)
    min_cut = next(bins_it)

    _data = list()
    grouped_data = list()

    desc = 'desc'
    keys = pd.unique(data[desc])

    # First bin
    _data = data[data[by] < min_cut].groupby(by=desc).sum()
    for key in keys:
        value = _data.loc[key]['value'] if _data.shape[0] > 0 else 0
        if norm_by is not None and key != norm_by:
            value /= _data.loc[norm_by]['value']
        grouped_data.append({by: f'$<{min_cut}$', 'value': value, 'desc': key})

    # Middle bins
    for max_cut in bins_it:
        _data = data[(data[by] >= min_cut) & (data[by] < max_cut)].groupby(by=desc).sum()
        for key in keys:
            value = _data.loc[key]['value'] if _data.shape[0] > 0 else 0
            if norm_by is not None and key != norm_by:
                value /= _data.loc[norm_by]['value']
            grouped_data.append({by: f'${min_cut}-{max_cut}$', 'value': value, 'desc': key})

        min_cut = max_cut

    # Last bin
    _data = data[data[by] >= min_cut].groupby(by=desc).sum()
    for key in keys:
        value = _data.loc[key]['value'] if _data.shape[0] > 0 else 0
        if norm_by is not None and key != norm_by:
            value /= _data.loc[norm_by]['value']
        grouped_data.append({by: f'$\geq{min_cut}$', 'value': value, 'desc': key})

    return pd.DataFrame(grouped_data)
