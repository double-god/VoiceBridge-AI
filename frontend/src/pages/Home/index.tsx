import { useState } from 'react';
import { AudioRecorder } from '@/components/features/AudioRecorder';
import { StatusCard } from '@/components/features/StatusCard';

export default function HomePage() {
  // recordId 由父组件管理，连接两个子组件
  const [currentRecordId, setCurrentRecordId] = useState<number | null>(null);

  const handleUploadSuccess = (recordId: number) => {
    console.log('上传成功，ID:', recordId);
    setCurrentRecordId(recordId);
  };

  const handleUploadStart = () => {
    // 开始新录音时，重置之前的状态
    setCurrentRecordId(null);
  };

  return (
    <div className="mx-auto max-w-2xl space-y-12 py-8">
      <div className="space-y-4 text-center">
        <h1 className="text-4xl font-bold tracking-tight text-gray-900">有什么我可以帮您的吗？</h1>
        <p className="text-lg text-gray-500">点击下方麦克风，告诉我您的需求。</p>
      </div>

      {/* 录音模块 */}
      <div className="flex justify-center">
        <AudioRecorder onUploadSuccess={handleUploadSuccess} onUploadStart={handleUploadStart} />
      </div>

      {/* 状态展示模块 - 有 ID 时才显示 */}
      {currentRecordId && (
        <div className="animate-in fade-in slide-in-from-bottom-8 duration-700">
          <StatusCard recordId={currentRecordId} />
        </div>
      )}
    </div>
  );
}
