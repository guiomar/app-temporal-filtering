#!/usr/local/bin/python3

import json
import mne
import warnings


def temporal_filtering(raw, param_filter_l_freq, param_filter_h_freq, param_filter_picks, param_filter_length, param_filter_l_trans_bandwidth,
	                   param_filter_h_trans_bandwidth, param_filer_n_jobs, param_filter_method, param_filter_iir_params, param_filter_phase,
	                   param_filter_fir_window, param_filter_fir_design, param_filter_skip_by_annotation, param_filter_pad,
	                   param_apply_notch, param_notch_freqs, param_notch_picks, param_notch_filter_length, param_notch_widths, 
	                   param_notch_trans_bandwith, param_notch_n_jobs, param_notch_method, param_notch_iir_parameters, param_notch_mt_bandwidth, 
	                   param_notch_pvalue, param_notch_phase, param_notch_fir_window, param_notch_fir_design, param_notch_pad,
	                   param_apply_resample, param_resample_sfreq, param_resample_npad, param_resample_window, param_resample_stim_picks,
	                   param_resample_n_jobs, param_resample_events, param_resample_pad):


    raw.load_data()
    raw_filtered = raw.filter(l_freq=param_filter_l_freq, h_freq=param_filter_h_freq, 
    	                      picks=param_filter_picks, filter_length=param_filter_length, 
    	                      l_trans_bandwidth=param_filter_l_trans_bandwidth, h_trans_bandwidth=param_filter_h_trans_bandwidth, 
    	                      n_jobs=param_filer_n_jobs, method=param_filter_method, 
	                          iir_params=param_filter_iir_params, phase=param_filter_phase,
	                          fir_winddow=param_filter_fir_window, fir_design=param_filter_fir_design, 
	                          skip_by_annotation=param_filter_skip_by_annotation, pad=param_filter_pad)

    if param_apply_notch is True:
        raw_filtered.notch_filter(freqs=param_notch_freqs, picks=param_notch_picks, filter_length=param_notch_filter_length, 
        	                      notch_widths=param_notch_widths, trans_bandwidth=param_notch_trans_bandwith, n_jobs=param_notch_n_jobs, 
        	                      method=param_notch_method, iir_params=param_notch_iir_parameters, 
	                              mt_bandwidth=param_notch_mt_bandwidth, pvalue=param_notch_pvalue, 
	                              phase=param_notch_phase, fir_window=param_notch_fir_window, fir_design=param_notch_fir_design, pad=param_notch_pad)

    if param_apply_resample is True:
        raw_filtered.resample(param_resample_sfreq=sfreq, npad=param_resample_npad, window=param_resample_window, stim_picks=param_resample_stim_picks,
	                          n_jobs=param_resample_n_jobs, events=param_resample_events, pad=param_resample_pad)

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
    raw_filtered = temporal_filtering(raw, config['param_filter_l_freq'], config['param_filter_h_freq'], config['param_filter_picks'], 
    	                              config['param_filter_length'], config['param_filter_l_trans_bandwidth'],
	                                  config['param_filter_h_trans_bandwidth'], config['param_filer_n_jobs'], 
	                                  config['param_filter_method'], config['param_filter_iir_params'], config['param_filter_phase'],
	                                  config['param_filter_fir_window'], config['param_filter_fir_design'], 
	                                  config['param_filter_skip_by_annotation'], config['param_filter_pad'],
	                                  config['param_apply_notch'], config['param_notch_freqs'], config['param_notch_picks'], 
	                                  config['param_notch_filter_length'], config['param_notch_widths'], 
	                                  config['param_notch_trans_bandwith'], config['param_notch_n_jobs'], config['param_notch_method'], 
	                                  config['param_notch_iir_parameters'], config['param_notch_mt_bandwidth'], 
	                                  config['param_notch_pvalue'], config['param_notch_phase'], config['param_notch_fir_window'], 
	                                  config['param_notch_fir_design'], config['param_notch_pad'],
	                                  config['param_apply_resample'], config['param_resample_sfreq'], config['param_resample_npad'], 
	                                  config['param_resample_window'], config['param_resample_stim_picks'],
	                                  config['param_resample_n_jobs'], config['param_resample_events'], config['param_resample_pad'])

    # Info message about filtering
    dict_json_product['brainlife'].append({'type': 'info', 'msg': f'Data was filtered between '
                                                                  f'{config["param_filter_l_freq"]} '
                                                                  f'and {config["param_filter_h_freq"]}.'})

    # Info message about notch filtering if applied
    if config['param_apply_notch'] is True:
        dict_json_product['brainlife'].append({'type': 'info', 'msg': 'Notch filter was applied.'})

    # Info message about resampling if applied
    if config['param_apply_resample'] is True:
        dict_json_product['brainlife'].append({'type': 'info', 'msg': 'Data was resampled at {config["param_sfreq"]}.'})

    # Success message in product.json    
    dict_json_product['brainlife'].append({'type': 'success', 'msg': 'Filtering was applied successfully.'})

    # Save the dict_json_product in a json file
    with open('product.json', 'w') as outfile:
        json.dump(dict_json_product, outfile)


if __name__ == '__main__':
    main()
