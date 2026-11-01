# The Shivah – Traduzione italiana

Traduzione italiana **amatoriale e non ufficiale** di [The Shivah](https://store.steampowered.com/app/252370/The_Shivah/), l'avventura punta e clicca di Wadjet Eye Games.

Sono tradotti circa 1.980 testi:

- **Sottotitoli** dei dialoghi e **narrazione**.
- **Opzioni di dialogo.**
- **Nomi di oggetti, hotspot e inventario.**
- **Email, giornale e ricerche di Ravnet**, registro contabile.
- **Barzellette** di Ravnet.
- **Obiettivi**, **menu** e **titoli di coda**.

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
- Crea il programma di disinstallazione `Disinstalla_Traduzione_Italiana.exe`. Lo trovi anche in *Impostazioni di Windows → App installate*.

### Metodo 2: installazione manuale

1. Copia i file di [`installer/files/`](installer/files) nella cartella del gioco, accanto a `Shivah.exe`.
2. Avvia `winsetup.exe`, scegli la lingua **Italiano_senza_accenti** e salva. In alternativa aggiungi in fondo ad `acsetup.cfg`:

   ```
   [language]
   translation=Italiano_senza_accenti
   ```

3. Avvia il gioco.

## Disinstallazione

- Esegui `Disinstalla_Traduzione_Italiana.exe` dalla cartella del gioco, oppure da *App installate* di Windows. Disattiva la traduzione e cancella i file `.tra`.
- In alternativa scegli la lingua predefinita in `winsetup.exe` e cancella i file `.tra`.

> ℹ️ La verifica dei file di Steam, o un aggiornamento del gioco, può riportare `acsetup.cfg` all'originale e disattivare la traduzione. In quel caso basta reinstallarla.

---

## Limitazioni note

- **Lettere accentate:** vedi sopra. La versione attiva usa l'apostrofo.
- **Testi nelle immagini:** le scritte disegnate nella grafica non sono tradotte.
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
  files/                file pronti da copiare nella cartella del gioco
    Italiano.tra
    Italiano_senza_accenti.tra
strumenti/
  genera.py             rigenera i file .tra da una copia del gioco
  extract.py            estrae i testi dal gioco
  tsv.py                applica italiano.tsv ai testi estratti
  build.py              compila i file .trs/.tra
  agsdata.py            lettura dei file di AGS
  show.py, addstring.py strumenti di lavoro per la traduzione
```

## Note tecniche

The Shivah usa il motore Adventure Game Studio (AGS 3.6.1), che carica le traduzioni da file `.tra` messi accanto all'eseguibile. Un file `.tra` contiene coppie *testo originale → testo tradotto*: il motore sostituisce ogni testo mostrato a schermo con la sua traduzione.

`traduzione/italiano.tsv` contiene solo i testi italiani. Ogni riga è associata al testo inglese tramite i primi 12 caratteri dell'hash SHA-1 del testo originale. Così il repository non contiene il testo inglese del gioco: `strumenti/genera.py` lo estrae dalla copia del gioco di chi lo usa e ricompila i file `.tra`.

```
python strumenti/genera.py "C:\...\steamapps\common\Shivah\Shivah.exe" uscita
```

Serve Python 3 e una copia originale del gioco. Il risultato contiene 1975 traduzioni su 1976: manca solo "Wait", un testo interno che l'estrattore non trova.

Il formato dei file di AGS segue la documentazione di [AGSUnpacker](https://github.com/adm244/AGSUnpacker).

Per ricompilare l'installer: `makensis installer/installer.nsi`.

---

## Avvertenze legali

Questo è un progetto amatoriale, senza scopo di lucro, non affiliato né approvato da Wadjet Eye Games.

*The Shivah* e tutti i relativi marchi e contenuti appartengono ai rispettivi proprietari. Per usare questa traduzione serve una copia originale del gioco.
