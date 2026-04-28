# RENTER
## Sovelluksen toiminnot

- Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
- Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan ilmoituksia.
- Käyttäjä pystyy lisäämään kuvia ilmoitukseen.
- Käyttäjä näkee sovellukseen lisätyt ilmoitukset.
- Käyttäjä pystyy tykkäämään ilmoituksista.
- Käyttäjä pystyy etsimään ilmoituksia hakusanoilla.
- Käyttäjä pystyy antamaan arvosanan (1-5) toiselle käyttäjälle, jos on asioinut tämän kanssa.
- Sovelluksessa on käyttäjäsivut, jotka näyttävät tilastoja (esim. käyttäjän arvosanoihin perustuvan luokituksen) ja käyttäjän lisäämät ilmoitukset.
- Käyttäjä pystyy valitsemaan ilmoitukselle yhden tai useamman, tietokannasta löytyvän luokittelun.
- Käyttäjä pystyy lähettämään tarjouksia kohteista.
- Käyttäjä pystyy kyväksymään/hylkäämään tarjouksia.

Sovelluksen pääasiallinen tietokohde on asuntoilmoitus ja toissijainen on luokittelu.

RENTER sovelluksen kautta käyttäjä pystyy luomaaan ilmoituksen vuokrattavasta kohteesta. Käyttäjät voivat tykätä sekä lähettämään tarjouksia kohteista. Lähetetyn tarjouksen jälkeen vuokranantaja voi joko hyväksyä tai hylätä tarjouksen. Hyväksytyn tarjouksen jälkeen vuokralainen voi edellen perua tarjouksen, mutta jos hän hyväksyy sen vuokrasuhde voi alkaa. Hyväksytyn tarjouksen jälkeen molemmat osapuolet näkevät toistensa yhteystiedot sekä hakemuksessa että toisen käyttäjän omilla sivuilla. Jokaisella käyttäjällä on myös luokitus (1-5 tähteä), joka perustuu muiden käyttäjien antamiin arvosanoihin. Hyväksytyn tarjouksen jälkeen molemmat osapuolet voivat antaa arvosanan toisilleen. Kyseinen toiminnallisuus pysyy auki koko vuokrasuhteen ajan, jotta käyttäjä voi vielä muokata antamaansa arvosanaa.

## Sovelluksen asennus
Asenna `flask`-kirjasto:
```bash
pip install flask
```
Luo tietokannan taulut ja lisää alkutiedot
```bash
sqlite3 database.db < schema.sql
sqlite3 database.db < init.sql
```
Käynnistä sovellus
```bash
flask run
```

## Sovelluksen testaus suurella tietomäärällä
Sovellusta testattiin seed.py tiedostoa käyttäen seuraavilla tietomäärillä:

| Taulu | Rivejä |
|---|---|
| Käyttäjiä | 1 000 |
| Ilmoituksia | 10 000 |
| Tarjouksia| ~20 000 |
| Tykkäyksiä | ~50 000 |

### Tulokset
Kaikki operaatiot suoriutuvat alle 0.1 sekunnissa. Operaatiot ovat lähestulkoon välittömiä myös suurella tietomäärällä, lukuunottamatta rekisteröintiä/kirjautumista jonka kesto oli 0.08 sekuntia johtuen salasanahashauksesta. Alla näkyy miten sovellus suoriutui testistä:

| Operaatio | Tarkennus | Aika |
|---|---|---|
| POST /create_account | Rekisteröinti & kirjautuminen | 0.08 s |
| GET / (sivu 1) | Etusivu sivutetuilla hakutuloksilla | 0.02 s |
| GET /2 (sivu 2) | Etusivu sivutus 2 | 0.01 s |
| GET /search_listings | Lomake hakuehdoilla | 0.03 s |
| GET /search_listings | Haku ilman rajoituksia | 0.01 s |
| GET /search_listings?municipality_id=23 | Haku yhdellä rajauksella | 0.01 s |
| GET /listing/9683 | Vuokrakohteen sivu | 0.04 s |
| GET /listing/9683?edit_offer=1 | Vuokrakohteen tarjoussivu | 0.01 s |
| POST /create_offer | Tarjouksen lähetys | 0.01 s |
| GET /user/1001 | Käyttäjäsivu | 0.05 s |

```bash
 * Running
Press CTRL+C to quit
elapsed time: 0.02 s
127.0.0.1 - - [28/Apr/2026 17:40:45] "GET / HTTP/1.1" 200 -
elapsed time: 0.0 s
127.0.0.1 - - [28/Apr/2026 17:40:45] "GET /static/main.css HTTP/1.1" 304 -
elapsed time: 0.0 s
127.0.0.1 - - [28/Apr/2026 17:40:52] "GET /register HTTP/1.1" 200 -
elapsed time: 0.0 s
127.0.0.1 - - [28/Apr/2026 17:40:52] "GET /static/main.css HTTP/1.1" 304 -
elapsed time: 0.08 s
127.0.0.1 - - [28/Apr/2026 17:41:05] "POST /create_account HTTP/1.1" 302 -
elapsed time: 0.0 s
127.0.0.1 - - [28/Apr/2026 17:41:05] "GET / HTTP/1.1" 200 -
elapsed time: 0.0 s
127.0.0.1 - - [28/Apr/2026 17:41:05] "GET /static/main.css HTTP/1.1" 304 -
elapsed time: 0.01 s
127.0.0.1 - - [28/Apr/2026 17:41:39] "GET /2 HTTP/1.1" 200 -
elapsed time: 0.0 s
127.0.0.1 - - [28/Apr/2026 17:41:39] "GET /static/main.css HTTP/1.1" 304 -
elapsed time: 0.03 s
127.0.0.1 - - [28/Apr/2026 17:41:44] "GET /search_listings HTTP/1.1" 200 -
elapsed time: 0.0 s
127.0.0.1 - - [28/Apr/2026 17:41:44] "GET /static/main.css HTTP/1.1" 304 -
elapsed time: 0.01 s
127.0.0.1 - - [28/Apr/2026 17:41:45] "GET /search_listings?property_type_id=&municipality_id=&min_rent=&max_rent=&size=&rooms_id=&condition_id=&rating= HTTP/1.1" 200 -
elapsed time: 0.0 s
127.0.0.1 - - [28/Apr/2026 17:41:45] "GET /static/main.css HTTP/1.1" 304 -
elapsed time: 0.02 s
127.0.0.1 - - [28/Apr/2026 17:41:52] "GET /search_listings?edit_search=1 HTTP/1.1" 200 -
elapsed time: 0.0 s
127.0.0.1 - - [28/Apr/2026 17:41:52] "GET /static/main.css HTTP/1.1" 304 -
elapsed time: 0.01 s
127.0.0.1 - - [28/Apr/2026 17:41:57] "GET /search_listings?property_type_id=&municipality_id=23&min_rent=&max_rent=&size=&rooms_id=&condition_id=&rating= HTTP/1.1" 200 -
elapsed time: 0.0 s
127.0.0.1 - - [28/Apr/2026 17:41:57] "GET /static/main.css HTTP/1.1" 304 -
elapsed time: 0.04 s
127.0.0.1 - - [28/Apr/2026 17:44:46] "GET /listing/9683 HTTP/1.1" 200 -
elapsed time: 0.0 s
127.0.0.1 - - [28/Apr/2026 17:44:46] "GET /static/main.css HTTP/1.1" 304 -
elapsed time: 0.01 s
127.0.0.1 - - [28/Apr/2026 17:44:48] "GET /listing/9683?edit_offer=1 HTTP/1.1" 200 -
elapsed time: 0.0 s
127.0.0.1 - - [28/Apr/2026 17:44:49] "GET /static/main.css HTTP/1.1" 304 -
elapsed time: 0.01 s
127.0.0.1 - - [28/Apr/2026 17:44:58] "POST /create_offer HTTP/1.1" 302 -
elapsed time: 0.01 s
127.0.0.1 - - [28/Apr/2026 17:44:58] "GET /listing/9683 HTTP/1.1" 200 -
elapsed time: 0.0 s
127.0.0.1 - - [28/Apr/2026 17:44:58] "GET /static/main.css HTTP/1.1" 304 -
elapsed time: 0.05 s
127.0.0.1 - - [28/Apr/2026 17:46:05] "GET /user/1001 HTTP/1.1" 200 -
elapsed time: 0.0 s
127.0.0.1 - - [28/Apr/2026 17:46:05] "GET /static/main.css HTTP/1.1" 304 -
```