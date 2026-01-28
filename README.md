# RENTER
## Sovelluksen toiminnot

-   Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
- Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan ilmoituksia.
- Käyttäjä pystyy lisäämään kuvia ilmoitukseen.
- Käyttäjä näkee sovellukseen lisätyt ilmoitukset.
- Käyttäjä pystyy etsimään ilmoituksia hakusananalla.
- Käyttäjä pystyy antamaan arvosanan (1-5) toiselle käyttäjälle, jos on asioinut tämän kanssa.
- Sovelluksessa on käyttäjäsivut, jotka näyttävät tilastoja (esim. käyttäjän arvosanoihin perustuvan luokituksen) ja käyttäjän lisäämät ilmoitukset.
- Käyttäjä pystyy valitsemaan ilmoitukselle yhden tai useamman, tietokannasta löytyvän luokittelun (esim. sijainti, luokitus).

Sovelluksen pääasiallinen tietokohde on asuntoilmoitus ja toissijainen on luokittelu.

## Sovelluksen asennus
Asenna `flask`-kirjasto:
```bash
pip install flask
```
Luo tietokannan taulut ja lisää alkutiedot
```bash
sqlite3 database.db < schema.sql
```
Käynnistä sovellus
```bash
flask run
```