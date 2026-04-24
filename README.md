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