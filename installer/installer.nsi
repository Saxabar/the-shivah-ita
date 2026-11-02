Unicode true
!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "grafica.nsh"

!define NAME "The Shivah - Traduzione Italiana"
!define VERSION "1.1"
!define UNKEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\Shivah_ITA"
!define GAMEDIR "steamapps\common\Shivah"
!define TRA "Italiano_senza_accenti"

Name "${NAME}"
OutFile "Shivah_Traduzione_Italiana_Setup.exe"
RequestExecutionLevel admin
SetCompressor /SOLID lzma
InstallDir "$PROGRAMFILES32\Steam\${GAMEDIR}"

VIProductVersion "${VERSION}.0.0"
VIAddVersionKey "ProductName" "${NAME}"
VIAddVersionKey "FileDescription" "${NAME}"
VIAddVersionKey "FileVersion" "${VERSION}"
VIAddVersionKey "LegalCopyright" "Traduzione amatoriale"

!define MUI_ABORTWARNING
!define MUI_WELCOMEPAGE_TITLE "Traduzione italiana di The Shivah"
!define MUI_WELCOMEPAGE_TEXT "Questo programma installa la traduzione italiana (amatoriale, non ufficiale) di The Shivah.$\r$\n$\r$\nSono tradotti sottotitoli, dialoghi, menu e testi del gioco, e alcune scritte grafiche; le voci restano in inglese.$\r$\n$\r$\nLa traduzione viene attivata in acsetup.cfg. Le scritte grafiche vengono corrette dentro Shivah.exe. Delle copie dei file originali vengono salvate come acsetup.cfg.bak_ita e Shivah.exe.bak_ita.$\r$\n$\r$\nChiudi il gioco prima di continuare."
!define MUI_FINISHPAGE_TITLE "Installazione completata"
!define MUI_FINISHPAGE_TEXT "Avvia il gioco: i testi saranno in italiano.$\r$\n$\r$\nI font del gioco non hanno le lettere accentate, per questo è attiva la versione con l'apostrofo (e', perche'). Per cambiare lingua usa winsetup.exe nella cartella del gioco.$\r$\n$\r$\nSe Steam verifica l'integrità dei file o aggiorna il gioco, la traduzione può essere disattivata: basta reinstallarla."

!insertmacro MUI_PAGE_WELCOME
!define MUI_PAGE_CUSTOMFUNCTION_LEAVE CheckDir
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "Italian"

Function .onInit
  ; Look for the Steam folder in the registry
  ReadRegStr $0 HKCU "Software\Valve\Steam" "SteamPath"
  ${If} $0 != ""
    ${If} ${FileExists} "$0\${GAMEDIR}\Shivah.exe"
      StrCpy $INSTDIR "$0\${GAMEDIR}"
    ${EndIf}
  ${EndIf}
  ; Look in the most common Steam libraries on other drives
  ${IfNot} ${FileExists} "$INSTDIR\Shivah.exe"
    ${ForEach} $2 67 90 + 1
      IntFmt $1 "%c" $2
      ${If} ${FileExists} "$1:\SteamLibrary\${GAMEDIR}\Shivah.exe"
        StrCpy $INSTDIR "$1:\SteamLibrary\${GAMEDIR}"
        ${Break}
      ${EndIf}
      ${If} ${FileExists} "$1:\STEAM\${GAMEDIR}\Shivah.exe"
        StrCpy $INSTDIR "$1:\STEAM\${GAMEDIR}"
        ${Break}
      ${EndIf}
    ${Next}
  ${EndIf}
FunctionEnd

Function CheckDir
  ${IfNot} ${FileExists} "$INSTDIR\Shivah.exe"
  ${OrIfNot} ${FileExists} "$INSTDIR\speech.vox"
    MessageBox MB_ICONEXCLAMATION "La cartella selezionata non sembra quella di The Shivah (manca Shivah.exe o speech.vox).$\r$\nSeleziona la cartella di installazione del gioco."
    Abort
  ${EndIf}
FunctionEnd

; --- Graphics patch -----------------------------------------------------------
; The translated sprites keep their size, so the patch overwrites byte ranges of
; Shivah.exe (see grafica.nsh). Adler-32 over those ranges tells the original
; executable from the patched one; any other version is left untouched.

!macro GFX_FUNCTIONS UN
  ; Adler-32 step over one range. In: offset, length on the stack; $R0 = exe handle.
  Function ${UN}GfxAdlerRange
    Pop $R4
    Pop $R3
    FileSeek $R0 $R3 SET
    loop:
      FileReadByte $R0 $R5
      IntOp $R1 $R1 + $R5
      IntOp $R1 $R1 % 65521
      IntOp $R2 $R2 + $R1
      IntOp $R2 $R2 % 65521
      IntOp $R4 $R4 - 1
      IntCmp $R4 0 0 0 loop
  FunctionEnd

  ; Returns in $R8: "orig", "new" or "other" for $INSTDIR\Shivah.exe
  Function ${UN}GfxState
    StrCpy $R8 "other"
    ClearErrors
    FileOpen $R0 "$INSTDIR\Shivah.exe" r
    IfErrors done
    FileSeek $R0 0 END $R7
    ${If} $R7 == ${GFX_EXE_SIZE}
      StrCpy $R1 1
      StrCpy $R2 0
      !insertmacro GFX_RANGES ${UN}GFX_ADLER
      ${If} $R1 == ${GFX_ORIG_A}
      ${AndIf} $R2 == ${GFX_ORIG_S}
        StrCpy $R8 "orig"
      ${ElseIf} $R1 == ${GFX_NEW_A}
      ${AndIf} $R2 == ${GFX_NEW_S}
        StrCpy $R8 "new"
      ${EndIf}
    ${EndIf}
    FileClose $R0
    done:
  FunctionEnd
!macroend

!macro GFX_ADLER OFF LEN
  Push ${OFF}
  Push ${LEN}
  Call GfxAdlerRange
!macroend

!macro un.GFX_ADLER OFF LEN
  Push ${OFF}
  Push ${LEN}
  Call un.GfxAdlerRange
!macroend

; Copy one range from the patch data ($R6) into the exe ($R0)
!macro GFX_WRITE OFF LEN
  Push ${OFF}
  Push ${LEN}
  Call GfxWriteRange
!macroend

Function GfxWriteRange
  Pop $R4
  Pop $R3
  FileSeek $R0 $R3 SET
  loop:
    FileReadByte $R6 $R5
    FileWriteByte $R0 $R5
    IntOp $R4 $R4 - 1
    IntCmp $R4 0 0 0 loop
FunctionEnd

!insertmacro GFX_FUNCTIONS ""
!insertmacro GFX_FUNCTIONS "un."

Function PatchGraphics
  Call GfxState
  ${If} $R8 == "new"
    DetailPrint "Scritte grafiche già tradotte in Shivah.exe."
    Return
  ${EndIf}
  ${If} $R8 != "orig"
    DetailPrint "Shivah.exe è di una versione diversa: scritte grafiche non tradotte."
    MessageBox MB_ICONINFORMATION "Shivah.exe non corrisponde alla versione per cui è stata preparata la traduzione delle scritte grafiche, quindi non viene modificato.$\r$\n$\r$\nI testi del gioco sono comunque tradotti." /SD IDOK
    Return
  ${EndIf}
  ${IfNot} ${FileExists} "$INSTDIR\Shivah.exe.bak_ita"
    DetailPrint "Backup di Shivah.exe in Shivah.exe.bak_ita..."
    CopyFiles /SILENT "$INSTDIR\Shivah.exe" "$INSTDIR\Shivah.exe.bak_ita"
  ${EndIf}
  DetailPrint "Traduzione delle scritte grafiche in Shivah.exe..."
  InitPluginsDir
  File "/oname=$PLUGINSDIR\grafica.bin" "files\grafica.bin"
  FileOpen $R6 "$PLUGINSDIR\grafica.bin" r
  FileOpen $R0 "$INSTDIR\Shivah.exe" a
  !insertmacro GFX_RANGES GFX_WRITE
  FileClose $R0
  FileClose $R6
  Call GfxState
  ${If} $R8 != "new"
    DetailPrint "Verifica fallita: ripristino di Shivah.exe..."
    CopyFiles /SILENT "$INSTDIR\Shivah.exe.bak_ita" "$INSTDIR\Shivah.exe"
    MessageBox MB_ICONEXCLAMATION "Non è stato possibile tradurre le scritte grafiche: Shivah.exe è stato ripristinato.$\r$\n$\r$\nI testi del gioco sono comunque tradotti." /SD IDOK
  ${EndIf}
FunctionEnd

Section "Installa"
  SetOutPath "$INSTDIR"
  ; Back up the original configuration (first time only)
  ${If} ${FileExists} "$INSTDIR\acsetup.cfg"
  ${AndIfNot} ${FileExists} "$INSTDIR\acsetup.cfg.bak_ita"
    DetailPrint "Backup di acsetup.cfg in acsetup.cfg.bak_ita..."
    CopyFiles /SILENT "$INSTDIR\acsetup.cfg" "$INSTDIR\acsetup.cfg.bak_ita"
  ${EndIf}

  DetailPrint "Copia dei file italiani..."
  File "files\Italiano.tra"
  File "files\Italiano_senza_accenti.tra"

  DetailPrint "Attivazione della traduzione..."
  WriteINIStr "$INSTDIR\acsetup.cfg" "language" "translation" "${TRA}"
  ; The user configuration written by winsetup.exe overrides the game folder one
  ${If} ${FileExists} "$PROFILE\Saved Games\Shivah\acsetup.cfg"
    WriteINIStr "$PROFILE\Saved Games\Shivah\acsetup.cfg" "language" "translation" "${TRA}"
  ${EndIf}

  Call PatchGraphics

  WriteUninstaller "$INSTDIR\Disinstalla_Traduzione_Italiana.exe"
  WriteRegStr HKLM "${UNKEY}" "DisplayName" "${NAME}"
  WriteRegStr HKLM "${UNKEY}" "DisplayVersion" "${VERSION}"
  WriteRegStr HKLM "${UNKEY}" "UninstallString" "$\"$INSTDIR\Disinstalla_Traduzione_Italiana.exe$\""
  WriteRegStr HKLM "${UNKEY}" "InstallLocation" "$INSTDIR"
  WriteRegStr HKLM "${UNKEY}" "Publisher" "Traduzione amatoriale"
  WriteRegDWORD HKLM "${UNKEY}" "NoModify" 1
  WriteRegDWORD HKLM "${UNKEY}" "NoRepair" 1
SectionEnd

Section "Uninstall"
  DetailPrint "Disattivazione della traduzione..."
  DeleteINIStr "$INSTDIR\acsetup.cfg" "language" "translation"
  ${If} ${FileExists} "$PROFILE\Saved Games\Shivah\acsetup.cfg"
    DeleteINIStr "$PROFILE\Saved Games\Shivah\acsetup.cfg" "language" "translation"
  ${EndIf}
  Delete "$INSTDIR\Italiano.tra"
  Delete "$INSTDIR\Italiano_senza_accenti.tra"
  Delete "$INSTDIR\acsetup.cfg.bak_ita"

  ; Restore Shivah.exe only if it is still the one patched by this installer;
  ; otherwise (Steam verify or update) the backup is stale and is just removed.
  ${If} ${FileExists} "$INSTDIR\Shivah.exe.bak_ita"
    Call un.GfxState
    ${If} $R8 == "new"
      DetailPrint "Ripristino di Shivah.exe originale..."
      Delete "$INSTDIR\Shivah.exe"
      Rename "$INSTDIR\Shivah.exe.bak_ita" "$INSTDIR\Shivah.exe"
    ${Else}
      Delete "$INSTDIR\Shivah.exe.bak_ita"
    ${EndIf}
  ${EndIf}
  Delete "$INSTDIR\Disinstalla_Traduzione_Italiana.exe"
  DeleteRegKey HKLM "${UNKEY}"
SectionEnd
