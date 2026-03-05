"""
main_test_cases.py — Comprehensive Location Matcher Test Cases
===============================================================
200 real-world style test cases covering sanctioned countries (Iran, North Korea,
Syria, Cuba, Russia) and their cities.

Each entry is a tuple:
    (query, elastic_result)

query        : A raw address string a user/system might submit.
elastic_result: A comma-separated string of names/aliases/abbreviations
               returned from an Elasticsearch hit that the matcher must score
               the query against (similar to the 'name' or 'alias_name' fields).

Intentional typos and misspellings are present in the query's country token so
the matcher's fuzzy / phonetic stages can be evaluated properly.

No expected scores are stored here — this file is purely a data source.
"""

from matcher.location_matcher import score_with_variants
from matcher.location_matcher import LocationMatcher

# ---------------------------------------------------------------------------
# TEST CASE DATA
# Format: (query_address, elastic_result_string)
# ---------------------------------------------------------------------------

TEST_CASES = [

    # ════════════════════════════════════════════════════════════════════════
    # IRAN — Cases 1-20
    # ════════════════════════════════════════════════════════════════════════

    # 1 — city missing from elastic result
    (
        "Unit 4B, Building 12, Azadi Street, District 4, Tehran, 14567, Kirana",
        "Iran, Islamic Republic of Iran, IRI, Persia, IR, IRN"
    ),
    # 2 — only abbreviations, no city or full name
    (
        "Apt 102, Pars Tower, Valiasr Avenue, Suite 2, Tehran, 19934, Iraanx",
        "IR, IRN, IRI, ایران, Tehran"
    ),
    # 3 — partial country match, different province
    (
        "Warehouse 5, Industrial Zone B, Shiraz Road, Shiraz, 71345, Irqn",
        "Iran, IRN, IR, Shiraz, Southern Province"
    ),
    # 4 — only Persian script and one alias
    (
        "Room 202, Block C, Tabriz Avenue, North Side, Tabriz, 51367, Ira-n",
        "ایران, IRI, Tabriz"
    ),
    # 5 — no city, minimal elastic
    (
        "Floor 3, Qom Plaza, Qom City Center, Qom, 37198, Iryaan",
        "Iran, Islamic Republic of Iran, IRN"
    ),
    # 6 — wrong province name
    (
        "Shop 15, Ahvaz Shopping Mall, Ahvaz Street, Ahvaz, 61357, Irrn",
        "Iran, IRI, IR, Ahvaz, Tehran Province"
    ),
    # 7 — city misspelled in elastic
    (
        "Suite 9, Rasht Central Building, Rasht District, Rasht, 41336, I-ran",
        "Iran, Islamic Republic of Iran, IR, Rasht, Gilan"
    ),
    # 8 — no province, minimal
    (
        "Building 7, Kerman Business Park, Kerman, 76135, Irann",
        "Iran, IRN, Kerman"
    ),
    # 9 — city absent, only country variants
    (
        "Apt 55, Azadi Heights, Tehrann Center, Tehran, 14567, Iraqn",
        "Iran, Islamic Republic of Iran, IRI, IR, IRN, Persia"
    ),
    # 10 — only script variants
    (
        "Floor 1, Vali Asr Office Complex, Tehran, 19934, Ir-an",
        "ایران, Persia, IRN, Tehran"
    ),
    # 11 — wrong country (partial overlap)
    (
        "Block 20, Enghelab Residential, Tehran, 15875, Irnaa",
        "Iraq, IRQ, IQ, Baghdad, Tehran"
    ),
    # 12 — elastic has only codes
    (
        "Suite 112, Shiraz Plaza, Shiraz, 71345, Iranx",
        "IR, IRN, SHZ, Shiraz"
    ),
    # 13 — province only, no full country name
    (
        "Building 30, Karaj Industrial Estate, Karaj, 31345, Irawn",
        "Alborz Province, Karaj, Iran, IRN"
    ),
    # 14 — city present but country missing
    (
        "Apt 12, Tabriz Central, Tabriz, 51367, I-ranx",
        "East Azerbaijan, Tabriz, IRI"
    ),
    # 15 — only one token matches
    (
        "Floor 8, Qom Tower, Qom, 37198, Irran",
        "Iran, Qom Province"
    ),
    # 16 — similar but different country
    (
        "Unit 25, Ahvaz Business Center, Ahvaz, 61357, Irano",
        "Iraq, Khuzestan, Ahvaz, IRN"
    ),
    # 17 — elastic has city typo
    (
        "Building 4, Rasht Residential Block, Rasht, 41336, Iryaan",
        "Iran, Islamic Republic, IR, Rasth, Gilan Province"
    ),
    # 18 — partial, no ISO codes
    (
        "Office 7, Kerman Main Square, Kerman, 76135, Irqn",
        "Iran, Persia, Kerman, Kerman Province"
    ),
    # 19 — no city in elastic
    (
        "Floor 10, Azadi Trade Center, Tehran, 14567, Ira-n",
        "Iran, Islamic Republic of Iran, IRI, Persia"
    ),
    # 20 — only script and city
    (
        "Apt 12, Vali Asr Executive, Tehran, 19934, Irrn",
        "ایران, Tehran, Valiasr"
    ),

    # ════════════════════════════════════════════════════════════════════════
    # NORTH KOREA — Cases 21-40
    # ════════════════════════════════════════════════════════════════════════

    # 21 — no DPRK/KP, only long name
    (
        "Room 101, Kim Il Sung Square, Central District, Pyongyang, 00100, Norkor",
        "North Korea, Democratic People's Republic of Korea, Pyongyang"
    ),
    # 22 — only abbreviations
    (
        "Unit 5, Ryomyong Street Apartments, Pyongyang, 00200, NKorea",
        "NK, KP, PRK, Pyongyang"
    ),
    # 23 — no city
    (
        "Building 22, Mirae Scientist Street, Central Area, Pyongyang, 00300, N-Korea",
        "North Korea, DPRK, NK, Korea (North)"
    ),
    # 24 — wrong country name variant
    (
        "Floor 8, Kwangbok Street Mall, Pyongyang, 00400, NKoraea",
        "South Korea, Republic of Korea, KR, Pyongyang"
    ),
    # 25 — province missing
    (
        "Apt 12, Chongjin Port District, Chongjin, 00500, Norkoa",
        "North Korea, DPRK, NK, Chongjin"
    ),
    # 26 — minimal tokens
    (
        "Building 33, Wonsan Industrial Road, Wonsan, 00600, Norkr",
        "DPRK, KP, Wonsan"
    ),
    # 27 — city absent
    (
        "Warehouse 45, Hamhung Industrial Zone, Hamhung, 00700, NK-orea",
        "North Korea, Democratic People's Republic of Korea, NK, PRK"
    ),
    # 28 — only one code matches
    (
        "Office 9, Nampo Business Hub, Nampo, 00800, Norker",
        "KP, Nampo, Korea"
    ),
    # 29 — wrong province
    (
        "Unit 7, Kaesong Industrial Park, Kaesong, 00900, N-Kora",
        "North Korea, DPRK, Kaesong, South Hwanghae"
    ),
    # 30 — partial long name
    (
        "Floor 2, Sinuiju Customs Building, Sinuiju, 01000, Norkora",
        "Democratic People's Republic of Korea, Sinuiju, North Pyongan"
    ),
    # 31 — no city
    (
        "Office 105, Kim Il Square, Pyongyang, 00100, Norkor-a",
        "North Korea, DPRK, NK, KP, Chosŏn"
    ),
    # 32 — only abbreviations
    (
        "Apt 6, Ryomyong Heights, Pyongyang, 00200, NKor",
        "NK, PRK, KP"
    ),
    # 33 — misspelled city in elastic
    (
        "Building 25, Mirae Center, Pyongyang, 00300, N-Korea",
        "North Korea, DPRK, Pyonyang, Korea (North)"
    ),
    # 34 — no province, minimal
    (
        "Suite 10, Kwangbok Tower, Pyongyang, 00400, NKore",
        "DPRK, KP, Pyongyang"
    ),
    # 35 — wrong country in elastic
    (
        "Unit 15, Chongjin Business Park, Chongjin, 00500, Norkor",
        "China, PRC, CN, Chongjin"
    ),
    # 36 — only province
    (
        "Floor 35, Wonsan Towers, Wonsan, 00600, Norkor-ea",
        "North Korea, Wonsan, Kangwon Province"
    ),
    # 37 — city typo in elastic
    (
        "Apt 48, Hamhung Residency, Hamhung, 00700, NKora",
        "North Korea, NK, Hamheung, South Hamgyong"
    ),
    # 38 — no province
    (
        "Building 11, Nampo Harbor Office, Nampo, 00800, N-Kore",
        "North Korea, DPRK, D.P.R.K., Nampo"
    ),
    # 39 — minimal match
    (
        "Suite 9, Kaesong Tech Hub, Kaesong, 00900, Norko",
        "DPRK, Kaesong"
    ),
    # 40 — wrong abbreviation
    (
        "Floor 4, Sinuiju Trade Zone, Sinuiju, 01000, NKorae",
        "DPRK, North Korea, KN, Sinuiju"
    ),

    # ════════════════════════════════════════════════════════════════════════
    # SYRIA — Cases 41-60
    # ════════════════════════════════════════════════════════════════════════

    # 41 — no city
    (
        "Office 77, Damascus Business Center, Damascus, 00010, XSyriaz",
        "Syria, Syrian Arab Republic, SY, Damascus, Al-Midan"
    ),
    # 42 — province missing
    (
        "Warehouse 12, Aleppo Industrial Complex, Aleppo, 00020, Syr1a",
        "Syria, SAR, SY, Aleppo, Halab"
    ),
    # 43 — script only + city
    (
        "Apt 5, Homs Residential Square, Homs, 00030, Syriah",
        "سوريا, Homs, Hims"
    ),
    # 44 — no full name
    (
        "Floor 9, Latakia Maritime Bureau, Latakia, 00040, Syr-ia",
        "SY, SYR, SAR, Latakia, Al-Ladhiqiyah"
    ),
    # 45 — minimal tokens
    (
        "Suite 14, Hama Commercial Plaza, Hama, 00050, Syryia",
        "Syria, Hama, Hamah"
    ),
    # 46 — wrong city name
    (
        "Building 21, Deir ez-Zor Logistics, Deir ez-Zor, 00060, Syrria",
        "Syria, SAR, SYR, Dayr az-Zawr, Euphrates Region"
    ),
    # 47 — no Arabic script
    (
        "Office 30, Raqqa Municipal Center, Raqqa, 00070, Sxria",
        "Syria, Syrian Arab Republic, Raqqa, Ar-Raqqah"
    ),
    # 48 — city typo in elastic
    (
        "Floor 4, Idlib Administrative Building, Idlib, 00080, Sy-ria",
        "Syria, SY, SYR, Idleb, Idlib Governorate"
    ),
    # 49 — only abbreviations
    (
        "Unit 11, Tartus Port Management, Tartus, 00090, Syriqa",
        "SY, SYR, Tartous, Tartus"
    ),
    # 50 — no city
    (
        "Building 6, Qamishli Commerce Hub, Qamishli, 00100, Syr-ia",
        "Syria, Syrian Arab Republic, SAR, سوريا"
    ),
    # 51 — partial country
    (
        "Apt 80, Damascus Heights, Damascus, 00010, Syri-a",
        "Syrian Arab Republic, SY, Damascus"
    ),
    # 52 — wrong province
    (
        "Suite 15, Aleppo Trade Office, Aleppo, 00020, Syrria",
        "Syria, SAR, Aleppo, Homs Governorate"
    ),
    # 53 — only script
    (
        "Floor 8, Homs Business Center, Homs, 00030, Syriya",
        "سوريا, Homs"
    ),
    # 54 — minimal
    (
        "Building 12, Latakia Port Plaza, Latakia, 00040, Syryia",
        "Syria, Lattakia"
    ),
    # 55 — no city in elastic
    (
        "Office 18, Hama Commerce Building, Hama, 00050, Sy-ria",
        "Syria, Syrian Arab Republic, SAR, SY, SYR, Syrie"
    ),
    # 56 — different region
    (
        "Unit 25, Deir ez-Zor Industrial Site, Deir ez-Zor, 00060, Syriqa",
        "Syria, SYR, Eastern Region, Deir ez-Zor"
    ),
    # 57 — no Arabic
    (
        "Floor 35, Raqqa Central Office, Raqqa, 00070, XSyria",
        "Syria, SAR, SY, Raqqa"
    ),
    # 58 — province only
    (
        "Apt 7, Idlib Regional HQ, Idlib, 00080, Syryia",
        "Syria, Idlib Governorate, SY"
    ),
    # 59 — minimal
    (
        "Building 15, Tartus Customs, Tartus, 00090, Syri",
        "SYR, Tartus, Syria"
    ),
    # 60 — typo in city
    (
        "Suite 9, Qamishli Industrial Hub, Qamishli, 00100, Syr-ia",
        "Syria, SAR, Qamishlo, Kamishli"
    ),

    # ════════════════════════════════════════════════════════════════════════
    # CUBA — Cases 61-80
    # ════════════════════════════════════════════════════════════════════════

    # 61 — no city
    (
        "Floor 50, Havana Business Plaza, Havana, 10100, Cubaqx",
        "Cuba, Republic of Cuba, CU, CUB"
    ),
    # 62 — only codes
    (
        "Office 10, Varadero Resort Complex, Varadero, 10200, Cuvba",
        "CU, CUB, Varadero, Cuba"
    ),
    # 63 — province missing
    (
        "Unit 22, Santiago Trade Center, Santiago, 10300, C-uba",
        "Cuba, República de Cuba, CUB, Santiago"
    ),
    # 64 — misspelled city
    (
        "Building 8, Camaguey Industrial Park, Camaguey, 10400, Cub-a",
        "Cuba, CU, CUB, Camaguey, Camaguey Province"
    ),
    # 65 — accented vs unaccented mismatch
    (
        "Apt 15, Holguin Administrative Bldg, Holguin, 10500, Cuuba",
        "Cuba, CUB, Holguín, Holguin Province"
    ),
    # 66 — no country name
    (
        "Floor 3, Pinar del Rio Commerce Hub, Pinar del Rio, 10600, Cubaa",
        "CU, CUB, Pinar del Río"
    ),
    # 67 — wrong province
    (
        "Suite 7, Cienfuegos Port Operations, Cienfuegos, 10700, Cbuac",
        "Cuba, República de Cuba, Cienfuegos, Havana Province"
    ),
    # 68 — minimal
    (
        "Building 12, Santa Clara Business Hub, Santa Clara, 10800, Cubaa",
        "Cuba, CUB, Santa Clara"
    ),
    # 69 — city typo
    (
        "Office 9, Guantanamo Logistics Site, Guantanamo, 10900, Cubqx",
        "Cuba, CU, Guantánamo, Guantanamo Province"
    ),
    # 70 — no province
    (
        "Floor 4, Bayamo Trade Center, Bayamo, 11000, Cubae",
        "Cuba, Republic of Cuba, CUB, Bayamo"
    ),
    # 71 — only script-adjacent and codes
    (
        "Unit 60, Havana Central Plaza, Havana, 10100, Cuba-a",
        "CU, CUB, Habana, La Habana"
    ),
    # 72 — wrong province
    (
        "Building 12, Varadero Executive Suite, Varadero, 10200, Cubaa",
        "Cuba, CUB, Varadero, Havana Province"
    ),
    # 73 — no full republic name
    (
        "Floor 25, Santiago Regional Office, Santiago, 10300, Cbuac",
        "Cuba, CU, Santiago de Cuba"
    ),
    # 74 — city absent
    (
        "Apt 10, Camaguey Commerce Bldg, Camaguey, 10400, Cubae",
        "Cuba, República de Cuba, CU, CUB, Camagüey Province"
    ),
    # 75 — minimal
    (
        "Suite 20, Holguin Administrative Hub, Holguin, 10500, Cubaqx",
        "CUB, Cuba, Holguín"
    ),
    # 76 — wrong city
    (
        "Building 5, Pinar del Rio Logistic Base, Pinar del Rio, 10600, Cuvba",
        "Cuba, CU, CUB, Pinar del Río, Havana Province"
    ),
    # 77 — no codes
    (
        "Office 10, Cienfuegos Municipal Plaza, Cienfuegos, 10700, C-uba",
        "Cuba, Republic of Cuba, Cienfuegos Province"
    ),
    # 78 — only city and one code
    (
        "Floor 15, Santa Clara Commerce Center, Santa Clara, 10800, Cub-a",
        "CUB, Santa Clara, Villa Clara Province"
    ),
    # 79 — city typo
    (
        "Unit 12, Guantanamo Port Authority, Guantanamo, 10900, Cuuba",
        "Cuba, CU, CUB, Guantanamo"
    ),
    # 80 — province absent
    (
        "Apt 8, Bayamo City Center, Bayamo, 11000, Cubaa",
        "Cuba, CUB, Bayamo"
    ),

    # ════════════════════════════════════════════════════════════════════════
    # RUSSIA — Cases 81-100
    # ════════════════════════════════════════════════════════════════════════

    # 81 — no city
    (
        "Floor 5, Lenina Office Complex, Moscow, 101000, Ruzzia",
        "Russia, Russian Federation, RU, RUS, Россия"
    ),
    # 82 — only script
    (
        "Building 12, Arbat Street Trade Center, Moscow, 102000, Ruusssia",
        "Россия, RF, Moscow, Moskva"
    ),
    # 83 — city typo
    (
        "Suite 8, Nevsky Prospekt Plaza, St. Petersburg, 190000, Russi-a",
        "Russia, RU, RUS, Sankt-Petersburg, Leningrad, SPb"
    ),
    # 84 — province only
    (
        "Office 22, Gorky Street Business Park, Nizhny Novgorod, 603000, Russiq",
        "Russia, RUS, Nizhny Novgorod, Volga Region"
    ),
    # 85 — minimal
    (
        "Warehouse 44, Pushkin Industrial Zone, Kazan, 420000, Rus-sia",
        "Russia, RF, Kazan"
    ),
    # 86 — no full name
    (
        "Floor 9, Tverskaya Business Center, Moscow, 125000, Russ-ia",
        "RU, RUS, RF, Moscow, Tverskoy"
    ),
    # 87 — city abbreviation only
    (
        "Apt 3, Sadovaya Street Residency, Rostov-on-Don, 344000, Ruzz-ia",
        "Russia, Russian Federation, RU, Rostov-na-Donu"
    ),
    # 88 — wrong region
    (
        "Suite 17, Komsomolsk Business Hub, Perm, 614000, Russya",
        "Russia, RUS, Perm, Siberian Region"
    ),
    # 89 — no region
    (
        "Building 21, Mira Avenue Trade Center, Sochi, 354000, Russa",
        "Russia, RF, Sochi, RUS"
    ),
    # 90 — partial name
    (
        "Office 6, Sovietskaya Regional Office, Ufa, 450000, R-ussia",
        "Russian Federation, RU, Ufa"
    ),
    # 91 — script + abbreviation only
    (
        "Unit 8, Lenina Business Center, Moscow, 101000, Ru-ssia",
        "Россия, RU, Moscow"
    ),
    # 92 — no district
    (
        "Floor 15, Arbat District HQ, Moscow, 102000, Russ-ia",
        "Russia, Russian Federation, RUS, Moscow"
    ),
    # 93 — city variant missing
    (
        "Apt 10, Nevsky Trade Prospekt, St. Petersburg, 190000, Ruzz-ia",
        "Russia, RU, RUS, Saint Petersburg"
    ),
    # 94 — old name only
    (
        "Building 25, Gorky Industrial Plaza, Nizhny Novgorod, 603000, Russya",
        "Russia, RF, Gorky, Nizhny Novgorod Oblast"
    ),
    # 95 — region only
    (
        "Suite 50, Pushkin Commerce Site, Kazan, 420000, Russa",
        "Russia, Tatarstan, Kazan"
    ),
    # 96 — no script
    (
        "Office 12, Tverskaya Logistics Center, Moscow, 125000, R-ussia",
        "Russia, Russian Federation, RF, Moscow"
    ),
    # 97 — minimal
    (
        "Floor 6, Sadovaya Plaza, Rostov-on-Don, 344000, Ruzzia",
        "Russia, RUS, Rostov"
    ),
    # 98 — only script and region
    (
        "Unit 20, Komsomolsk Trade Zone, Perm, 614000, Ruusssia",
        "Россия, Perm, Permsky Kray"
    ),
    # 99 — no region
    (
        "Apt 25, Mira Avenue Residential, Sochi, 354000, Russi-a",
        "Russia, RU, RUS, Sochi"
    ),
    # 100 — province only
    (
        "Warehouse 9, Sovietskaya Industrial Park, Ufa, 450000, Russiq",
        "Russia, RF, Ufa, Bashkortostan"
    ),

    # ════════════════════════════════════════════════════════════════════════
    # IRAN — Cases 101-120  (different addresses + partial elastic)
    # ════════════════════════════════════════════════════════════════════════

    # 101
    (
        "No. 18, Hafez Blvd, North Tehran, 14398, Persi-a",
        "Iran, Islamic Republic of Iran, IRI, IR, IRN, Tehran"
    ),
    # 102
    (
        "Plot 9, Imam Reza Highway, Mashhad, 91888, Irqan",
        "Iran, Persia, IRN, Mashhad, Khorasan"
    ),
    # 103
    (
        "Block A, Chamran Expressway, West Tehran, 19847, Iraan",
        "Iran, IRI, I.R.I., ایران, Tehran, Vanak"
    ),
    # 104
    (
        "Unit 3, Chahar Bagh Street, Isfahan, 81534, Irani",
        "Iran, Islamic Republic of Iran, IRN, IR, Esfahan"
    ),
    # 105
    (
        "Warehouse 7, Zand Boulevard, Shiraz, 71468, Ir4n",
        "Iran, IRI, Persia, Shiraz"
    ),
    # 106
    (
        "Office 14, Pardis Technology Park, Tehran, 16548, I.R.I-n",
        "Iran, IRN, IR, IRI, Tehran, Pardis"
    ),
    # 107
    (
        "Floor 2, Shahid Rajaee Port Rd, Bandar Abbas, 79387, Irzan",
        "Iran, Islamic Republic of Iran, IR, Bandar Abbas, Hormozgan"
    ),
    # 108
    (
        "Suite 6, Amir Chakhmaq Square, Yazd, 89176, Irraan",
        "Iran, IRN, Yazd Province, Yazd"
    ),
    # 109
    (
        "Apt 22, Imam Khomeini Blvd, Bushehr, 75389, Ira_n",
        "Iran, IRI, Persia, Bushehr"
    ),
    # 110
    (
        "Building 11, Shariati Avenue, Arak, 38246, IRaann",
        "Iran, IRN, IR, Arak, Markazi"
    ),
    # 111
    (
        "Unit 8, Sabalan Road, Ardabil, 56489, Iiran",
        "Iran, Islamic Republic of Iran, IRI, Ardabil"
    ),
    # 112
    (
        "Floor 4, Ekbatan Township, Hamadan, 65389, Irann",
        "Iran, IR, IRN, Hamedan, Hamadan Province"
    ),
    # 113
    (
        "Office 6, Mehran Border Crossing Rd, Ilam, 69478, Irqan",
        "Iran, IRI, I.R.I., Ilam Province"
    ),
    # 114
    (
        "Building 9, Falak-ol-Aflak Blvd, Khorramabad, 68249, Iraqn",
        "Iran, IRN, IR, Khorramabad, Lorestan Province"
    ),
    # 115
    (
        "Suite 12, Doosti Park Road, Zahedan, 98348, Iraen",
        "Iran, IRI, IR, Zahedan, Sistan"
    ),
    # 116
    (
        "Apt 33, Naharkhoran Forest Rd, Gorgan, 49389, I-raan",
        "Iran, Islamic Republic, IRN, Gorgan, Golestan"
    ),
    # 117
    (
        "Floor 5, Azadi Square East Wing, Sanandaj, 66389, Irzan",
        "Iran, IRI, IR, Sanandaj, Kurdistan"
    ),
    # 118
    (
        "Unit 14, Shahrood Science Campus, Semnan, 35489, Irraan",
        "Iran, IRN, Semnan Province"
    ),
    # 119
    (
        "Building 7, Taleghani Petrochemical Rd, Ahvaz, 61589, Irann",
        "Iran, Islamic Republic of Iran, IR, Ahvaz, Khuzestan"
    ),
    # 120
    (
        "Suite 3, Koohsangi Park Blvd, Mashhad, 91489, Iiraan",
        "Iran, IRI, Persia, Mashhad, Razavi Khorasan"
    ),

    # ════════════════════════════════════════════════════════════════════════
    # NORTH KOREA — Cases 121-140  (different addresses + partial elastic)
    # ════════════════════════════════════════════════════════════════════════

    # 121
    (
        "Unit 7, Pothonggang Riverside, Pyongyang, 00175, D.P.R.K-n",
        "North Korea, DPRK, NK, Pyongyang, Chosŏn"
    ),
    # 122
    (
        "Floor 3, Taedong River Embankment, Pyongyang, 00260, NKorea-a",
        "North Korea, Democratic People's Republic, NK, Pyongyang"
    ),
    # 123
    (
        "Building 8, Rason Port Logistics, Rajin, 00375, Nrth-Korea",
        "North Korea, DPRK, D.P.R.K., Rajin, Rason"
    ),
    # 124
    (
        "Apt 4, Sonbong Free Trade Ave, Sonbong, 00465, NKoera",
        "North Korea, NK, KP, Sonbong"
    ),
    # 125
    (
        "Office 11, Kim Chaek Steel Mill Rd, Chongjin, 00575, NrthKorea",
        "North Korea, DPRK, Chongjin, North Hamgyong"
    ),
    # 126
    (
        "Suite 2, Yalu River Trade Post, Hyesan, 00665, D-PRK",
        "North Korea, NK, PRK, Hyesan, Ryanggang"
    ),
    # 127
    (
        "Unit 9, Paektu Mountain Base Rd, Samjiyon, 00775, Nth-Korea",
        "North Korea, DPRK, D.P.R.K., Samjiyon"
    ),
    # 128
    (
        "Building 5, Chongchon River Industrial Zone, Kusong, 00875, NKoreia",
        "North Korea, NK, KP, Kusong, North Pyongan"
    ),
    # 129
    (
        "Floor 7, Mirae Scientists Ave, Pyongsong, 00965, NorKora",
        "North Korea, DPRK, Pyongsong, South Pyongan"
    ),
    # 130
    (
        "Apt 14, Sariwon Industrial Blvd, Sariwon, 01065, NKorrea",
        "North Korea, NK, PRK, Sariwon"
    ),
    # 131
    (
        "Office 3, Tanchon Port Access Rd, Tanchon, 01175, NKorea_n",
        "North Korea, DPRK, D.P.R.K., Tanchon, South Hamgyong"
    ),
    # 132
    (
        "Suite 8, Kanggye Mountain Pass, Kanggye, 01275, NKoriea",
        "North Korea, NK, KP, Kanggye, Chagang"
    ),
    # 133
    (
        "Building 12, Haeju Bay Road, Haeju, 01375, DPRK-a",
        "North Korea, DPRK, Haeju, South Hwanghae"
    ),
    # 134
    (
        "Floor 9, Pyongyang Metro Line 2, Pyongyang, 00110, Nkorrea",
        "North Korea, NK, KP, PRK, Pyongyang"
    ),
    # 135
    (
        "Unit 6, Wonsan Beach Resort Rd, Wonsan, 00620, NKoraee",
        "North Korea, DPRK, Wonsan, Kangwon"
    ),
    # 136
    (
        "Apt 18, Nampo Dock Workers Estate, Nampo, 00820, Nkoreaa",
        "North Korea, NK, Nampo, South Pyongan"
    ),
    # 137
    (
        "Building 10, Hamhung Textile District, Hamhung, 00720, NorthKoera",
        "North Korea, DPRK, D.P.R.K., Hamhung, South Hamgyong"
    ),
    # 138
    (
        "Suite 7, Kaesong Koryo Hotel Rd, Kaesong, 00920, NKorea.n",
        "North Korea, NK, PRK, Kaesong, North Hwanghae"
    ),
    # 139
    (
        "Office 5, Sinuiju Textile Mill Blvd, Sinuiju, 01020, Norh-Korea",
        "North Korea, DPRK, D.P.R.K., Sinuiju"
    ),
    # 140
    (
        "Floor 6, Kim Il Sung University Rd, Pyongyang, 00130, NKoraae",
        "North Korea, NK, KP, Pyongyang, Central Bank"
    ),

    # ════════════════════════════════════════════════════════════════════════
    # SYRIA — Cases 141-160  (different addresses + partial elastic)
    # ════════════════════════════════════════════════════════════════════════

    # 141
    (
        "Building 4, Umayyad Square, Damascus, 00015, Syriq",
        "Syria, Syrian Arab Republic, SY, Damascus, Al-Midan"
    ),
    # 142
    (
        "Suite 9, Al-Madina Souq, Aleppo, 00025, Syri-ia",
        "Syria, SAR, SYR, Aleppo, Halab"
    ),
    # 143
    (
        "Floor 6, Queen Zenobia Road, Tadmur, 00035, Syri4a",
        "Syria, SY, Tadmur, Palmyra, Homs Governorate"
    ),
    # 144
    (
        "Apt 3, Convent of Our Lady Rd, Maalula, 00045, Sy-rria",
        "Syria, SYR, Maaloula, Rif Dimashq"
    ),
    # 145
    (
        "Office 15, Shahba Roman Theater Rd, Sweida, 00055, Syira",
        "Syria, SAR, As-Suwayda, Sweida Governorate"
    ),
    # 146
    (
        "Building 8, Hauran Plain Road, Daraa, 00065, Syri-qa",
        "Syria, SY, SYR, Daraa, Daraa Governorate"
    ),
    # 147
    (
        "Unit 7, Khabur River Logistics, Al-Hasakah, 00075, Syriaa",
        "Syria, Syrian Arab Republic, Al-Hasakah, Hasakah Governorate"
    ),
    # 148
    (
        "Floor 3, Euphrates Bridge Rd, Deir Hafer, 00085, Syr1ia",
        "Syria, SAR, Deir Hafer, Aleppo Governorate"
    ),
    # 149
    (
        "Suite 11, Crac des Chevaliers Rd, Safita, 00095, Sy-r-ia",
        "Syria, SY, Safita, Tartus Governorate"
    ),
    # 150
    (
        "Building 5, Orontes Valley Industrial, Jisr al-Shughur, 00105, Syrja",
        "Syria, SYR, Jisr al-Shughur, Idlib Governorate"
    ),
    # 151
    (
        "Apt 9, Baniyas Coastal Highway, Baniyas, 00015, Syrria",
        "Syria, SAR, Baniyas, Tartus"
    ),
    # 152
    (
        "Office 12, Al-Qaim Border Road, Al-Bukamal, 00025, Syriay",
        "Syria, SY, SYR, Al-Bukamal, Deir ez-Zor Governorate"
    ),
    # 153
    (
        "Floor 5, Orontes River Rd, Hama, 00035, Syrha",
        "Syria, Syrian Arab Republic, Hama, Hamah"
    ),
    # 154
    (
        "Unit 10, Euphrates Rd West, Kobani, 00045, Syri-ah",
        "Syria, SAR, Kobani, Ayn al-Arab"
    ),
    # 155
    (
        "Building 3, Hauran Wheat Depot Rd, Nawa, 00055, Syriah",
        "Syria, SYR, Nawa, Daraa Governorate"
    ),
    # 156
    (
        "Suite 8, UN Buffer Zone Rd, Quneitra, 00065, Syiria",
        "Syria, SY, Quneitra, Quneitra Governorate"
    ),
    # 157
    (
        "Apt 2, Raqqa Riverside Blvd, Raqqa, 00075, Syraiah",
        "Syria, SAR, SYR, Raqqa, Ar-Raqqah"
    ),
    # 158
    (
        "Office 7, Jaghjagh River Rd, Qamishli, 00085, Syrya",
        "Syria, SY, Qamishli, Qamishlo, Kamishly"
    ),
    # 159
    (
        "Building 14, Ash-Sharia Blvd, Masyaf, 00095, Syr-ria",
        "Syria, Syrian Arab Republic, Masyaf, Hama Governorate"
    ),
    # 160
    (
        "Floor 4, Khabur Bridge Road, Ras al-Ayn, 00105, Sy-riaa",
        "Syria, SAR, Ras al-Ayn, Sere Kaniye"
    ),

    # ════════════════════════════════════════════════════════════════════════
    # CUBA — Cases 161-175  (different addresses + partial elastic)
    # ════════════════════════════════════════════════════════════════════════

    # 161
    (
        "Suite 4, Plaza Mayor Rd, Trinidad, 72250, Kuuba",
        "Cuba, CUB, Trinidad, Sancti Spíritus"
    ),
    # 162
    (
        "Building 17, Sierra Maestra Blvd, Manzanillo, 87650, Cuuba",
        "Cuba, Republic of Cuba, Manzanillo, Granma"
    ),
    # 163
    (
        "Floor 2, Juan Gualberto Gomez Ave, Las Tunas, 75150, Cub-ia",
        "Cuba, CU, CUB, Las Tunas"
    ),
    # 164
    (
        "Apt 6, Libertad Boulevard, Ciego de Avila, 69350, Kuuba",
        "Cuba, República de Cuba, Ciego de Ávila"
    ),
    # 165
    (
        "Office 9, Nuevitas Bay Access Rd, Nuevitas, 71150, Cubba",
        "Cuba, CUB, Nuevitas, Camagüey Province"
    ),
    # 166
    (
        "Unit 3, Monserrate Blvd, Matanzas, 40150, Cubxa",
        "Cuba, CU, CUB, Matanzas Province"
    ),
    # 167
    (
        "Building 5, Tobacco Growers Rd, Artemisa, 33850, Cub4a",
        "Cuba, Republic of Cuba, Artemisa"
    ),
    # 168
    (
        "Suite 14, Yayabo River Rd, Sancti Spiritus, 60150, C-uuba",
        "Cuba, CUB, Sancti Spíritus, Sancti Spiritus"
    ),
    # 169
    (
        "Floor 8, Crocodile Farm Rd, Nueva Gerona, 25150, Kubba",
        "Cuba, CU, Nueva Gerona, Isla de la Juventud"
    ),
    # 170
    (
        "Apt 4, Mayabeque Blvd, San Jose, 32550, Cuuba",
        "Cuba, CUB, San José de las Lajas, Mayabeque"
    ),
    # 171
    (
        "Building 11, Guantanamo Bay Fence Rd, Guantanamo, 10950, C.U.B.a",
        "Cuba, Republic of Cuba, Guantánamo, Guantanamo Province"
    ),
    # 172
    (
        "Office 16, Malecon Seafront, Havana, 10150, Kubba",
        "Cuba, CU, CUB, La Habana, Havana"
    ),
    # 173
    (
        "Floor 3, Cienfuegos Bay Rd, Cienfuegos, 10750, Cuuba",
        "Cuba, CUB, Cienfuegos, Cienfuegos Province"
    ),
    # 174
    (
        "Suite 2, Varadero Beach Access, Cardenas, 41850, Cubaa",
        "Cuba, CU, Cárdenas, Matanzas Province"
    ),
    # 175
    (
        "Unit 22, Ignacio Agramonte Ave, Camaguey, 10450, Cub-ba",
        "Cuba, CUB, Camagüey, Camaguey Province"
    ),

    # ════════════════════════════════════════════════════════════════════════
    # RUSSIA — Cases 176-200  (different addresses + partial elastic)
    # ════════════════════════════════════════════════════════════════════════

    # 176
    (
        "Building 9, Svetlanskaya Street, Vladivostok, 690050, Ruziah",
        "Russia, RU, RUS, Vladivostok, Primorsky Krai"
    ),
    # 177
    (
        "Floor 7, Akademgorodok Campus Rd, Novosibirsk, 630050, Rusiy-a",
        "Russia, Russian Federation, RF, Novosibirsk, Novosibirsk Oblast"
    ),
    # 178
    (
        "Suite 5, Yekaterinburg City Arena Rd, Yekaterinburg, 620050, Russsia",
        "Russia, RUS, Yekaterinburg, Ekaterinburg, Sverdlovsk Oblast"
    ),
    # 179
    (
        "Apt 38, Irtysh Embankment, Omsk, 644050, Rusiia",
        "Russia, RF, Omsk, Omsk Oblast"
    ),
    # 180
    (
        "Office 5, Volga Embankment Blvd, Samara, 443050, Ru-ssia",
        "Russia, Russian Federation, RU, Samara, Samara Oblast"
    ),
    # 181
    (
        "Building 22, Kirova Street, Chelyabinsk, 454050, Russ-ya",
        "Russia, RUS, Chelyabinsk, Chelyabinsk Oblast"
    ),
    # 182
    (
        "Floor 6, Yenisei River Blvd, Krasnoyarsk, 660050, Rosssia",
        "Russia, RF, Россия, Krasnoyarsk, Krasnoyarsk Krai"
    ),
    # 183
    (
        "Suite 4, Mamayev Kurgan Road, Volgograd, 400050, Ruz-ia",
        "Russia, RU, RUS, Volgograd, Stalingrad"
    ),
    # 184
    (
        "Apt 12, Kuban River Blvd, Krasnodar, 350050, Rus-sia",
        "Russia, Russian Federation, Krasnodar, Krasnodar Krai"
    ),
    # 185
    (
        "Unit 18, Volga Bluff Rd, Saratov, 410050, Ruzzia",
        "Russia, RF, RUS, Saratov, Saratov Oblast"
    ),
    # 186
    (
        "Building 14, Tura River Rd, Tyumen, 625050, Rrusia",
        "Russia, RU, Tyumen, Tyumen Oblast"
    ),
    # 187
    (
        "Office 9, Angara River Blvd, Irkutsk, 664050, Ruusia",
        "Russia, RUS, Россия, Irkutsk, Irkutsk Oblast"
    ),
    # 188
    (
        "Floor 3, Amur River Embankment, Khabarovsk, 680050, Russsia",
        "Russia, RF, Khabarovsk, Khabarovsk Krai"
    ),
    # 189
    (
        "Suite 28, Kola Bay Port Rd, Murmansk, 183050, Rrussiya",
        "Russia, Russian Federation, RU, Murmansk, Murmansk Oblast"
    ),
    # 190
    (
        "Apt 5, Kant Island Rd, Kaliningrad, 236050, Rus-ia",
        "Russia, RUS, RF, Kaliningrad, Königsberg"
    ),
    # 191
    (
        "Building 36, Velikaya River Rd, Pskov, 180050, Rossiya-n",
        "Russia, RU, Россия, Pskov, Pskov Oblast"
    ),
    # 192
    (
        "Floor 11, Seim River Blvd, Kursk, 305050, Russi-ya",
        "Russia, RUS, RF, Kursk, Kursk Oblast"
    ),
    # 193
    (
        "Office 2, Desna River Industrial Rd, Bryansk, 241050, Russyia",
        "Russia, RU, Bryansk, Bryansk Oblast"
    ),
    # 194
    (
        "Unit 15, Upa River Blvd, Tula, 300050, Ruzz-ia",
        "Russia, RUS, Россия, Tula, Tula Oblast"
    ),
    # 195
    (
        "Suite 6, Voronezh Reservoir Rd, Voronezh, 394050, Rusiay",
        "Russia, RF, RU, Voronezh, Voronezh Oblast"
    ),
    # 196
    (
        "Building 4, Kotorosl River Blvd, Yaroslavl, 150050, Russa",
        "Russia, RUS, Yaroslavl, Yaroslavl Oblast"
    ),
    # 197
    (
        "Apt 17, Terek River Rd, Vladikavkaz, 362050, Russ_ia",
        "Russia, RF, Россия, Vladikavkaz, North Ossetia"
    ),
    # 198
    (
        "Floor 6, Sunzha River Industrial Blvd, Grozny, 364050, Russiqa",
        "Russia, RU, RUS, Grozny, Chechnya"
    ),
    # 199
    (
        "Office 8, Caspian Waterfront, Makhachkala, 367050, Russ-iya",
        "Russia, RUS, Россия, Makhachkala, Dagestan"
    ),
    # 200
    (
        "Suite 25, Volga Delta Fishery Rd, Astrakhan, 414050, Ruussia",
        "Russia, RF, RU, Astrakhan, Astrakhan Oblast"
    ),
]


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Helper: parse the comma-separated elastic result string into (name, aliases)
# ---------------------------------------------------------------------------

def _parse_elastic(elastic_result: str):
    """Split 'Name, Alias1, Alias2, ...' into (name, [alias1, alias2, ...])."""
    parts = [p.strip() for p in elastic_result.split(",") if p.strip()]
    name = parts[0] if parts else ""
    aliases = parts[1:] if len(parts) > 1 else []
    return name, aliases


# ---------------------------------------------------------------------------
# Quick runner — prints (index, score, best_variant, query, elastic_result)
# ---------------------------------------------------------------------------

def run_all(verbose: bool = False):
    results = []
    for i, (query, elastic_result) in enumerate(TEST_CASES, start=1):
        name, aliases = _parse_elastic(elastic_result)
        score, debug = score_with_variants(query, name, aliases=aliases)
        results.append((i, query, elastic_result, score, debug["best_variant"]))
        if verbose:
            print(
                f"[{i:03d}] score={score:.4f} best={debug['best_variant']!r:20s} | "
                f"{query[:55]!r}"
            )
# Quick runner — prints (index, score, query, elastic_result) for all 200
# ---------------------------------------------------------------------------

def run_all(verbose: bool = False):
    matcher = LocationMatcher()
    results = []
    for i, (query, elastic_result) in enumerate(TEST_CASES, start=1):
        score = matcher.match(query, elastic_result)
        results.append((i, query, elastic_result, score))
        if verbose:
            print(
                f"[{i:03d}] score={score:.4f} | "
                f"{query!r}  vs  {elastic_result[:60]!r}"
            )
    return results


if __name__ == "__main__":
    run_all(verbose=True)

