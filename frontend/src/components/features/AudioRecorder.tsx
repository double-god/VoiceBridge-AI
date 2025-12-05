import { useState, useRef } from 'react';
import { Mic, Square, UploadCloud } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';
import { voiceApi } from '@/api';
import { cn } from '@/lib/utils';

interface AudioRecorderProps {
  onUploadStart?: () => void;
  onUploadSuccess: (recordId: number) => void;
  onUploadError?: (error: Error) => void;
}

export function AudioRecorder({
  onUploadStart,
  onUploadSuccess,
  onUploadError,
}: AudioRecorderProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const handleUpload = async (blob: Blob) => {
    try {
      setIsUploading(true);
      onUploadStart?.();

      const response = await voiceApi.uploadAudio(blob);

      // 兼容后端返回 code 0 或 200
      if (response.code === 0 || response.code === 200) {
        onUploadSuccess(response.data.record_id);
      } else {
        throw new Error(response.msg || '上传失败');
      }
    } catch (error) {
      console.error('上传失败', error);
      onUploadError?.(error as Error);
    } finally {
      setIsUploading(false);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);

      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = async () => {
        // 停止所有轨道
        stream.getTracks().forEach((track) => track.stop());
        // 合成音频
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' });
        await handleUpload(audioBlob);
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error('无法访问麦克风', err);
      alert('无法访问麦克风，请检查权限设置');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  return (
    <Card className="mx-auto w-full border-[0.3vh] border-dashed border-gray-300 bg-gradient-to-br from-gray-50 to-blue-50/30 shadow-xl">
      <CardContent className="flex flex-col items-center justify-center space-y-[4vh] py-[6vh] md:py-[8vh]">
        <div
          className={cn(
            'flex h-[15vh] w-[15vh] items-center justify-center rounded-full shadow-2xl transition-all duration-500 md:h-[18vh] md:w-[18vh]',
            isRecording ? 'animate-pulse bg-red-100' : 'bg-blue-100',
            isUploading && 'bg-gray-100'
          )}
        >
          {isUploading ? (
            <UploadCloud className="h-[7vh] w-[7vh] animate-bounce text-gray-500 md:h-[8vh] md:w-[8vh]" />
          ) : isRecording ? (
            <Mic className="h-[7vh] w-[7vh] text-red-500 md:h-[8vh] md:w-[8vh]" />
          ) : (
            <Mic className="h-[7vh] w-[7vh] text-blue-500 md:h-[8vh] md:w-[8vh]" />
          )}
        </div>

        <div className="space-y-[1.5vh] text-center">
          <h3 className="text-[2.5vh] font-semibold text-gray-900 md:text-[3vh]">
            {isUploading ? '正在上传...' : isRecording ? '录音中...' : '点击开始录音'}
          </h3>
          <p className="text-[1.8vh] text-gray-500 md:text-[2vh]">
            {isUploading ? '请稍候，正在将音频发送至服务器...' : '请清晰地说出您的需求'}
          </p>
        </div>

        <div className="flex gap-[2vh]">
          {!isRecording ? (
            <Button
              size="lg"
              onClick={startRecording}
              disabled={isUploading}
              className="h-[6vh] w-[20vh] rounded-full text-[2vh] shadow-lg transition-all hover:shadow-xl md:h-[7vh] md:w-[25vh] md:text-[2.2vh]"
            >
              <Mic className="mr-[1vh] h-[2.5vh] w-[2.5vh]" />
              开始录音
            </Button>
          ) : (
            <Button
              size="lg"
              variant="danger"
              onClick={stopRecording}
              className="h-[6vh] w-[20vh] animate-pulse rounded-full text-[2vh] shadow-lg transition-all hover:shadow-xl md:h-[7vh] md:w-[25vh] md:text-[2.2vh]"
            >
              <Square className="mr-[1vh] h-[2.5vh] w-[2.5vh] fill-current" />
              停止录音
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
