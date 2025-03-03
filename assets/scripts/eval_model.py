import logging, os, sys, time
from datasets import load_dataset, get_dataset_config_names

RID = f"{int(time.time())}"
c_log, f_log = logging.getLogger("console"), logging.getLogger("file")

LANGS = [
    {"c": "ar", "n": "Arabic"}, {"c": "cs", "n": "Czech"},
    {"c": "de", "n": "German"}, {"c": "en", "n": "English"}, {"c": "es", "n": "Spanish"},
    {"c": "fa", "n": "Persian"}, {"c": "fr", "n": "French"}, {"c": "he", "n": "Hebrew"},
    {"c": "hi", "n": "Hindi"}, {"c": "id", "n": "Indonesian"}, {"c": "it", "n": "Italian"},
    {"c": "ja", "n": "Japanese"}, {"c": "km", "n": "Khmer"}, {"c": "ko", "n": "Korean"},
    {"c": "lo", "n": "Lao"}, {"c": "ms", "n": "Malay"}, {"c": "my", "n": "Burmese"},
    {"c": "nl", "n": "Dutch"}, {"c": "pl", "n": "Polish"}, {"c": "pt", "n": "Portuguese"},
    {"c": "ru", "n": "Russian"}, {"c": "th", "n": "Thai"}, {"c": "tl", "n": "Tagalog"},
    {"c": "tr", "n": "Turkish"}, {"c": "ur", "n": "Urdu"}, {"c": "vi", "n": "Vietnamese"},
    {"c": "zh", "n": "Chinese"}, {"c": "as", "n": "Assamese"}, {"c": "syl", "n": "Sylheti"}
]

SCHEMATA = ["smoldoc", "smolsent", "gatitos"]

flores2smol = {
'ace_Arab': 'ace-Arab', 'ace_Latn': 'ace', 'acm_Arab': 'acm', 'acq_Arab': 'acq', 'aeb_Arab': 'aeb', 'afr_Latn': 'af', 'ajp_Arab': 'ajp',
'aka_Latn': 'ak', 'als_Latn': 'sq', 'amh_Ethi': 'am', 'apc_Arab': 'apc', 'arb_Arab': 'ar', 'arb_Latn': 'ar-Latn', 'ars_Arab': 'ars',
'ary_Arab': 'ar-MA', 'arz_Arab': 'arz', 'asm_Beng': 'as', 'ast_Latn': 'ast', 'awa_Deva': 'awa', 'ayr_Latn': 'ay', 'azb_Arab': 'azb',
'azj_Latn': 'az', 'bak_Cyrl': 'ba', 'bam_Latn': 'bm', 'ban_Latn': 'ban', 'bel_Cyrl': 'be', 'bem_Latn': 'bem', 'ben_Beng': 'bn',
'bho_Deva': 'bho', 'bjn_Arab': 'bjn-Arab', 'bjn_Latn': 'bjn', 'bod_Tibt': 'bo', 'bos_Latn': 'bs', 'bug_Latn': 'bug', 'bul_Cyrl': 'bg',
'cat_Latn': 'ca', 'ceb_Latn': 'ceb', 'ces_Latn': 'cs', 'cjk_Latn': 'cjk', 'ckb_Arab': 'ckb', 'crh_Latn': 'crh-Latn', 'cym_Latn': 'cy',
'dan_Latn': 'da', 'deu_Latn': 'de', 'dik_Latn': 'din', 'dyu_Latn': 'dyu', 'dzo_Tibt': 'dz', 'ell_Grek': 'el', 'eng_Latn': 'en',
'epo_Latn': 'eo', 'est_Latn': 'et', 'eus_Latn': 'eu', 'ewe_Latn': 'ee', 'fao_Latn': 'fo', 'fij_Latn': 'fj', 'fin_Latn': 'fi',
'fon_Latn': 'fon', 'fra_Latn': 'fr', 'fur_Latn': 'fur', 'fuv_Latn': 'ff', 'gaz_Latn': 'om', 'gla_Latn': 'gd', 'gle_Latn': 'ga',
'glg_Latn': 'gl', 'grn_Latn': 'gn', 'guj_Gujr': 'gu', 'hat_Latn': 'ht', 'hau_Latn': 'ha', 'heb_Hebr': 'iw', 'hin_Deva': 'hi',
'hne_Deva': 'hne', 'hrv_Latn': 'hr', 'hun_Latn': 'hu', 'hye_Armn': 'hy', 'ibo_Latn': 'ig', 'ilo_Latn': 'ilo', 'ind_Latn': 'id',
'isl_Latn': 'is', 'ita_Latn': 'it', 'jav_Latn': 'jv', 'jpn_Jpan': 'ja', 'kab_Latn': 'kab', 'kac_Latn': 'kac', 'kam_Latn': 'kam',
'kan_Knda': 'kn', 'kas_Arab': 'ks', 'kas_Deva': 'ks-Deva', 'kat_Geor': 'ka', 'kaz_Cyrl': 'kk', 'kbp_Latn': 'kbp', 'kea_Latn': 'kea',
'khk_Cyrl': 'mn', 'khm_Khmr': 'km', 'kik_Latn': 'ki', 'kin_Latn': 'rw', 'kir_Cyrl': 'ky', 'kmb_Latn': 'kmb', 'kmr_Latn': 'ku',
'knc_Arab': 'kr-Arab', 'knc_Latn': 'kr', 'kon_Latn': 'kg', 'kor_Hang': 'ko', 'lao_Laoo': 'lo', 'lij_Latn': 'lij', 'lim_Latn': 'li',
'lin_Latn': 'ln', 'lit_Latn': 'lt', 'lmo_Latn': 'lmo', 'ltg_Latn': 'ltg', 'ltz_Latn': 'lb', 'lua_Latn': 'lua', 'lug_Latn': 'lg',
'luo_Latn': 'luo', 'lus_Latn': 'lus', 'lvs_Latn': 'lv', 'mag_Deva': 'mag', 'mai_Deva': 'mai', 'mal_Mlym': 'ml', 'mar_Deva': 'mr',
'min_Arab': 'min-Arab', 'min_Latn': 'min', 'mkd_Cyrl': 'mk', 'mlt_Latn': 'mt', 'mni_Beng': 'mni', 'mos_Latn': 'mos', 'mri_Latn': 'mi',
'mya_Mymr': 'my', 'nld_Latn': 'nl', 'nno_Latn': 'nn', 'nob_Latn': 'no', 'npi_Deva': 'ne', 'nso_Latn': 'nso', 'nus_Latn': 'nus',
'nya_Latn': 'ny', 'oci_Latn': 'oc', 'ory_Orya': 'or', 'pag_Latn': 'pag', 'pan_Guru': 'pa', 'pap_Latn': 'pap', 'pbt_Arab': 'ps',
'pes_Arab': 'fa', 'plt_Latn': 'mg', 'pol_Latn': 'pl', 'por_Latn': 'pt', 'prs_Arab': 'fa-AF', 'quy_Latn': 'quy', 'ron_Latn': 'ro',
'run_Latn': 'rn', 'rus_Cyrl': 'ru', 'sag_Latn': 'sg', 'san_Deva': 'sa', 'sat_Olck': 'sat', 'scn_Latn': 'scn', 'shn_Mymr': 'shn',
'sin_Sinh': 'si', 'slk_Latn': 'sk', 'slv_Latn': 'sl', 'smo_Latn': 'sm', 'sna_Latn': 'sn', 'snd_Arab': 'sd', 'som_Latn': 'so',
'sot_Latn': 'st', 'spa_Latn': 'es', 'srd_Latn': 'sc', 'srp_Cyrl': 'sr', 'ssw_Latn': 'ss', 'sun_Latn': 'su', 'swe_Latn': 'sv',
'swh_Latn': 'sw', 'szl_Latn': 'szl', 'tam_Taml': 'ta', 'taq_Latn': 'taq', 'taq_Tfng': 'taq-Tfng', 'tat_Cyrl': 'tt', 'tel_Telu': 'te',
'tgk_Cyrl': 'tg', 'tgl_Latn': 'fil', 'tha_Thai': 'th', 'tir_Ethi': 'ti', 'tpi_Latn': 'tpi', 'tsn_Latn': 'tn', 'tso_Latn': 'ts',
'tuk_Latn': 'tk', 'tum_Latn': 'tum', 'tur_Latn': 'tr', 'twi_Latn': 'ak', 'tzm_Tfng': 'ber', 'uig_Arab': 'ug', 'ukr_Cyrl': 'uk',
'umb_Latn': 'umb', 'urd_Arab': 'ur', 'uzn_Latn': 'uz', 'vec_Latn': 'vec', 'vie_Latn': 'vi', 'war_Latn': 'war', 'wol_Latn': 'wo',
'xho_Latn': 'xh', 'ydd_Hebr': 'yi', 'yor_Latn': 'yo', 'yue_Hant': 'yue', 'zho_Hans': 'zh', 'zho_Hant': 'zh-Hant', 'zsm_Latn': 'ms', 'zul_Latn': 'zu',}

def log(m, c=True):
    try:
        if hasattr(f_log, 'handlers') and f_log.handlers: f_log.info(m)
        if c and hasattr(c_log, 'handlers') and c_log.handlers:
            try: c_log.info(m)
            except UnicodeEncodeError: c_log.info(m.encode('ascii', errors='replace').decode('ascii'))
    except: pass

def setup(od=None):
    bd = os.path.abspath(od) if od else os.getcwd()
    ld, rd = os.path.join(bd, "logs"), os.path.join(bd, "results")
    for p in [ld, rd]: os.makedirs(p, exist_ok=True)
    
    global c_log, f_log
    for lg in [c_log, f_log]: 
        if lg.handlers: lg.handlers.clear()
    
    c_handler = logging.StreamHandler()
    c_handler.setFormatter(logging.Formatter("[%(asctime)s] %(message)s", "%X"))
    c_log.addHandler(c_handler)
    c_log.setLevel(logging.INFO)
    
    f_handler = logging.FileHandler(os.path.join(ld, f"{RID}_eval.log"), encoding='utf-8')
    f_handler.setFormatter(logging.Formatter("[%(asctime)s] %(message)s", "%X"))
    f_log.addHandler(f_handler)
    f_log.setLevel(logging.INFO)
    
    log(f"Setup complete. Logs: {ld}, Results: {rd}")
    return {"b": bd, "r": rd, "l": ld}

def main():
    _ = setup()
    log(f"Starting dataset download")
    log(f"Run ID: {RID}")
    
    log(f"LANGS: {[(l['c'], l['n']) for l in LANGS]}")
    num_langs = len([l for l in LANGS if l['c'] != 'en'])
    log(f"Number of languages to evaluate (excluding English): {num_langs}")
    configs = get_dataset_config_names("google/smol")
    log(f"Found {len(configs)} configs")
    log(f"All configs: {configs}")

    config_by_schema = {schema: [c for c in configs if c.startswith(schema)] for schema in SCHEMATA}
    
    lang_schema_mapping = {}
    
    for lang in LANGS:
        if lang["c"] == "en": continue
        
        smol_code = flores2smol.get(f"{lang['c']}_Latn", lang["c"])
        
        found = False
        for schema in SCHEMATA:
            config_name = f"{schema}__en_{smol_code}"
            if config_name in config_by_schema[schema]:
                lang_schema_mapping[lang["n"]] = schema
                found = True
                break

            alt_config_names = [
                f"{schema}__en_{smol_code.replace('zh', 'yue')}",
                f"{schema}__yue_{smol_code.replace('yue', 'zh')}",
                f"{schema}__en_{smol_code.replace('ar', 'ar-MA')}",
                f"{schema}__en_{smol_code.replace('bn', 'as')}",
                f"{schema}__en_{smol_code.replace('bn', 'syl')}",
                f"{schema}__en_{smol_code.replace('bn', 'ctg')}",
                f"{schema}__en_{smol_code.replace('as', 'bn')}",
                f"{schema}__en_{smol_code.replace('syl', 'bn')}",
                f"{schema}__en_{smol_code.replace('ctg', 'bn')}"
            ]
            
            for alt_config_name in alt_config_names:
                if alt_config_name in config_by_schema[schema]:
                    lang_schema_mapping[lang["n"]] = schema
                    found = True
                    break
            if found: break
        if not found:
            log(f"ERROR: No dataset found for {lang['n']} ({lang['c']})")
            sys.exit(1)
    
    log(f"Language to Schema mapping: {lang_schema_mapping}")

if __name__ == "__main__":
    main()
