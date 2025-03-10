; Configurações básicas
Name "WhatsApp Scheduler"
OutFile "WhatsAppScheduler_Setup.exe"
InstallDir "$PROGRAMFILES\WhatsApp Scheduler"
RequestExecutionLevel admin

; Páginas do instalador
Page directory
Page instfiles

; Página de desinstalação
UninstPage uninstConfirm
UninstPage instfiles

; Seção principal de instalação
Section "Principal"
    SetOutPath "$INSTDIR"
    
    ; Arquivos principais
    File "dist\WhatsAppScheduler.exe"
    
    ; Criar diretório para templates
    SetOutPath "$INSTDIR\templates"
    File /r "templates\*.*"
    
    ; Criar diretório para assets
    SetOutPath "$INSTDIR\assets"
    File /r "assets\*.*"
    
    ; Criar diretório de dados no AppData
    CreateDirectory "$APPDATA\WhatsAppScheduler"
    CreateDirectory "$APPDATA\WhatsAppScheduler\data"
    CreateDirectory "$APPDATA\WhatsAppScheduler\logs"
    
    ; Copiar ícone para AppData
    SetOutPath "$APPDATA\WhatsAppScheduler"
    File "assets\whatsapp_icon.png"
    
    ; Criar atalhos
    CreateDirectory "$SMPROGRAMS\WhatsApp Scheduler"
    CreateShortcut "$SMPROGRAMS\WhatsApp Scheduler\WhatsApp Scheduler.lnk" "$INSTDIR\WhatsAppScheduler.exe"
    CreateShortcut "$DESKTOP\WhatsApp Scheduler.lnk" "$INSTDIR\WhatsAppScheduler.exe"
    
    ; Criar desinstalador
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    
    ; Registrar no Windows
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\WhatsAppScheduler" \
                 "DisplayName" "WhatsApp Scheduler"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\WhatsAppScheduler" \
                 "UninstallString" "$\"$INSTDIR\Uninstall.exe$\""
SectionEnd

Section "Uninstall"
    ; Remover arquivos
    Delete "$INSTDIR\WhatsAppScheduler.exe"
    RMDir /r "$INSTDIR\templates"
    RMDir /r "$INSTDIR\assets"
    Delete "$INSTDIR\Uninstall.exe"
    
    ; Remover atalhos
    Delete "$SMPROGRAMS\WhatsApp Scheduler\WhatsApp Scheduler.lnk"
    RMDir "$SMPROGRAMS\WhatsApp Scheduler"
    Delete "$DESKTOP\WhatsApp Scheduler.lnk"
    
    ; Remover registro
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\WhatsAppScheduler"
    
    ; Remover diretório de instalação
    RMDir "$INSTDIR"
    
    ; Perguntar se deseja remover dados do usuário
    MessageBox MB_YESNO "Deseja remover todos os dados do usuário?" IDNO NoRemoveUserData
        RMDir /r "$APPDATA\WhatsAppScheduler"
    NoRemoveUserData:
SectionEnd