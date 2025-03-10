@echo off
echo Limpando diretorios anteriores...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

echo Criando executavel...
pyinstaller --noconfirm ^
    --onefile ^
    --windowed ^
    --add-data "templates;templates" ^
    --add-data "assets;assets" ^
    --hidden-import=pywhatkit ^
    --hidden-import=csv ^
    --hidden-import=json ^
    --hidden-import=datetime ^
    --hidden-import=threading ^
    --hidden-import=webbrowser ^
    --hidden-import=flask ^
    --hidden-import=tkinter ^
    --hidden-import=pystray ^
    --hidden-import=keyboard ^
    --hidden-import=PIL ^
    --hidden-import=PIL._tkinter_finder ^
    --hidden-import=plyer ^
    --hidden-import=logging ^
    --hidden-import=pystray._win32 ^
    --hidden-import=pyautogui ^
    --hidden-import=subprocess ^
    --collect-all pywhatkit ^
    --collect-all plyer ^
    --collect-all PIL ^
    --collect-all flask ^
    --collect-data certifi ^
    --copy-metadata pywhatkit ^
    --copy-metadata Pillow ^
    --copy-metadata plyer ^
    --copy-metadata flask ^
    --name "WhatsAppScheduler" ^
    app.py

if errorlevel 1 (
    echo Erro ao criar o executavel!
    pause
    exit /b 1
)

echo Criando instalador...
if exist "C:\Program Files (x86)\NSIS\makensis.exe" (
    "C:\Program Files (x86)\NSIS\makensis.exe" installer.nsi
) else if exist "C:\Program Files\NSIS\makensis.exe" (
    "C:\Program Files\NSIS\makensis.exe" installer.nsi
) else (
    echo NSIS nao encontrado! Certifique-se de que esta instalado.
    pause
    exit /b 1
)

if errorlevel 1 (
    echo Erro ao criar o instalador!
    pause
    exit /b 1
)

echo Build completo!
pause