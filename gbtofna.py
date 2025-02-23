import re
import argparse


def parse_gb_file(gb_content):
    """
    解析 GB 格式文件内容，提取序列和基因信息
    :param gb_content: GB 格式文件的文本内容
    :return: 包含基因标签和对应序列的记录列表
    """
    # 提取完整的 DNA 序列
    origin_start = gb_content.find("ORIGIN")
    if origin_start == -1:
        return []
    origin_lines = gb_content[origin_start:].splitlines()[1:]
    sequence = ''.join(re.findall(r'[acgt]', ''.join(origin_lines)))

    # 提取基因信息，修改正则表达式以匹配两种情况
    gene_pattern = re.compile(r'gene\s+(?:complement\()?(\d+)\.\.(\d+)(?:\))?\s+/locus_tag="([^"]+)"')
    gene_matches = gene_pattern.findall(gb_content)

    records = []
    for match in gene_matches:
        start = int(match[0])
        end = int(match[1])
        locus_tag = match[2]
        gene_sequence = sequence[start - 1:end]
        records.append((locus_tag, gene_sequence))

    return records


def convert_to_fna(records):
    """
    将解析后的记录转换为 FNA 格式的文本
    :param records: 包含基因标签和对应序列的记录列表
    :return: FNA 格式的文本内容
    """
    fna_content = ""
    for i, (locus_tag, sequence) in enumerate(records, start=1):
        header = f">seq{i} {locus_tag}"
        # 每行 60 个字符分割序列
        sequence_lines = [sequence[j:j + 60] for j in range(0, len(sequence), 60)]
        fna_content += f"{header}\n"
        fna_content += "\n".join(sequence_lines) + "\n"
    return fna_content


def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='将 GB 格式文件转换为 FNA 格式文件')
    parser.add_argument('-i', '--input', required=True, help='输入的 GB 格式文件路径')
    parser.add_argument('-o', '--output', required=True, help='输出的 FNA 格式文件路径')
    args = parser.parse_args()

    try:
        # 读取输入的 GB 文件内容
        with open(args.input, 'r') as gb_file:
            gb_content = gb_file.read()
    except FileNotFoundError:
        print(f"错误：未找到输入文件 {args.input}。")
        return

    # 解析 GB 文件内容
    records = parse_gb_file(gb_content)
    # 转换为 FNA 格式
    fna_content = convert_to_fna(records)

    try:
        # 将转换后的内容写入输出文件
        with open(args.output, 'w') as fna_file:
            fna_file.write(fna_content)
        print(f"转换完成，结果已保存为 {args.output}")
    except Exception as e:
        print(f"保存输出文件时出错: {e}")


if __name__ == "__main__":
    main()
