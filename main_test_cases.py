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

from matcher.location_matcher import LocationMatcher

# ---------------------------------------------------------------------------
# TEST CASE DATA
# Format: (query_address, elastic_result_string)
# ---------------------------------------------------------------------------

TEST_CASES = [

    # ════════════════════════════════════════════════════════════════════════
    # IRAN — Cases 1-20  (user-provided queries)
    # ════════════════════════════════════════════════════════════════════════

    # 1
    (
        "Unit 4B, Building 12, Azadi Street, District 4, Tehran, 14567, Kirana",
        "Iran, Islamic Republic of Iran, IRI, I.R.I., I.R.I, Persia, ایران, IR, IRN, Tehran, Islamic Republic"
    ),
    # 2
    (
        "Apt 102, Pars Tower, Valiasr Avenue, Suite 2, Tehran, 19934, Iraanx",
        "Iran, Islamic Republic of Iran, Persia, IRI, I.R.I, ایران, IR, IRN, Tehran, Valiasr, Islamic Republic"
    ),
    # 3
    (
        "Warehouse 5, Industrial Zone B, Shiraz Road, Shiraz, 71345, Irqn",
        "Iran, Islamic Republic of Iran, IRI, I.R.I., Persia, ایران, IRN, IR, Shiraz, Fars Province"
    ),
    # 4
    (
        "Room 202, Block C, Tabriz Avenue, North Side, Tabriz, 51367, Ira-n",
        "Iran, Islamic Republic of Iran, IRI, I.R.I, Persia, ایران, IR, IRN, Tabriz, East Azerbaijan"
    ),
    # 5
    (
        "Floor 3, Qom Plaza, Qom City Center, Qom, 37198, Iryaan",
        "Iran, Islamic Republic of Iran, IRI, Persia, ایران, IRN, IR, Qom, Qom Province"
    ),
    # 6
    (
        "Shop 15, Ahvaz Shopping Mall, Ahvaz Street, Ahvaz, 61357, Irrn",
        "Iran, Islamic Republic of Iran, IRI, I.R.I., Persia, ایران, IR, IRN, Ahvaz, Khuzestan"
    ),
    # 7
    (
        "Suite 9, Rasht Central Building, Rasht District, Rasht, 41336, I-ran",
        "Iran, Islamic Republic of Iran, IRI, I.R.I, Persia, ایران, IR, IRN, Rasht, Gilan Province"
    ),
    # 8
    (
        "Building 7, Kerman Business Park, Kerman, 76135, Irann",
        "Iran, Islamic Republic of Iran, IRI, Persia, ایران, IRN, IR, Kerman, Kerman Province"
    ),
    # 9
    (
        "Apt 55, Azadi Heights, Tehrann Center, Tehran, 14567, Iraqn",
        "Iran, Islamic Republic of Iran, IRI, I.R.I., Persia, ایران, IR, IRN, Tehran"
    ),
    # 10
    (
        "Floor 1, Vali Asr Office Complex, Tehran, 19934, Ir-an",
        "Iran, Islamic Republic of Iran, IRI, I.R.I, Persia, ایران, IR, IRN, Tehran, Valiasr"
    ),
    # 11
    (
        "Block 20, Enghelab Residential, Tehran, 15875, Irnaa",
        "Iran, Islamic Republic of Iran, IRI, Persia, ایران, IRN, IR, Tehran"
    ),
    # 12
    (
        "Suite 112, Shiraz Plaza, Shiraz, 71345, Iranx",
        "Iran, Islamic Republic of Iran, IRI, I.R.I., Persia, ایران, IR, IRN, Shiraz"
    ),
    # 13
    (
        "Building 30, Karaj Industrial Estate, Karaj, 31345, Irawn",
        "Iran, Islamic Republic of Iran, IRI, I.R.I, Persia, ایران, IR, IRN, Karaj, Alborz Province"
    ),
    # 14
    (
        "Apt 12, Tabriz Central, Tabriz, 51367, I-ranx",
        "Iran, Islamic Republic of Iran, IRI, Persia, ایران, IRN, IR, Tabriz, East Azerbaijan"
    ),
    # 15
    (
        "Floor 8, Qom Tower, Qom, 37198, Irran",
        "Iran, Islamic Republic of Iran, IRI, I.R.I., Persia, ایران, IR, IRN, Qom"
    ),
    # 16
    (
        "Unit 25, Ahvaz Business Center, Ahvaz, 61357, Irano",
        "Iran, Islamic Republic of Iran, IRI, I.R.I, Persia, ایران, IR, IRN, Ahvaz, Khuzestan"
    ),
    # 17
    (
        "Building 4, Rasht Residential Block, Rasht, 41336, Iryaan",
        "Iran, Islamic Republic of Iran, IRI, Persia, ایران, IRN, IR, Rasht, Gilan Province"
    ),
    # 18
    (
        "Office 7, Kerman Main Square, Kerman, 76135, Irqn",
        "Iran, Islamic Republic of Iran, IRI, I.R.I., Persia, ایران, IR, IRN, Kerman"
    ),
    # 19
    (
        "Floor 10, Azadi Trade Center, Tehran, 14567, Ira-n",
        "Iran, Islamic Republic of Iran, IRI, I.R.I, Persia, ایران, IR, IRN, Tehran"
    ),
    # 20
    (
        "Apt 12, Vali Asr Executive, Tehran, 19934, Irrn",
        "Iran, Islamic Republic of Iran, IRI, Persia, ایران, IRN, IR, Tehran, Valiasr"
    ),

    # ════════════════════════════════════════════════════════════════════════
    # NORTH KOREA — Cases 21-40  (user-provided queries)
    # ════════════════════════════════════════════════════════════════════════

    # 21
    (
        "Room 101, Kim Il Sung Square, Central District, Pyongyang, 00100, Norkor",
        "North Korea, Democratic People's Republic of Korea, DPRK, D.P.R.K., NK, KP, PRK, Korea (North), Pyongyang, Chosŏn"
    ),
    # 22
    (
        "Unit 5, Ryomyong Street Apartments, Pyongyang, 00200, NKorea",
        "North Korea, Democratic People's Republic of Korea, DPRK, D.P.R.K., NK, KP, PRK, Korea (North), Pyongyang"
    ),
    # 23
    (
        "Building 22, Mirae Scientist Street, Central Area, Pyongyang, 00300, N-Korea",
        "North Korea, Democratic People's Republic of Korea, DPRK, NK, KP, PRK, Korea (North), Pyongyang, Chosŏn"
    ),
    # 24
    (
        "Floor 8, Kwangbok Street Mall, Pyongyang, 00400, NKoraea",
        "North Korea, Democratic People's Republic of Korea, DPRK, D.P.R.K., NK, KP, PRK, Korea (North), Pyongyang"
    ),
    # 25
    (
        "Apt 12, Chongjin Port District, Chongjin, 00500, Norkoa",
        "North Korea, Democratic People's Republic of Korea, DPRK, NK, KP, PRK, Korea (North), Chongjin, North Hamgyong"
    ),
    # 26
    (
        "Building 33, Wonsan Industrial Road, Wonsan, 00600, Norkr",
        "North Korea, Democratic People's Republic of Korea, DPRK, D.P.R.K., NK, KP, PRK, Korea (North), Wonsan, Kangwon Province"
    ),
    # 27
    (
        "Warehouse 45, Hamhung Industrial Zone, Hamhung, 00700, NK-orea",
        "North Korea, Democratic People's Republic of Korea, DPRK, NK, KP, PRK, Korea (North), Hamhung, South Hamgyong"
    ),
    # 28
    (
        "Office 9, Nampo Business Hub, Nampo, 00800, Norker",
        "North Korea, Democratic People's Republic of Korea, DPRK, D.P.R.K., NK, KP, PRK, Korea (North), Nampo, South Pyongan"
    ),
    # 29
    (
        "Unit 7, Kaesong Industrial Park, Kaesong, 00900, N-Kora",
        "North Korea, Democratic People's Republic of Korea, DPRK, NK, KP, PRK, Korea (North), Kaesong, North Hwanghae"
    ),
    # 30
    (
        "Floor 2, Sinuiju Customs Building, Sinuiju, 01000, Norkora",
        "North Korea, Democratic People's Republic of Korea, DPRK, D.P.R.K., NK, KP, PRK, Korea (North), Sinuiju, North Pyongan"
    ),
    # 31
    (
        "Office 105, Kim Il Square, Pyongyang, 00100, Norkor-a",
        "North Korea, Democratic People's Republic of Korea, DPRK, NK, KP, PRK, Korea (North), Pyongyang, Chosŏn"
    ),
    # 32
    (
        "Apt 6, Ryomyong Heights, Pyongyang, 00200, NKor",
        "North Korea, Democratic People's Republic of Korea, DPRK, D.P.R.K., NK, KP, PRK, Korea (North), Pyongyang"
    ),
    # 33
    (
        "Building 25, Mirae Center, Pyongyang, 00300, N-Korea",
        "North Korea, Democratic People's Republic of Korea, DPRK, NK, KP, PRK, Korea (North), Pyongyang"
    ),
    # 34
    (
        "Suite 10, Kwangbok Tower, Pyongyang, 00400, NKore",
        "North Korea, Democratic People's Republic of Korea, DPRK, D.P.R.K., NK, KP, PRK, Korea (North), Pyongyang"
    ),
    # 35
    (
        "Unit 15, Chongjin Business Park, Chongjin, 00500, Norkor",
        "North Korea, Democratic People's Republic of Korea, DPRK, NK, KP, PRK, Korea (North), Chongjin, North Hamgyong"
    ),
    # 36
    (
        "Floor 35, Wonsan Towers, Wonsan, 00600, Norkor-ea",
        "North Korea, Democratic People's Republic of Korea, DPRK, D.P.R.K., NK, KP, PRK, Korea (North), Wonsan, Kangwon Province"
    ),
    # 37
    (
        "Apt 48, Hamhung Residency, Hamhung, 00700, NKora",
        "North Korea, Democratic People's Republic of Korea, DPRK, NK, KP, PRK, Korea (North), Hamhung, South Hamgyong"
    ),
    # 38
    (
        "Building 11, Nampo Harbor Office, Nampo, 00800, N-Kore",
        "North Korea, Democratic People's Republic of Korea, DPRK, D.P.R.K., NK, KP, PRK, Korea (North), Nampo"
    ),
    # 39
    (
        "Suite 9, Kaesong Tech Hub, Kaesong, 00900, Norko",
        "North Korea, Democratic People's Republic of Korea, DPRK, NK, KP, PRK, Korea (North), Kaesong, North Hwanghae"
    ),
    # 40
    (
        "Floor 4, Sinuiju Trade Zone, Sinuiju, 01000, NKorae",
        "North Korea, Democratic People's Republic of Korea, DPRK, D.P.R.K., NK, KP, PRK, Korea (North), Sinuiju"
    ),

    # ════════════════════════════════════════════════════════════════════════
    # SYRIA — Cases 41-60  (user-provided queries)
    # ════════════════════════════════════════════════════════════════════════

    # 41
    (
        "Office 77, Damascus Business Center, Damascus, 00010, XSyriaz",
        "Syria, Syrian Arab Republic, SAR, SY, SYR, Syrie, Suriye, سوريا, Damascus, Ash-Sham, Bilad al-Sham"
    ),
    # 42
    (
        "Warehouse 12, Aleppo Industrial Complex, Aleppo, 00020, Syr1a",
        "Syria, Syrian Arab Republic, SAR, SY, SYR, سوريا, Aleppo, Halab, Haleb"
    ),
    # 43
    (
        "Apt 5, Homs Residential Square, Homs, 00030, Syriah",
        "Syria, Syrian Arab Republic, SAR, SY, SYR, Syrie, سوريا, Homs, Hims"
    ),
    # 44
    (
        "Floor 9, Latakia Maritime Bureau, Latakia, 00040, Syr-ia",
        "Syria, Syrian Arab Republic, SAR, SY, SYR, سوريا, Latakia, Lattakia, Al-Ladhiqiyah"
    ),
    # 45
    (
        "Suite 14, Hama Commercial Plaza, Hama, 00050, Syryia",
        "Syria, Syrian Arab Republic, SAR, SY, SYR, Syrie, سوريا, Hama, Hamah"
    ),
    # 46
    (
        "Building 21, Deir ez-Zor Logistics, Deir ez-Zor, 00060, Syrria",
        "Syria, Syrian Arab Republic, SAR, SY, SYR, سوريا, Deir ez-Zor, Dayr az-Zawr"
    ),
    # 47
    (
        "Office 30, Raqqa Municipal Center, Raqqa, 00070, Sxria",
        "Syria, Syrian Arab Republic, SAR, SY, SYR, Syrie, سوريا, Raqqa, Ar-Raqqah"
    ),
    # 48
    (
        "Floor 4, Idlib Administrative Building, Idlib, 00080, Sy-ria",
        "Syria, Syrian Arab Republic, SAR, SY, SYR, سوريا, Idlib, Idleb"
    ),
    # 49
    (
        "Unit 11, Tartus Port Management, Tartus, 00090, Syriqa",
        "Syria, Syrian Arab Republic, SAR, SY, SYR, Syrie, سوريا, Tartus, Tartous"
    ),
    # 50
    (
        "Building 6, Qamishli Commerce Hub, Qamishli, 00100, Syr-ia",
        "Syria, Syrian Arab Republic, SAR, SY, SYR, سوريا, Qamishli, Qamishlo, Al-Qamishli"
    ),
    # 51
    (
        "Apt 80, Damascus Heights, Damascus, 00010, Syri-a",
        "Syria, Syrian Arab Republic, SAR, SY, SYR, Syrie, سوريا, Damascus, Ash-Sham"
    ),
    # 52
    (
        "Suite 15, Aleppo Trade Office, Aleppo, 00020, Syrria",
        "Syria, Syrian Arab Republic, SAR, SY, SYR, سوريا, Aleppo, Halab"
    ),
    # 53
    (
        "Floor 8, Homs Business Center, Homs, 00030, Syriya",
        "Syria, Syrian Arab Republic, SAR, SY, SYR, Syrie, سوريا, Homs, Hims"
    ),
    # 54
    (
        "Building 12, Latakia Port Plaza, Latakia, 00040, Syryia",
        "Syria, Syrian Arab Republic, SAR, SY, SYR, سوريا, Latakia, Lattakia"
    ),
    # 55
    (
        "Office 18, Hama Commerce Building, Hama, 00050, Sy-ria",
        "Syria, Syrian Arab Republic, SAR, SY, SYR, Syrie, سوريا, Hama, Hamah"
    ),
    # 56
    (
        "Unit 25, Deir ez-Zor Industrial Site, Deir ez-Zor, 00060, Syriqa",
        "Syria, Syrian Arab Republic, SAR, SY, SYR, سوريا, Deir ez-Zor, Dayr az-Zawr"
    ),
    # 57
    (
        "Floor 35, Raqqa Central Office, Raqqa, 00070, XSyria",
        "Syria, Syrian Arab Republic, SAR, SY, SYR, Syrie, سوريا, Raqqa, Ar-Raqqah"
    ),
    # 58
    (
        "Apt 7, Idlib Regional HQ, Idlib, 00080, Syryia",
        "Syria, Syrian Arab Republic, SAR, SY, SYR, سوريا, Idlib, Idleb"
    ),
    # 59
    (
        "Building 15, Tartus Customs, Tartus, 00090, Syri",
        "Syria, Syrian Arab Republic, SAR, SY, SYR, Syrie, سوريا, Tartus, Tartous"
    ),
    # 60
    (
        "Suite 9, Qamishli Industrial Hub, Qamishli, 00100, Syr-ia",
        "Syria, Syrian Arab Republic, SAR, SY, SYR, سوريا, Qamishli, Qamishlo"
    ),

    # ════════════════════════════════════════════════════════════════════════
    # CUBA — Cases 61-80  (user-provided queries)
    # ════════════════════════════════════════════════════════════════════════

    # 61
    (
        "Floor 50, Havana Business Plaza, Havana, 10100, Cubaqx",
        "Cuba, Republic of Cuba, República de Cuba, CU, CUB, La Habana, Havana, Habana"
    ),
    # 62
    (
        "Office 10, Varadero Resort Complex, Varadero, 10200, Cuvba",
        "Cuba, Republic of Cuba, República de Cuba, CU, CUB, Varadero, Matanzas Province"
    ),
    # 63
    (
        "Unit 22, Santiago Trade Center, Santiago, 10300, C-uba",
        "Cuba, Republic of Cuba, República de Cuba, CU, CUB, Santiago de Cuba, Santiago"
    ),
    # 64
    (
        "Building 8, Camaguey Industrial Park, Camaguey, 10400, Cub-a",
        "Cuba, Republic of Cuba, República de Cuba, CU, CUB, Camagüey, Camaguey"
    ),
    # 65
    (
        "Apt 15, Holguin Administrative Bldg, Holguin, 10500, Cuuba",
        "Cuba, Republic of Cuba, República de Cuba, CU, CUB, Holguín, Holguin"
    ),
    # 66
    (
        "Floor 3, Pinar del Rio Commerce Hub, Pinar del Rio, 10600, Cubaa",
        "Cuba, Republic of Cuba, República de Cuba, CU, CUB, Pinar del Río, Pinar del Rio"
    ),
    # 67
    (
        "Suite 7, Cienfuegos Port Operations, Cienfuegos, 10700, Cbuac",
        "Cuba, Republic of Cuba, República de Cuba, CU, CUB, Cienfuegos"
    ),
    # 68
    (
        "Building 12, Santa Clara Business Hub, Santa Clara, 10800, Cubaa",
        "Cuba, Republic of Cuba, República de Cuba, CU, CUB, Santa Clara, Villa Clara Province"
    ),
    # 69
    (
        "Office 9, Guantanamo Logistics Site, Guantanamo, 10900, Cubqx",
        "Cuba, Republic of Cuba, República de Cuba, CU, CUB, Guantánamo, Guantanamo"
    ),
    # 70
    (
        "Floor 4, Bayamo Trade Center, Bayamo, 11000, Cubae",
        "Cuba, Republic of Cuba, República de Cuba, CU, CUB, Bayamo, Granma Province"
    ),
    # 71
    (
        "Unit 60, Havana Central Plaza, Havana, 10100, Cuba-a",
        "Cuba, Republic of Cuba, República de Cuba, CU, CUB, La Habana, Havana"
    ),
    # 72
    (
        "Building 12, Varadero Executive Suite, Varadero, 10200, Cubaa",
        "Cuba, Republic of Cuba, República de Cuba, CU, CUB, Varadero, Matanzas Province"
    ),
    # 73
    (
        "Floor 25, Santiago Regional Office, Santiago, 10300, Cbuac",
        "Cuba, Republic of Cuba, República de Cuba, CU, CUB, Santiago de Cuba, Santiago"
    ),
    # 74
    (
        "Apt 10, Camaguey Commerce Bldg, Camaguey, 10400, Cubae",
        "Cuba, Republic of Cuba, República de Cuba, CU, CUB, Camagüey, Camaguey"
    ),
    # 75
    (
        "Suite 20, Holguin Administrative Hub, Holguin, 10500, Cubaqx",
        "Cuba, Republic of Cuba, República de Cuba, CU, CUB, Holguín, Holguin"
    ),
    # 76
    (
        "Building 5, Pinar del Rio Logistic Base, Pinar del Rio, 10600, Cuvba",
        "Cuba, Republic of Cuba, República de Cuba, CU, CUB, Pinar del Río, Pinar del Rio"
    ),
    # 77
    (
        "Office 10, Cienfuegos Municipal Plaza, Cienfuegos, 10700, C-uba",
        "Cuba, Republic of Cuba, República de Cuba, CU, CUB, Cienfuegos"
    ),
    # 78
    (
        "Floor 15, Santa Clara Commerce Center, Santa Clara, 10800, Cub-a",
        "Cuba, Republic of Cuba, República de Cuba, CU, CUB, Santa Clara, Villa Clara Province"
    ),
    # 79
    (
        "Unit 12, Guantanamo Port Authority, Guantanamo, 10900, Cuuba",
        "Cuba, Republic of Cuba, República de Cuba, CU, CUB, Guantánamo, Guantanamo"
    ),
    # 80
    (
        "Apt 8, Bayamo City Center, Bayamo, 11000, Cubaa",
        "Cuba, Republic of Cuba, República de Cuba, CU, CUB, Bayamo, Granma Province"
    ),

    # ════════════════════════════════════════════════════════════════════════
    # RUSSIA — Cases 81-100  (user-provided queries)
    # ════════════════════════════════════════════════════════════════════════

    # 81
    (
        "Floor 5, Lenina Office Complex, Moscow, 101000, Ruzzia",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Moscow, Moskva, Moskau"
    ),
    # 82
    (
        "Building 12, Arbat Street Trade Center, Moscow, 102000, Ruusssia",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Moscow, Moskva"
    ),
    # 83
    (
        "Suite 8, Nevsky Prospekt Plaza, St. Petersburg, 190000, Russi-a",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Saint Petersburg, St. Petersburg, Leningrad, SPb"
    ),
    # 84
    (
        "Office 22, Gorky Street Business Park, Nizhny Novgorod, 603000, Russiq",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Nizhny Novgorod, Nizhniy Novgorod, Gorky"
    ),
    # 85
    (
        "Warehouse 44, Pushkin Industrial Zone, Kazan, 420000, Rus-sia",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Kazan, Tatarstan"
    ),
    # 86
    (
        "Floor 9, Tverskaya Business Center, Moscow, 125000, Russ-ia",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Moscow, Moskva, Tverskoy"
    ),
    # 87
    (
        "Apt 3, Sadovaya Street Residency, Rostov-on-Don, 344000, Ruzz-ia",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Rostov-on-Don, Rostov, Rostov-na-Donu"
    ),
    # 88
    (
        "Suite 17, Komsomolsk Business Hub, Perm, 614000, Russya",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Perm, Permsky Kray"
    ),
    # 89
    (
        "Building 21, Mira Avenue Trade Center, Sochi, 354000, Russa",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Sochi, Krasnodar Krai"
    ),
    # 90
    (
        "Office 6, Sovietskaya Regional Office, Ufa, 450000, R-ussia",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Ufa, Bashkortostan"
    ),
    # 91
    (
        "Unit 8, Lenina Business Center, Moscow, 101000, Ru-ssia",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Moscow, Moskva"
    ),
    # 92
    (
        "Floor 15, Arbat District HQ, Moscow, 102000, Russ-ia",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Moscow, Moskva, Arbat"
    ),
    # 93
    (
        "Apt 10, Nevsky Trade Prospekt, St. Petersburg, 190000, Ruzz-ia",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Saint Petersburg, St. Petersburg, SPb"
    ),
    # 94
    (
        "Building 25, Gorky Industrial Plaza, Nizhny Novgorod, 603000, Russya",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Nizhny Novgorod, Gorky"
    ),
    # 95
    (
        "Suite 50, Pushkin Commerce Site, Kazan, 420000, Russa",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Kazan, Tatarstan"
    ),
    # 96
    (
        "Office 12, Tverskaya Logistics Center, Moscow, 125000, R-ussia",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Moscow, Moskva"
    ),
    # 97
    (
        "Floor 6, Sadovaya Plaza, Rostov-on-Don, 344000, Ruzzia",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Rostov-on-Don, Rostov-na-Donu"
    ),
    # 98
    (
        "Unit 20, Komsomolsk Trade Zone, Perm, 614000, Ruusssia",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Perm, Permsky Kray"
    ),
    # 99
    (
        "Apt 25, Mira Avenue Residential, Sochi, 354000, Russi-a",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Sochi, Krasnodar Krai"
    ),
    # 100
    (
        "Warehouse 9, Sovietskaya Industrial Park, Ufa, 450000, Russiq",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Ufa, Bashkortostan"
    ),

    # ════════════════════════════════════════════════════════════════════════
    # IRAN — Cases 101-120  (generated)
    # ════════════════════════════════════════════════════════════════════════

    # 101
    (
        "Apt 7, Mehrabad Airport Road, Tehran, 13145, Iraan",
        "Iran, Islamic Republic of Iran, IRI, I.R.I., I.R.I, Persia, ایران, IR, IRN, Tehran, Mehrabad"
    ),
    # 102
    (
        "Suite 33, Mashhad Grand Bazaar, Mashhad, 91735, Irn",
        "Iran, Islamic Republic of Iran, IRI, Persia, ایران, IRN, IR, Mashhad, Razavi Khorasan"
    ),
    # 103
    (
        "Building 15, Vanak Square Office, Tehran, 19689, Persi-a",
        "Iran, Islamic Republic of Iran, IRI, I.R.I., Persia, Persis, ایران, IR, IRN, Tehran, Vanak"
    ),
    # 104
    (
        "Floor 6, Isfahan Grand Mosque Complex, Isfahan, 81456, Iraan",
        "Iran, Islamic Republic of Iran, IRI, Persia, ایران, IRN, IR, Isfahan, Esfahan, Isfahan Province"
    ),
    # 105
    (
        "Unit 9, Bazaar-e Vakil, Shiraz, 71357, Ir4n",
        "Iran, Islamic Republic of Iran, IRI, I.R.I, Persia, ایران, IR, IRN, Shiraz, Fars Province, Vakil Bazaar"
    ),
    # 106
    (
        "Office 22, Kish Island Free Trade Zone, Kish, 79417, Irani",
        "Iran, Islamic Republic of Iran, IRI, Persia, ایران, IRN, IR, Kish, Kish Island, Hormozgan"
    ),
    # 107
    (
        "Warehouse 3, Bandar Abbas Port, Bandar Abbas, 79159, I.R.I-n",
        "Iran, Islamic Republic of Iran, IRI, I.R.I., I.R.I, Persia, ایران, IR, IRN, Bandar Abbas, Hormozgan"
    ),
    # 108
    (
        "Floor 11, Yazd Heritage District, Yazd, 89158, Irann",
        "Iran, Islamic Republic of Iran, IRI, Persia, ایران, IRN, IR, Yazd, Yazd Province"
    ),
    # 109
    (
        "Building 40, Bushehr Nuclear Site Rd, Bushehr, 75147, Ira_n",
        "Iran, Islamic Republic of Iran, IRI, I.R.I., Persia, ایران, IR, IRN, Bushehr, Bushehr Province"
    ),
    # 110
    (
        "Suite 5, Arak Heavy Water Industrial Park, Arak, 38135, IRaann",
        "Iran, Islamic Republic of Iran, IRI, Persia, ایران, IRN, IR, Arak, Markazi Province"
    ),
    # 111
    (
        "Apt 19, Ardabil Central Square, Ardabil, 56157, Iiran",
        "Iran, Islamic Republic of Iran, IRI, I.R.I, Persia, ایران, IR, IRN, Ardabil, Ardabil Province"
    ),
    # 112
    (
        "Office 8, Hamadan Ancient Site Blvd, Hamadan, 65178, Irann",
        "Iran, Islamic Republic of Iran, IRI, Persia, ایران, IRN, IR, Hamadan, Hamedan, Hamadan Province"
    ),
    # 113
    (
        "Building 17, Ilam Border Trade Facility, Ilam, 69317, Irqan",
        "Iran, Islamic Republic of Iran, IRI, I.R.I., Persia, ایران, IR, IRN, Ilam, Ilam Province"
    ),
    # 114
    (
        "Floor 7, Khorramabad Mountain Road, Khorramabad, 68137, Iraqn",
        "Iran, Islamic Republic of Iran, IRI, Persia, ایران, IRN, IR, Khorramabad, Lorestan"
    ),
    # 115
    (
        "Unit 33, Zahedan Southeast Hub, Zahedan, 98167, Iraen",
        "Iran, Islamic Republic of Iran, IRI, I.R.I, Persia, ایران, IR, IRN, Zahedan, Sistan and Baluchestan"
    ),
    # 116
    (
        "Apt 55, Gorgan Northern Office, Gorgan, 49178, I-raan",
        "Iran, Islamic Republic of Iran, IRI, Persia, ایران, IRN, IR, Gorgan, Golestan Province"
    ),
    # 117
    (
        "Suite 22, Sanandaj Kurdistan Plaza, Sanandaj, 66177, Irzan",
        "Iran, Islamic Republic of Iran, IRI, I.R.I., Persia, ایران, IR, IRN, Sanandaj, Kurdistan Province"
    ),
    # 118
    (
        "Building 44, Semnan Desert Logistics, Semnan, 35197, Irraan",
        "Iran, Islamic Republic of Iran, IRI, Persia, ایران, IRN, IR, Semnan, Semnan Province"
    ),
    # 119
    (
        "Floor 2, Ahvaz Petrochemical Complex, Ahvaz, 61457, Irann",
        "Iran, Islamic Republic of Iran, IRI, I.R.I, Persia, ایران, IR, IRN, Ahvaz, Khuzestan, Petrochemical"
    ),
    # 120
    (
        "Office 10, Mashhad Imam Reza Shrine District, Mashhad, 91367, Iiraan",
        "Iran, Islamic Republic of Iran, IRI, Persia, ایران, IRN, IR, Mashhad, Razavi Khorasan, Imam Reza"
    ),

    # ════════════════════════════════════════════════════════════════════════
    # NORTH KOREA — Cases 121-140  (generated)
    # ════════════════════════════════════════════════════════════════════════

    # 121
    (
        "Apt 22, Paektusan Research Institute, Pyongyang, 00150, D.P.R.K-n",
        "North Korea, Democratic People's Republic of Korea, DPRK, D.P.R.K., NK, KP, PRK, Korea (North), Pyongyang, Chosŏn"
    ),
    # 122
    (
        "Floor 14, Mansudae Art Studio, Pyongyang, 00250, NKorea-a",
        "North Korea, Democratic People's Republic of Korea, DPRK, NK, KP, PRK, Korea (North), Pyongyang, Mansudae"
    ),
    # 123
    (
        "Building 3, Rajin Free Economic Zone, Rajin, 00350, Nrth-Korea",
        "North Korea, Democratic People's Republic of Korea, DPRK, D.P.R.K., NK, KP, PRK, Korea (North), Rajin, Rason Special City"
    ),
    # 124
    (
        "Suite 7, Sonbong Industrial Estate, Sonbong, 00450, NKoera",
        "North Korea, Democratic People's Republic of Korea, DPRK, NK, KP, PRK, Korea (North), Sonbong, Rason"
    ),
    # 125
    (
        "Unit 30, Chongjin Steel Complex, Chongjin, 00550, NrthKorea",
        "North Korea, Democratic People's Republic of Korea, DPRK, D.P.R.K., NK, KP, PRK, Korea (North), Chongjin, North Hamgyong"
    ),
    # 126
    (
        "Office 5, Hyesan Border Trade Post, Hyesan, 00650, D-PRK",
        "North Korea, Democratic People's Republic of Korea, DPRK, NK, KP, PRK, Korea (North), Hyesan, Ryanggang Province"
    ),
    # 127
    (
        "Apt 18, Samjiyon Mountain Resort, Samjiyon, 00750, Nth-Korea",
        "North Korea, Democratic People's Republic of Korea, DPRK, D.P.R.K., NK, KP, PRK, Korea (North), Samjiyon, Ryanggang"
    ),
    # 128
    (
        "Building 9, Kusong Munitions Factory, Kusong, 00850, NKoreia",
        "North Korea, Democratic People's Republic of Korea, DPRK, NK, KP, PRK, Korea (North), Kusong, North Pyongan"
    ),
    # 129
    (
        "Floor 5, Pyongsong Science City, Pyongsong, 00950, NorKora",
        "North Korea, Democratic People's Republic of Korea, DPRK, D.P.R.K., NK, KP, PRK, Korea (North), Pyongsong, South Pyongan"
    ),
    # 130
    (
        "Suite 12, Sariwon Textile Factory, Sariwon, 01050, NKorrea",
        "North Korea, Democratic People's Republic of Korea, DPRK, NK, KP, PRK, Korea (North), Sariwon, North Hwanghae"
    ),
    # 131
    (
        "Warehouse 6, Tanchon Zinc Smelter, Tanchon, 01150, NKorea_n",
        "North Korea, Democratic People's Republic of Korea, DPRK, D.P.R.K., NK, KP, PRK, Korea (North), Tanchon, South Hamgyong"
    ),
    # 132
    (
        "Unit 4, Kanggye Arms Industrial District, Kanggye, 01250, NKoriea",
        "North Korea, Democratic People's Republic of Korea, DPRK, NK, KP, PRK, Korea (North), Kanggye, Chagang Province"
    ),
    # 133
    (
        "Office 19, Haeju Port Operations, Haeju, 01350, DPRK-a",
        "North Korea, Democratic People's Republic of Korea, DPRK, D.P.R.K., NK, KP, PRK, Korea (North), Haeju, South Hwanghae"
    ),
    # 134
    (
        "Building 7, Pyongyang Munitions Belt, Pyongyang, 00100, Nkorrea",
        "North Korea, Democratic People's Republic of Korea, DPRK, NK, KP, PRK, Korea (North), Pyongyang"
    ),
    # 135
    (
        "Floor 3, Wonsan Aerospace Complex, Wonsan, 00600, NKoraee",
        "North Korea, Democratic People's Republic of Korea, DPRK, D.P.R.K., NK, KP, PRK, Korea (North), Wonsan, Kangwon Province"
    ),
    # 136
    (
        "Apt 33, Nampo Copper Smelter, Nampo, 00800, Nkoreaa",
        "North Korea, Democratic People's Republic of Korea, DPRK, NK, KP, PRK, Korea (North), Nampo, South Pyongan"
    ),
    # 137
    (
        "Suite 25, Hamhung Chemical Plant, Hamhung, 00700, NorthKoera",
        "North Korea, Democratic People's Republic of Korea, DPRK, D.P.R.K., NK, KP, PRK, Korea (North), Hamhung, South Hamgyong"
    ),
    # 138
    (
        "Building 14, Kaesong Joint Industrial Complex, Kaesong, 00900, NKorea.n",
        "North Korea, Democratic People's Republic of Korea, DPRK, NK, KP, PRK, Korea (North), Kaesong, North Hwanghae"
    ),
    # 139
    (
        "Office 8, Sinuiju Special Administrative Region, Sinuiju, 01000, Norh-Korea",
        "North Korea, Democratic People's Republic of Korea, DPRK, D.P.R.K., NK, KP, PRK, Korea (North), Sinuiju, North Pyongan"
    ),
    # 140
    (
        "Floor 10, Pyongyang Central Bank Building, Pyongyang, 00100, NKoraae",
        "North Korea, Democratic People's Republic of Korea, DPRK, NK, KP, PRK, Korea (North), Pyongyang, Central Bank"
    ),

    # ════════════════════════════════════════════════════════════════════════
    # SYRIA — Cases 141-160  (generated)
    # ════════════════════════════════════════════════════════════════════════

    # 141
    (
        "Building 18, Al-Midan Industrial Quarter, Damascus, 00010, Syriq",
        "Syria, Syrian Arab Republic, SAR, SY, SYR, Syrie, سوريا, Damascus, Ash-Sham, Al-Midan"
    ),
    # 142
    (
        "Suite 6, Aleppo Citadel Trade Zone, Aleppo, 00020, Syri-ia",
        "Syria, Syrian Arab Republic, SAR, SY, SYR, سوريا, Aleppo, Halab, Aleppo Citadel"
    ),
    # 143
    (
        "Floor 12, Palmyra Archaeological District, Tadmur, 00030, Syri4a",
        "Syria, Syrian Arab Republic, SAR, SY, SYR, Syrie, سوريا, Tadmur, Palmyra, Homs Governorate"
    ),
    # 144
    (
        "Apt 9, Maalula Christian Quarter, Maalula, 00040, Sy-rria",
        "Syria, Syrian Arab Republic, SAR, SY, SYR, سوريا, Maaloula, Maalula, Rif Dimashq"
    ),
    # 145
    (
        "Office 33, Sweida Druze Administrative Hub, Sweida, 00050, Syira",
        "Syria, Syrian Arab Republic, SAR, SY, SYR, Syrie, سوريا, Sweida, As-Suwayda, As-Suwayda Governorate"
    ),
    # 146
    (
        "Building 20, Daraa Southern Border Office, Daraa, 00060, Syri-qa",
        "Syria, Syrian Arab Republic, SAR, SY, SYR, سوريا, Daraa, Dar'a, Daraa Governorate"
    ),
    # 147
    (
        "Unit 14, Al-Hasakah Grain Depot, Al-Hasakah, 00070, Syriaa",
        "Syria, Syrian Arab Republic, SAR, SY, SYR, Syrie, سوريا, Al-Hasakah, Al-Hasaka, Hasakah Governorate"
    ),
    # 148
    (
        "Floor 8, Deir Hafer Oil Hub, Deir Hafer, 00080, Syr1ia",
        "Syria, Syrian Arab Republic, SAR, SY, SYR, سوريا, Deir Hafer, Aleppo Governorate"
    ),
    # 149
    (
        "Suite 3, Safita Mountain Hotel Office, Safita, 00090, Sy-r-ia",
        "Syria, Syrian Arab Republic, SAR, SY, SYR, Syrie, سوريا, Safita, Tartus Governorate"
    ),
    # 150
    (
        "Building 11, Jisr al-Shughur Border Post, Jisr al-Shughur, 00100, Syrja",
        "Syria, Syrian Arab Republic, SAR, SY, SYR, سوريا, Jisr al-Shughur, Idlib Governorate"
    ),
    # 151
    (
        "Apt 16, Baniyas Oil Refinery District, Baniyas, 00010, Syrria",
        "Syria, Syrian Arab Republic, SAR, SY, SYR, Syrie, سوريا, Baniyas, Tartus Governorate"
    ),
    # 152
    (
        "Office 25, Al-Bukamal Border Trade, Al-Bukamal, 00020, Syriay",
        "Syria, Syrian Arab Republic, SAR, SY, SYR, سوريا, Al-Bukamal, Abu Kamal, Deir ez-Zor Governorate"
    ),
    # 153
    (
        "Floor 9, Sahl Al-Ghab Agricultural Zone, Hama, 00030, Syrha",
        "Syria, Syrian Arab Republic, SAR, SY, SYR, Syrie, سوريا, Hama, Hamah, Sahl Al-Ghab"
    ),
    # 154
    (
        "Unit 21, Ayn al-Arab Border Crossing, Kobani, 00040, Syri-ah",
        "Syria, Syrian Arab Republic, SAR, SY, SYR, سوريا, Kobani, Ayn al-Arab, Aleppo Governorate"
    ),
    # 155
    (
        "Building 8, Nawa Wheat Storage, Nawa, 00050, Syriah",
        "Syria, Syrian Arab Republic, SAR, SY, SYR, Syrie, سوريا, Nawa, Daraa Governorate"
    ),
    # 156
    (
        "Suite 17, Quneitra Buffer Zone Office, Quneitra, 00060, Syiria",
        "Syria, Syrian Arab Republic, SAR, SY, SYR, سوريا, Quneitra, Al-Qunaytirah, Quneitra Governorate"
    ),
    # 157
    (
        "Apt 5, Tal Afar Logistics Hub, Raqqa, 00070, Syraiah",
        "Syria, Syrian Arab Republic, SAR, SY, SYR, Syrie, سوريا, Raqqa, Ar-Raqqah"
    ),
    # 158
    (
        "Office 14, Kamishly Trade Junction, Qamishli, 00080, Syrya",
        "Syria, Syrian Arab Republic, SAR, SY, SYR, سوريا, Qamishli, Qamishlo, Kamishly"
    ),
    # 159
    (
        "Building 30, Masyaf Military Complex, Masyaf, 00090, Syr-ria",
        "Syria, Syrian Arab Republic, SAR, SY, SYR, Syrie, سوريا, Masyaf, Hama Governorate"
    ),
    # 160
    (
        "Floor 6, Ras al-Ayn Water Authority, Ras al-Ayn, 00100, Sy-riaa",
        "Syria, Syrian Arab Republic, SAR, SY, SYR, سوريا, Ras al-Ayn, Sere Kaniye, Hasakah Governorate"
    ),

    # ════════════════════════════════════════════════════════════════════════
    # CUBA — Cases 161-175  (generated)
    # ════════════════════════════════════════════════════════════════════════

    # 161
    (
        "Suite 8, Trinidad Colonial Quarter, Trinidad, 72200, Kuuba",
        "Cuba, Republic of Cuba, República de Cuba, CU, CUB, Trinidad, Sancti Spíritus Province"
    ),
    # 162
    (
        "Building 33, Manzanillo Port Complex, Manzanillo, 87600, Cuuba",
        "Cuba, Republic of Cuba, República de Cuba, CU, CUB, Manzanillo, Granma Province"
    ),
    # 163
    (
        "Floor 4, Las Tunas Sugar Mill, Las Tunas, 75100, Cub-ia",
        "Cuba, Republic of Cuba, República de Cuba, CU, CUB, Las Tunas, Las Tunas Province"
    ),
    # 164
    (
        "Apt 12, Ciego de Avila Industrial Estate, Ciego de Avila, 69300, Kuuba",
        "Cuba, Republic of Cuba, República de Cuba, CU, CUB, Ciego de Ávila, Ciego de Avila Province"
    ),
    # 165
    (
        "Office 18, Nuevitas Bay Port Operations, Nuevitas, 71100, Cubba",
        "Cuba, Republic of Cuba, República de Cuba, CU, CUB, Nuevitas, Camagüey Province"
    ),
    # 166
    (
        "Unit 5, Matanzas Chemical Hub, Matanzas, 40100, Cubxa",
        "Cuba, Republic of Cuba, República de Cuba, CU, CUB, Matanzas, Matanzas Province"
    ),
    # 167
    (
        "Building 9, Artemisa Tobacco Factory, Artemisa, 33800, Cub4a",
        "Cuba, Republic of Cuba, República de Cuba, CU, CUB, Artemisa, Artemisa Province"
    ),
    # 168
    (
        "Suite 27, Sancti Spiritus Archive, Sancti Spiritus, 60100, C-uuba",
        "Cuba, Republic of Cuba, República de Cuba, CU, CUB, Sancti Spíritus, Sancti Spiritus Province"
    ),
    # 169
    (
        "Floor 11, Isla de la Juventud Administrative Center, Nueva Gerona, 25100, Kubba",
        "Cuba, Republic of Cuba, República de Cuba, CU, CUB, Nueva Gerona, Isla de la Juventud"
    ),
    # 170
    (
        "Apt 6, Mayabeque Provincial Hall, San Jose, 32500, Cuuba",
        "Cuba, Republic of Cuba, República de Cuba, CU, CUB, San José de las Lajas, Mayabeque Province"
    ),
    # 171
    (
        "Building 15, Guantanamo Naval Base Perimeter, Guantanamo, 10900, C.U.B.a",
        "Cuba, Republic of Cuba, República de Cuba, CU, CUB, Guantánamo, Guantanamo Province"
    ),
    # 172
    (
        "Office 22, Havana International Trade Fair, Havana, 10100, Kubba",
        "Cuba, Republic of Cuba, República de Cuba, CU, CUB, La Habana, Havana, Habana"
    ),
    # 173
    (
        "Floor 7, Cienfuegos Nuclear Power Plant Road, Cienfuegos, 10700, Cuuba",
        "Cuba, Republic of Cuba, República de Cuba, CU, CUB, Cienfuegos, Cienfuegos Province"
    ),
    # 174
    (
        "Suite 4, Cardenas Trade Zone, Cardenas, 41800, Cubaa",
        "Cuba, Republic of Cuba, República de Cuba, CU, CUB, Cárdenas, Matanzas Province"
    ),
    # 175
    (
        "Unit 30, Camagüey Railroad Depot, Camaguey, 10400, Cub-ba",
        "Cuba, Republic of Cuba, República de Cuba, CU, CUB, Camagüey, Camaguey, Camaguey Province"
    ),

    # ════════════════════════════════════════════════════════════════════════
    # RUSSIA — Cases 176-200  (generated)
    # ════════════════════════════════════════════════════════════════════════

    # 176
    (
        "Building 22, Vladivostok Pacific Port, Vladivostok, 690000, Ruziah",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Vladivostok, Primorsky Krai"
    ),
    # 177
    (
        "Floor 3, Novosibirsk Science City, Novosibirsk, 630000, Rusiy-a",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Novosibirsk, Akademgorodok, Novosibirsk Oblast"
    ),
    # 178
    (
        "Suite 11, Yekaterinburg Ural Industrial Hub, Yekaterinburg, 620000, Russsia",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Yekaterinburg, Ekaterinburg, Sverdlovsk Oblast"
    ),
    # 179
    (
        "Apt 44, Omsk Petrochemical Refinery, Omsk, 644000, Rusiia",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Omsk, Omsk Oblast"
    ),
    # 180
    (
        "Office 8, Samara Volga Trade Center, Samara, 443000, Ru-ssia",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Samara, Samara Oblast, Kuybyshev"
    ),
    # 181
    (
        "Building 30, Chelyabinsk Metallurgical Plant, Chelyabinsk, 454000, Russ-ya",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Chelyabinsk, Chelyabinsk Oblast"
    ),
    # 182
    (
        "Floor 9, Krasnoyarsk Siberian Logistics, Krasnoyarsk, 660000, Rosssia",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Krasnoyarsk, Krasnoyarsk Krai"
    ),
    # 183
    (
        "Suite 6, Volgograd Stalingrad Memorial District, Volgograd, 400000, Ruz-ia",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Volgograd, Stalingrad, Volgograd Oblast"
    ),
    # 184
    (
        "Apt 15, Krasnodar Agri Export Hub, Krasnodar, 350000, Rus-sia",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Krasnodar, Krasnodar Krai"
    ),
    # 185
    (
        "Unit 22, Saratov Arms Research Institute, Saratov, 410000, Ruzzia",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Saratov, Saratov Oblast"
    ),
    # 186
    (
        "Building 18, Tyumen Oil Ministry, Tyumen, 625000, Rrusia",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Tyumen, Tyumen Oblast"
    ),
    # 187
    (
        "Office 12, Irkutsk Lake Baikal Trade Zone, Irkutsk, 664000, Ruusia",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Irkutsk, Irkutsk Oblast"
    ),
    # 188
    (
        "Floor 5, Khabarovsk Far East Commerce, Khabarovsk, 680000, Russsia",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Khabarovsk, Khabarovsk Krai"
    ),
    # 189
    (
        "Suite 33, Murmansk Arctic Port, Murmansk, 183000, Rrussiya",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Murmansk, Murmansk Oblast"
    ),
    # 190
    (
        "Apt 7, Kaliningrad Baltic Enclave Office, Kaliningrad, 236000, Rus-ia",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Kaliningrad, Königsberg, Kaliningrad Oblast"
    ),
    # 191
    (
        "Building 40, Pskov Border Crossing Hub, Pskov, 180000, Rossiya-n",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Pskov, Pskov Oblast"
    ),
    # 192
    (
        "Floor 14, Kursk Nuclear Power Station Road, Kursk, 305000, Russi-ya",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Kursk, Kursk Oblast"
    ),
    # 193
    (
        "Office 3, Bryansk Defense Industry Park, Bryansk, 241000, Russyia",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Bryansk, Bryansk Oblast"
    ),
    # 194
    (
        "Unit 19, Tula Arms Manufacturing District, Tula, 300000, Ruzz-ia",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Tula, Tula Oblast"
    ),
    # 195
    (
        "Suite 8, Voronezh Aviation Industrial Estate, Voronezh, 394000, Rusiay",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Voronezh, Voronezh Oblast"
    ),
    # 196
    (
        "Building 6, Yaroslavl Chemical Industry Site, Yaroslavl, 150000, Russa",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Yaroslavl, Yaroslavl Oblast"
    ),
    # 197
    (
        "Apt 21, Vladikavkaz North Caucasus Complex, Vladikavkaz, 362000, Russ_ia",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Vladikavkaz, North Ossetia"
    ),
    # 198
    (
        "Floor 8, Grozny Chechen Industrial Site, Grozny, 364000, Russiqa",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Grozny, Chechnya, Chechen Republic"
    ),
    # 199
    (
        "Office 11, Makhachkala Caspian Port, Makhachkala, 367000, Russ-iya",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Makhachkala, Dagestan"
    ),
    # 200
    (
        "Suite 30, Astrakhan Volga Delta Trade Hub, Astrakhan, 414000, Ruussia",
        "Russia, Russian Federation, Rossiya, RU, RUS, Россия, RF, Astrakhan, Astrakhan Oblast"
    ),
]


# ---------------------------------------------------------------------------
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

