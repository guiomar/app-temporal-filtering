#!/usr/local/bin/python3

import json
import mne
import numpy as np


def temporal_filtering(raw, param_filter_l_freq, param_filter_h_freq, param_filter_picks, param_filter_length,
                       param_filter_l_trans_bandwidth, param_filter_h_trans_bandwidth, param_filer_n_jobs,
                       param_filter_method, param_filter_iir_params, param_filter_phase, param_filter_fir_window,
                       param_filter_fir_design, param_filter_skip_by_annotation, param_filter_pad, param_apply_notch,
                       param_notch_freqs_start, param_notch_freqs_end, param_notch_freqs_step, param_notch_picks,
                       param_notch_filter_length, param_notch_widths, param_notch_trans_bandwith, param_notch_n_jobs,
                       param_notch_method, param_notch_iir_parameters, param_notch_mt_bandwidth, param_notch_p_value,
                       param_notch_phase, param_notch_fir_window, param_notch_fir_design, param_notch_pad,
                       param_apply_resample, param_resample_sfreq, param_resample_npad, param_resample_window,
                       param_resample_stim_picks, param_resample_n_jobs, param_resample_events, param_resample_pad):
    """Perform filtering using MNE Python and save the file once filtered.

    Parameters
    ----------
    raw: instance of mne.io.Raw
        Data to be filtered.

    Returns
    -------
    raw_filtered: instance of mne.io.Raw
        The raw data after filtering.
    """

    raw.load_data()

    # Bandpass, lowpass, or highpass filter
    raw_filtered = raw.filter(l_freq=param_filter_l_freq, h_freq=param_filter_h_freq, 
                              picks=param_filter_picks, filter_length=param_filter_length,
                              l_trans_bandwidth=param_filter_l_trans_bandwidth,
                              h_trans_bandwidth=param_filter_h_trans_bandwidth, n_jobs=param_filer_n_jobs,
                              method=param_filter_method, iir_params=param_filter_iir_params, phase=param_filter_phase,
                              fir_window=param_filter_fir_window, fir_design=param_filter_fir_design,
                              skip_by_annotation=param_filter_skip_by_annotation, pad=param_filter_pad)

    # Notch
    if param_apply_notch is True:
        freqs = np.arange(param_notch_freqs_start, param_notch_freqs_end, param_notch_freqs_step)
        raw_filtered.notch_filter(freqs=freqs, picks=param_notch_picks,
                                  filter_length=param_notch_filter_length, notch_widths=param_notch_widths,
                                  trans_bandwidth=param_notch_trans_bandwith, n_jobs=param_notch_n_jobs,
                                  method=param_notch_method, iir_params=param_notch_iir_parameters,
                                  mt_bandwidth=param_notch_mt_bandwidth, p_value=param_notch_p_value,
                                  phase=param_notch_phase, fir_window=param_notch_fir_window,
                                  fir_design=param_notch_fir_design, pad=param_notch_pad)

    # Resample
    if param_apply_resample is True:
        raw_filtered.resample(sfreq=param_resample_sfreq, npad=param_resample_npad, window=param_resample_window,
                              stim_picks=param_resample_stim_picks, n_jobs=param_resample_n_jobs,
                              events=param_resample_events, pad=param_resample_pad)

    # Save file
    raw.save("out_dir_temporal_filtering/filtered-raw.fif", overwrite=True)

    return raw_filtered


def _compute_snr(meg_file):
    # Compute the SNR

    # select only MEG channels and exclude the bad channels
    meg_file = meg_file.pick_types(meg=True, exclude='bads')

    # create fixed length events
    array_events = mne.make_fixed_length_events(meg_file, duration=10)

    # create epochs
    epochs = mne.Epochs(meg_file, array_events)

    # mean signal amplitude on each epoch
    epochs_data = epochs.get_data()
    mean_signal_amplitude_per_epoch = epochs_data.mean(axis=(1, 2))  # mean on channels and times

    # mean across all epochs and its std error
    mean_final = mean_signal_amplitude_per_epoch.mean()
    std_error_final = np.std(mean_signal_amplitude_per_epoch, ddof=1) / np.sqrt(
        np.size(mean_signal_amplitude_per_epoch))

    # compute SNR
    snr = mean_final / std_error_final

    return snr


def _generate_report(data_file_before, raw_before_preprocessing, raw_after_preprocessing, bad_channels,
                     comments_about_filtering, notch_freqs_start, resample_sfreq, snr_before, snr_after):
    # Generate a report

    # Instance of mne.Report
    report = mne.Report(title='Results of filtering ', verbose=True)

    # Plot MEG signals in temporal domain
    fig_raw = raw_before_preprocessing.pick(['meg'], exclude='bads').plot(duration=10, butterfly=False,
                                                                          show_scrollbars=False, proj=False)
    fig_raw_maxfilter = raw_after_preprocessing.pick(['meg'], exclude='bads').plot(duration=10, butterfly=False,
                                                                                   show_scrollbars=False, proj=False)
    # Plot power spectral density
    fig_raw_psd = raw_before_preprocessing.plot_psd()
    fig_raw_maxfilter_psd = raw_after_preprocessing.plot_psd()

    # Add figures to report
    # Add figures to report
    report.add_figs_to_section(fig_raw, captions='MEG signals before filtering', section='Temporal domain')
    report.add_figs_to_section(fig_raw_maxfilter, captions='MEG signals after filtering',
                               comments=comments_about_filtering,
                               section='Temporal domain')
    report.add_figs_to_section(fig_raw_psd, captions='Power spectral density before filtering',
                               section='Frequency domain')
    report.add_figs_to_section(fig_raw_maxfilter_psd, captions='Power spectral density after filtering',
                               comments=comments_about_filtering,
                               section='Frequency domain')

    # Check if MaxFilter was already applied on the data
    if raw_before_preprocessing.info['proc_history']:
        sss_info = raw_before_preprocessing.info['proc_history'][0]['max_info']['sss_info']
        tsss_info = raw_before_preprocessing.info['proc_history'][0]['max_info']['max_st']
        if bool(sss_info) or bool(tsss_info) is True:
            message_channels = f'Bad channels have been interpolated during MaxFilter.'
    else:
        message_channels = bad_channels

    # Put this info in html format
    # Give some info about the file before preprocessing
    sampling_frequency = raw_before_preprocessing.info['sfreq']
    highpass = raw_before_preprocessing.info['highpass']
    lowpass = raw_before_preprocessing.info['lowpass']

    # Put this info in html format
    # Info on data
    html_text_info = f"""<html>

        <head>
            <style type="text/css">
                table {{ border-collapse: collapse;}}
                td {{ text-align: center; border: 1px solid #000000; border-style: dashed; font-size: 15px; }}
            </style>
        </head>

        <body>
            <table width="50%" height="80%" border="2px">
                <tr>
                    <td>Input file: {data_file_before}</td>
                </tr>
                <tr>
                    <td>Bad channels: {message_channels}</td>
                </tr>
                <tr>
                    <td>Sampling frequency: {sampling_frequency}Hz</td>
                </tr>
                <tr>
                    <td>Highpass: {highpass}Hz</td>
                </tr>
                <tr>
                    <td>Lowpass: {lowpass}Hz</td>
                </tr>
            </table>
        </body>

        </html>"""

    # Info on SNR
    html_text_snr = f"""<html>

    <head>
        <style type="text/css">
            table {{ border-collapse: collapse;}}
            td {{ text-align: center; border: 1px solid #000000; border-style: dashed; font-size: 15px; }}
        </style>
    </head>

    <body>
        <table width="50%" height="80%" border="2px">
            <tr>
                <td>SNR before filtering: {snr_before}</td>
            </tr>
            <tr>
                <td>SNR after filtering: {snr_after}</td>
            </tr>
        </table>
    </body>

    </html>"""

    # Info on SNR
    html_text_summary_filtering = f"""<html>

    <head>
        <style type="text/css">
            table {{ border-collapse: collapse;}}
            td {{ text-align: center; border: 1px solid #000000; border-style: dashed; font-size: 15px; }}
        </style>
    </head>

    <body>
        <table width="50%" height="80%" border="2px">
            <tr>
                <td>Temporal filtering: {comments_about_filtering}</td>
            </tr>
            <tr>
                <td>Notch: {notch_freqs_start}</td>
            </tr>
            <tr>
                <td>Resampling: {resample_sfreq}</td>
            </tr>
        </table>
    </body>

    </html>"""

    # Add html to reports
    report.add_htmls_to_section(html_text_info, captions='MEG recording features', section='Info', replace=False)
    report.add_htmls_to_section(html_text_summary_filtering, captions='Summary filtering applied', section='Filtering info',
                                replace=False)
    report.add_htmls_to_section(html_text_snr, captions='Signal to noise ratio', section='Signal to noise ratio',
                                replace=False)

    # Save report
    report.save('out_dir_report/report_filtering.html', overwrite=True)


def main():

    # Generate a json.product to display messages on Brainlife UI
    dict_json_product = {'brainlife': []}

    # Load inputs from config.json
    with open('config.json') as config_json:
        config = json.load(config_json)

    # Read the files
    data_file = config.pop('fif')
    raw = mne.io.read_raw_fif(data_file, allow_maxshield=True)

    # Info message about filtering

    # Band pass filter
    comments_about_filtering = ''
    if config['param_filter_l_freq'] is not None and config['param_filter_h_freq'] is not None:
        comments_about_filtering = f'Data was filtered between ' \
                                   f'{config["param_filter_l_freq"]} ' \
                                   f'and {config["param_filter_h_freq"]}Hz.'
        dict_json_product['brainlife'].append({'type': 'info', 'msg': comments_about_filtering})

    # Lowpass filter
    elif config['param_filter_l_freq'] is None and config['param_filter_h_freq'] is not None:
        comments_about_filtering = f'Lowpass filter was applied at {config["param_filter_h_freq"]}Hz.'
        dict_json_product['brainlife'].append({'type': 'info', 'msg': comments_about_filtering})

    # Highpass filter
    elif config['param_filter_l_freq'] is not None and config['param_filter_h_freq'] is None:
        comments_about_filtering = f'Highpass filter was applied at {config["param_filter_l_freq"]}Hz.'
        dict_json_product['brainlife'].append({'type': 'info', 'msg': comments_about_filtering})

    # Raise an exception if both param_filter_l_freq and param_filter_h_freq are None
    elif config['param_filter_l_freq'] is None and config['param_filter_h_freq'] is None:
        value_error_message = f'You must specify a value for param_filter_l_freq or param_filter_h_freq, ' \
                              f"they can't both be set to None."
        # Raise exception
        raise ValueError(value_error_message)

    # Keep bad channels in memory
    bad_channels = raw.info['bads']

    # Apply temporal filtering
    raw_copy = raw.copy()
    raw_filtered = temporal_filtering(raw_copy, config['param_filter_l_freq'], config['param_filter_h_freq'],
                                      config['param_filter_picks'], config['param_filter_length'],
                                      config['param_filter_l_trans_bandwidth'],
                                      config['param_filter_h_trans_bandwidth'], config['param_filer_n_jobs'],
                                      config['param_filter_method'], config['param_filter_iir_params'],
                                      config['param_filter_phase'], config['param_filter_fir_window'],
                                      config['param_filter_fir_design'], config['param_filter_skip_by_annotation'],
                                      config['param_filter_pad'], config['param_apply_notch'],
                                      config['param_notch_freqs_start'], config['param_notch_freqs_end'],
                                      config['param_notch_freqs_step'], config['param_notch_picks'],
                                      config['param_notch_filter_length'], config['param_notch_widths'],
                                      config['param_notch_trans_bandwith'], config['param_notch_n_jobs'],
                                      config['param_notch_method'], config['param_notch_iir_parameters'],
                                      config['param_notch_mt_bandwidth'], config['param_notch_p_value'],
                                      config['param_notch_phase'], config['param_notch_fir_window'],
                                      config['param_notch_fir_design'], config['param_notch_pad'],
                                      config['param_apply_resample'], config['param_resample_sfreq'],
                                      config['param_resample_npad'], config['param_resample_window'],
                                      config['param_resample_stim_picks'], config['param_resample_n_jobs'],
                                      config['param_resample_events'], config['param_resample_pad'])
    del raw_copy

    # Info message about notch filtering if applied
    if config['param_apply_notch'] is True:
        dict_json_product['brainlife'].append({'type': 'info', 'msg': 'Notch filter was applied.'})
        config['param_notch_freqs_start'] = f'{config['param_notch_freqs_start']}Hz and its harmonics.'
    else:
        config['param_notch_freqs_start'] = 'No Notch filter was applied'

    # Info message about resampling if applied
    if config['param_apply_resample'] is True:
        dict_json_product['brainlife'].append({'type': 'info', 'msg': 'Data was resampled at {config["param_sfreq"]}.'})
    else:
    	config['param_resample_sfreq'] = 'Data was not resampled.'

    # Success message in product.json    
    dict_json_product['brainlife'].append({'type': 'success', 'msg': 'Filtering was applied successfully.'})

    # Compute SNR
    snr_before = _compute_snr(raw)
    snr_after = _compute_snr(raw_filtered)

    # Generate a report
    _generate_report(data_file, raw, raw_filtered, bad_channels, comments_about_filtering, config['param_notch_freqs_start'], config['param_resample_sfreq'], snr_before, snr_after)

    # Save the dict_json_product in a json file
    with open('product.json', 'w') as outfile:
        json.dump(dict_json_product, outfile)


if __name__ == '__main__':
    main()
