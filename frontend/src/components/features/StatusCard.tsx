import { useEffect, useRef } from 'react';
import { CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { useVoiceProgress } from '@/hooks';
import { cn } from '@/lib/utils';

interface StatusCardProps {
  recordId: number | null;
}

export function StatusCard({ recordId }: StatusCardProps) {
  const { status, progress, message, result, error, isCompleted } = useVoiceProgress(recordId);

  const audioRef = useRef<HTMLAudioElement | null>(null);

  // 自动播放逻辑
  useEffect(() => {
    if (status === 'completed' && result?.analysis_result?.tts_audio_url && audioRef.current) {
      audioRef.current.play().catch((e) => console.log('自动播放被拦截:', e));
    }
  }, [status, result]);

  if (!recordId) return null;

  return (
    <Card className="mx-auto mt-6 w-full max-w-md overflow-hidden shadow-lg transition-all duration-500">
      <CardHeader
        className={cn(
          'border-b transition-colors duration-300',
          status === 'completed' ? 'bg-green-50' : status === 'failed' ? 'bg-red-50' : 'bg-blue-50'
        )}
      >
        <div className="flex items-center gap-3">
          {status === 'completed' ? (
            <CheckCircle2 className="h-6 w-6 text-green-600" />
          ) : status === 'failed' ? (
            <AlertCircle className="h-6 w-6 text-red-600" />
          ) : (
            <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
          )}
          <CardTitle className="text-lg">
            {status === 'completed'
              ? '处理完成'
              : status === 'failed'
                ? '处理失败'
                : 'AI 正在思考...'}
          </CardTitle>
        </div>
      </CardHeader>

      <CardContent className="space-y-6 pt-6">
        {/* 进度条 */}
        {!isCompleted && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm text-gray-600">
              <span>{message}</span>
              <span className="font-medium">{progress}%</span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-gray-100">
              <div
                className="h-full bg-blue-500 transition-all duration-500 ease-out"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}

        {/* 错误信息 */}
        {status === 'failed' && (
          <div className="rounded-lg bg-red-50 p-4 text-sm text-red-700">
            {error || '发生未知错误'}
          </div>
        )}

        {/* 结果展示 */}
        {status === 'completed' && result && (
          <div className="animate-in fade-in slide-in-from-bottom-4 space-y-4 duration-500">
            <div className="space-y-1">
              <span className="text-xs font-semibold uppercase tracking-wider text-gray-400">
                您的指令
              </span>
              <p className="rounded-md bg-gray-50 p-3 text-gray-700">
                {result.analysis_result?.refined_text ||
                  result.analysis_result?.asr_text ||
                  '无内容'}
              </p>
            </div>

            {result.analysis_result?.tts_audio_url && (
              <div className="pt-2">
                <audio
                  ref={audioRef}
                  controls
                  className="h-10 w-full"
                  src={result.analysis_result.tts_audio_url}
                />
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
