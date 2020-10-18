-- Gaia schema
CREATE SCHEMA gaiadr2;

-- Regions catalogue
CREATE TABLE IF NOT EXISTS public.regions (
  id serial PRIMARY KEY,
  name text UNIQUE NOT NULL,
  ra double precision DEFAULT NULL,
  dec double precision DEFAULT NULL,
  diam float DEFAULT NULL,
  width float DEFAULT NULL,
  height float DEFAULT NULL,
  properties jsonb DEFAULT NULL,
  UNIQUE (ra, dec)
);

COMMENT ON COLUMN public.regions.id IS 'Entry ID';

COMMENT ON COLUMN public.regions.name IS 'Region name';

COMMENT ON COLUMN public.regions.ra IS 'Right Ascension J2000 (degrees)';

COMMENT ON COLUMN public.regions.dec IS 'Declination J2000 (degrees)';

COMMENT ON COLUMN public.regions.diam IS 'Angular apparent diameter (arcmin)';

COMMENT ON COLUMN public.regions.width IS 'Angular apparent width (arcmin)';

COMMENT ON COLUMN public.regions.height IS 'Angular apparent height (arcmin)';

COMMENT ON COLUMN public.regions.properties IS 'Region properties';

CREATE FUNCTION public.create_partition_table ()
  RETURNS TRIGGER
  LANGUAGE 'plpgsql'
  COST 100 VOLATILE
  SECURITY DEFINER
  AS $BODY$
BEGIN
  EXECUTE 'CREATE TABLE IF NOT EXISTS gaiadr2.region_' || NEW.id || ' PARTITION OF public.gaiadr2_source FOR VALUES IN (' || NEW.id || ');';
  RETURN new;
END;
$BODY$;

CREATE TRIGGER create_partition_table_tri
  AFTER INSERT ON public.regions
  FOR EACH ROW
  EXECUTE FUNCTION public.create_partition_table ();

-- https://gea.esac.esa.int/archive/documentation/GDR2/Gaia_archive/chap_datamodel/sec_dm_main_tables/ssec_dm_gaia_source.html
CREATE TABLE IF NOT EXISTS public.gaiadr2_source (
  region_id integer REFERENCES public.regions (id) NOT NULL,
  source_id bigint NOT NULL,
  solution_id bigint NOT NULL,
  designation text NOT NULL,
  random_index bigint,
  ref_epoch double precision,
  ra double precision,
  ra_error double precision,
  dec double precision,
  dec_error double precision,
  parallax double precision,
  parallax_error double precision,
  parallax_over_error float,
  pmra double precision,
  pmra_error double precision,
  pmdec double precision,
  pmdec_error double precision,
  ra_dec_corr float,
  ra_parallax_corr float,
  ra_pmra_corr float,
  ra_pmdec_corr float,
  dec_parallax_corr float,
  dec_pmra_corr float,
  dec_pmdec_corr float,
  parallax_pmra_corr float,
  parallax_pmdec_corr float,
  pmra_pmdec_corr float,
  astrometric_n_obs_al integer,
  astrometric_n_obs_ac integer,
  astrometric_n_good_obs_al integer,
  astrometric_n_bad_obs_al integer,
  astrometric_gof_al float,
  astrometric_chi2_al float,
  astrometric_excess_noise double precision,
  astrometric_excess_noise_sig double precision,
  astrometric_params_solved integer,
  astrometric_primary_flag boolean,
  astrometric_weight_al float,
  astrometric_pseudo_colour double precision,
  astrometric_pseudo_colour_error double precision,
  mean_varpi_factor_al float,
  astrometric_matched_observations smallint,
  visibility_periods_used smallint,
  astrometric_sigma5d_max float,
  frame_rotator_object_type integer,
  matched_observations smallint,
  duplicated_source boolean,
  phot_g_n_obs integer,
  phot_g_mean_flux double precision,
  phot_g_mean_flux_error double precision,
  phot_g_mean_flux_over_error float,
  phot_g_mean_mag float,
  phot_bp_n_obs integer,
  phot_bp_mean_flux double precision,
  phot_bp_mean_flux_error float,
  phot_bp_mean_flux_over_error float,
  phot_bp_mean_mag float,
  phot_rp_n_obs integer,
  phot_rp_mean_flux double precision,
  phot_rp_mean_flux_error double precision,
  phot_rp_mean_flux_over_error float,
  phot_rp_mean_mag float,
  phot_bp_rp_excess_factor float,
  phot_proc_mode integer,
  bp_rp float,
  bp_g float,
  g_rp float,
  radial_velocity double precision,
  radial_velocity_error double precision,
  rv_nb_transits integer,
  rv_template_teff float,
  rv_template_logg float,
  rv_template_fe_h float,
  phot_variable_flag text,
  l double precision,
  b double precision,
  ecl_lon double precision,
  ecl_lat double precision,
  priam_flags bigint,
  teff_val float,
  teff_percentile_lower float,
  teff_percentile_upper float,
  a_g_val float,
  a_g_percentile_lower float,
  a_g_percentile_upper float,
  e_bp_min_rp_val float,
  e_bp_min_rp_percentile_lower float,
  e_bp_min_rp_percentile_upper float,
  flame_flags bigint,
  radius_val float,
  radius_percentile_lower float,
  radius_percentile_upper float,
  lum_val float,
  lum_percentile_lower float,
  lum_percentile_upper float,
  PRIMARY KEY (region_id, source_id)
)
PARTITION BY LIST (region_id);

CREATE INDEX source_id_idx ON public.gaiadr2_source (source_id);

COMMENT ON TABLE public.gaiadr2_source IS 'Table that replicates Gaia DR2 data. More info at: https://gea.esac.esa.int/archive/documentation/GDR2/Gaia_archive/chap_datamodel/sec_dm_main_tables/ssec_dm_gaia_source.html';

COMMENT ON COLUMN public.gaiadr2_source.region_id IS 'ID of the container region';

COMMENT ON COLUMN public.gaiadr2_source.source_id IS 'Unique source identifier (unique within a particular Data Release)';

COMMENT ON COLUMN public.gaiadr2_source.solution_id IS 'Solution Identifier';

COMMENT ON COLUMN public.gaiadr2_source.designation IS 'Unique source designation (unique across all Data Releases)';

COMMENT ON COLUMN public.gaiadr2_source.random_index IS 'Random index used to select subsets';

COMMENT ON COLUMN public.gaiadr2_source.ref_epoch IS 'Reference epoch (Time[Julian Years])';

COMMENT ON COLUMN public.gaiadr2_source.ra IS 'Right ascension (Angle[deg])';

COMMENT ON COLUMN public.gaiadr2_source.ra_error IS 'Standard error of right ascension (Angle[mas])';

COMMENT ON COLUMN public.gaiadr2_source.dec IS 'Declination (Angle[deg])';

COMMENT ON COLUMN public.gaiadr2_source.dec_error IS 'Standard error of declination (Angle[mas])';

COMMENT ON COLUMN public.gaiadr2_source.parallax IS 'Parallax (Angle[mas])';

COMMENT ON COLUMN public.gaiadr2_source.parallax_error IS 'Standard error of parallax (Angle[mas])';

COMMENT ON COLUMN public.gaiadr2_source.parallax_over_error IS 'Parallax divided by its error';

COMMENT ON COLUMN public.gaiadr2_source.pmra IS 'Proper motion in right ascension direction (Angular Velocity[mas/year])';

COMMENT ON COLUMN public.gaiadr2_source.pmra_error IS 'Standard error of proper motion in right ascension direction (Angular Velocity[mas/year])';

COMMENT ON COLUMN public.gaiadr2_source.pmdec IS 'Proper motion in declination direction (Angular Velocity[mas/year])';

COMMENT ON COLUMN public.gaiadr2_source.pmdec_error IS 'Standard error of proper motion in declination direction (Angular Velocity[mas/year])';

COMMENT ON COLUMN public.gaiadr2_source.ra_dec_corr IS 'Correlation between right ascension and declination (Dimensionless[see description])';

COMMENT ON COLUMN public.gaiadr2_source.ra_parallax_corr IS 'Correlation between right ascension and parallax (Dimensionless[see description])';

COMMENT ON COLUMN public.gaiadr2_source.ra_pmra_corr IS 'Correlation between right ascension and proper motion in right ascension (Dimensionless[see description])';

COMMENT ON COLUMN public.gaiadr2_source.ra_pmdec_corr IS 'Correlation between right ascension and proper motion in declination (Dimensionless[see description])';

COMMENT ON COLUMN public.gaiadr2_source.dec_parallax_corr IS 'Correlation between declination and parallax (Dimensionless[see description])';

COMMENT ON COLUMN public.gaiadr2_source.dec_pmra_corr IS 'Correlation between declination and proper motion in right ascension (Dimensionless[see description])';

COMMENT ON COLUMN public.gaiadr2_source.dec_pmdec_corr IS 'Correlation between declination and proper motion in declination (Dimensionless[see description])';

COMMENT ON COLUMN public.gaiadr2_source.parallax_pmra_corr IS 'Correlation between parallax and proper motion in right ascension (Dimensionless[see description])';

COMMENT ON COLUMN public.gaiadr2_source.parallax_pmdec_corr IS 'Correlation between parallax and proper motion in declination (Dimensionless[see description])';

COMMENT ON COLUMN public.gaiadr2_source.pmra_pmdec_corr IS 'Correlation between proper motion in right ascension and proper motion in declination (Dimensionless[see description])';

COMMENT ON COLUMN public.gaiadr2_source.astrometric_n_obs_al IS 'Total number of observations AL';

COMMENT ON COLUMN public.gaiadr2_source.astrometric_n_obs_ac IS 'Total number of observations AC';

COMMENT ON COLUMN public.gaiadr2_source.astrometric_n_good_obs_al IS 'Number of good observations AL';

COMMENT ON COLUMN public.gaiadr2_source.astrometric_n_bad_obs_al IS 'Number of bad observations AL';

COMMENT ON COLUMN public.gaiadr2_source.astrometric_gof_al IS 'Goodness of fit statistic of model wrt along-scan observations';

COMMENT ON COLUMN public.gaiadr2_source.astrometric_chi2_al IS 'AL chi-square value';

COMMENT ON COLUMN public.gaiadr2_source.astrometric_excess_noise IS 'Excess noise of the source';

COMMENT ON COLUMN public.gaiadr2_source.astrometric_excess_noise_sig IS 'Significance of excess noise';

COMMENT ON COLUMN public.gaiadr2_source.astrometric_params_solved IS 'Which parameters have been solved for?';

COMMENT ON COLUMN public.gaiadr2_source.astrometric_primary_flag IS 'Primary or seconday';

COMMENT ON COLUMN public.gaiadr2_source.astrometric_weight_al IS 'Mean astrometric weight of the source (Angle[mas^−2])';

COMMENT ON COLUMN public.gaiadr2_source.astrometric_pseudo_colour IS 'Astrometrically determined pseudocolour of the source (Misc[μm^−1])';

COMMENT ON COLUMN public.gaiadr2_source.astrometric_pseudo_colour_error IS 'Standard error of the pseudocolour of the source (Misc[μm^−1])';

COMMENT ON COLUMN public.gaiadr2_source.mean_varpi_factor_al IS 'Mean Parallax factor AL';

COMMENT ON COLUMN public.gaiadr2_source.astrometric_matched_observations IS 'Matched FOV transits used in the AGIS solution';

COMMENT ON COLUMN public.gaiadr2_source.visibility_periods_used IS 'Number of visibility periods used in Astrometric solution';

COMMENT ON COLUMN public.gaiadr2_source.astrometric_sigma5d_max IS 'The longest semi-major axis of the 5-d error ellipsoid (Angle[mas])';

COMMENT ON COLUMN public.gaiadr2_source.frame_rotator_object_type IS 'The type of the source mainly used for frame rotation';

COMMENT ON COLUMN public.gaiadr2_source.matched_observations IS 'Amount of observations matched to this source';

COMMENT ON COLUMN public.gaiadr2_source.duplicated_source IS 'Source with duplicate sources';

COMMENT ON COLUMN public.gaiadr2_source.phot_g_n_obs IS 'Number of observations contributing to G photometry';

COMMENT ON COLUMN public.gaiadr2_source.phot_g_mean_flux IS 'G-band mean flux (Flux[e-/s])';

COMMENT ON COLUMN public.gaiadr2_source.phot_g_mean_flux_error IS 'Error on G-band mean flux (Flux[e-/s])';

COMMENT ON COLUMN public.gaiadr2_source.phot_g_mean_flux_over_error IS 'G-band mean flux divided by its error';

COMMENT ON COLUMN public.gaiadr2_source.phot_g_mean_mag IS 'G-band mean magnitude (Magnitude[mag])';

COMMENT ON COLUMN public.gaiadr2_source.phot_bp_n_obs IS 'Number of observations contributing to BP photometry';

COMMENT ON COLUMN public.gaiadr2_source.phot_bp_mean_flux IS 'Integrated BP mean flux (Flux[e-/s])';

COMMENT ON COLUMN public.gaiadr2_source.phot_bp_mean_flux_error IS 'Error on the integrated BP mean flux (Flux[e-/s])';

COMMENT ON COLUMN public.gaiadr2_source.phot_bp_mean_flux_over_error IS 'Integrated BP mean flux divided by its error';

COMMENT ON COLUMN public.gaiadr2_source.phot_bp_mean_mag IS 'Integrated BP mean magnitude (Magnitude[mag])';

COMMENT ON COLUMN public.gaiadr2_source.phot_rp_n_obs IS 'Number of observations contributing to RP photometry';

COMMENT ON COLUMN public.gaiadr2_source.phot_rp_mean_flux IS 'Integrated RP mean flux (Flux[e-/s])';

COMMENT ON COLUMN public.gaiadr2_source.phot_rp_mean_flux_error IS 'Error on the integrated RP mean flux (Flux[e-/s])';

COMMENT ON COLUMN public.gaiadr2_source.phot_rp_mean_flux_over_error IS 'Integrated RP mean flux divided by its error';

COMMENT ON COLUMN public.gaiadr2_source.phot_rp_mean_mag IS 'Integrated RP mean magnitude (Magnitude[mag])';

COMMENT ON COLUMN public.gaiadr2_source.phot_bp_rp_excess_factor IS 'BP/RP excess factor';

COMMENT ON COLUMN public.gaiadr2_source.phot_proc_mode IS 'Photometry processing mode';

COMMENT ON COLUMN public.gaiadr2_source.bp_rp IS 'BP - RP colour (Magnitude[mag])';

COMMENT ON COLUMN public.gaiadr2_source.bp_g IS 'BP - G colour (Magnitude[mag])';

COMMENT ON COLUMN public.gaiadr2_source.g_rp IS 'RP colour (Magnitude[mag])';

COMMENT ON COLUMN public.gaiadr2_source.radial_velocity IS 'Radial velocity (Velocity[km/s])';

COMMENT ON COLUMN public.gaiadr2_source.radial_velocity_error IS 'Radial velocity error (Velocity[km/s])';

COMMENT ON COLUMN public.gaiadr2_source.rv_nb_transits IS 'Number of transits used to compute radial velocity';

COMMENT ON COLUMN public.gaiadr2_source.rv_template_teff IS 'Teff of the template used to compute radial velocity (Temperature[K])';

COMMENT ON COLUMN public.gaiadr2_source.rv_template_logg IS 'logg of the template used to compute radial velocity (GravitySurface[log cgs])';

COMMENT ON COLUMN public.gaiadr2_source.rv_template_fe_h IS 'Fe/H of the template used to compute radial velocity (Abundances[dex])';

COMMENT ON COLUMN public.gaiadr2_source.phot_variable_flag IS 'Photometric variability flag (Dimensionless[see description])';

COMMENT ON COLUMN public.gaiadr2_source.l IS 'Galactic longitude (Angle[deg])';

COMMENT ON COLUMN public.gaiadr2_source.b IS 'Galactic latitude (Angle[deg])';

COMMENT ON COLUMN public.gaiadr2_source.ecl_lon IS 'Ecliptic longitude (Angle[deg])';

COMMENT ON COLUMN public.gaiadr2_source.ecl_lat IS 'Ecliptic latitude (Angle[deg])';

COMMENT ON COLUMN public.gaiadr2_source.priam_flags IS 'flags for the Apsis-Priam results (Dimensionless[see description])';

COMMENT ON COLUMN public.gaiadr2_source.teff_val IS 'Stellar effective temperature (Temperature[K])';

COMMENT ON COLUMN public.gaiadr2_source.teff_percentile_lower IS 'teff_val lower uncertainty (Temperature[K])';

COMMENT ON COLUMN public.gaiadr2_source.teff_percentile_upper IS 'teff_val upper uncertainty (Temperature[K])';

COMMENT ON COLUMN public.gaiadr2_source.a_g_val IS 'Line-of-sight extinction in the G band, A_G (Magnitude[mag])';

COMMENT ON COLUMN public.gaiadr2_source.a_g_percentile_lower IS 'a_g_val lower uncertainty (Magnitude[mag])';

COMMENT ON COLUMN public.gaiadr2_source.a_g_percentile_upper IS 'a_g_val upper uncertainty (Magnitude[mag])';

COMMENT ON COLUMN public.gaiadr2_source.e_bp_min_rp_val IS 'Line-of-sight reddening E(BP-RP) (Magnitude[mag])';

COMMENT ON COLUMN public.gaiadr2_source.e_bp_min_rp_percentile_lower IS 'e_bp_min_rp_val lower uncertainty (Magnitude[mag])';

COMMENT ON COLUMN public.gaiadr2_source.e_bp_min_rp_percentile_upper IS 'e_bp_min_rp_val upper uncertainty (Magnitude[mag])';

COMMENT ON COLUMN public.gaiadr2_source.flame_flags IS 'Flags for the Apsis-FLAME results (Dimensionless[see description])';

COMMENT ON COLUMN public.gaiadr2_source.radius_val IS 'Stellar radius (Length & Distance[Solar Radius])';

COMMENT ON COLUMN public.gaiadr2_source.radius_percentile_lower IS 'radius_val lower uncertainty (Length & Distance[Solar Radius])';

COMMENT ON COLUMN public.gaiadr2_source.radius_percentile_upper IS 'radius_val upper uncertainty (Length & Distance[Solar Radius])';

COMMENT ON COLUMN public.gaiadr2_source.lum_val IS 'Stellar luminosity (Luminosity[Solar Luminosity])';

COMMENT ON COLUMN public.gaiadr2_source.lum_percentile_lower IS 'lum_val lower uncertainty (Luminosity[Solar Luminosity])';

COMMENT ON COLUMN public.gaiadr2_source.lum_percentile_upper IS 'lum_val upper uncertainty (Luminosity[Solar Luminosity])';
