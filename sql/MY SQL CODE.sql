-- Table: public.financial_risk_data

-- DROP TABLE IF EXISTS public.financial_risk_data;

CREATE TABLE IF NOT EXISTS public.financial_risk_data
(
    bond_id character varying(300) COLLATE pg_catalog."default" NOT NULL,
    issuer character varying(300) COLLATE pg_catalog."default" NOT NULL,
    face_value numeric,
    coupon_rate numeric,
    years_to_maturity numeric,
    ytm numeric,
    frequency integer,
    historical_volatility numeric
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.financial_risk_data
    OWNER to postgres;
