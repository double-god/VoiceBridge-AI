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
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-2xl mx-auto space-y-8">
        <header className="text-center space-y-2 mb-10 pt-10">
          <h1 className="text-3xl font-bold text-gray-900">VoiceBridge AI</h1>
          <p className="text-gray-500">您的智能语音助手</p>
        </header>

        {/* 录音模块 */}
        <AudioRecorder 
          onUploadSuccess={handleUploadSuccess}
          onUploadStart={handleUploadStart}
        />

        {/* 状态展示模块 - 有 ID 时才显示 */}
        {currentRecordId && (
          <StatusCard recordId={currentRecordId} />
        )}
      </div>
    </div>
  );
}
