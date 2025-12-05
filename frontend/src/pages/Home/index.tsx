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
    <div className="mx-auto flex min-h-[80vh] w-full max-w-[90vw] flex-col items-center justify-start py-[6vh] lg:max-w-[80vw] xl:max-w-[70vw]">
      <div className="mb-[6vh] w-full space-y-[2vh] text-center">
        <h1 className="text-[4vh] font-bold tracking-tight text-gray-900 md:text-[5vh] lg:text-[6vh]">有什么我可以帮您的吗？</h1>
        <p className="text-[2vh] text-gray-500 md:text-[2.5vh]">点击下方麦克风，告诉我您的需求。</p>
      </div>

      {/* 录音模块 */}
      <div className="mb-[6vh] w-full">
        <AudioRecorder onUploadSuccess={handleUploadSuccess} onUploadStart={handleUploadStart} />
      </div>

      {/* 状态展示模块 - 有 ID 时才显示 */}
      {currentRecordId && (
        <div className="animate-in fade-in slide-in-from-bottom-8 w-full duration-700">
          <StatusCard recordId={currentRecordId} />
        </div>
      )}
    </div>
  );
}
