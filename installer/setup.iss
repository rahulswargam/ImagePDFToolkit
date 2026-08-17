; Inno Setup script for FileForge Toolkit.
; Build with: ISCC installer\setup.iss  (run from the project root)
; Produces:   dist\FileForgeToolkit-Setup.exe

#define MyAppName "FileForge Toolkit"
#define MyAppPublisher "Rahul Swargam"
#define VersionFile FileOpen(SourcePath + "..\VERSION")
#define MyAppVersion Trim(FileRead(VersionFile))
#expr FileClose(VersionFile)
#define MyAppExeName "FileForgeToolkit.exe"
#define MyOldAppExeName "ImagePDFToolkit.exe"
#define MyAppCopyright "Copyright © 2026 Rahul Swargam"

[Setup]
AppId={{6B2E6C7B-6E7C-4E1E-9C7C-6B2E6C7B6E7C}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppCopyright={#MyAppCopyright}
AppComments={#MyAppName} — fast, private, offline image and PDF tools.
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\dist
OutputBaseFilename=FileForgeToolkit-Setup
SetupIconFile=..\assets\icons\app.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} Setup
VersionInfoProductName={#MyAppName}
VersionInfoCopyright={#MyAppCopyright}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"

; Upgrading users had "ImagePDFToolkit.exe" installed under the old name.
; The AppId stays the same (so this upgrade lands in the same directory),
; but the exe itself is now named "FileForgeToolkit.exe" — clean up the
; stale old-named file so it doesn't linger as an orphan.
[InstallDelete]
Type: files; Name: "{app}\{#MyOldAppExeName}"

[Files]
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "downloads\vc_redist.x64.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall skipifsourcedoesntexist

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{tmp}\vc_redist.x64.exe"; Parameters: "/install /quiet /norestart"; StatusMsg: "Installing required Windows components..."; Check: VCRedistNeedsInstall; Flags: waituntilterminated
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent

[Code]
function VCRedistNeedsInstall(): Boolean;
var
  Installed: Cardinal;
begin
  Result := True;
  if RegQueryDWordValue(HKLM64, 'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\X64', 'Installed', Installed) then
  begin
    if Installed = 1 then
      Result := False;
  end;
end;
