Unicode true
!include "MUI2.nsh"
!include "LogicLib.nsh"

!define NAME "The Shivah - Traduzione Italiana"
!define VERSION "1.0"
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
!define MUI_WELCOMEPAGE_TEXT "Questo programma installa la traduzione italiana (amatoriale, non ufficiale) di The Shivah.$\r$\n$\r$\nSono tradotti sottotitoli, dialoghi, menu e testi del gioco; le voci restano in inglese.$\r$\n$\r$\nLa traduzione viene attivata in acsetup.cfg; una copia del file originale viene salvata come acsetup.cfg.bak_ita.$\r$\n$\r$\nChiudi il gioco prima di continuare."
!define MUI_FINISHPAGE_TITLE "Installazione completata"
!define MUI_FINISHPAGE_TEXT "Avvia il gioco: i testi saranno in italiano.$\r$\n$\r$\nI font del gioco non hanno le lettere accentate, per questo è attiva la versione con l'apostrofo (e', perche'). Per cambiare lingua usa winsetup.exe nella cartella del gioco.$\r$\n$\r$\nSe Steam verifica l'integrità dei file, la traduzione può essere disattivata: basta reinstallarla."

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
  Delete "$INSTDIR\Disinstalla_Traduzione_Italiana.exe"
  DeleteRegKey HKLM "${UNKEY}"
SectionEnd
