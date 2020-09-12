-- Gaia schema
CREATE SCHEMA cdalvaro;

-- Regions catalogue
CREATE TABLE IF NOT EXISTS cdalvaro.regions (
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

COMMENT ON COLUMN cdalvaro.regions.id
    IS 'Identificador del registro en la tabla';


CREATE FUNCTION create_partition_table()
RETURNS TRIGGER
LANGUAGE 'plpgsql'
COST 100
VOLATILE SECURITY DEFINER
AS $BODY$
  BEGIN
    EXECUTE 'CREATE TABLE IF NOT EXISTS gaiadr2.gaia_source_rg' || new.id
      || ' PARTITION OF gaiadr2.gaia_source FOR VALUES IN (' || new.id || ');';
    RETURN new;
  END;
$BODY$;

CREATE TRIGGER create_partition_table_tri
  AFTER INSERT ON cdalvaro.regions
  FOR EACH ROW
  EXECUTE FUNCTION create_partition_table();

-- Gaia schema
CREATE SCHEMA gaiadr2;

-- https://gea.esac.esa.int/archive/documentation/GDR2/Gaia_archive/chap_datamodel/sec_dm_main_tables/ssec_dm_gaia_source.html
CREATE TABLE IF NOT EXISTS gaiadr2.gaia_source (
  region_id integer REFERENCES cdalvaro.regions(id) NOT NULL,
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
  astrometric_primary_flag BOOLEAN,
  astrometric_weight_al float,
  astrometric_pseudo_colour double precision,
  astrometric_pseudo_colour_error double precision,
  mean_varpi_factor_al float,
  astrometric_matched_observations SMALLINT,
  visibility_periods_used SMALLINT,
  astrometric_sigma5d_max float,
  frame_rotator_object_type integer,
  matched_observations SMALLINT,
  duplicated_source BOOLEAN,
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
PARTITION BY LIST(region_id);

CREATE INDEX source_id_idx ON gaiadr2.gaia_source (source_id);
