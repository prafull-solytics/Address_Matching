# LocationMatcher — Test Cases

> Auto-generated from `test_edge_cases.py`  

> Total test cases: **204**

---


## EC-1 — AbbreviationAmbiguity

*8 test case(s)*

| # | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------|----------------|---------------------------|-------|
| 1 | `CA` | `California` | [0.8, 0.92] |  |
| 2 | `CA` | `Canada` | [0.8, 0.92] |  |
| 3 | `CA` | `California` | see test |  |
| 4 | `CA` | `Canada` | see test |  |
| 5 | `IL` | `Illinois` | [0.8, 0.92] |  |
| 6 | `TX` | `Texas` | [0.8, 0.92] |  |
| 7 | `DC` | `District of Columbia` | [0.8, 0.92] |  |
| 8 | `123 Main St, Springfield, IL` | `Illinois` | [0.8, 0.92] |  |

## EC-2 — CompoundConcatenated

*6 test case(s)*

| # | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------|----------------|---------------------------|-------|
| 1 | `NewYork` | `New York` | [0.75, 0.9] |  |
| 2 | `SanFrancisco` | `San Francisco` | [0.75, 0.9] |  |
| 3 | `SouthKorea` | `South Korea` | [0.6, 0.85] |  |
| 4 | `NewYork` | `New York` | compound > nomatch |  |
| 5 | `Abcdefg` | `New York` | compound > nomatch |  |
| 6 | `GuineaBissau` | `Guinea-Bissau` | [0.75, 0.92] |  |

## EC-3 — GarbageVariations

*13 test case(s)*

| # | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------|----------------|---------------------------|-------|
| 1 | `---` | `Iran` | == 0.0 |  |
| 2 | `...` | `Iran` | == 0.0 |  |
| 3 | `nil` | `Iran` | == 0.0 |  |
| 4 | `TBD` | `Iran` | == 0.0 |  |
| 5 | `test` | `Iran` | == 0.0 |  |
| 6 | `None` | `Iran` | raises TypeError |  |
| 7 | `123` | `Iran` | raises TypeError |  |
| 8 | `Iran` | `None` | raises TypeError |  |
| 9 | `` | `` | == 0.0 |  |
| 10 | ` ` | `Iran` | == 0.0 |  |
| 11 | `	 ` | `Iran` | == 0.0 |  |
| 12 | `!@#$%^&*()` | `Iran` | == 0.0 |  |
| 13 | `999 888 777` | `Iran` | [0.0, 0.05] |  |

## EC-4 — UnicodeExtended

*6 test case(s)*

| # | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------|----------------|---------------------------|-------|
| 1 | `CÔTE D'IVOIRE` | `Cote Ivoire` | [0.85, 1.0] |  |
| 2 | `SÃO PAULO` | `Sao Paulo` | [0.9, 1.0] |  |
| 3 | `Zürich` | `Zurich` | [0.9, 1.0] |  |
| 4 | `Łódź` | `Lodz` | [0.7, 1.0] |  |
| 5 | `İstanbul` | `Istanbul` | [0.9, 1.0] |  |
| 6 | `Français` | `Francais` | [0.9, 1.0] |  |

## EC-5 — ResultLongerThanQuery

*9 test case(s)*

| # | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------|----------------|---------------------------|-------|
| 1 | `Korea` | `North Korea` | [0.35, 0.55] |  |
| 2 | `York` | `New York` | [0.4, 0.6] |  |
| 3 | `Arabia` | `Saudi Arabia` | [0.4, 0.6] |  |
| 4 | `Guinea` | `Papua New Guinea` | [0.2, 0.5] |  |
| 5 | `North Korea` | `North Korea` | full > partial |  |
| 6 | `Korea` | `North Korea` | full > partial |  |
| 7 | `Papua New Guinea` | `Papua New Guinea` | [0.95, 1.0] |  |
| 8 | `Papua Guinea` | `Papua New Guinea` | [0.55, 0.8] |  |
| 9 | `North` | `North Korea` | [0.65, 0.85] |  |

## EC-6 — CollisionContextDetection

*14 test case(s)*

| # | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------|----------------|---------------------------|-------|
| 1 | `Turkey, Istanbul` | `Turkey` | [0.95, 1.0] |  |
| 2 | `China, Beijing` | `China` | [0.95, 1.0] |  |
| 3 | `Jordan, Amman` | `Jordan` | [0.95, 1.0] |  |
| 4 | `Georgia, USA` | `Georgia` | [0.95, 1.0] |  |
| 5 | `Turkey sandwich shop` | `Turkey` | [0.0, 0.35] |  |
| 6 | `China Cabinet Store, LA` | `China` | [0.0, 0.35] |  |
| 7 | `Jordan shoes store` | `Jordan` | [0.0, 0.4] |  |
| 8 | `Nice apartment for rent` | `Nice` | [0.0, 0.4] |  |
| 9 | `Turkey, Istanbul` | `Turkey` | geo > com |  |
| 10 | `Turkey sandwich shop` | `Turkey` | geo > com |  |
| 11 | `China, Beijing` | `China` | geo > com |  |
| 12 | `China Cabinet Store, LA` | `China` | geo > com |  |
| 13 | `Jordan, Amman` | `Jordan` | geo > com |  |
| 14 | `Jordan shoes store` | `Jordan` | geo > com |  |

## EC-7 — AlternateNamesContext

*10 test case(s)*

| # | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------|----------------|---------------------------|-------|
| 1 | `Bombay, Maharashtra, India` | `Mumbai` | [0.78, 0.92] |  |
| 2 | `Calcutta, West Bengal, India` | `Kolkata` | [0.78, 0.92] |  |
| 3 | `Constantinople, Turkey` | `Istanbul` | [0.78, 0.92] |  |
| 4 | `Deutschland` | `Germany` | [0.75, 0.9] |  |
| 5 | `Nippon` | `Japan` | [0.75, 0.9] |  |
| 6 | `Holland` | `Netherlands` | [0.75, 0.9] |  |
| 7 | `India` | `India` | exact > alt |  |
| 8 | `Bharat` | `India` | exact > alt |  |
| 9 | `Mumbai` | `Mumbai` | exact > alt |  |
| 10 | `Bombay` | `Mumbai` | exact > alt |  |

## EC-8 — SubstringEdgeCases

*8 test case(s)*

| # | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------|----------------|---------------------------|-------|
| 1 | `Parisian cafe` | `Paris` | [0.2, 0.5] |  |
| 2 | `Pakistani market` | `Pakistan` | [0.3, 0.55] |  |
| 3 | `American food` | `America` | [0.3, 0.55] |  |
| 4 | `DParis Hotel` | `Paris` | [0.3, 0.55] |  |
| 5 | `Paris, France` | `Paris` | exact > sub |  |
| 6 | `Parisian cafe` | `Paris` | exact > sub |  |
| 7 | `Bird sanctuary near lake` | `Ir` | [0.0, 0.25] |  |
| 8 | `Marine Drive, India` | `Iran` | [0.0, 0.15] |  |

## EC-9 — VeryLongAddresses

*9 test case(s)*

| # | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------|----------------|---------------------------|-------|
| 1 | `Suite 500, 100 Broadway, Floor 12, Manhattan, New York, NY, 10005, USA` | `USA` | [0.95, 1.0] |  |
| 2 | `Suite 500, 100 Broadway, Floor 12, Manhattan, New York, NY, 10005, USA` | `Manhattan` | [0.95, 1.0] |  |
| 3 | `Suite 500, 100 Broadway, Floor 12, Manhattan, New York, NY, 10005, USA` | `New York` | [0.95, 1.0] |  |
| 4 | `Flat 1, 2nd Floor, Building A, Green Complex, MG Road, Koramangala, Bangalore, Karnataka, India, 560001` | `India` | [0.95, 1.0] |  |
| 5 | `Flat 1, 2nd Floor, Building A, Green Complex, MG Road, Koramangala, Bangalore, Karnataka, India, 560001` | `Bangalore` | [0.95, 1.0] |  |
| 6 | `Flat 1, 2nd Floor, Building A, Green Complex, MG Road, Koramangala, Bangalore, Karnataka, India, 560001` | `Karnataka` | [0.95, 1.0] |  |
| 7 | `Flat 3, 27 Baker St, London W1U 8EW, United Kingdom` | `London` | [0.95, 1.0] |  |
| 8 | `Suite 500, 100 Broadway, Floor 12, Manhattan, New York, NY, 10005, USA` | `Tokyo` | [0.0, 0.05] |  |
| 9 | `Flat 1, 2nd Floor, Building A, Green Complex, MG Road, Koramangala, Bangalore, Karnataka, India, 560001` | `China` | [0.0, 0.05] |  |

## EC-10 — ScatteredTokens

*7 test case(s)*

| # | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------|----------------|---------------------------|-------|
| 1 | `Korea, officially North, country` | `North Korea` | [0.55, 0.97] |  |
| 2 | `Korea North` | `North Korea` | [0.72, 0.97] |  |
| 3 | `Korea is a great place, North` | `North Korea` | [0.3, 0.97] |  |
| 4 | `North Korea` | `North Korea` | ordered > reversed_ |  |
| 5 | `Korea North` | `North Korea` | ordered > reversed_ |  |
| 6 | `Korea North` | `North Korea` | reversed_ > absent |  |
| 7 | `Tokyo Japan` | `North Korea` | reversed_ > absent |  |

## EC-11 — ExactTokenPresence

*15 test case(s)*

| # | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------|----------------|---------------------------|-------|
| 1 | `Paris, France` | `France` | >= 0.95 | France in Paris addr |
| 2 | `Berlin, Germany` | `Germany` | >= 0.95 | Germany in Berlin addr |
| 3 | `Tokyo, Japan` | `Japan` | >= 0.95 | Japan in Tokyo addr |
| 4 | `Mumbai, India` | `India` | >= 0.95 | India in Mumbai addr |
| 5 | `Cairo, Egypt` | `Egypt` | >= 0.95 | Egypt in Cairo addr |
| 6 | `Lima, Peru` | `Peru` | >= 0.95 | Peru in Lima addr |
| 7 | `Beijing, China` | `Beijing` | >= 0.95 | Beijing exact |
| 8 | `Moscow, Russia` | `Russia` | >= 0.95 | Russia exact |
| 9 | `Sydney, Australia` | `Australia` | >= 0.95 | Australia exact |
| 10 | `Seoul, South Korea` | `Seoul` | [0.78, 0.9] |  |
| 11 | `Paris, France` | `Germany` | <= 0.05 | Germany NOT in Paris addr |
| 12 | `Berlin, Germany` | `France` | <= 0.05 | France NOT in Berlin addr |
| 13 | `Tokyo, Japan` | `China` | <= 0.05 | China NOT in Tokyo addr |
| 14 | `Mumbai, India` | `Pakistan` | <= 0.05 | Pakistan NOT in Mumbai addr |
| 15 | `Seoul, South Korea` | `Japan` | <= 0.05 | Japan NOT in Seoul addr |

## EC-12 — DirectionalEdgeCases

*6 test case(s)*

| # | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------|----------------|---------------------------|-------|
| 1 | `North Korea` | `South Korea` | [0.35, 0.6] |  |
| 2 | `East Africa` | `West Africa` | [0.5, 0.95] |  |
| 3 | `North Korea` | `North Korea` | [0.95, 1.0] |  |
| 4 | `Korea` | `North Korea` | [0.35, 0.55] |  |
| 5 | `Western Australia` | `Australia` | [0.75, 0.9] |  |
| 6 | `South Mumbai, Maharashtra, India` | `India` | [0.95, 1.0] |  |

## EC-13 — HyphenConnector

*6 test case(s)*

| # | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------|----------------|---------------------------|-------|
| 1 | `Guinea-Bissau` | `Guinea-Bissau` | [0.92, 1.0] |  |
| 2 | `Guinea Bissau` | `Guinea-Bissau` | [0.88, 1.0] |  |
| 3 | `Bosnia Herzegovina` | `Bosnia and Herzegovina` | [0.8, 0.95] |  |
| 4 | `Bosnia and Herzegovina` | `Bosnia and Herzegovina` | [0.92, 1.0] |  |
| 5 | `Trinidad and Tobago` | `Trinidad and Tobago` | [0.92, 1.0] |  |
| 6 | `Trinidad Tobago` | `Trinidad and Tobago` | [0.8, 0.95] |  |

## EC-14 — ArticlePrefixStripping

*5 test case(s)*

| # | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------|----------------|---------------------------|-------|
| 1 | `The Gambia` | `Gambia` | [0.88, 1.0] |  |
| 2 | `Kingdom of Saudi Arabia` | `Saudi Arabia` | [0.8, 0.95] |  |
| 3 | `State of New York` | `New York` | [0.8, 0.95] |  |
| 4 | `Province of Quebec` | `Quebec` | [0.82, 1.0] |  |
| 5 | `Republic of Korea` | `South Korea` | [0.4, 0.65] |  |

## EC-15 — TypoExtended

*9 test case(s)*

| # | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------|----------------|---------------------------|-------|
| 1 | `Iarn` | `Iran` | [0.78, 0.88] |  |
| 2 | `Germny` | `Germany` | [0.8, 0.92] |  |
| 3 | `Australiaa` | `Australia` | [0.8, 0.92] |  |
| 4 | `Frnace` | `France` | [0.75, 0.9] |  |
| 5 | `Noth Korea` | `North Korea` | [0.78, 0.99] |  |
| 6 | `Iran` | `Iran` | exact > typo |  |
| 7 | `Iarn` | `Iran` | exact > typo |  |
| 8 | `Germny` | `Germany` | one >= two * 0.9 |  |
| 9 | `Grmany` | `Germany` | one >= two * 0.9 |  |

## EC-16 — DebugContract

*6 test case(s)*

| # | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------|----------------|---------------------------|-------|
| 1 | `—` | `—` | see test |  |
| 2 | `—` | `—` | see test |  |
| 3 | `Hirani` | `Iran` | see test |  |
| 4 | `—` | `—` | see test |  |
| 5 | `—` | `—` | == 0.0 |  |
| 6 | `—` | `—` | >= 0.95 |  |

## EC-17 — ScoreOrdering

*18 test case(s)*

| # | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------|----------------|---------------------------|-------|
| 1 | `United States` | `United States` | exact > abbrev |  |
| 2 | `USA` | `United States` | exact > abbrev |  |
| 3 | `Germany` | `Germany` | exact > alt |  |
| 4 | `Deutschland` | `Germany` | exact > alt |  |
| 5 | `France` | `France` | exact > fuzzy |  |
| 6 | `Frnace` | `France` | exact > fuzzy |  |
| 7 | `Tehran, Iran` | `Iran` | exact > substr |  |
| 8 | `Hirani` | `Iran` | exact > substr |  |
| 9 | `Paris, France` | `Paris` | geo > com |  |
| 10 | `Nice apartment for rent` | `Nice` | geo > com |  |
| 11 | `South Korea` | `South Korea` | full > partial |  |
| 12 | `Korea` | `South Korea` | full > partial |  |
| 13 | `Tehran, Iran` | `Iran` | clean > noisy |  |
| 14 | `Marine Irani Rd` | `Iran` | clean > noisy |  |
| 15 | `North Korea` | `North Korea` | ordered > reversed_ |  |
| 16 | `Korea North` | `North Korea` | ordered > reversed_ |  |
| 17 | `Iran` | `Iran` | short >= long |  |
| 18 | `10, Green Apt, Iran` | `Iran` | short >= long |  |

## EC-18 — PhoneticMatching

*4 test case(s)*

| # | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------|----------------|---------------------------|-------|
| 1 | `Eyran` | `Iran` | [0.55, 0.85] |  |
| 2 | `Corea` | `Korea` | [0.65, 0.88] |  |
| 3 | `Iran` | `Iran` | exact > phonetic |  |
| 4 | `Eyran` | `Iran` | exact > phonetic |  |

## EC-19 — MultiEntityIndependent

*8 test case(s)*

| # | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------|----------------|---------------------------|-------|
| 1 | `addr` | `Manhattan` | >= 0.85 |  |
| 2 | `addr` | `New York` | >= 0.85 |  |
| 3 | `addr` | `United States` | >= 0.85 |  |
| 4 | `Paris, France` | `Paris` | >= 0.88 |  |
| 5 | `Paris, France` | `France` | >= 0.88 |  |
| 6 | `addr` | `Bangalore` | >= 0.95 |  |
| 7 | `addr` | `Karnataka` | >= 0.95 |  |
| 8 | `addr` | `India` | >= 0.95 |  |

## EC-20 — PunctuationExtended

*9 test case(s)*

| # | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------|----------------|---------------------------|-------|
| 1 | `Iran/Iraq` | `Iran` | >= 0.85 |  |
| 2 | `Iran/Iraq` | `Iraq` | >= 0.85 |  |
| 3 | `France\|Germany` | `France` | [0.85, 1.0] |  |
| 4 | `Korea\Japan` | `Korea` | [0.85, 1.0] |  |
| 5 | `Iran;` | `Iran` | [0.92, 1.0] |  |
| 6 | `Iran!` | `Iran` | [0.92, 1.0] |  |
| 7 | `[Iran]` | `Iran` | [0.92, 1.0] |  |
| 8 | `North.Korea` | `North Korea` | [0.8, 1.0] |  |
| 9 | `Paris,France` | `France` | [0.88, 1.0] |  |

## EC-21 — ModerateCommercial

*4 test case(s)*

| # | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------|----------------|---------------------------|-------|
| 1 | `Victoria Secret outlet` | `Victoria` | [0.4, 0.7] |  |
| 2 | `Panama hat shop` | `Panama` | [0.4, 0.7] |  |
| 3 | `Chile pepper sauce` | `Chile` | [0.4, 0.7] |  |
| 4 | `Guinea pig pet store` | `Guinea` | [0.4, 0.7] |  |

## EC-22 — IdenticalStrings

*6 test case(s)*

| # | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------|----------------|---------------------------|-------|
| 1 | `Iran` | `Iran` | == 1.0 |  |
| 2 | `North Korea` | `North Korea` | == 1.0 |  |
| 3 | `Los Angeles` | `Los Angeles` | [0.95, 1.0] |  |
| 4 | `IRAN` | `Iran` | == 1.0 |  |
| 5 | `Réunion` | `Reunion` | [0.9, 1.0] |  |
| 6 | `  Iran  ` | `Iran` | [0.95, 1.0] |  |

## EC-23 — NonMatch

*8 test case(s)*

| # | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------|----------------|---------------------------|-------|
| 1 | `Paris, France` | `Tokyo` | <= 0.05 |  |
| 2 | `Berlin, Germany` | `Moscow` | <= 0.05 |  |
| 3 | `Mumbai, India` | `Lagos` | <= 0.05 |  |
| 4 | `Sydney, Australia` | `Beijing` | <= 0.05 |  |
| 5 | `Cairo, Egypt` | `Lima` | <= 0.05 |  |
| 6 | `Toronto, Canada` | `Seoul` | <= 0.05 |  |
| 7 | `Bangkok, Thailand` | `Madrid` | <= 0.05 |  |
| 8 | `Nairobi, Kenya` | `Oslo` | <= 0.05 |  |

## EC-24 — RepeatedTokens

*4 test case(s)*

| # | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------|----------------|---------------------------|-------|
| 1 | `India India India` | `India` | [0.92, 1.0] |  |
| 2 | `North Korea North Korea` | `North Korea` | [0.92, 1.0] |  |
| 3 | `France` | `France` | see test |  |
| 4 | `France France` | `France` | see test |  |

## EC-25 — MixedAddressPatterns

*6 test case(s)*

| # | Query | Elastic Result | Expected Score / Condition | Notes |
|---|-------|----------------|---------------------------|-------|
| 1 | `c/o Jane Doe, Manchester, England` | `Manchester` | [0.95, 1.0] |  |
| 2 | `ATTENTION: Dr. Kumar, Chennai, India` | `Chennai` | [0.95, 1.0] |  |
| 3 | `Ship to: Warehouse, Manila, Philippines` | `Manila` | [0.95, 1.0] |  |
| 4 | `Delivery to: Mumbai, India - URGENT` | `India` | [0.95, 1.0] |  |
| 5 | `P.O. Box 44, France` | `France` | [0.6, 0.7] |  |
| 6 | `400001, Mumbai` | `Mumbai` | [0.9, 1.0] |  |
