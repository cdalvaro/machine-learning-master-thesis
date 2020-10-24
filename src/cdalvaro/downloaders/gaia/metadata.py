from typing import List


class GaiaMetadata:
    """
    Class containing Gaia DR2 metadata
    """

    _columns = ('solution_id', 'designation', 'source_id', 'random_index', 'ref_epoch', 'ra', 'ra_error', 'dec',
                'dec_error', 'parallax', 'parallax_error', 'parallax_over_error', 'pmra', 'pmra_error', 'pmdec',
                'pmdec_error', 'ra_dec_corr', 'ra_parallax_corr', 'ra_pmra_corr', 'ra_pmdec_corr', 'dec_parallax_corr',
                'dec_pmra_corr', 'dec_pmdec_corr', 'parallax_pmra_corr', 'parallax_pmdec_corr', 'pmra_pmdec_corr',
                'astrometric_n_obs_al', 'astrometric_n_obs_ac', 'astrometric_n_good_obs_al', 'astrometric_n_bad_obs_al',
                'astrometric_gof_al', 'astrometric_chi2_al', 'astrometric_excess_noise', 'astrometric_excess_noise_sig',
                'astrometric_params_solved', 'astrometric_primary_flag', 'astrometric_weight_al',
                'astrometric_pseudo_colour', 'astrometric_pseudo_colour_error', 'mean_varpi_factor_al',
                'astrometric_matched_observations', 'visibility_periods_used', 'astrometric_sigma5d_max',
                'frame_rotator_object_type', 'matched_observations', 'duplicated_source', 'phot_g_n_obs',
                'phot_g_mean_flux', 'phot_g_mean_flux_error', 'phot_g_mean_flux_over_error', 'phot_g_mean_mag',
                'phot_bp_n_obs', 'phot_bp_mean_flux', 'phot_bp_mean_flux_error', 'phot_bp_mean_flux_over_error',
                'phot_bp_mean_mag', 'phot_rp_n_obs', 'phot_rp_mean_flux', 'phot_rp_mean_flux_error',
                'phot_rp_mean_flux_over_error', 'phot_rp_mean_mag', 'phot_bp_rp_excess_factor', 'phot_proc_mode',
                'bp_rp', 'bp_g', 'g_rp', 'radial_velocity', 'radial_velocity_error', 'rv_nb_transits',
                'rv_template_teff', 'rv_template_logg', 'rv_template_fe_h', 'phot_variable_flag', 'l', 'b', 'ecl_lon',
                'ecl_lat', 'priam_flags', 'teff_val', 'teff_percentile_lower', 'teff_percentile_upper', 'a_g_val',
                'a_g_percentile_lower', 'a_g_percentile_upper', 'e_bp_min_rp_val', 'e_bp_min_rp_percentile_lower',
                'e_bp_min_rp_percentile_upper', 'flame_flags', 'radius_val', 'radius_percentile_lower',
                'radius_percentile_upper', 'lum_val', 'lum_percentile_lower', 'lum_percentile_upper')

    @staticmethod
    def columns():
        """
        Gaia DR2 database columns.

        Returns:
            tuple(str): A tuple containing the Gaia DR2 columns
        """
        return GaiaMetadata._columns
