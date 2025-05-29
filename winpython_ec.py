#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WinPython EXE Compiler (WinPythonEC)
Automatyczny kompilator EXE oparty na środowisku WinPython

Autor: Cody (Sourcegraph AI Assistant)
"""

import os
import sys
import subprocess
import shutil
import zipfile
import tempfile
from pathlib import Path
import argparse


class WinPythonEXECompiler:
    def __init__(self):
        self.winpython_path = None
        self.python_exe = None
        self.pip_exe = None
        
    def show_menu(self):
        """Wyświetla menu z opisem działania programu"""
        print("=" * 70)
        print("🐍 WinPython EXE Compiler (WinPythonEC) 🐍")
        print("=" * 70)
        print("DZIAŁANIE:")
        print("Program kompiluje skrypty Python (.py) do samodzielnych plików EXE")
        print("używając środowiska WinPython i PyInstaller.")
        print()
        print("FUNKCJE:")
        print("• Wykorzystuje przenośne środowisko WinPython")
        print("• Automatycznie instaluje PyInstaller jeśli potrzeba")
        print("• Kompiluje w trybie --onefile (jeden plik EXE)")
        print("• Obsługuje dodatkowe biblioteki")
        print("• Pakuje wynik do archiwum ZIP")
        print("• Nie modyfikuje systemowego Pythona")
        print()
        print("ZASTOSOWANIE:")
        print("Idealne do tworzenia aplikacji do dystrybucji bez wymagania")
        print("instalacji Pythona na komputerze docelowym.")
        print("=" * 70)
        print()

    def validate_winpython_path(self, path):
        """Sprawdza czy podana ścieżka to prawidłowe środowisko WinPython"""
        if not os.path.exists(path):
            return False, "Podana ścieżka nie istnieje"
            
        # Szukamy python.exe w różnych możliwych lokalizacjach
        possible_python_paths = [
            os.path.join(path, "python.exe"),
            os.path.join(path, "Scripts", "python.exe"),
            os.path.join(path, "python-3*", "python.exe"),
        ]
        
        # Sprawdzamy również w podfolderach
        for root, dirs, files in os.walk(path):
            if "python.exe" in files:
                python_path = os.path.join(root, "python.exe")
                # Sprawdzamy czy to nie systemowy Python
                if "WinPython" in python_path or path.lower() in python_path.lower():
                    self.python_exe = python_path
                    # Szukamy pip.exe w tym samym folderze lub Scripts
                    pip_path = os.path.join(os.path.dirname(python_path), "Scripts", "pip.exe")
                    if not os.path.exists(pip_path):
                        pip_path = os.path.join(os.path.dirname(python_path), "pip.exe")
                    
                    if os.path.exists(pip_path):
                        self.pip_exe = pip_path
                    else:
                        self.pip_exe = None
                    
                    return True, "Środowisko WinPython znalezione"
        
        return False, "Nie znaleziono python.exe w środowisku WinPython"

    def check_pyinstaller(self):
        """Sprawdza czy PyInstaller jest zainstalowany"""
        try:
            result = subprocess.run([self.python_exe, "-m", "pip", "show", "pyinstaller"], 
                                  capture_output=True, text=True, check=False)
            return result.returncode == 0
        except Exception:
            return False

    def install_pyinstaller(self):
        """Instaluje PyInstaller w środowisku WinPython"""
        print("🔧 PyInstaller nie jest zainstalowany. Instaluję...")
        try:
            if self.pip_exe and os.path.exists(self.pip_exe):
                cmd = [self.pip_exe, "install", "pyinstaller"]
            else:
                cmd = [self.python_exe, "-m", "pip", "install", "pyinstaller"]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            
            if result.returncode == 0:
                print("✅ PyInstaller został pomyślnie zainstalowany")
                return True
            else:
                print(f"❌ Błąd instalacji PyInstaller: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Wyjątek podczas instalacji PyInstaller: {e}")
            return False

    def install_additional_libraries(self, libraries):
        """Instaluje dodatkowe biblioteki"""
        if not libraries:
            return True
            
        print(f"📦 Instaluję dodatkowe biblioteki: {', '.join(libraries)}")
        
        for lib in libraries:
            try:
                if self.pip_exe and os.path.exists(self.pip_exe):
                    cmd = [self.pip_exe, "install", lib]
                else:
                    cmd = [self.python_exe, "-m", "pip", "install", lib]
                
                result = subprocess.run(cmd, capture_output=True, text=True, check=False)
                
                if result.returncode == 0:
                    print(f"✅ {lib} - zainstalowana pomyślnie")
                else:
                    print(f"⚠️  {lib} - błąd instalacji: {result.stderr}")
                    return False
            except Exception as e:
                print(f"❌ Wyjątek podczas instalacji {lib}: {e}")
                return False
        
        return True

    def compile_to_exe(self, script_path, output_dir):
        """Kompiluje skrypt Python do EXE używając PyInstaller"""
        print("🔨 Rozpoczynam kompilację...")
        
        script_name = os.path.splitext(os.path.basename(script_path))[0]
        
        # Przygotowujemy komendę PyInstaller
        cmd = [
            self.python_exe, "-m", "PyInstaller",
            "--onefile",
            "--distpath", output_dir,
            "--workpath", os.path.join(output_dir, "build"),
            "--specpath", os.path.join(output_dir, "spec"),
            script_path
        ]
        
        try:
            print(f"Wykonuję: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            
            if result.returncode == 0:
                exe_path = os.path.join(output_dir, f"{script_name}.exe")
                if os.path.exists(exe_path):
                    print(f"✅ Kompilacja zakończona pomyślnie!")
                    print(f"📁 Plik EXE: {exe_path}")
                    return exe_path
                else:
                    print("❌ Kompilacja zakończona, ale nie znaleziono pliku EXE")
                    return None
            else:
                print(f"❌ Błąd kompilacji:")
                print(f"STDOUT: {result.stdout}")
                print(f"STDERR: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ Wyjątek podczas kompilacji: {e}")
            return None

    def create_zip_package(self, exe_path, output_dir):
        """Tworzy archiwum ZIP z plikiem EXE"""
        if not exe_path or not os.path.exists(exe_path):
            return None
            
        exe_name = os.path.splitext(os.path.basename(exe_path))[0]
        zip_path = os.path.join(output_dir, f"{exe_name}_package.zip")
        
        try:
            print("📦 Tworzę archiwum ZIP...")
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(exe_path, os.path.basename(exe_path))
                
                # Dodajemy plik README
                readme_content = f"""
{exe_name} - Aplikacja Python skompilowana do EXE

Utworzono przy użyciu WinPython EXE Compiler (WinPythonEC)

URUCHOMIENIE:
Wystarczy uruchomić plik {os.path.basename(exe_path)}

WYMAGANIA:
Brak - aplikacja jest samodzielna i nie wymaga instalacji Pythona.

Data utworzenia: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                zipf.writestr("README.txt", readme_content)
            
            print(f"✅ Archiwum utworzone: {zip_path}")
            return zip_path
            
        except Exception as e:
            print(f"❌ Błąd tworzenia archiwum: {e}")
            return None

    def cleanup_build_files(self, output_dir):
        """Usuwa pliki tymczasowe po kompilacji"""
        try:
            build_dir = os.path.join(output_dir, "build")
            spec_dir = os.path.join(output_dir, "spec")
            
            if os.path.exists(build_dir):
                shutil.rmtree(build_dir)
                print("🧹 Usunięto folder build")
                
            if os.path.exists(spec_dir):
                shutil.rmtree(spec_dir)
                print("🧹 Usunięto folder spec")
                
        except Exception as e:
            print(f"⚠️  Nie udało się usunąć plików tymczasowych: {e}")

    def run_interactive(self):
        """Uruchamia program w trybie interaktywnym"""
        self.show_menu()
        
        # Pobieramy ścieżkę do WinPython
        while True:
            winpython_path = input("📁 Podaj ścieżkę do WinPython (np. C:\\WinPython\\WPy64-310111): ").strip()
            if not winpython_path:
                print("❌ Ścieżka nie może być pusta!")
                continue
                
            is_valid, message = self.validate_winpython_path(winpython_path)
            if is_valid:
                self.winpython_path = winpython_path
                print(f"✅ {message}")
                print(f"🐍 Python: {self.python_exe}")
                break
            else:
                print(f"❌ {message}")
                continue
        
        # Pobieramy ścieżkę do skryptu
        while True:
            script_path = input("\n📄 Podaj ścieżkę do skryptu Python (.py): ").strip()
            if not script_path:
                print("❌ Ścieżka nie może być pusta!")
                continue
                
            if not os.path.exists(script_path):
                print("❌ Plik nie istnieje!")
                continue
                
            if not script_path.lower().endswith('.py'):
                print("❌ Plik musi mieć rozszerzenie .py!")
                continue
                
            break
        
        # Dodatkowe biblioteki
        print("\n📚 Dodatkowe biblioteki (opcjonalne)")
        libraries_input = input("Podaj nazwy bibliotek oddzielone spacją (Enter = pomiń): ").strip()
        additional_libraries = libraries_input.split() if libraries_input else []
        
        # Sprawdzamy i instalujemy PyInstaller
        if not self.check_pyinstaller():
            if not self.install_pyinstaller():
                print("❌ Nie udało się zainstalować PyInstaller. Przerywam.")
                return False
        else:
            print("✅ PyInstaller jest już zainstalowany")
        
        # Instalujemy dodatkowe biblioteki
        if additional_libraries:
            if not self.install_additional_libraries(additional_libraries):
                print("⚠️  Niektóre biblioteki nie zostały zainstalowane. Kontynuuję...")
        
        # Przygotowujemy folder wyjściowy
        output_dir = os.path.join(self.winpython_path, "compiled_apps")
        os.makedirs(output_dir, exist_ok=True)
        
        # Kompilujemy
        exe_path = self.compile_to_exe(script_path, output_dir)
        
        if exe_path:
            # Tworzymy archiwum
            zip_path = self.create_zip_package(exe_path, output_dir)
            
            # Sprzątamy
            self.cleanup_build_files(output_dir)
            
            print("\n" + "=" * 50)
            print("🎉 KOMPILACJA ZAKOŃCZONA POMYŚLNIE! 🎉")
            print("=" * 50)
            print(f"📁 Plik EXE: {exe_path}")
            if zip_path:
                print(f"📦 Archiwum: {zip_path}")
            print("=" * 50)
            
            return True
        else:
            print("\n❌ Kompilacja nie powiodła się!")
            return False

    def run_cli(self, args):
        """Uruchamia program z argumentami linii poleceń"""
        # Walidacja WinPython
        is_valid, message = self.validate_winpython_path(args.winpython)
        if not is_valid:
            print(f"❌ {message}")
            return False
            
        self.winpython_path = args.winpython
        print(f"✅ Środowisko WinPython: {self.winpython_path}")
        
        # Walidacja skryptu
        if not os.path.exists(args.script):
            print(f"❌ Skrypt nie istnieje: {args.script}")
            return False
            
        if not args.script.lower().endswith('.py'):
            print("❌ Plik musi mieć rozszerzenie .py!")
            return False
        
        # Sprawdzamy PyInstaller
        if not self.check_pyinstaller():
            if not self.install_pyinstaller():
                return False
        
                # Instalujemy dodatkowe biblioteki
        if args.libraries:
            if not self.install_additional_libraries(args.libraries):
                print("⚠️  Niektóre biblioteki nie zostały zainstalowane.")
        
        # Kompilujemy
        output_dir = os.path.join(self.winpython_path, "compiled_apps")
        os.makedirs(output_dir, exist_ok=True)
        
        exe_path = self.compile_to_exe(args.script, output_dir)
        
        if exe_path:
            # Tworzymy archiwum jeśli nie wyłączono
            zip_path = None
            if not args.no_zip:
                zip_path = self.create_zip_package(exe_path, output_dir)
            
            # Sprzątamy jeśli nie wyłączono
            if not args.keep_build:
                self.cleanup_build_files(output_dir)
            
            print("\n🎉 KOMPILACJA ZAKOŃCZONA POMYŚLNIE!")
            print(f"📁 Plik EXE: {exe_path}")
            if zip_path:
                print(f"📦 Archiwum: {zip_path}")
            
            return True
        else:
            print("❌ Kompilacja nie powiodła się!")
            return False


def create_argument_parser():
    """Tworzy parser argumentów linii poleceń"""
    parser = argparse.ArgumentParser(
        description="WinPython EXE Compiler - Kompiluje skrypty Python do EXE używając WinPython",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady użycia:

  Tryb interaktywny:
    python winpython_ec.py

  Tryb CLI:
    python winpython_ec.py -w "C:\\WinPython\\WPy64-310111" -s "moj_skrypt.py"
    
  Z dodatkowymi bibliotekami:
    python winpython_ec.py -w "C:\\WinPython\\WPy64-310111" -s "app.py" -l requests numpy pandas
    
  Bez tworzenia ZIP:
    python winpython_ec.py -w "C:\\WinPython\\WPy64-310111" -s "app.py" --no-zip
        """
    )
    
    parser.add_argument(
        "-w", "--winpython",
        help="Ścieżka do folderu WinPython (np. C:\\WinPython\\WPy64-310111)"
    )
    
    parser.add_argument(
        "-s", "--script",
        help="Ścieżka do skryptu Python (.py) do skompilowania"
    )
    
    parser.add_argument(
        "-l", "--libraries",
        nargs="*",
        help="Dodatkowe biblioteki do zainstalowania (oddzielone spacją)"
    )
    
    parser.add_argument(
        "--no-zip",
        action="store_true",
        help="Nie twórz archiwum ZIP z wynikiem"
    )
    
    parser.add_argument(
        "--keep-build",
        action="store_true",
        help="Zachowaj pliki tymczasowe kompilacji (build, spec)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="WinPython EXE Compiler v1.0"
    )
    
    return parser


def main():
    """Główna funkcja programu"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    compiler = WinPythonEXECompiler()
    
    # Jeśli nie podano argumentów, uruchamiamy tryb interaktywny
    if not args.winpython and not args.script:
        try:
            success = compiler.run_interactive()
            sys.exit(0 if success else 1)
        except KeyboardInterrupt:
            print("\n\n⏹️  Program przerwany przez użytkownika")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Nieoczekiwany błąd: {e}")
            sys.exit(1)
    
    # Sprawdzamy czy podano wymagane argumenty dla trybu CLI
    if not args.winpython:
        print("❌ Wymagana ścieżka do WinPython (-w/--winpython)")
        parser.print_help()
        sys.exit(1)
        
    if not args.script:
        print("❌ Wymagana ścieżka do skryptu (-s/--script)")
        parser.print_help()
        sys.exit(1)
    
    # Uruchamiamy w trybie CLI
    try:
        success = compiler.run_cli(args)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Program przerwany przez użytkownika")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Nieoczekiwany błąd: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

