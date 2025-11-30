"""
CHAT 格式 (.cha) 解析器
用于解析 TalkBank 的转写文件

CHAT 格式参考: https://talkbank.org/manuals/CHAT.html
"""

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Utterance:
    """单条话语"""

    speaker: str  # 说话人 (*PAR, *INV 等)
    text: str  # 话语内容
    start_ms: int | None  # 开始时间 (毫秒)
    end_ms: int | None  # 结束时间 (毫秒)


@dataclass
class ChaDocument:
    """解析后的 .cha 文档"""

    participants: dict[
        str, str
    ]  # {代码: 角色名}，如 {"PAR": "Participant", "INV": "Investigator"}
    utterances: list[Utterance]  # 所有话语
    metadata: dict  # 元数据 (@UTF8, @Begin, @Languages 等)


class ChaParser:
    """
    CHAT 格式解析器

    Usage:
        parser = ChaParser()
        doc = parser.parse("path/to/file.cha")
        for utt in doc.utterances:
            print(f"{utt.speaker}: {utt.text}")
    """

    # 正则模式
    PARTICIPANT_PATTERN = re.compile(r"@Participants:\s*(.+)")
    UTTERANCE_PATTERN = re.compile(r"^\*(\w+):\s*(.+?)(?:\s*\x15(\d+)_(\d+)\x15)?$")
    METADATA_PATTERN = re.compile(r"^@(\w+):\s*(.*)$")
    TIMESTAMP_PATTERN = re.compile(r"\x15(\d+)_(\d+)\x15")  # 时间戳标记

    def parse(self, file_path: str | Path) -> ChaDocument:
        """
        解析 .cha 文件

        Args:
            file_path: .cha 文件路径

        Returns:
            解析后的文档对象
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        # 尝试不同编码
        content = None
        for encoding in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
            try:
                content = file_path.read_text(encoding=encoding)
                break
            except UnicodeDecodeError:
                continue

        if content is None:
            raise ValueError(f"无法解码文件: {file_path}")

        return self._parse_content(content)

    def _parse_content(self, content: str) -> ChaDocument:
        """解析文件内容"""
        participants = {}
        utterances = []
        metadata = {}

        lines = content.split("\n")
        current_utterance = None

        for line in lines:
            line = line.strip()

            if not line:
                continue

            # 解析参与者
            if line.startswith("@Participants:"):
                participants = self._parse_participants(line)
                continue

            # 解析元数据
            if line.startswith("@"):
                match = self.METADATA_PATTERN.match(line)
                if match:
                    key, value = match.groups()
                    metadata[key] = value
                continue

            # 解析话语行
            if line.startswith("*"):
                # 保存上一条
                if current_utterance:
                    utterances.append(current_utterance)

                current_utterance = self._parse_utterance_line(line)
                continue

            # 续行（以 Tab 开头的是上一行的延续）
            if line.startswith("\t") and current_utterance:
                # 提取时间戳
                ts_match = self.TIMESTAMP_PATTERN.search(line)
                if ts_match and current_utterance.start_ms is None:
                    current_utterance.start_ms = int(ts_match.group(1))
                    current_utterance.end_ms = int(ts_match.group(2))

        # 别忘了最后一条
        if current_utterance:
            utterances.append(current_utterance)

        return ChaDocument(
            participants=participants, utterances=utterances, metadata=metadata
        )

    def _parse_participants(self, line: str) -> dict[str, str]:
        """解析参与者行"""
        # @Participants: PAR Participant, INV Investigator
        match = self.PARTICIPANT_PATTERN.match(line)
        if not match:
            return {}

        participants = {}
        parts = match.group(1).split(",")
        for part in parts:
            tokens = part.strip().split()
            if len(tokens) >= 2:
                code = tokens[0]
                role = " ".join(tokens[1:])
                participants[code] = role

        return participants

    def _parse_utterance_line(self, line: str) -> Utterance:
        """解析话语行"""
        # *PAR: hello world . 123_456
        match = self.UTTERANCE_PATTERN.match(line)

        if match:
            speaker = match.group(1)
            text = match.group(2).strip()
            start_ms = int(match.group(3)) if match.group(3) else None
            end_ms = int(match.group(4)) if match.group(4) else None
        else:
            # 简单解析
            if ":" in line:
                speaker = line[1 : line.index(":")]
                text = line[line.index(":") + 1 :].strip()
            else:
                speaker = "UNK"
                text = line
            start_ms = None
            end_ms = None

        # 清理文本中的时间戳标记
        text = self.TIMESTAMP_PATTERN.sub("", text).strip()

        return Utterance(speaker=speaker, text=text, start_ms=start_ms, end_ms=end_ms)

    def to_dict(self, doc: ChaDocument) -> dict:
        """转换为字典格式，方便导出 JSON"""
        return {
            "participants": doc.participants,
            "metadata": doc.metadata,
            "utterances": [
                {
                    "speaker": u.speaker,
                    "text": u.text,
                    "start_ms": u.start_ms,
                    "end_ms": u.end_ms,
                }
                for u in doc.utterances
            ],
        }
