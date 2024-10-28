#define MyAppName "Master-W"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Wamphyre"
#define MyAppURL "https://github.com/Wamphyre/Master-W"
#define MyAppExeName "Master-W.exe"

[Setup]
; Configuración básica
AppId={{5D89C9B4-F2A2-4E8B-9C71-DC391A7F9FE2}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=installer
OutputBaseFilename=Master-W-Setup
SetupIconFile=icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64os
ArchitecturesInstallIn64BitMode=x64os
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=Aplicación de masterización de audio por referencia
VersionInfoCopyright=Copyright (C) 2024 {#MyAppPublisher}
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Desinstalar {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
Type: dirifempty; Name: "{app}"

[Code]
var
  ResultCode: Integer;  // Declaramos la variable globalmente

// Verificar si ya existe una instalación previa
function InitializeSetup(): Boolean;
var
  UninstPath: string;
  UninstallString: string;
begin
  Result := True;
  if RegQueryStringValue(HKLM, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppName}_is1',
    'UninstallString', UninstallString) then
  begin
    UninstPath := RemoveQuotes(UninstallString);
    if FileExists(UninstPath) then
    begin
      if MsgBox('Se ha detectado una instalación previa de {#MyAppName}. ' +
        '¿Desea desinstalarla antes de continuar?', mbConfirmation, MB_YESNO) = IDYES then
      begin
        if not Exec(UninstPath, '/SILENT', '', SW_SHOW, ewWaitUntilTerminated, ResultCode) then
        begin
          MsgBox('Error al desinstalar la versión anterior. Código: ' + IntToStr(ResultCode), 
                 mbError, MB_OK);
          Result := False;
        end
        else
        begin
          // Esperar un momento para asegurar que la desinstalación se complete
          Sleep(1000);
          Result := True;
        end;
      end
      else
        Result := False;
    end;
  end;
end;

// Función para eliminar archivos y carpetas residuales durante la desinstalación
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  AppPath: string;
  ReturnCode: Integer;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    AppPath := ExpandConstant('{app}');
    if DirExists(AppPath) then
    begin
      Sleep(500); // Esperar un momento para asegurar que los archivos estén liberados
      DelTree(AppPath, True, True, True);
    end;
      
    // Limpiar carpeta de datos de usuario si existe
    AppPath := ExpandConstant('{localappdata}\{#MyAppName}');
    if DirExists(AppPath) then
    begin
      Sleep(250);
      DelTree(AppPath, True, True, True);
    end;
      
    // Limpiar carpeta de configuración si existe
    AppPath := ExpandConstant('{userappdata}\{#MyAppName}');
    if DirExists(AppPath) then
    begin
      Sleep(250);
      DelTree(AppPath, True, True, True);
    end;
  end;
end;