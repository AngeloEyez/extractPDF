#!/usr/bin/env python3
"""
PDF 解密工具

使用已知的 User Password 解鎖 PDF 並另存為無保護的檔案。
這將移除 Owner Password (Admin Password) 的限制。

使用方式:
    python decrypt_pdf.py <input_pdf> <output_pdf> <password>
    python decrypt_pdf.py <input_pdf> <password>  (將輸出到 <input_filename>_decrypted.pdf)
"""

import sys
import os
import fitz  # PyMuPDF


def decrypt_pdf(input_path: str, output_path: str, password: str):
    """
    解密 PDF 並另存新檔

    Args:
        input_path: 輸入 PDF 路徑
        output_path: 輸出 PDF 路徑
        password: User Password
    """
    print(f"處理檔案: {input_path}")
    
    try:
        doc = fitz.open(input_path)
    except Exception as e:
        print(f"錯誤: 無法開啟檔案 - {e}")
        sys.exit(1)

    if not doc.is_encrypted:
        print("警告: 檔案未加密，無需解密。")
        doc.save(output_path)
        print(f"已另存為: {output_path}")
        return

    print("檔案已加密，嘗試解鎖...")
    if doc.authenticate(password):
        print("密碼驗證成功！")
        try:
            # 另存為新檔，預設會移除加密（除非重新指定 encryption 參數）
            doc.save(output_path)
            print("--------------------------------------------------")
            print(f"成功！已移除密碼保護。")
            print(f"解密檔案: {output_path}")
            print("說明: 新檔案已無密碼保護，Admin Password 限制已移除。")
            print("--------------------------------------------------")
        except Exception as e:
            print(f"錯誤: 儲存檔案失敗 - {e}")
            sys.exit(1)
    else:
        print("錯誤: 密碼驗證失敗！請確認密碼正確。")
        sys.exit(1)
    
    doc.close()


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    input_path = sys.argv[1]
    
    if len(sys.argv) == 3:
        # python decrypt_pdf.py <input> <password>
        password = sys.argv[2]
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_decrypted{ext}"
    else:
        # python decrypt_pdf.py <input> <output> <password>
        output_path = sys.argv[2]
        password = sys.argv[3]

    if not os.path.exists(input_path):
        print(f"錯誤: 找不到輸入檔案 '{input_path}'")
        sys.exit(1)

    decrypt_pdf(input_path, output_path, password)


if __name__ == "__main__":
    main()
