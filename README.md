# The Shivah – Traduzione italiana

Traduzione italiana **amatoriale e non ufficiale** di [The Shivah](https://store.steampowered.com/app/252370/The_Shivah/), l'avventura punta e clicca di Wadjet Eye Games.

Sono tradotti circa 1.980 testi:

- **Sottotitoli** dei dialoghi e **narrazione**.
- **Opzioni di dialogo.**
- **Nomi di oggetti, hotspot e inventario.**
- **Email, giornale e ricerche di Ravnet**, registro contabile.
- **Barzellette** di Ravnet.
- **Obiettivi**, **menu** e **titoli di coda**.
- **Scritte grafiche** (dalla versione 1.1): la linguetta *INDIZI*, le etichette degli indizi, i pulsanti *Conti* e *Posta* del computer di Jack e la barzelletta della schermata del titolo.

Le voci restano in inglese.

> ⚠️ I font del gioco non hanno le lettere accentate. Per questo è attiva la versione **senza accenti**, che le scrive con l'apostrofo (e', perche'). È inclusa anche la versione con gli accenti veri, ma con i font originali gli accenti compaiono come quadratini.

---

## Installazione

### Metodo 1: installer (consigliato)

1. Scarica `Shivah_Traduzione_Italiana_Setup.exe` dalla pagina [**Releases**](../../releases).
2. Chiudi il gioco ed esegui l'installer.
   - Windows potrebbe mostrare l'avviso "PC protetto" (SmartScreen), perché l'eseguibile non è firmato digitalmente. In quel caso clicca **Ulteriori informazioni**, poi **Esegui comunque**.
3. L'installer cerca da solo la cartella del gioco: guarda nel percorso di Steam e nelle librerie più comuni. Se non la trova, selezionala a mano.
   - Di solito è `...\steamapps\common\Shivah`.
4. Avvia il gioco.

L'installer fa queste cose:

- Copia `Italiano_senza_accenti.tra` e `Italiano.tra` nella cartella del gioco.
- La prima volta salva una copia di `acsetup.cfg` come `acsetup.cfg.bak_ita`.
- Attiva la traduzione in `acsetup.cfg`.
- Traduce le scritte grafiche dentro `Shivah.exe`, dopo averne salvato una copia come `Shivah.exe.bak_ita`. Lo fa solo se `Shivah.exe` è proprio la versione per cui la patch è stata preparata (la versione Steam attuale). Altrimenti lascia l'eseguibile com'è e installa solo i testi.
- Crea il programma di disinstallazione `Disinstalla_Traduzione_Italiana.exe`. Lo trovi anche in *Impostazioni di Windows → App installate*.

### Metodo 2: installazione manuale

1. Copia i file di [`installer/files/`](installer/files) nella cartella del gioco, accanto a `Shivah.exe`.
2. Avvia `winsetup.exe`, scegli la lingua **Italiano_senza_accenti** e salva. In alternativa aggiungi in fondo ad `acsetup.cfg`:

   ```
   [language]
   translation=Italiano_senza_accenti
   ```

3. Avvia il gioco.

Con l'installazione manuale le scritte grafiche restano in inglese: per tradurle serve l'installer, che modifica `Shivah.exe`.

## Disinstallazione

- Esegui `Disinstalla_Traduzione_Italiana.exe` dalla cartella del gioco, oppure da *App installate* di Windows. Disattiva la traduzione, cancella i file `.tra` e rimette al suo posto il `Shivah.exe` originale.
- In alternativa scegli la lingua predefinita in `winsetup.exe`, cancella i file `.tra` e usa la verifica dei file di Steam per ripristinare `Shivah.exe`.

> ℹ️ La verifica dei file di Steam, o un aggiornamento del gioco, può riportare `acsetup.cfg` e `Shivah.exe` all'originale e disattivare la traduzione. In quel caso basta reinstallarla.

---

## Limitazioni note

- **Lettere accentate:** vedi sopra. La versione attiva usa l'apostrofo.
- **Testi nelle immagini:** sono tradotte le scritte grafiche elencate sopra. Per farle stare nello spazio originale alcune sono abbreviate: *Conti* (Ledger), *Joe e Ethan* (Joe's Meeting), *Joe ebreo?* (Joe Jewish?). La linguetta *INV* resta così, e restano in inglese i nomi propri e gli indirizzi sulla mappa.
- **Ricerche di Ravnet:** le parole da cercare (cognomi, nomi di luoghi) restano quelle originali, perché il gioco le confronta con il testo inglese.
- **Prove nel gioco:** la traduzione non è ancora stata provata da cima a fondo. Le segnalazioni sono benvenute.

## Segnalare errori

Apri una [**Issue**](../../issues) indicando:

- il testo sbagliato;
- in quale scena compare;
- se possibile, uno screenshot.

---

## Struttura del repository

```
traduzione/
  italiano.tsv          testi italiani (chiave hash del testo inglese, TAB, traduzione)
installer/
  installer.nsi         sorgente dell'installer (NSIS 3)
  grafica.nsh           zone di Shivah.exe da modificare e checksum (generato)
  files/                file pronti da copiare nella cartella del gioco
    Italiano.tra
    Italiano_senza_accenti.tra
    grafica.bin         pixel delle scritte grafiche tradotte (usato dall'installer)
strumenti/
  genera.py             rigenera i file .tra da una copia del gioco
  extract.py            estrae i testi dal gioco
  tsv.py                applica italiano.tsv ai testi estratti
  build.py              compila i file .trs/.tra
  agsdata.py            lettura dei file di AGS
  show.py, addstring.py strumenti di lavoro per la traduzione
  grafica/
    genera_patch.py     rigenera grafica.bin e grafica.nsh da Shivah.exe originale
    graphics.py         raccoglie le scritte ridisegnate
    tabpatch.py         linguetta INDIZI
    clues.py            etichette degli indizi
    buttons.py          pulsanti Conti e Posta (usa render.ps1 e il font Georgia di Windows)
    joke.py             barzelletta del titolo
    spr.py              lettura del file degli sprite (acsprset.spr)
```

## Note tecniche

The Shivah usa il motore Adventure Game Studio (AGS 3.6.1), che carica le traduzioni da file `.tra` messi accanto all'eseguibile. Un file `.tra` contiene coppie *testo originale → testo tradotto*: il motore sostituisce ogni testo mostrato a schermo con la sua traduzione.

`traduzione/italiano.tsv` contiene solo i testi italiani. Ogni riga è associata al testo inglese tramite i primi 12 caratteri dell'hash SHA-1 del testo originale. Così il repository non contiene il testo inglese del gioco: `strumenti/genera.py` lo estrae dalla copia del gioco di chi lo usa e ricompila i file `.tra`.

```
python strumenti/genera.py "C:\...\steamapps\common\Shivah\Shivah.exe" uscita
```

Serve Python 3 e una copia originale del gioco. Il risultato contiene 1975 traduzioni su 1976: manca solo "Wait", un testo interno che l'estrattore non trova.

Le scritte grafiche sono sprite dentro l'archivio dei dati, che è attaccato in fondo a `Shivah.exe`. Gli sprite interessati non sono compressi e quelli tradotti hanno le stesse dimensioni degli originali, quindi la patch sovrascrive solo i loro pixel (14 sprite, circa 9.800 byte) senza spostare niente nell'archivio. Le lettere sono prese dai font pixel del gioco stesso; le poche che mancavano (D e Z della linguetta, U, P e l'accento della barzelletta) sono disegnate nello stesso stile.

L'installer riconosce l'eseguibile originale e quello già tradotto con un checksum Adler-32 calcolato sulle sole zone da modificare, così non deve contenere i pixel originali del gioco. Per rigenerare la patch:

```
python strumenti/grafica/genera_patch.py "C:\...\steamapps\common\Shivah\Shivah.exe"
```

Il formato dei file di AGS segue la documentazione di [AGSUnpacker](https://github.com/adm244/AGSUnpacker).

Per ricompilare l'installer: `makensis installer/installer.nsi`.

---

## Avvertenze legali

Questo è un progetto amatoriale, senza scopo di lucro, non affiliato né approvato da Wadjet Eye Games.

*The Shivah* e tutti i relativi marchi e contenuti appartengono ai rispettivi proprietari. Per usare questa traduzione serve una copia originale del gioco.
