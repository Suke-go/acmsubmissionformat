import os
import json
import requests
import tarfile
import lzma
from urllib.parse import urljoin
# install "request" by yourself

def download_and_extract_tex_package(package_name, base_url, save_dir):
    possible_patterns = [
        f"{package_name}.tar.xz",
        f"{package_name}.r*.tar.xz",
        f"{package_name}.doc.tar.xz",
        f"{package_name}.doc.r*.tar.xz",
        f"{package_name}.source.tar.xz",
        f"{package_name}.source.r*.tar.xz"
    ]
    
    architectures = [
        "aarch64-linux", "amd64-freebsd", "amd64-netbsd",
        "armhf-linux", "i386-freebsd", "i386-linux",
        "i386-netbsd", "i386-solaris"
    ]
    
    for arch in architectures:
        possible_patterns.append(f"{package_name}.{arch}.tar.xz")
        possible_patterns.append(f"{package_name}.{arch}.r*.tar.xz")
    
    for pattern in possible_patterns:
        dir_url = urljoin(base_url, "archive/")
        response = requests.get(dir_url)
        if response.status_code == 200:
            for line in response.text.splitlines():
                if pattern.replace("*", "") in line:
                    filename = line.split('"')[-2]
                    if filename.startswith(package_name) and filename.endswith(".tar.xz"):
                        file_url = urljoin(dir_url, filename)
                        file_response = requests.get(file_url, stream=True)
                        if file_response.status_code == 200:
                            save_path = os.path.join(save_dir, filename)
                            with open(save_path, 'wb') as f:
                                for chunk in file_response.iter_content(chunk_size=8192):
                                    f.write(chunk)
                            print(f"パッケージ '{filename}' をダウンロードしました: {save_path}")
                            
                            extract_dir = os.path.join(save_dir, package_name)
                            os.makedirs(extract_dir, exist_ok=True)
                            try:
                                with lzma.open(save_path) as xz:
                                    with tarfile.open(fileobj=xz) as tar:
                                        tar.extractall(path=extract_dir)
                                print(f"パッケージ '{filename}' を {extract_dir} に解凍しました")
                                
                                os.remove(save_path)
                                print(f"圧縮ファイル '{save_path}' を削除しました")
                            except Exception as e:
                                print(f"解凍中にエラーが発生しました: {str(e)}")
                            
                            return True
    
    print(f"パッケージ '{package_name}' が見つかりませんでした。")
    return False

def main():
    # CTAN website
    base_url = "https://ftp.kddilabs.jp/CTAN/systems/texlive/tlnet/"
    #make sure that your texlive year.
    save_dir = r"C:\texlive\~~~\texmf-dist\tex\latex"
    
    os.makedirs(save_dir, exist_ok=True)
    
    with open('packages.json', 'r') as f:
        packages = json.load(f)
    
    for package in packages:
        download_and_extract_tex_package(package, base_url, save_dir)

if __name__ == "__main__":
    main()
