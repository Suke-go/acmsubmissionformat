import os
import json
import requests
import tarfile
import lzma
from urllib.parse import urljoin

def download_and_extract_tex_package(package_name, base_url, save_dir):
    # パッケージの可能なファイル名のパターンを生成
    possible_patterns = [
        f"{package_name}.tar.xz",
        f"{package_name}.r*.tar.xz",
        f"{package_name}.doc.tar.xz",
        f"{package_name}.doc.r*.tar.xz",
        f"{package_name}.source.tar.xz",
        f"{package_name}.source.r*.tar.xz"
    ]
    
    # アーキテクチャ依存のパッケージの場合のパターン
    architectures = [
        "aarch64-linux", "amd64-freebsd", "amd64-netbsd",
        "armhf-linux", "i386-freebsd", "i386-linux",
        "i386-netbsd", "i386-solaris"
    ]
    
    for arch in architectures:
        possible_patterns.append(f"{package_name}.{arch}.tar.xz")
        possible_patterns.append(f"{package_name}.{arch}.r*.tar.xz")
    
    for pattern in possible_patterns:
        # ディレクトリ一覧を取得
        dir_url = urljoin(base_url, "archive/")
        response = requests.get(dir_url)
        if response.status_code == 200:
            # ファイル名のパターンにマッチするファイルを探す
            for line in response.text.splitlines():
                if pattern.replace("*", "") in line:
                    filename = line.split('"')[-2]
                    if filename.startswith(package_name) and filename.endswith(".tar.xz"):
                        # ファイルをダウンロード
                        file_url = urljoin(dir_url, filename)
                        file_response = requests.get(file_url, stream=True)
                        if file_response.status_code == 200:
                            save_path = os.path.join(save_dir, filename)
                            with open(save_path, 'wb') as f:
                                for chunk in file_response.iter_content(chunk_size=8192):
                                    f.write(chunk)
                            print(f"パッケージ '{filename}' をダウンロードしました: {save_path}")
                            
                            # ファイルを解凍
                            extract_dir = os.path.join(save_dir, package_name)
                            os.makedirs(extract_dir, exist_ok=True)
                            try:
                                with lzma.open(save_path) as xz:
                                    with tarfile.open(fileobj=xz) as tar:
                                        tar.extractall(path=extract_dir)
                                print(f"パッケージ '{filename}' を {extract_dir} に解凍しました")
                                
                                # 解凍後、元の圧縮ファイルを削除
                                os.remove(save_path)
                                print(f"圧縮ファイル '{save_path}' を削除しました")
                            except Exception as e:
                                print(f"解凍中にエラーが発生しました: {str(e)}")
                            
                            return True
    
    print(f"パッケージ '{package_name}' が見つかりませんでした。")
    return False

def main():
    # CTANミラーサイトのベースURL
    base_url = "https://ftp.kddilabs.jp/CTAN/systems/texlive/tlnet/"
    
    # 保存先ディレクトリ
    save_dir = r"C:\texlive\2024\texmf-dist\tex\latex"
    
    # ディレクトリが存在しない場合は作成
    os.makedirs(save_dir, exist_ok=True)
    
    # パッケージリストを読み込む（JSONファイルから）
    with open('packages.json', 'r') as f:
        packages = json.load(f)
    
    # 各パッケージをダウンロードして解凍
    for package in packages:
        download_and_extract_tex_package(package, base_url, save_dir)

if __name__ == "__main__":
    main()