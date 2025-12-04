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
    <Card className="mx-auto w-full max-w-md border-2 border-dashed border-gray-200 bg-gray-50/50">
      <CardContent className="flex flex-col items-center justify-center space-y-6 py-10">
        <div
          className={cn(
            'flex h-24 w-24 items-center justify-center rounded-full transition-all duration-500',
            isRecording ? 'animate-pulse bg-red-100' : 'bg-blue-100',
            isUploading && 'bg-gray-100'
          )}
        >
          {isUploading ? (
            <UploadCloud className="h-10 w-10 animate-bounce text-gray-500" />
          ) : isRecording ? (
            <Mic className="h-10 w-10 text-red-500" />
          ) : (
            <Mic className="h-10 w-10 text-blue-500" />
          )}
        </div>

        <div className="space-y-2 text-center">
          <h3 className="text-lg font-semibold text-gray-900">
            {isUploading ? '正在上传...' : isRecording ? '录音中...' : '点击开始录音'}
          </h3>
          <p className="text-sm text-gray-500">
            {isUploading ? '请稍候，正在将音频发送至服务器...' : '请清晰地说出您的需求'}
          </p>
        </div>

        <div className="flex gap-4">
          {!isRecording ? (
            <Button
              size="lg"
              onClick={startRecording}
              disabled={isUploading}
              className="w-40 rounded-full shadow-lg transition-all hover:shadow-xl"
            >
              <Mic className="mr-2 h-4 w-4" />
              开始录音
            </Button>
          ) : (
            <Button
              size="lg"
              variant="danger"
              onClick={stopRecording}
              className="w-40 animate-pulse rounded-full shadow-lg transition-all hover:shadow-xl"
            >
              <Square className="mr-2 h-4 w-4 fill-current" />
              停止录音
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
