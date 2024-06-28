import pefile

# 指定要解析的PE文件路径
pe_file_path = r'C:\Users\Administrator\Desktop\PPCI_new\PPCI_adv32\ppci-master-2_2023213 初通版本\ppci-master-2\ppci-master-2\ppci\arch\riscv\coff.exe'

# 使用pefile库打开PE文件
pe = pefile.PE(pe_file_path)

# 打印PE文件的基本信息
print("PE文件基本信息:")
print(f"文件路径: {pe_file_path}")
print(f"文件大小: {pe.FILE_HEADER.SizeOfOptionalHeader} bytes")
print(f"入口点地址: 0x{pe.OPTIONAL_HEADER.AddressOfEntryPoint:08X}")
print(f"节表数量: {pe.FILE_HEADER.NumberOfSections}")

# 打印导入表信息
print("\n导入表信息:")
for entry in pe.DIRECTORY_ENTRY_IMPORT:
    print(f"DLL名称: {entry.dll.decode()}")
    for imp in entry.imports:
        print(f"  - 函数名称: {imp.name.decode() if imp.name else 'Ordinal'}")
        print(f"    地址: 0x{imp.address:08X}")

# 关闭PE文件
pe.close()