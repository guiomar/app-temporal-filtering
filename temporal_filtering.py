#!/usr/local/bin/python3

import json
import mne
import warnings


def temporal_filtering(raw, param_apply_notch, param_notch_frequencies, param_filter_l_freq,
                       param_filter_h_freq, param_apply_resample, param_sfreq):

    raw_filtered = raw.filter(param_filter_l_freq, param_filter_h_freq)

    if param_apply_notch is True:
        # raw.load_data()
        raw_filtered.notch_filter(freqs=param_notch_frequencies)

    if param_apply_resample is True:
        raw_filtered.resample(param_sfreq)

    # Save file
    raw.save("out_dir_temporal_filtering/filtered-raw.fif", overwrite=True)

    return raw_filtered


def main():

    # Generate a json.product to display messages on Brainlife UI
    dict_json_product = {'brainlife': []}

    # Load inputs from config.json
    with open('config.json') as config_json:
        config = json.load(config_json)

    # Read the files
    data_file = config.pop('fif')
    raw = mne.io.read_raw_fif(data_file, allow_maxshield=True)

    # Apply temporal filtering
    raw_filtered = temporal_filtering(raw, config['param_apply_notch'], config['param_notch_frequencies'],
                                      config['param_filter_l_freq'],
                                      config['param_filter_h_freq'], config['param_apply_resample'],
                                      config['param_sfreq'])

    # Info message about notch filtering
    if config['param_apply_notch'] is True:
        dict_json_product['brainlife'].append({'type': 'info', 'msg': 'Notch filter was applied.'})

    # Info message about filtering
    dict_json_product['brainlife'].append({'type': 'info', 'msg': f'Data was filtered between '
                                                                  f'{config["param_filter_l_freq"]} '
                                                                  f'and {config["param_filter_h_freq"]}.'})

    # Info message about resampling
    if config['param_resample'] is True:
        dict_json_product['brainlife'].append({'type': 'info', 'msg': 'Data was resampled at {config["param_sfreq"]}.'})

    # Success message in product.json
    dict_json_product['brainlife'].append({'type': 'success', 'msg': 'Filtering was applied successfully.'})

    # Save the dict_json_product in a json file
    with open('product.json', 'w') as outfile:
        json.dump(dict_json_product, outfile)


if __name__ == '__main__':
    main()
