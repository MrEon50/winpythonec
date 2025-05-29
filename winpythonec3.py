#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WinPython EXE Compiler - Wersja naprawiona dla WinPython
Specjalnie dostosowana do struktury WinPython

Autor: Cody (Sourcegraph AI Assistant)
Wersja: 3.0 WinPython Edition
"""

import os
import sys
import subprocess
import shutil
import zipfile
import glob
from pathlib import Path
import argparse
import datetime


class WinPythonCompiler:
    def __init__(self):
        self.winpython_root = None
        self.python_exe = None
        self.scripts_path = None
        self.site_packages = None
        self.python_path_env = None
        
    def show_menu(self):
        """Wyświetla menu programu"""
        print("=" * 70)
        print("🐍 WinPython EXE Compiler v3.0 - WinPython Edition 🐍")
        print("=" * 70)
        print("SPECJALNIE DOSTOSOWANY DO WINPYTHON!")
        print()
        print("DZIAŁANIE:")
        print("• Automatycznie konfiguruje środowisko WinPython")
        print("• Instaluje PyInstaller w odpowiednim miejscu")
        print("• Kompiluje skrypty do samodzielnych plików EXE")
        print("• Wykorzystuje wszystkie biblioteki WinPython")
        print()
        print("WYMAGANIA:")
        print("• WinPython (pobierz z: https://winpython.github.io/)")
        print("• Podaj ścieżkę do głównego folderu WinPython")
        print("=" * 70)
        print()

    def setup_winpython_environment(self, winpython_path):
        """Konfiguruje środowisko WinPython"""
        print(f"🔧 Konfiguruję środowisko WinPython...")
        
        if not os.path.exists(winpython_path):
            return False, "Podana ścieżka nie istnieje"
        
        self.winpython_root = winpython_path
        
        # Znajdź python.exe
        python_patterns = [
            os.path.join(winpython_path, "python-*.*.*.amd64", "python.exe"),
            os.path.join(winpython_path, "python-*", "python.exe"),
        ]
        
        for pattern in python_patterns:
            matches = glob.glob(pattern)
            if matches:
                self.python_exe = matches[0]
                break
        
        if not self.python_exe:
            return False, "Nie znaleziono python.exe w WinPython"
        
        print(f"✅ Python: {self.python_exe}")
        
        # Znajdź Scripts
        python_dir = os.path.dirname(self.python_exe)
        self.scripts_path = os.path.join(python_dir, "Scripts")
        
        if not os.path.exists(self.scripts_path):
            os.makedirs(self.scripts_path, exist_ok=True)
        
        print(f"✅ Scripts: {self.scripts_path}")
        
        # Znajdź site-packages
        self.site_packages = os.path.join(python_dir, "Lib", "site-packages")
        if not os.path.exists(self.site_packages):
            return False, f"Nie znaleziono site-packages: {self.site_packages}"
        
        print(f"✅ Site-packages: {self.site_packages}")
        
        # Przygotuj zmienne środowiskowe
        self.setup_python_environment()
        
        # Test Python
        try:
            result = subprocess.run([self.python_exe, "--version"], 
                                  capture_output=True, text=True, 
                                  env=self.python_path_env, check=False)
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"✅ {version}")
                return True, f"WinPython skonfigurowany - {version}"
            else:
                return False, "Python nie odpowiada"
        except Exception as e:
            return False, f"Błąd testowania Python: {e}"

    def setup_python_environment(self):
        """Przygotowuje zmienne środowiskowe dla WinPython"""
        # Skopiuj obecne środowisko
        self.python_path_env = os.environ.copy()
        
        # Dodaj ścieżki WinPython na początek PATH
        python_dir = os.path.dirname(self.python_exe)
        new_paths = [
            python_dir,  # Folder z python.exe
            self.scripts_path,  # Folder Scripts
            self.site_packages,  # Site-packages
        ]
        
        current_path = self.python_path_env.get('PATH', '')
        new_path = os.pathsep.join(new_paths + [current_path])
        self.python_path_env['PATH'] = new_path
        
        # Ustaw PYTHONPATH
        self.python_path_env['PYTHONPATH'] = self.site_packages
        
        print(f"🔧 Skonfigurowano zmienne środowiskowe")

    def install_pyinstaller_properly(self):
        """Instaluje PyInstaller w WinPython"""
        print("📦 Instaluję PyInstaller w WinPython...")
        
        try:
            # Użyj pip z odpowiednimi zmiennymi środowiskowymi
            cmd = [self.python_exe, "-m", "pip", "install", "pyinstaller", "--upgrade"]
            
            print(f"Wykonuję: {' '.join(cmd)}")
            result = subprocess.run(cmd, 
                                  capture_output=True, 
                                  text=True, 
                                  env=self.python_path_env,
                                  check=False)
            
            if result.returncode == 0:
                print("✅ PyInstaller zainstalowany")
                
                # Sprawdź instalację
                return self.verify_pyinstaller()
            else:
                print(f"❌ Błąd instalacji PyInstaller:")
                print(f"STDERR: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Wyjątek podczas instalacji: {e}")
            return False

    def verify_pyinstaller(self):
        """Sprawdza czy PyInstaller działa"""
        print("🔍 Sprawdzam PyInstaller...")
        
        try:
            # Test importu
            cmd = [self.python_exe, "-c", "import PyInstaller; print('PyInstaller OK')"]
            result = subprocess.run(cmd, 
                                  capture_output=True, 
                                  text=True, 
                                  env=self.python_path_env,
                                  check=False)
            
            if result.returncode == 0:
                print("✅ PyInstaller można zaimportować")
                
                # Test komendy
                cmd2 = [self.python_exe, "-m", "PyInstaller", "--version"]
                result2 = subprocess.run(cmd2, 
                                       capture_output=True, 
                                       text=True, 
                                       env=self.python_path_env,
                                       check=False)
                
                if result2.returncode == 0:
                    version = result2.stdout.strip()
                    print(f"✅ PyInstaller {version} gotowy")
                    return True
                else:
                    print(f"⚠️  PyInstaller import OK, ale komenda nie działa: {result2.stderr}")
                    return False
            else:
                print(f"❌ Nie można zaimportować PyInstaller: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Błąd sprawdzania PyInstaller: {e}")
            return False

    def list_packages(self):
        """Pokazuje zainstalowane pakiety"""
        try:
            cmd = [self.python_exe, "-m", "pip", "list"]
            result = subprocess.run(cmd, 
                                  capture_output=True, 
                                  text=True, 
                                  env=self.python_path_env,
                                  check=False)
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')[2:]  # Pomijamy nagłówki
                valid_lines = [line for line in lines if line.strip()]
                
                print("📦 Dostępne pakiety:")
                for line in valid_lines[:10]:
                    print(f"   {line}")
                if len(valid_lines) > 10:
                    print(f"   ... i {len(valid_lines)-10} więcej")
                print()
        except Exception:
            print("⚠️  Nie udało się pobrać listy pakietów")

    def install_libraries(self, libraries):
        """Instaluje dodatkowe biblioteki"""
        if not libraries:
            return True
            
        print(f"📦 Instaluję biblioteki: {', '.join(libraries)}")
        
        for lib in libraries:
            try:
                cmd = [self.python_exe, "-m", "pip", "install", lib]
                result = subprocess.run(cmd, 
                                      capture_output=True, 
                                      text=True, 
                                      env=self.python_path_env,
                                      check=False)
                
                if result.returncode == 0:
                    print(f"✅ {lib} - zainstalowana")
                else:
                    print(f"❌ {lib} - błąd: {result.stderr}")
                    return False
            except Exception as e:
                print(f"❌ Błąd instalacji {lib}: {e}")
                return False
        
        return True

    def compile_script(self, script_path, output_dir):
        """Kompiluje skrypt do EXE"""
        print("🔨 Kompilacja do EXE...")
        
        script_name = os.path.splitext(os.path.basename(script_path))[0]
        exe_name = f"{script_name}_compiled"
        
        # Sprawdź czy to nie samo-kompilacja
        try:
            if os.path.abspath(__file__) == os.path.abspath(script_path):
                print("⚠️  Wykryto samo-kompilację - dodaję '_compiled' do nazwy")
        except:
            pass
        
        # Komenda PyInstaller
        cmd = [
            self.python_exe, "-m", "PyInstaller",
            "--onefile",
            "--distpath", output_dir,
            "--workpath", os.path.join(output_dir, "build"),
            "--specpath", os.path.join(output_dir, "spec"),
            "--clean",
            "--name", exe_name,
            script_path
        ]
        
        try:
            print(f"Wykonuję: {' '.join(cmd)}")
            print("⏳ Kompilacja w toku...")
            
            # Uruchom z odpowiednim środowiskiem
            result = subprocess.run(cmd, 
                                  capture_output=True, 
                                  text=True, 
                                  env=self.python_path_env,
                                  check=False)
            
            if result.returncode == 0:
                exe_path = os.path.join(output_dir, f"{exe_name}.exe")
                if os.path.exists(exe_path):
                    size_mb = os.path.getsize(exe_path) / (1024*1024)
                    print(f"✅ Kompilacja zakończona!")
                    print(f"📁 EXE: {exe_path}")
                    print(f"📏 Rozmiar: {size_mb:.1f} MB")
                    return exe_path
                else:
                    print("❌ Kompilacja OK, ale nie ma pliku EXE")
                    return None
            else:
                print("❌ Błąd kompilacji:")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                
                # Analiza błędów
                error_text = (result.stdout + result.stderr).lower()
                if "no module named" in error_text:
                    print("💡 Brakuje modułów - sprawdź czy wszystkie biblioteki są zainstalowane")
                elif "permission" in error_text:
                    print("💡 Problem z uprawnieniami - uruchom jako administrator")
                elif "recursion" in error_text:
                    print("💡 Problem z rekursją - prawdopodobnie samo-kompilacja")
                
                return None
                
        except Exception as e:
            print(f"❌ Wyjątek podczas kompilacji: {e}")
            return None

    def create_package(self, exe_path, output_dir):
        """Tworzy pakiet ZIP"""
        if not exe_path or not os.path.exists(exe_path):
            return None
            
        exe_name = os.path.splitext(os.path.basename(exe_path))[0]
        zip_path = os.path.join(output_dir, f"{exe_name}_package.zip")
        
        try:
            print("📦 Tworzę pakiet ZIP...")
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(exe_path, os.path.basename(exe_path))
                
                readme = f"""
{exe_name} - Aplikacja Python

Skompilowano: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Kompilator: WinPython EXE Compiler v3.0
Rozmiar: {os.path.getsize(exe_path) / (1024*1024):.1f} MB

URUCHOMIENIE:
Uruchom plik {os.path.basename(exe_path)}

WYMAGANIA:
Brak - aplikacja jest samodzielna
"""
                zipf.writestr("README.txt", readme)
            
            print(f"✅ Pakiet: {zip_path}")
            return zip_path
            
        except Exception as e:
            print(f"❌ Błąd tworzenia pakietu: {e}")
            return None

    def cleanup(self, output_dir):
        """Usuwa pliki tymczasowe"""
        try:
            for folder in ["build", "spec"]:
                folder_path = os.path.join(output_dir, folder)
                if os.path.exists(folder_path):
                    shutil.rmtree(folder_path)
                    print(f"🧹 Usunięto {folder}")
            
            # Usuń pliki .spec
            for spec_file in glob.glob(os.path.join(output_dir, "*.spec")):
                os.remove(spec_file)
                print(f"🧹 Usunięto {os.path.basename(spec_file)}")
                
        except Exception as e:
            print(f"⚠️  Błąd sprzątania: {e}")

    def test_exe(self, exe_path):
        """Testuje skompilowany EXE"""
        try:
            print("🧪 Testuję EXE...")
            process = subprocess.Popen([exe_path], 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE)
            
            try:
                stdout, stderr = process.communicate(timeout=3)
                if process.returncode == 0:
                    print("✅ EXE działa!")
                    return True
                else:
                    print(f"⚠️  EXE zakończony z kodem: {process.returncode}")
                    return False
            except subprocess.TimeoutExpired:
                process.terminate()
                print("✅ EXE uruchomiony i działa!")
                return True
                
        except Exception as e:
            print(f"❌ Błąd testowania: {e}")
            return False

    def run_interactive(self):
        """Tryb interaktywny"""
        self.show_menu()
        
        # Konfiguracja WinPython
        while True:
            print("📁 Podaj ścieżkę do WinPython:")
            print("   Przykład: C:\\Users\\Endorfinka\\Desktop\\WinPython\\WPy64-310111")
            path = input("   Ścieżka: ").strip().strip('"')
            
            if not path:
                print("❌ Ścieżka nie może być pusta!")
                continue
                
            success, message = self.setup_winpython_environment(path)
            if success:
                print(f"✅ {message}")
                break
            else:
                print(f"❌ {message}")
                continue
        
        # Instalacja PyInstaller
        if not self.verify_pyinstaller():
            print("\n🔧 PyInstaller nie jest dostępny...")
            if not self.install_pyinstaller_properly():
                print("❌ Nie udało się zainstalować PyInstaller")
                return False
        
        # Pokaż pakiety
        self.list_packages()
        
        # Wybór skryptu
        while True:
            script_path = input("\n📄 Ścieżka do skryptu (.py): ").strip().strip('"')
            
            if not script_path:
                print("❌ Podaj ścieżkę!")
                continue
                
            if not os.path.exists(script_path):
                print("❌ Plik nie istnieje!")
                continue
                
            if not script_path.lower().endswith('.py'):
                print("❌ Musi być plik .py!")
                continue
                
            break
        
        # Dodatkowe biblioteki
        print("\n📚 Dodatkowe biblioteki (opcjonalne):")
        libs_input = input("   Nazwy oddzielone spacją (Enter = pomiń): ").strip()
        libraries = libs_input.split() if libs_input else []
        
        if libraries:
            if not self.install_libraries(libraries):
                choice = input("Kontynuować mimo błędów? (t/n): ").lower()
                if choice not in ['t', 'tak', 'y', 'yes']:
                    return False
        
        # Kompilacja
        output_dir = os.path.join(self.winpython_root, "compiled_apps")
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n📁 Folder wyjściowy: {output_dir}")
        print("\n" + "="*60)
        print("🚀 ROZPOCZYNAM KOMPILACJĘ")
        print("="*60)
        
        exe_path = self.compile_script(script_path, output_dir)
        
        if exe_path:
            # Pakiet ZIP
            zip_path = self.create_package(exe_path, output_dir)
            
            # Test
            test_choice = input("\nTestować EXE? (t/n): ").lower()
            if test_choice in ['t', 'tak', 'y', 'yes']:
                self.test_exe(exe_path)
            
            # Sprzątanie
            cleanup_choice = input("Usunąć pliki tymczasowe? (t/n): ").lower()
            if cleanup_choice in ['t', 'tak', 'y', 'yes']:
                self.cleanup(output_dir)
            
            # Wyniki
            print("\n" + "="*70)
            print("🎉 KOMPILACJA ZAKOŃCZONA POMYŚLNIE! 🎉")
            print("="*70)
            print(f"📁 EXE: {exe_path}")
            if zip_path:
                print(f"📦 Pakiet: {zip_path}")
            print(f"📂 Folder: {output_dir}")
            print("="*70)
            
            # Otwórz folder
            open_choice = input("\nOtworzyć folder? (t/n): ").lower()
            if open_choice in ['t', 'tak', 'y', 'yes']:
                try:
                    os.startfile(output_dir)
                except:
                    print(f"📂 Otwórz ręcznie: {output_dir}")
            
            return True
        else:
            print("\n❌ KOMPILACJA NIEUDANA!")
            print("💡 Sprawdź błędy powyżej")
            return False

    def run_cli(self, args):
        """Tryb CLI"""
        # Setup WinPython
        success, message = self.setup_winpython_environment(args.winpython)
        if not success:
            print(f"❌ {message}")
            return False
        print(f"✅ {message}")
        
        # PyInstaller
        if not self.verify_pyinstaller():
            if not self.install_pyinstaller_properly():
                return False
        
        # Walidacja skryptu
        if not os.path.exists(args.script):
            print(f"❌ Skrypt nie istnieje: {args.script}")
            return False
            
        if not args.script.lower().endswith('.py'):
            print("❌ Musi być plik .py!")
            return False
        
        # Biblioteki
        if args.libraries:
            if not self.install_libraries(args.libraries):
                print("⚠️  Błędy instalacji bibliotek")
        
        # Kompilacja
        output_dir = os.path.join(self.winpython_root, "compiled_apps")
        os.makedirs(output_dir, exist_ok=True)
        
        exe_path = self.compile_script(args.script, output_dir)
        
        if exe_path:
            if not args.no_zip:
                self.create_package(exe_path, output_dir)
            
            if not args.keep_build:
                self.cleanup(output_dir)
            
            print(f"\n✅ Sukces! EXE: {exe_path}")
            return True
        else:
            print("❌ Kompilacja nieudana!")
            return False


def create_parser():
    """Parser argumentów"""
    parser = argparse.ArgumentParser(
        description="WinPython EXE Compiler v3.0 - Specjalnie dla WinPython",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady:

  Tryb interaktywny:
    python winpythonec.py

  Tryb CLI:
    python winpythonec.py -w "C:\\WinPython\\WPy64-310111" -s "test.py"
    
  Z bibliotekami:
    python winpythonec.py -w "C:\\WinPython\\WPy64-310111" -s "app.py" -l requests numpy

Funkcje v3.0:
  • Prawidłowa konfiguracja środowiska WinPython
  • Automatyczne ustawienie zmiennych środowiskowych
  • Instalacja PyInstaller w odpowiednim miejscu
  • Pełna kompatybilność z WinPython
        """
    )
    
    parser.add_argument("-w", "--winpython", help="Ścieżka do WinPython")
    parser.add_argument("-s", "--script", help="Skrypt do kompilacji (.py)")
    parser.add_argument("-l", "--libraries", nargs="*", help="Dodatkowe biblioteki")
    parser.add_argument("--no-zip", action="store_true", help="Bez pakietu ZIP")
    parser.add_argument("--keep-build", action="store_true", help="Zachowaj pliki build")
    parser.add_argument("--version", action="version", version="WinPython EXE Compiler v3.0")
    
    return parser


def main():
    """Główna funkcja"""
    print("🚀 WinPython EXE Compiler v3.0 - WinPython Edition")
    
    parser = create_parser()
    args = parser.parse_args()
    
    compiler = WinPythonCompiler()
    
    # Tryb interaktywny
    if not args.winpython and not args.script:
        try:
            success = compiler.run_interactive()
            if success:
                print("\n✅ Program zakończony pomyślnie!")
                input("Naciśnij Enter...")
            sys.exit(0 if success else 1)
        except KeyboardInterrupt:
            print("\n⏹️  Przerwano przez użytkownika")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Błąd: {e}")
            import traceback
            traceback.print_exc()
            input("Naciśnij Enter...")
            sys.exit(1)
    
    # Sprawdź argumenty CLI
    if not args.winpython:
        print("❌ Wymagana ścieżka WinPython (-w)")
        sys.exit(1)
        
    if not args.script:
        print("❌ Wymagany skrypt (-s)")
        sys.exit(1)
    
    # Tryb CLI
    try:
        success = compiler.run_cli(args)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Przerwano")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Błąd: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

