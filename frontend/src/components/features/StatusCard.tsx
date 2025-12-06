import { useEffect, useRef } from 'react';
import { CheckCircle2, AlertCircle, Loader2, X } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { useVoiceProgress } from '@/hooks';
import { cn } from '@/lib/utils';

interface StatusCardProps {
  recordId: number | null;
}

export function StatusCard({ recordId }: StatusCardProps) {
  const { status, progress, message, result, error, isCompleted, cancel } = useVoiceProgress(recordId);

  const audioRef = useRef<HTMLAudioElement | null>(null);

  // 自动播放逻辑
  useEffect(() => {
    if (status === 'completed' && result?.analysis_result?.tts_audio_url && audioRef.current) {
      audioRef.current.play().catch((e) => console.log('自动播放被拦截:', e));
    }
  }, [status, result]);

  if (!recordId) return null;

  return (
    <Card className="mx-auto w-full overflow-hidden shadow-2xl transition-all duration-500">
      <CardHeader
        className={cn(
          'border-b-[0.3vh] transition-colors duration-300',
          status === 'completed' ? 'bg-green-50' : 
          status === 'failed' || status === 'cancelled' ? 'bg-red-50' : 
          'bg-blue-50'
        )}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-[2vh]">
            {status === 'completed' ? (
              <CheckCircle2 className="h-[3.5vh] w-[3.5vh] text-green-600" />
            ) : status === 'failed' || status === 'cancelled' ? (
              <AlertCircle className="h-[3.5vh] w-[3.5vh] text-red-600" />
            ) : (
              <Loader2 className="h-[3.5vh] w-[3.5vh] animate-spin text-blue-600" />
            )}
            <CardTitle className="text-[2.5vh] md:text-[3vh]">
              {status === 'completed'
                ? '处理完成'
                : status === 'failed'
                  ? '处理失败'
                  : status === 'cancelled'
                    ? '已取消'
                    : 'AI 正在思考...'}
            </CardTitle>
          </div>
          {/* 处理中时显示取消按钮 */}
          {!isCompleted && (
            <Button
              size="sm"
              variant="outline"
              onClick={cancel}
              className="h-[4vh] gap-[0.8vh] text-[1.6vh] text-red-600 hover:bg-red-50 hover:text-red-700"
            >
              <X className="h-[2vh] w-[2vh]" />
              取消
            </Button>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-[3vh] pt-[3vh] md:space-y-[4vh] md:pt-[4vh]">
        {/* 进度条 */}
        {!isCompleted && (
          <div className="space-y-[1.5vh]">
            <div className="flex justify-between text-[1.8vh] text-gray-600 md:text-[2vh]">
              <span>{message}</span>
              <span className="font-medium">{progress}%</span>
            </div>
            <div className="h-[1.2vh] overflow-hidden rounded-full bg-gray-100">
              <div
                className="h-full bg-blue-500 transition-all duration-500 ease-out"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}

        {/* 错误信息或取消信息 */}
        {(status === 'failed' || status === 'cancelled') && (
          <div className="rounded-[1.5vh] bg-red-50 p-[2.5vh] text-[1.8vh] text-red-700 md:text-[2vh]">
            {error || (status === 'cancelled' ? '任务已被取消' : '发生未知错误')}
          </div>
        )}

        {/* 结果展示 */}
        {status === 'completed' && result && (
          <div className="animate-in fade-in slide-in-from-bottom-4 space-y-[2.5vh] duration-500 md:space-y-[3vh]">
            <div className="space-y-[1.5vh]">
              <span className="text-[1.4vh] font-semibold uppercase tracking-wider text-gray-400 md:text-[1.6vh]">
                {
                  result.analysis_result?.decision === 'boundary' ? 'AI 确认' :
                  result.analysis_result?.decision === 'reject' ? 'AI 反馈' :
                  '您的指令'
                }
              </span>
              <p className="rounded-[1.5vh] bg-gray-50 p-[2.5vh] text-[1.8vh] leading-relaxed text-gray-700 md:text-[2vh]">
                {result.analysis_result?.response_text ||
                  result.analysis_result?.refined_text ||
                  result.analysis_result?.asr_text ||
                  '无内容'}
              </p>
            </div>

            {result.analysis_result?.tts_audio_url && (
              <div className="pt-[1.5vh]">
                <audio
                  ref={audioRef}
                  controls
                  className="h-[5vh] w-full md:h-[6vh]"
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
